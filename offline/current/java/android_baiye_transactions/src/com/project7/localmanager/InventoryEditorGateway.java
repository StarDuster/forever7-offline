package com.project7.localmanager;

import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** Same-session offline inventory/catalog editor. Original Store remains sole owner. */
public final class InventoryEditorGateway {
    private static final String CATALOG = "q7InventoryCatalogAsk";
    private static final String EDIT = "q7InventoryEditAsk";
    private static final String OPS = "_q7_inventory_ops_v1";
    private static final int MAX_BATCH = 64;
    private static final int MAX_CG_BATCH = 1024;
    private static final int MAX_RECEIPTS = 4096;
    private static final int LIMIT = 1000000;
    private static final int MAX_PROFILE_BYTES = 8 * 1024 * 1024;
    private static final Map<String, Object> ACCOUNT_LOCKS = new LinkedHashMap<>();
    private static final Method WRITE = BaiyeTransactions.Access.method(LocalGatewayServer.class, "writeFrame", void.class, false, OutputStream.class, int.class, byte[].class);
    private static final Method CALLBACK = BaiyeTransactions.Access.method(LocalGatewayServer.class, "completeCallback", void.class, false, OutputStream.class, byte[].class, int.class, String.class);
    private static final Method SPEND = BaiyeTransactions.Access.method(LocalCommerceEngine.class, "spend", byte[].class, true, byte[].class, String.class, int.class);
    private InventoryEditorGateway() {}

    public static boolean handleRequest(LocalGatewayServer gateway, OutputStream out, byte[] eid,
            String method, byte[] params, Integer callback, String account,
            LocalTutorialStore.Progress progress, LocalEventEngine engine) throws IOException {
        if (!CATALOG.equals(method) && !EDIT.equals(method)) return false;
        Object lock;
        synchronized (ACCOUNT_LOCKS) {
            lock = ACCOUNT_LOCKS.get(account);
            if (lock == null) ACCOUNT_LOCKS.put(account, lock = new Object());
        }
        synchronized (lock) {
            return handleRequestLocked(gateway, out, eid, method, params, callback, account, progress, engine);
        }
    }

    private static boolean handleRequestLocked(LocalGatewayServer gateway, OutputStream out, byte[] eid,
            String method, byte[] params, Integer callback, String account,
            LocalTutorialStore.Progress progress, LocalEventEngine engine) throws IOException {
        LocalResourceEngine.Result result;
        LocalProfileStore store = null;
        boolean refresh = false;
        try {
            if (account == null || !account.matches("[a-z0-9_.-]{1,32}")) throw new Rejected();
            Object provider = unwrapProvider(BaiyeTransactions.Access.PROVIDER.get(gateway));
            if (provider == null || provider.getClass() != LocalProfileStore.class) throw new Rejected();
            store = (LocalProfileStore) provider;
            if (CATALOG.equals(method)) result = catalog(store, account, params);
            else {
                result = replay(store, account, params);
                if (result != null) refresh = true;
                if (result == null) {
                    BaiyeTransactions.Outcome outcome = BaiyeTransactions.transactOutcome(store, account,
                            (before, resources) -> edit(before, resources, params, progress),
                            observed -> receiptResult(observed, params));
                    result = outcome.result;
                    refresh = true;
                }
            }
        } catch (BaiyeTransactions.UncertainCommit uncertain) {
            if (!EDIT.equals(method) || store == null) throw uncertain;
            try { result = recover(store, account, params); }
            catch (ReflectiveOperationException error) { throw new IOException(error); }
            if (result == null) throw uncertain;
            refresh = true;
        } catch (Rejected rejected) {
            result = failure(method, rejected.message, rejected.reason, params);
        } catch (ReflectiveOperationException error) {
            throw new IOException(error);
        }
        if (refresh && engine != null) refreshEngine(store, account, progress, engine, result.profile);
        publish(gateway, out, eid, result, method, callback);
        return true;
    }

    private static void refreshEngine(LocalProfileStore store, String account,
            LocalTutorialStore.Progress progress, LocalEventEngine engine, byte[] committed) throws IOException {
        // Stock snapshot performs time-driven normalization and can write.
        // Repair the live projection from the actual committed image without
        // entering that separate mutation path, including after a lost reply.
        synchronized (engine) {
            try {
                engine.refreshProfile(readProfile(store, account));
            } catch (ReflectiveOperationException unavailable) {
                throw new IOException("Inventory projection unavailable", unavailable);
            }
        }
    }

    private static LocalResourceEngine.Result replay(LocalProfileStore store, String account, byte[] params)
            throws IOException, ReflectiveOperationException, Rejected {
        String op = optionalString(params, "op", null);
        if (op == null || !op.matches("[0-9a-f]{32}")) return null;
        List<byte[]> rows = array(params, "batch", false);
        String fingerprint = fingerprint(op, rows);
        byte[] profile = readProfile(store, account);
        for (byte[] receipt : receipts(profile)) {
            if (!op.equals(BsonLite.stringValue(receipt, "op"))) continue;
            if (!fingerprint.equals(BsonLite.stringValue(receipt, "digest")))
                throw new Rejected("操作ID已用于不同请求。", 2);
            return replayResult(profile, receipt);
        }
        return null;
    }

    private static LocalResourceEngine.Result recover(LocalProfileStore store, String account, byte[] params)
            throws IOException, ReflectiveOperationException, Rejected {
        return receiptResult(readProfile(store, account), params);
    }

    private static LocalResourceEngine.Result receiptResult(byte[] profile, byte[] params)
            throws IOException, Rejected {
        String op = optionalString(params, "op", null);
        if (op == null || !op.matches("[0-9a-f]{32}")) return null;
        List<byte[]> rows = array(params, "batch", false);
        String fingerprint = fingerprint(op, rows);
        for (byte[] receipt : receipts(profile)) {
            if (op.equals(BsonLite.stringValue(receipt, "op")) &&
                    fingerprint.equals(BsonLite.stringValue(receipt, "digest")))
                return replayResult(profile, receipt);
        }
        return null;
    }

    private static final class InventoryIndex {
        final Map<Integer, Long> itemCounts = new LinkedHashMap<>();
        final Map<Integer, Long> treasureCounts = new LinkedHashMap<>();
    }

    private static List<byte[]> arrayRows(byte[] array) throws Rejected {
        BaiyeTransactions.document(array);
        List<byte[]> rows = LocalResourceEngine.array(array);
        if (rows.size() != BsonLite.keys(array).size()) throw new Rejected("对象数组无效。");
        return rows;
    }

    private static InventoryIndex inventoryIndex(byte[] profile) throws Rejected {
        InventoryIndex index = new InventoryIndex();
        Set<String> uuids = new HashSet<>();
        Map<String, Integer> seen = new LinkedHashMap<>();
        byte[] inv = BsonLite.documentValue(profile, "inv");
        byte[] items = inv == null ? null : BsonLite.arrayValue(inv, "items");
        if (items != null) {
            for (byte[] row : arrayRows(items)) {
                String uuid = BsonLite.uuidValue(row, "u");
                Integer id = BsonLite.intValue(row, "i");
                if (uuid == null || id == null || !uuids.add(uuid))
                    throw new Rejected("背包实例无效。");
                int count = integer(BsonLite.numericValue(row, "w"));
                if (count <= 0) throw new Rejected("背包数量无效。");
                index.itemCounts.put(id, add(index.itemCounts.get(id), count));
                seen.put(uuid, id);
            }
        }
        byte[] manager = BsonLite.documentValue(profile, "heromgr");
        byte[] heroes = manager == null ? null : BsonLite.arrayValue(manager, "hrs");
        if (heroes != null) {
            for (byte[] row : arrayRows(heroes)) {
                byte[] hero = BsonLite.documentValue(row, "1");
                byte[] ti = hero == null ? null : BsonLite.documentValue(hero, "ti");
                byte[] heroItems = ti == null ? null : BsonLite.arrayValue(ti, "items");
                if (heroItems == null) continue;
                for (byte[] item : arrayRows(heroItems)) {
                    String uuid = BsonLite.uuidValue(item, "u");
                    Integer id = BsonLite.intValue(item, "i");
                    if (uuid == null || id == null) throw new Rejected("影装实例无效。");
                    Integer prior = seen.putIfAbsent(uuid, id);
                    if (prior != null && !prior.equals(id)) throw new Rejected("影装 UUID 冲突。");
                }
            }
        }
        for (Map.Entry<String, Integer> entry : seen.entrySet())
            index.treasureCounts.put(entry.getValue(),
                    add(index.treasureCounts.get(entry.getValue()), 1));
        return index;
    }

    private static long add(Long prior, long value) {
        return prior == null ? value : Math.addExact(prior, value);
    }

    private static LocalResourceEngine.Result catalog(LocalProfileStore store, String account, byte[] params)
            throws IOException, ReflectiveOperationException, Rejected {
        BaiyeTransactions.document(params);
        List<String> keys = BsonLite.keys(params);
        Set<String> allowed = new HashSet<>(Arrays.asList("g", "q", "n", "o", "op", "_cbid_"));
        if (!allowed.containsAll(keys)) throw new Rejected();
        String nonce = optionalString(params, "op", null);
        if (nonce != null && !nonce.matches("[0-9a-f]{32}")) throw new Rejected();
        String group = optionalString(params, "g", "item");
        if (!Arrays.asList("item", "currency", "treasure").contains(group)) throw new Rejected("目录类别无效。");
        String requestQuery = optionalString(params, "q", "");
        String query = requestQuery.toLowerCase(java.util.Locale.ROOT);
        int limit = optionalInt(params, "n", 50);
        if (limit < 1 || limit > 100) throw new Rejected();
        // Catalog pages are ordered slices: the editor asks for [offset, offset+limit)
        // so a 380-entry treasure table is reachable instead of stopping at the
        // first page and looking incomplete.
        int offset = optionalInt(params, "o", 0);
        if (offset < 0) throw new Rejected();
        int matched = 0;
        byte[] profile = readProfile(store, account);
        InventoryIndex index = inventoryIndex(profile);
        LocalResourceEngine.Result result = new LocalResourceEngine.Result(profile);
        List<byte[]> rows = new ArrayList<>();
        if ("currency".equals(group)) {
            for (String key : coins()) {
                String label = currencyName(store.resources(), key);
                if (query.length() > 0 && !key.toLowerCase(java.util.Locale.ROOT).contains(query) &&
                        !label.toLowerCase(java.util.Locale.ROOT).contains(query)) continue;
                if (matched++ < offset) continue;
                rows.add(catalogRow("currency", 0, label, 0, 0, key, LocalResourceEngine.value(profile, key)));
                if (rows.size() >= limit) break;
            }
        } else {
            for (LocalResourceCatalog.Item item : store.resources().items.values()) {
                if (item == null || item.id <= 0 || item.wrap <= 0) continue;
                boolean treasure = item.type == 5;
                if (!treasure && item.type == 8) continue;
                if ("treasure".equals(group) != treasure) continue;
                String name = item.name == null ? "" : item.name;
                if (query.length() > 0 && !(Integer.toString(item.id).contains(query) || name.toLowerCase(java.util.Locale.ROOT).contains(query))) continue;
                if (matched++ < offset) continue;
                long count = treasure ? index.treasureCounts.getOrDefault(item.id, 0L)
                        : index.itemCounts.getOrDefault(item.id, 0L);
                rows.add(catalogRow(treasure ? "treasure" : "item", item.id, name, item.type,
                        treasure ? 100 : LIMIT, null, count));
                if (rows.size() >= limit) break;
            }
        }
        result.add("q7InventoryCatalogReply", BsonLite.document("rs", true, "g", group,
                "q", requestQuery, "o", offset, "op", nonce == null ? "" : nonce, "rows", rows));
        return result;
    }

    private static LocalResourceEngine.Result edit(byte[] before, LocalResourceCatalog resources, byte[] params,
            LocalTutorialStore.Progress progress) throws Rejected, IOException {
        BaiyeTransactions.document(params);
        List<String> keys = BsonLite.keys(params);
        Set<String> allowed = new HashSet<>(Arrays.asList("op", "batch", "_cbid_"));
        if (!allowed.containsAll(keys) || !keys.contains("op") || !keys.contains("batch")) throw new Rejected("参数不完整。");
        String op = BsonLite.stringValue(params, "op");
        if (op == null || !op.matches("[0-9a-f]{32}")) throw new Rejected("操作ID无效。");
        List<byte[]> rows = array(params, "batch", true);
        // CG unlocks are one row per id, so that class gets a wider batch.
        int cap = MAX_BATCH;
        boolean cgOnly = rows.size() > 0;
        for (byte[] row : rows) {
            if (!"cg".equals(optionalString(row, "k", ""))) { cgOnly = false; break; }
        }
        if (cgOnly) cap = MAX_CG_BATCH;
        if (rows.size() < 1 || rows.size() > cap) throw new Rejected("批量数量无效。");
        return commitRows(before, resources, rows, op, "q7InventoryEditReply", progress, 0);
    }

    private static LocalResourceEngine.Result commitRows(byte[] before, LocalResourceCatalog resources,
            List<byte[]> rows, String op, String replyMethod, LocalTutorialStore.Progress progress, int granted)
            throws Rejected, IOException {
        String fingerprint = fingerprint(op, rows);
        List<byte[]> receipts = receipts(before);
        for (byte[] receipt : receipts) {
            String prior = BsonLite.stringValue(receipt, "op");
            if (!op.equals(prior)) continue;
            if (!fingerprint.equals(BsonLite.stringValue(receipt, "digest")))
                throw new Rejected("操作ID已用于不同请求。", 2);
            throw new BaiyeTransactions.Replay(replayResult(before, receipt));
        }
        if (receipts.size() >= MAX_RECEIPTS) throw new Rejected("操作收据已满（4096），请先在游戏内完成或清理未决操作。");
        busy(before, progress);
        Set<String> beforeItems = inventoryUuids(before);
        LocalResourceEngine.Result result = new LocalResourceEngine.Result(before);
        for (byte[] row : rows) {
            try {
                applyRow(result, resources, row);
            } catch (IllegalArgumentException | ArithmeticException invalid) {
                throw new Rejected("资源校验失败。", 1);
            }
        }
        LocalResourceEngine.syncCurrencies(result);
        Set<String> afterItems = inventoryUuids(result.profile);
        List<String> deleted = new ArrayList<>();
        for (String uuid : beforeItems) if (!afterItems.contains(uuid)) deleted.add(uuid);
        byte[] reply = granted > 0 ? BsonLite.document("m", replyMethod, "p",
                        BsonLite.document("rs", true, "op", op, "n", granted))
                : BsonLite.document("m", replyMethod, "p", BsonLite.document("rs", true, "op", op));
        result.add(replyMethod, granted > 0 ? BsonLite.document("rs", true, "op", op, "n", granted)
                : BsonLite.document("rs", true, "op", op));
        receipts.add(BsonLite.document("op", op, "digest", fingerprint, "reply", reply,
                "deleted", deletedString(deleted), "commit", receipts.size() + 1));
        byte[] receiptDoc = BsonLite.withProfileInt(BsonLite.EMPTY_DOCUMENT, "schema", 1);
        receiptDoc = BsonLite.withProfileArray(receiptDoc, "ops", receipts);
        result.profile = BsonLite.withProfileDocument(result.profile, OPS, receiptDoc);
        if (result.profile.length > MAX_PROFILE_BYTES) throw new Rejected("角色档案过大。");
        return result;
    }

    private static void applyRow(LocalResourceEngine.Result result, LocalResourceCatalog resources, byte[] row) throws IOException {
        BaiyeTransactions.document(row);
        List<String> keys = BsonLite.keys(row);
        Set<String> allowed = new HashSet<>(Arrays.asList("k", "i", "c", "m", "n", "q"));
        if (!allowed.containsAll(keys) || !keys.contains("k") || !keys.contains("m")) throw new Rejected("行参数无效。");
        String kind = BsonLite.stringValue(row, "k");
        if ("bulk".equals(kind)) {
            applyBulk(result, resources, BsonLite.stringValue(row, "m"));
            return;
        }
        if ("cg".equals(kind)) {
            applyCg(result, BsonLite.numericValue(row, "i"));
            return;
        }
        String mode = BsonLite.stringValue(row, "m");
        int amount = integer(BsonLite.numericValue(row, "n"));
        if (amount < 0 || amount > LIMIT) throw new Rejected("数量边界无效。");
        if ("item".equals(kind)) {
            int id = integer(BsonLite.numericValue(row, "i"));
            LocalResourceCatalog.Item item = resources.items.get(id);
            if (item == null || item.type == 5) throw new Rejected("道具ID无效。");
            long before = BaiyeTransactions.count(result.profile, id);
            long target = "set".equals(mode) ? amount : Math.addExact(before, amount);
            if (target < 0 || target > LIMIT || !"set".equals(mode) && !"add".equals(mode)) throw new Rejected("道具数量无效。");
            long delta = target - before;
            if (delta > 0) LocalResourceEngine.grant(result, resources, "item", id, (int) delta, 1);
            else if (delta < 0) LocalGiftEngine.consume(result, id, (int) -delta);
            if (BaiyeTransactions.count(result.profile, id) != target) throw new Rejected("道具数量后置校验失败。");
        } else if ("currency".equals(kind)) {
            String key = BsonLite.stringValue(row, "c");
            if (!currency(key)) throw new Rejected("货币类型无效。");
            int before = LocalResourceEngine.value(result.profile, key);
            long target = "set".equals(mode) ? amount : "add".equals(mode) ? (long) before + amount : -1;
            if (target < 0 || target > Integer.MAX_VALUE) throw new Rejected("货币数量无效。");
            int delta = (int) (target - before);
            if (delta > 0) LocalResourceEngine.grant(result, resources, key, 0, delta, 1);
            else if (delta < 0) result.profile = (byte[]) BaiyeTransactions.call(SPEND, null, result.profile, key, -delta);
            if (LocalResourceEngine.value(result.profile, key) != target) throw new Rejected("货币数量后置校验失败。");
        } else if ("treasure".equals(kind)) {
            if (!"create".equals(mode)) throw new Rejected("影装只支持独立生成。");
            int id = integer(BsonLite.numericValue(row, "i"));
            int quality = optionalInt(row, "q", 1);
            LocalResourceCatalog.Item item = resources.items.get(id);
            if (item == null || item.type != 5 || quality < 1 || amount < 1 || amount > 100) throw new Rejected("影装ID或数量无效。");
            LocalResourceEngine.grant(result, resources, "treasure", id, amount, quality);
        } else {
            throw new Rejected("编辑类别无效。");
        }
    }

    /**
     * One-tap class grant. Letters are the 2018/… valentine family, gifts are
     * the per-hero present rows, shards are hero fragments, currency tops every
     * coin up to LIMIT. Missing entries are added at one; owned rows keep their
     * amount so a second tap is a no-op.
     */
    private static void applyBulk(LocalResourceEngine.Result result, LocalResourceCatalog resources, String kind)
            throws IOException {
        if (kind == null) throw new Rejected("快捷类别无效。");
        if ("currency".equals(kind)) {
            List<String> coins;
            try { coins = coins(); } catch (ReflectiveOperationException missing) { throw new Rejected("货币表不可用。"); }
            for (String key : coins) {
                int delta = LIMIT - LocalResourceEngine.value(result.profile, key);
                if (delta > 0) LocalResourceEngine.grant(result, resources, key, 0, delta, 1);
            }
            return;
        }
        boolean letters = "letters".equals(kind);
        // The replica letter picker offers the 2018/2019 letters a player does
        // not own yet; pre-granting both families empties that list.
        boolean keep = "letters_keep".equals(kind);
        // Recovery for profiles that granted everything: drop only the two
        // families the replica picker offers, so it lists heroes again.
        boolean reset = "letters_reset".equals(kind);
        boolean gifts = "gifts".equals(kind);
        boolean shards = "shards".equals(kind);
        if (!letters && !keep && !gifts && !shards && !reset) throw new Rejected("快捷类别无效。");
        if (keep) letters = true;
        List<Integer> ids = new ArrayList<>(resources.items.keySet());
        Collections.sort(ids);
        for (Integer value : ids) {
            if (value == null || value <= 0) continue;
            LocalResourceCatalog.Item item = resources.items.get(value);
            if (item == null || item.wrap <= 0 || item.type == 5) continue;
            String name = item.name == null ? "" : item.name;
            boolean hit = letters ? name.contains("情书")
                    : shards ? item.type == 3
                    : item.type == 13 && name.startsWith("礼物");
            if (hit && keep && (name.startsWith("情书2018") ||
                    name.startsWith("情书2019"))) hit = false;
            if (reset && (name.startsWith("情书2018") || name.startsWith("情书2019"))) {
                long owned = BaiyeTransactions.count(result.profile, value);
                if (owned > 0) LocalGiftEngine.consume(result, value, (int) owned);
                continue;
            }
            if (!hit) continue;
            if (BaiyeTransactions.count(result.profile, value) >= 1) continue;
            LocalResourceEngine.grant(result, resources, "item", value, 1, 1);
        }
        if (letters) {
            // Letter selectors (replica / 2020 / 2021 / past) stay usable when
            // the full letter set is owned: top each one up to 99 uses.
            int[] selectors = {11514, 11527, 13064, 13172, 15403};
            for (int id : selectors) {
                LocalResourceCatalog.Item item = resources.items.get(id);
                if (item == null || item.wrap <= 0 || item.type == 5) continue;
                long current = BaiyeTransactions.count(result.profile, id);
                if (current >= 99) continue;
                LocalResourceEngine.grant(result, resources, "item", id, (int) (99 - current), 1);
            }
        }
    }

    /** Merges one CG id into the profile's unlock list. */
    private static void applyCg(LocalResourceEngine.Result result, Number raw) throws IOException {
        int cg = integer(raw);
        if (cg < 1 || cg > 1000000) throw new Rejected("CG编号无效。");
        List<Integer> current = BsonLite.keys(result.profile).contains("cgs")
                ? BsonLite.intArrayValues(result.profile, "cgs") : null;
        java.util.TreeSet<Integer> merged = new java.util.TreeSet<>();
        if (current != null) merged.addAll(current);
        if (!merged.add(cg)) return;
        result.profile = BsonLite.withProfileArray(result.profile, "cgs",
                new ArrayList<Integer>(merged));
    }

    private static void busy(byte[] profile, LocalTutorialStore.Progress progress) throws Rejected {
        for (String key : new String[]{"q7Battle", "q7WingBattle", "q7DailyBattle"})
            if (activeDocument(profile, key)) throw new Rejected("当前战斗进行中。");
        byte[] weekResult = BsonLite.documentValue(profile, "q7WeekResult");
        if (weekResult != null && (Boolean.TRUE.equals(BsonLite.boolValue(weekResult, "active")) ||
                Boolean.TRUE.equals(BsonLite.boolValue(weekResult, "pending"))))
            throw new Rejected("当前周目结算进行中。");
        byte[] transition = BsonLite.documentValue(profile, "q7WeekTransition");
        String transitionId = transition == null ? null : BsonLite.stringValue(transition, "id");
        if (transitionId != null && (progress == null || !transitionId.equals(progress.weekCommit)))
            throw new Rejected("当前周目切换进行中。");
    }

    private static boolean activeDocument(byte[] profile, String key) {
        byte[] value = BsonLite.documentValue(profile, key);
        return value != null && !BsonLite.keys(value).isEmpty();
    }

    private static boolean currency(String key) {
        return LocalResourceEngine.currency(key);
    }

    private static List<String> coins() throws ReflectiveOperationException {
        Field field = LocalResourceEngine.class.getDeclaredField("COINS");
        field.setAccessible(true);
        String[] values = (String[]) field.get(null);
        if (values == null || values.length == 0) throw new ReflectiveOperationException("COINS");
        return Arrays.asList(values.clone());
    }

    private static String fingerprint(String op, List<byte[]> rows) throws Rejected {
        StringBuilder out = new StringBuilder(op);
        for (byte[] row : rows) {
            BaiyeTransactions.document(row);
            List<String> keys = BsonLite.keys(row);
            Set<String> allowed = new HashSet<>(Arrays.asList("k", "i", "c", "m", "n", "q"));
            if (!allowed.containsAll(keys) || !keys.contains("k") || !keys.contains("m")) throw new Rejected("行参数无效。");
            String kind = BsonLite.stringValue(row, "k");
            String mode = BsonLite.stringValue(row, "m");
            out.append('\u0000').append(kind).append(':').append(mode);
            if ("bulk".equals(kind)) continue;
            if ("cg".equals(kind)) {
                out.append(':').append(integer(BsonLite.numericValue(row, "i")));
                continue;
            }
            int amount = integer(BsonLite.numericValue(row, "n"));
            out.append(':').append(amount);
            if ("item".equals(kind)) out.append(':').append(integer(BsonLite.numericValue(row, "i")));
            else if ("currency".equals(kind)) {
                String key = BsonLite.stringValue(row, "c");
                if (key == null) throw new Rejected("货币类型无效。");
                out.append(':').append(key);
            } else if ("treasure".equals(kind)) out.append(':').append(integer(BsonLite.numericValue(row, "i")))
                    .append(':').append(optionalInt(row, "q", 1));
            else throw new Rejected("编辑类别无效。");
        }
        return sha256(out.toString().getBytes(StandardCharsets.UTF_8));
    }

    /** First seven names match the stock MainActivity resource-type spinner. */
    private static String currencyName(LocalResourceCatalog resources, String key) {
        String[] keys = {"money", "yuanbao", "crystal", "summonCoin", "giftCoin", "friendCoin", "souvenir"};
        String[] labels = {"\u91d1\u5e01", "\u94bb\u77f3", "\u6676\u94bb", "\u6b27\u6cca", "\u94c3\u94db", "\u53cb\u60c5\u70b9", "\u7eaa\u5ff5\u5238"};
        for (int i = 0; i < keys.length; i++) if (keys[i].equals(key)) return labels[i];
        LocalResourceCatalog.Item item = resources.items.get(LocalResourceEngine.currencyItem(key));
        return item != null && item.name != null && !item.name.isEmpty() ? item.name : key;
    }

    private static List<byte[]> receipts(byte[] profile) throws Rejected {
        try {
            byte[] ops = BsonLite.documentValue(profile, OPS);
            if (ops == null && !BsonLite.keys(profile).contains(OPS)) return new ArrayList<>();
            if (ops == null || !Integer.valueOf(1).equals(BsonLite.intValue(ops, "schema")))
                throw new Rejected("收据格式无效。");
            List<byte[]> rows = array(ops, "ops", false);
            if (rows.isEmpty()) throw new Rejected("收据记录为空。");
            return rows;
        } catch (Rejected | RuntimeException invalid) {
            throw new Rejected("历史操作记录需要核对，已保留原操作。", 2);
        }
    }

    private static LocalResourceEngine.Result replayResult(byte[] profile, byte[] receipt) throws Rejected {
        try {
            return replayResultChecked(profile, receipt);
        } catch (Rejected | RuntimeException invalid) {
            throw new Rejected("已提交操作的记录需要核对，已保留原操作。", 2);
        }
    }

    private static LocalResourceEngine.Result replayResultChecked(byte[] profile, byte[] receipt) throws Rejected {
        byte[] reply = BsonLite.documentValue(receipt, "reply");
        if (reply == null) throw new Rejected("操作收据不完整。");
        String method = BsonLite.stringValue(reply, "m");
        byte[] parameters = BsonLite.documentValue(reply, "p");
        if (!"q7InventoryEditReply".equals(method) || parameters == null ||
                !Boolean.TRUE.equals(BsonLite.boolValue(parameters, "rs")) ||
                !BsonLite.stringValue(receipt, "op").equals(BsonLite.stringValue(parameters, "op")))
            throw new Rejected("操作收据无效。");
        LocalResourceEngine.Result result = new LocalResourceEngine.Result(profile);
        List<BsonLite.UuidValue> deleted = deletedList(BsonLite.stringValue(receipt, "deleted"));
        if (!deleted.isEmpty()) result.add("deleteItems", BsonLite.document("i", deleted));
        byte[] items = inventoryRows(profile);
        if (items != null) result.add("updateItems", BsonLite.document("i", LocalResourceEngine.array(items)));
        LocalResourceEngine.syncCurrencies(result);
        result.add(method, parameters);
        return result;
    }

    private static Set<String> inventoryUuids(byte[] profile) throws Rejected {
        Set<String> uuids = new HashSet<>();
        byte[] inv = BsonLite.documentValue(profile, "inv");
        byte[] items = inv == null ? null : BsonLite.arrayValue(inv, "items");
        if (items == null) return uuids;
        BaiyeTransactions.document(items);
        for (byte[] row : LocalResourceEngine.array(items)) {
            String uuid = BsonLite.uuidValue(row, "u");
            if (uuid == null || !uuids.add(uuid)) throw new Rejected("背包 UUID 无效。");
        }
        return uuids;
    }

    private static String deletedString(List<String> deleted) {
        StringBuilder out = new StringBuilder();
        for (String uuid : deleted) {
            if (out.length() > 0) out.append(',');
            out.append(uuid);
        }
        return out.toString();
    }

    private static List<BsonLite.UuidValue> deletedList(String value) throws Rejected {
        List<BsonLite.UuidValue> result = new ArrayList<>();
        if (value == null || value.length() == 0) return result;
        for (String uuid : value.split(",")) {
            if (uuid.length() == 0) throw new Rejected("删除收据无效。");
            result.add(new BsonLite.UuidValue(uuid));
        }
        return result;
    }

    private static byte[] inventoryRows(byte[] profile) throws Rejected {
        byte[] inv = BsonLite.documentValue(profile, "inv");
        if (inv == null) return null;
        byte[] items = BsonLite.arrayValue(inv, "items");
        if (items == null) return null;
        BaiyeTransactions.document(items);
        List<byte[]> rows = LocalResourceEngine.array(items);
        if (rows.size() != BsonLite.keys(items).size()) throw new Rejected("背包数组无效。");
        return items;
    }

    private static byte[] readProfile(LocalProfileStore store, String account) throws IOException, ReflectiveOperationException, Rejected {
        synchronized (store) {
            synchronized (BaiyeTransactions.Access.LOCK.get(null)) {
                File directory = (File) BaiyeTransactions.Access.DIR.get(store);
                File file = new File(directory, account + ".bson");
                if (!file.isFile() || !file.getCanonicalFile().getParentFile().equals(directory.getCanonicalFile()))
                    throw new IOException("Inventory profile unavailable");
                byte[] profile = (byte[]) BaiyeTransactions.call(BaiyeTransactions.Access.READ, null, file);
                BaiyeTransactions.document(profile);
                if (!account.equals(BsonLite.stringValue(profile, "account")) ||
                        !account.equals(BsonLite.stringValue(profile, "an")))
                    throw new IOException("Inventory profile identity unavailable");
                return profile;
            }
        }
    }

    private static byte[] catalogRow(String kind, int id, String name, int type, int limit,
            String currency, long count) throws IOException {
        java.io.ByteArrayOutputStream body = new java.io.ByteArrayOutputStream();
        stringElement(body, "k", kind);
        if (id > 0) intElement(body, "i", id);
        if (name != null) stringElement(body, "name", name);
        if (type > 0) intElement(body, "type", type);
        if (limit > 0) intElement(body, "limit", limit);
        if (currency != null) stringElement(body, "c", currency);
        longElement(body, "n", count);
        byte[] payload = body.toByteArray();
        java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream();
        int32Bytes(out, payload.length + 5);
        out.write(payload, 0, payload.length);
        out.write(0);
        return out.toByteArray();
    }

    private static void stringElement(java.io.ByteArrayOutputStream out, String key, String value) throws IOException {
        out.write(2);
        cstring(out, key);
        byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
        int32Bytes(out, bytes.length + 1);
        out.write(bytes, 0, bytes.length);
        out.write(0);
    }

    private static void intElement(java.io.ByteArrayOutputStream out, String key, int value) throws IOException {
        out.write(16);
        if (key != null) cstring(out, key);
        int32Bytes(out, value);
    }

    private static void int32Bytes(java.io.ByteArrayOutputStream out, int value) throws IOException {
        out.write(value & 255);
        out.write((value >>> 8) & 255);
        out.write((value >>> 16) & 255);
        out.write((value >>> 24) & 255);
    }

    private static void longElement(java.io.ByteArrayOutputStream out, String key, long value) throws IOException {
        out.write(18);
        cstring(out, key);
        longElementBytes(out, value);
    }

    private static void longElementBytes(java.io.ByteArrayOutputStream out, long value) throws IOException {
        out.write((int) (value & 255));
        out.write((int) ((value >>> 8) & 255));
        out.write((int) ((value >>> 16) & 255));
        out.write((int) ((value >>> 24) & 255));
        out.write((int) ((value >>> 32) & 255));
        out.write((int) ((value >>> 40) & 255));
        out.write((int) ((value >>> 48) & 255));
        out.write((int) ((value >>> 56) & 255));
    }

    private static void cstring(java.io.ByteArrayOutputStream out, String value) throws IOException {
        byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
        out.write(bytes, 0, bytes.length);
        out.write(0);
    }

    private static List<byte[]> array(byte[] doc, String key, boolean optional) throws Rejected {
        byte[] value = BsonLite.arrayValue(doc, key);
        if (value == null) {
            if (optional && !BsonLite.keys(doc).contains(key)) return new ArrayList<>();
            throw new Rejected("数组字段无效。");
        }
        BaiyeTransactions.document(value);
        List<byte[]> rows = LocalResourceEngine.array(value);
        if (rows.size() != BsonLite.keys(value).size()) throw new Rejected("数组元素无效。");
        return rows;
    }

    private static String optionalString(byte[] doc, String key, String fallback) throws Rejected {
        if (!BsonLite.keys(doc).contains(key)) return fallback;
        String value = BsonLite.stringValue(doc, key);
        if (value == null) throw new Rejected("字符串字段无效。");
        return value;
    }

    private static int optionalInt(byte[] doc, String key, int fallback) throws Rejected {
        if (!BsonLite.keys(doc).contains(key)) return fallback;
        return integer(BsonLite.numericValue(doc, key));
    }

    private static int integer(Number value) throws Rejected {
        if (!(value instanceof Integer) && !(value instanceof Long)) throw new Rejected("整数类型无效。");
        long n = value.longValue();
        if (n < 0 || n > Integer.MAX_VALUE) throw new Rejected("整数边界无效。");
        return (int) n;
    }

    private static LocalResourceEngine.Result failure(String method, String message, int reason, byte[] params) {
        LocalResourceEngine.Result result = new LocalResourceEngine.Result(BsonLite.EMPTY_DOCUMENT);
        result.add("showMessageStr", BsonLite.document("m", message));
        String reply = CATALOG.equals(method) ? "q7InventoryCatalogReply" : "q7InventoryEditReply";
        String op = validOp(params);
        byte[] body = op == null ? BsonLite.document("rs", false, "reason", reason)
                : BsonLite.document("rs", false, "reason", reason, "op", op);
        result.add(reply, body);
        return result;
    }

    private static String validOp(byte[] params) {
        if (params == null) return null;
        try {
            String op = BsonLite.stringValue(params, "op");
            return op != null && op.matches("[0-9a-f]{32}") ? op : null;
        } catch (RuntimeException invalid) { return null; }
    }

    private static void publish(LocalGatewayServer gateway, OutputStream out, byte[] eid,
            LocalResourceEngine.Result result, String requestMethod, Integer callback) throws IOException {
        for (LocalResourceEngine.Reply reply : result.replies)
            BaiyeTransactions.call(WRITE, gateway, out, 5, ProtoLite.entityMessage(eid, digest(reply.method), reply.parameters));
        if (callback != null && callback > 0)
            BaiyeTransactions.call(CALLBACK, gateway, out, eid, callback, requestMethod);
    }

    private static byte[] digest(String method) {
        try { return MessageDigest.getInstance("MD5").digest(method.getBytes(StandardCharsets.UTF_8)); }
        catch (NoSuchAlgorithmException e) { throw new IllegalStateException(e); }
    }

    private static String sha256(byte[] data) {
        try {
            byte[] hash = MessageDigest.getInstance("SHA-256").digest(data);
            StringBuilder out = new StringBuilder();
            for (byte b : hash) out.append(String.format(java.util.Locale.ROOT, "%02x", b & 255));
            return out.toString();
        } catch (NoSuchAlgorithmException e) { throw new IllegalStateException(e); }
    }

    private static Object unwrapProvider(Object provider) {
        if (provider == null || !"FailureSafeProfileProvider".equals(provider.getClass().getSimpleName())) return provider;
        try {
            Method method = provider.getClass().getDeclaredMethod("delegate");
            method.setAccessible(true);
            Object delegate = method.invoke(provider);
            return delegate == null ? provider : delegate;
        } catch (Exception ignored) { return provider; }
    }

    private static final class Rejected extends IOException {
        final String message;
        final int reason;
        Rejected() { this("本次管理操作未提交。", 1); }
        Rejected(String message) { this(message, 1); }
        Rejected(String message, int reason) { super(message); this.message = message; this.reason = reason; }
    }
}
