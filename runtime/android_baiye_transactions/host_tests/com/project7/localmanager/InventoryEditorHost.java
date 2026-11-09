package com.project7.localmanager;

import android.system.Os;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

/** Actual manager transaction test for the new inventory editor gateway. */
public final class InventoryEditorHost {
    static void check(boolean value, String message) { if (!value) throw new AssertionError(message); }
    static String op(char fill) { char[] chars = new char[32]; Arrays.fill(chars, fill); return new String(chars); }
    static byte[] edit(String op, byte[]... rows) { return edit(op, 9, rows); }
    static byte[] edit(String op, int callback, byte[]... rows) { return BsonLite.document("op", op, "batch", Arrays.asList(rows), "_cbid_", callback); }
    static byte[] row(String kind, int id, String mode, int n) { return BsonLite.document("k", kind, "i", id, "m", mode, "n", n); }
    static byte[] currency(String key, String mode, int n) { return BsonLite.document("k", "currency", "c", key, "m", mode, "n", n); }
    static List<ProtoLite.EntityMessage> call(BaiyeHost.Disk disk, String method, byte[] params) throws Exception {
        return call(disk, method, params, null);
    }
    static List<ProtoLite.EntityMessage> call(BaiyeHost.Disk disk, String method, byte[] params,
            LocalTutorialStore.Progress progress) throws Exception {
        return call(disk, method, params, progress, null);
    }
    static List<ProtoLite.EntityMessage> call(BaiyeHost.Disk disk, String method, byte[] params,
            LocalTutorialStore.Progress progress, LocalEventEngine engine) throws Exception {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        check(InventoryEditorGateway.handleRequest(disk.g, out, BaiyeHost.EID, method, params, 11,
                BaiyeHost.ACCOUNT, progress, engine), "handled");
        return BaiyeHost.frames(out.toByteArray());
    }
    static int bsonFieldType(byte[] doc, String wanted) {
        int pos = 4;
        while (pos < doc.length - 1) {
            int type = doc[pos++] & 255;
            int start = pos;
            while (doc[pos] != 0) pos++;
            String key = new String(doc, start, pos - start, java.nio.charset.StandardCharsets.UTF_8);
            pos++;
            if (key.equals(wanted)) return type;
            if (type == 1 || type == 18) pos += 8;
            else if (type == 16) pos += 4;
            else if (type == 2) { int n = java.nio.ByteBuffer.wrap(doc, pos, 4).order(java.nio.ByteOrder.LITTLE_ENDIAN).getInt(); pos += 4 + n; }
            else if (type == 3 || type == 4) { int n = java.nio.ByteBuffer.wrap(doc, pos, 4).order(java.nio.ByteOrder.LITTLE_ENDIAN).getInt(); pos += n; }
            else if (type == 7) pos += 12;
            else if (type == 5) { int n = java.nio.ByteBuffer.wrap(doc, pos, 4).order(java.nio.ByteOrder.LITTLE_ENDIAN).getInt(); pos += 5 + n; }
            else throw new AssertionError("unsupported bson type " + type);
        }
        throw new AssertionError("missing bson field " + wanted);
    }

    static int bsonArrayFirstType(byte[] doc, String wanted) {
        int pos = 4;
        while (pos < doc.length - 1) {
            int type = doc[pos++] & 255;
            int start = pos;
            while (doc[pos] != 0) pos++;
            String key = new String(doc, start, pos - start, java.nio.charset.StandardCharsets.UTF_8);
            pos++;
            if (key.equals(wanted)) {
                if (type != 4) throw new AssertionError("not array");
                return doc[pos + 4] & 255;
            }
            if (type == 1 || type == 18) pos += 8;
            else if (type == 16) pos += 4;
            else if (type == 2) { int n = java.nio.ByteBuffer.wrap(doc, pos, 4).order(java.nio.ByteOrder.LITTLE_ENDIAN).getInt(); pos += 4 + n; }
            else if (type == 3 || type == 4) { int n = java.nio.ByteBuffer.wrap(doc, pos, 4).order(java.nio.ByteOrder.LITTLE_ENDIAN).getInt(); pos += n; }
            else if (type == 7) pos += 12;
            else if (type == 5) { int n = java.nio.ByteBuffer.wrap(doc, pos, 4).order(java.nio.ByteOrder.LITTLE_ENDIAN).getInt(); pos += 5 + n; }
            else throw new AssertionError("unsupported bson type " + type);
        }
        throw new AssertionError("missing bson field " + wanted);
    }

    static boolean hasMethod(List<ProtoLite.EntityMessage> frames, String method) {
        for (ProtoLite.EntityMessage frame : frames)
            if (Arrays.equals(frame.methodMd5, BaiyeGateway.digest(method))) return true;
        return false;
    }
    static boolean lastMethod(List<ProtoLite.EntityMessage> frames, String method) {
        byte[] callback = BaiyeGateway.digest("serverCallbackCarrier");
        for (int i = frames.size() - 1; i >= 0; i--) {
            ProtoLite.EntityMessage frame = frames.get(i);
            if (Arrays.equals(frame.methodMd5, callback)) continue;
            return Arrays.equals(frame.methodMd5, BaiyeGateway.digest(method));
        }
        return false;
    }
    static ProtoLite.EntityMessage reply(List<ProtoLite.EntityMessage> frames, String method) {
        for (ProtoLite.EntityMessage frame : frames)
            if (Arrays.equals(frame.methodMd5, BaiyeGateway.digest(method))) return frame;
        throw new AssertionError("missing " + method);
    }
    static void callback(List<ProtoLite.EntityMessage> frames) {
        int callbacks = 0;
        for (ProtoLite.EntityMessage frame : frames)
            if (Arrays.equals(frame.methodMd5, BaiyeGateway.digest("serverCallbackCarrier"))) callbacks++;
        check(callbacks == 1, "one stock callback");
    }
    static long inventory(byte[] profile, int id) { return BaiyeTransactions.count(profile, id); }
    static int treasureCount(byte[] profile, int id) {
        byte[] items = BsonLite.arrayValue(BsonLite.documentValue(profile, "inv"), "items");
        int count = 0;
        Set<String> uuids = new HashSet<>();
        for (byte[] row : LocalResourceEngine.array(items)) {
            check(uuids.add(BsonLite.uuidValue(row, "u")), "unique uuid");
            if (Integer.valueOf(id).equals(BsonLite.intValue(row, "i"))) count++;
        }
        return count;
    }
    static byte[] fullProfile(int itemRows, int heroes) {
        List<byte[]> items = new ArrayList<>();
        for (int i = 0; i < itemRows; i++) items.add(BaiyeHost.item(1, 1));
        List<byte[]> heroRows = new ArrayList<>();
        for (int i = 0; i < heroes; i++) {
            byte[] treasure = BaiyeHost.item(1001, 1);
            heroRows.add(BsonLite.document("0", i + 1, "1", BsonLite.document("ti",
                    BsonLite.document("items", Arrays.asList(treasure)))));
        }
        return BsonLite.document("account", BaiyeHost.ACCOUNT, "an", BaiyeHost.ACCOUNT, "st", 900999,
                "money", 0, "inv", BsonLite.document("items", items, "opaque", "preserve"),
                "heromgr", BsonLite.document("hrs", heroRows), "unknown", "preserve");
    }

    static byte[] profile(int item, int count, int money) {
        return BsonLite.document("account", BaiyeHost.ACCOUNT, "an", BaiyeHost.ACCOUNT, "st", 900999,
                "money", money, "inv", BsonLite.document("items", count > 0 ? Arrays.asList(BaiyeHost.item(item, count)) : Arrays.asList(), "opaque", "preserve"),
                "unknown", "preserve");
    }
    public static void main(String[] args) throws Exception {
        File assets = new File(args[0]);
        android.content.Context context = new android.content.Context(assets, new android.content.res.AssetManager(assets));
        HistoryDrawPolicy.prepare(context);
        SelectorPolicy.prepare(context);
        try (BaiyeHost.Disk disk = new BaiyeHost.Disk(assets, profile(1, 5, 100))) {
            byte[] before = disk.read();
            byte[] params = edit(op('a'), row("item", 1, "set", 7), currency("money", "set", 70));
            List<ProtoLite.EntityMessage> first = call(disk, "q7InventoryEditAsk", params);
            callback(first);
            byte[] editReply = reply(first, "q7InventoryEditReply").parameters;
            check(BsonLite.boolValue(editReply, "rs"), "accepted");
            check(inventory(disk.read(), 1) == 7, "item set exact");
            check(BsonLite.intValue(disk.read(), "money") == 70, "currency set exact");
            check("preserve".equals(BsonLite.stringValue(disk.read(), "unknown")), "unknown preserved");
            byte[] receiptDoc = BsonLite.documentValue(disk.read(), "_q7_inventory_ops_v1");
            check(receiptDoc != null && BsonLite.keys(receiptDoc).size() == 2, "receipt envelope");
            byte[] committed = disk.read();
            callback(call(disk, "q7InventoryEditAsk", edit(op('a'), 77, row("item", 1, "set", 7), currency("money", "set", 70))));
            check(Arrays.equals(committed, disk.read()), "same business op/digest replay ignores changed callback and does not write");
            callback(call(disk, "q7InventoryEditAsk", edit(op('a'), BsonLite.document("k", "item", "i", 1, "m", "set", "n", 7), currency("money", "set", 70))));
            check(Arrays.equals(committed, disk.read()), "same business op/digest replay normalizes BSON key order and numeric encoding");
            List<ProtoLite.EntityMessage> conflict = call(disk, "q7InventoryEditAsk", edit(op('a'), row("item", 1, "add", 1)));
            check(!BsonLite.boolValue(reply(conflict, "q7InventoryEditReply").parameters, "rs"), "same op different digest rejected");
            check(op('a').equals(BsonLite.stringValue(reply(conflict, "q7InventoryEditReply").parameters, "op")), "failure echoes validated op");
            check(Arrays.equals(committed, disk.read()), "conflict no mutation");
            byte[] failed = disk.read();
            List<ProtoLite.EntityMessage> missing = call(disk, "q7InventoryEditAsk", edit(op('b'), row("item", 999999, "add", 1)));
            check(!BsonLite.boolValue(reply(missing, "q7InventoryEditReply").parameters, "rs"), "unknown catalog id rejected");
            check(Arrays.equals(failed, disk.read()), "rejected no mutation");
            callback(call(disk, "q7InventoryEditAsk", edit(op('c'), BsonLite.document("k", "treasure", "i", 1001, "m", "create", "n", 2, "q", 1))));
            check(treasureCount(disk.read(), 1001) == 2, "treasure create exact");
            callback(call(disk, "q7InventoryEditAsk", edit(op('d'), currency("money", "set", 25))));
            check(BsonLite.intValue(disk.read(), "money") == 25, "currency spend exact");
            callback(call(disk, "q7InventoryEditAsk", edit(op('e'), currency("money", "add", 30))));
            check(BsonLite.intValue(disk.read(), "money") == 55, "currency add exact");
            byte[] busy = BsonLite.withProfileDocument(disk.read(), "q7Battle", BsonLite.document("battle", 1));
            try (BaiyeHost.Disk busyDisk = new BaiyeHost.Disk(assets, busy)) {
                byte[] busyBefore = busyDisk.read();
                List<ProtoLite.EntityMessage> rejected = call(busyDisk, "q7InventoryEditAsk", edit(op('f'), row("item", 1, "add", 1)));
                check(!BsonLite.boolValue(reply(rejected, "q7InventoryEditReply").parameters, "rs"), "busy rejected");
                check(Arrays.equals(busyBefore, busyDisk.read()), "busy no mutation");
            }
            try (BaiyeHost.Disk emptyBattle = new BaiyeHost.Disk(assets, BsonLite.withProfileDocument(profile(1, 1, 0), "q7Battle", BsonLite.EMPTY_DOCUMENT))) {
                List<ProtoLite.EntityMessage> idle = call(emptyBattle, "q7InventoryEditAsk", edit(op('1'), row("item", 1, "add", 1)));
                check(BsonLite.boolValue(reply(idle, "q7InventoryEditReply").parameters, "rs"), "empty battle accepted");
                check(inventory(emptyBattle.read(), 1) == 2, "empty battle document is idle");
            }
            try (BaiyeHost.Disk completedWeek = new BaiyeHost.Disk(assets, BsonLite.withProfileDocument(profile(1, 1, 0), "q7WeekResult", BsonLite.document("week", 3, "version", 2)))) {
                callback(call(completedWeek, "q7InventoryEditAsk", edit(op('2'), row("item", 1, "add", 1))));
                check(inventory(completedWeek.read(), 1) == 2, "completed week result does not permanently block");
            }
            LocalTutorialStore.Progress committedWeek = LocalTutorialStore.Progress.fresh();
            committedWeek.weekCommit = "committed-transition";
            try (BaiyeHost.Disk transition = new BaiyeHost.Disk(assets, BsonLite.withProfileDocument(profile(1, 1, 0),
                    "q7WeekTransition", BsonLite.document("id", "committed-transition")))) {
                callback(call(transition, "q7InventoryEditAsk", edit(op('7'), row("item", 1, "add", 1)), committedWeek));
                check(inventory(transition.read(), 1) == 2, "committed transition allows editing");
            }
            LocalTutorialStore.Progress pendingWeek = LocalTutorialStore.Progress.fresh();
            pendingWeek.weekCommit = "other-commit";
            try (BaiyeHost.Disk transition = new BaiyeHost.Disk(assets, BsonLite.withProfileDocument(profile(1, 1, 0),
                    "q7WeekTransition", BsonLite.document("id", "pending-transition")))) {
                byte[] pendingBefore = transition.read();
                List<ProtoLite.EntityMessage> rejected = call(transition, "q7InventoryEditAsk",
                        edit(op('8'), row("item", 1, "add", 1)), pendingWeek);
                check(!BsonLite.boolValue(reply(rejected, "q7InventoryEditReply").parameters, "rs"), "pending transition rejected");
                check(Arrays.equals(pendingBefore, transition.read()), "pending transition no mutation");
            }
            List<byte[]> receipts = new ArrayList<>();
            for (int i = 0; i < 4096; i++) {
                String prior = String.format(java.util.Locale.ROOT, "%032x", i);
                receipts.add(BsonLite.document("op", prior, "digest", prior, "reply", BsonLite.document("m", "q7InventoryEditReply", "p", BsonLite.document("rs", true))));
            }
            byte[] fullReceipts = BsonLite.withProfileArray(BsonLite.withProfileInt(BsonLite.EMPTY_DOCUMENT, "schema", 1), "ops", receipts);
            try (BaiyeHost.Disk full = new BaiyeHost.Disk(assets, BsonLite.withProfileDocument(profile(1, 1, 0), "_q7_inventory_ops_v1", fullReceipts))) {
                byte[] fullBefore = full.read();
                List<ProtoLite.EntityMessage> rejected = call(full, "q7InventoryEditAsk", edit(op('3'), row("item", 1, "add", 1)));
                check(!BsonLite.boolValue(reply(rejected, "q7InventoryEditReply").parameters, "rs"), "receipt cap rejects new op at 4096");
                check(Arrays.equals(fullBefore, full.read()), "receipt cap no mutation");
            }
            Os.afterRename = (name) -> {
                Os.afterRename = null;
                byte[] pending = BsonLite.withProfileString(Files.readAllBytes(disk.file.toPath()), "pendingApply", "x");
                Files.write(disk.file.toPath(), pending);
                throw new IllegalStateException("fixture post-rename pendingApply");
            };
            callback(call(disk, "q7InventoryEditAsk", edit(op('4'), row("item", 1, "add", 1))));
            check(inventory(disk.read(), 1) == 8, "post-rename receipt recovers committed operation");
            check("x".equals(BsonLite.stringValue(disk.read(), "pendingApply")), "pendingApply image kept");
            try (BaiyeHost.Disk concurrent = new BaiyeHost.Disk(assets, profile(1, 1, 0))) {
                int writes = Os.renames;
                ExecutorService pool = Executors.newFixedThreadPool(2);
                CountDownLatch start = new CountDownLatch(1);
                try {
                    List<Future<List<ProtoLite.EntityMessage>>> jobs = new ArrayList<>();
                    for (int i = 0; i < 2; i++) jobs.add(pool.submit(() -> {
                        start.await(5, TimeUnit.SECONDS);
                        return call(concurrent, "q7InventoryEditAsk", edit(op('6'), row("item", 1, "add", 1)));
                    }));
                    start.countDown();
                    for (Future<List<ProtoLite.EntityMessage>> job : jobs)
                        check(BsonLite.boolValue(reply(job.get(10, TimeUnit.SECONDS), "q7InventoryEditReply").parameters, "rs"), "concurrent accepted");
                    check(inventory(concurrent.read(), 1) == 2, "same op concurrent applies once");
                    check(Os.renames == writes + 1, "same op concurrent writes once");
                } finally {
                    pool.shutdownNow();
                    Os.renames = writes;
                }
            }
            try (BaiyeHost.Disk distinct = new BaiyeHost.Disk(assets, profile(1, 0, 0))) {
                int writes = Os.renames;
                ExecutorService pool = Executors.newFixedThreadPool(2);
                CountDownLatch start = new CountDownLatch(1);
                try {
                    List<Future<List<ProtoLite.EntityMessage>>> jobs = new ArrayList<>();
                    String[] ops = {op('9'), op('a')};
                    int[] amounts = {10, 20};
                    for (int i = 0; i < 2; i++) {
                        final int index = i;
                        jobs.add(pool.submit(() -> {
                            start.await(5, TimeUnit.SECONDS);
                            return call(distinct, "q7InventoryEditAsk",
                                    edit(ops[index], row("item", 1, "add", amounts[index])));
                        }));
                    }
                    start.countDown();
                    for (Future<List<ProtoLite.EntityMessage>> job : jobs)
                        check(BsonLite.boolValue(reply(job.get(10, TimeUnit.SECONDS), "q7InventoryEditReply").parameters, "rs"), "distinct concurrent accepted");
                    check(inventory(distinct.read(), 1) == 30, "distinct concurrent ops both apply");
                    check(Os.renames == writes + 2, "distinct concurrent ops write twice");
                } finally {
                    pool.shutdownNow();
                    Os.renames = writes;
                }
            }
            try (BaiyeHost.Disk engineDisk = new BaiyeHost.Disk(assets, profile(1, 1, 0))) {
                LocalTutorialStore.Progress progress = LocalTutorialStore.Progress.fresh();
                progress.weekCommit = "engine-week";
                LocalEventCatalog graph = new LocalEventCatalog(new FileInputStream(new File(assets, "event_graph.tsv")));
                LocalNewbeeCatalog newbees = new LocalNewbeeCatalog(new ByteArrayInputStream(new byte[0]));
                LocalEventEngine engine = new LocalEventEngine(graph, newbees, progress, 0,
                        engineDisk.read(), true);
                byte[] engineOp = edit(op('c'), row("item", 1, "add", 1));
                callback(call(engineDisk, "q7InventoryEditAsk", engineOp, null, engine));
                check(inventory(engineDisk.read(), 1) == 2, "non-empty engine commit");
                byte[] engineCommitted = engineDisk.read();
                try (BaiyeHost.Disk retry = new BaiyeHost.Disk(assets, engineCommitted)) {
                    LocalEventEngine retryEngine = new LocalEventEngine(graph, newbees, progress, 0,
                            engineCommitted, true);
                    callback(call(retry, "q7InventoryEditAsk", engineOp, null, retryEngine));
                    check(Arrays.equals(engineCommitted, retry.read()), "non-empty engine replay read-only");
                }
            }
            try (BaiyeHost.Disk snapshotDisk = new BaiyeHost.Disk(assets, profile(1, 1, 0))) {
                LocalTutorialStore.Progress snapshotProgress = LocalTutorialStore.Progress.fresh();
                snapshotProgress.weekCommit = "snapshot-week";
                LocalEventCatalog graph = new LocalEventCatalog(new FileInputStream(new File(assets, "event_graph.tsv")));
                LocalNewbeeCatalog newbees = new LocalNewbeeCatalog(new ByteArrayInputStream(new byte[0]));
                byte[] snapProfile = snapshotDisk.read();
                LocalEventEngine snapEngine = new LocalEventEngine(graph, newbees, snapshotProgress, 0, snapProfile, true);
                Field refreshTimes = LocalProfileStore.class.getDeclaredField("fullRefreshTimes");
                refreshTimes.setAccessible(true);
                @SuppressWarnings("unchecked") java.util.Map<String, Long> times =
                        (java.util.Map<String, Long>) refreshTimes.get(snapshotDisk.store);
                times.put(BaiyeHost.ACCOUNT, System.currentTimeMillis());
                Method refresh = InventoryEditorGateway.class.getDeclaredMethod("refreshEngine",
                        LocalProfileStore.class, String.class, LocalTutorialStore.Progress.class,
                        LocalEventEngine.class, byte[].class);
                refresh.setAccessible(true);
                File backup = new File(snapshotDisk.file.getParentFile(), "inventory-engine.backup");
                Files.move(snapshotDisk.file.toPath(), backup.toPath());
                try {
                    refresh.invoke(null, snapshotDisk.store, BaiyeHost.ACCOUNT, snapshotProgress,
                            snapEngine, snapProfile);
                    throw new AssertionError("snapshot failure must propagate");
                } catch (InvocationTargetException snapshotFailure) {
                    check(snapshotFailure.getCause() instanceof java.io.IOException, "snapshot failure is unknown IOException");
                }
                check(!snapshotDisk.file.exists(), "snapshot failure did not write profile");
                Files.move(backup.toPath(), snapshotDisk.file.toPath());
                refresh.invoke(null, snapshotDisk.store, BaiyeHost.ACCOUNT, snapshotProgress,
                        snapEngine, snapProfile);
            }
            try (BaiyeHost.Disk many = new BaiyeHost.Disk(assets, fullProfile(1925, 140))) {
                long started = System.nanoTime();
                List<ProtoLite.EntityMessage> itemCatalog = call(many, "q7InventoryCatalogAsk",
                        BsonLite.document("g", "item", "q", "1", "n", 50, "_cbid_", 51));
                long itemMillis = (System.nanoTime() - started) / 1000000L;
                byte[] itemRows = BsonLite.arrayValue(reply(itemCatalog, "q7InventoryCatalogReply").parameters, "rows");
                byte[] firstItem = LocalResourceEngine.array(itemRows).get(0);
                check(1925L == BsonLite.numericValue(firstItem, "n").longValue(), "indexed full item count");
                started = System.nanoTime();
                List<ProtoLite.EntityMessage> treasureCatalog = call(many, "q7InventoryCatalogAsk",
                        BsonLite.document("g", "treasure", "q", "1001", "n", 50, "_cbid_", 52));
                long treasureMillis = (System.nanoTime() - started) / 1000000L;
                byte[] treasureRows = BsonLite.arrayValue(reply(treasureCatalog, "q7InventoryCatalogReply").parameters, "rows");
                byte[] tre = LocalResourceEngine.array(treasureRows).get(0);
                check(140L == BsonLite.numericValue(tre, "n").longValue(), "indexed mirrored treasure count");
                check(itemMillis < 1500 && treasureMillis < 1500,
                        "full-collection catalog bounded ms=" + itemMillis + "/" + treasureMillis);
                System.out.println("PERF_CATALOG_1925_ITEMS_140_HEROES_MS=" + itemMillis + "/" + treasureMillis);
                // A 380-entry treasure table needs ordered slices, not one page.
                List<ProtoLite.EntityMessage> firstPage = call(many, "q7InventoryCatalogAsk",
                        BsonLite.document("g", "treasure", "n", 100, "o", 0, "_cbid_", 55));
                List<byte[]> pageOne = LocalResourceEngine.array(BsonLite.arrayValue(
                        reply(firstPage, "q7InventoryCatalogReply").parameters, "rows"));
                List<ProtoLite.EntityMessage> secondPage = call(many, "q7InventoryCatalogAsk",
                        BsonLite.document("g", "treasure", "n", 100, "o", 100, "_cbid_", 56));
                List<byte[]> pageTwo = LocalResourceEngine.array(BsonLite.arrayValue(
                        reply(secondPage, "q7InventoryCatalogReply").parameters, "rows"));
                check(pageOne.size() == 100 && pageTwo.size() == 100, "treasure pages are full slices");
                check(BsonLite.numericValue(pageOne.get(0), "i").longValue() !=
                        BsonLite.numericValue(pageTwo.get(0), "i").longValue(),
                        "page two starts past page one");
                List<ProtoLite.EntityMessage> deepPage = call(many, "q7InventoryCatalogAsk",
                        BsonLite.document("g", "treasure", "n", 100, "o", 200, "_cbid_", 57));
                List<byte[]> pageThree = LocalResourceEngine.array(BsonLite.arrayValue(
                        reply(deepPage, "q7InventoryCatalogReply").parameters, "rows"));
                check(pageThree.size() <= 100, "later pages stay bounded by the requested size");
                List<ProtoLite.EntityMessage> past = call(many, "q7InventoryCatalogAsk",
                        BsonLite.document("g", "treasure", "n", 100, "o", 5000, "_cbid_", 58));
                check(LocalResourceEngine.array(BsonLite.arrayValue(
                        reply(past, "q7InventoryCatalogReply").parameters, "rows")).isEmpty(),
                        "offset past the catalog is an empty page");
            }
            try (BaiyeHost.Disk quick = new BaiyeHost.Disk(assets, profile(1, 1, 0))) {
                List<ProtoLite.EntityMessage> letters = call(quick, "q7InventoryEditAsk",
                        edit(op('6'), BsonLite.document("k", "bulk", "m", "letters")));
                check(Boolean.TRUE.equals(BsonLite.boolValue(reply(letters, "q7InventoryEditReply").parameters, "rs")),
                        "letters bulk row accepted");
                check(inventory(quick.read(), 519) == 1, "a 2018 letter is owned after the bulk row");
                check(inventory(quick.read(), 11527) == 99, "the replica-letter selector is topped to 99");
                List<ProtoLite.EntityMessage> cgRows = call(quick, "q7InventoryEditAsk", edit(op('7'),
                        BsonLite.document("k", "cg", "i", 1, "m", "add"),
                        BsonLite.document("k", "cg", "i", 2, "m", "add"),
                        BsonLite.document("k", "cg", "i", 3, "m", "add")));
                check(Boolean.TRUE.equals(BsonLite.boolValue(reply(cgRows, "q7InventoryEditReply").parameters, "rs")),
                        "cg rows accepted");
                check(BsonLite.intArrayValues(quick.read(), "cgs").equals(Arrays.asList(1, 2, 3)),
                        "cg ids merged into the profile");
                List<ProtoLite.EntityMessage> again = call(quick, "q7InventoryEditAsk", edit(op('8'),
                        BsonLite.document("k", "cg", "i", 2, "m", "add")));
                check(Boolean.TRUE.equals(BsonLite.boolValue(reply(again, "q7InventoryEditReply").parameters, "rs")),
                        "repeated cg row is a no-op");
                check(BsonLite.intArrayValues(quick.read(), "cgs").equals(Arrays.asList(1, 2, 3)),
                        "no duplicate cg entries");
                call(quick, "q7InventoryEditAsk", edit(op('9'),
                        BsonLite.document("k", "bulk", "m", "currency")));
                check(BaiyeTransactions.count(quick.read(), 519) == 1, "currency bulk keeps items untouched");
                try (BaiyeHost.Disk keepDisk = new BaiyeHost.Disk(assets, profile(1, 1, 0))) {
                    call(keepDisk, "q7InventoryEditAsk", edit(op('b'),
                            BsonLite.document("k", "bulk", "m", "letters_keep")));
                    check(inventory(keepDisk.read(), 8803) == 1, "keep variant grants other years");
                    check(inventory(keepDisk.read(), 519) == 0, "keep variant leaves 2018 letters exchangeable");
                    check(inventory(keepDisk.read(), 8005) == 0, "keep variant leaves 2019 letters exchangeable");
                    check(inventory(keepDisk.read(), 11527) == 99, "keep variant stocks the replica letter");
                }
                try (BaiyeHost.Disk resetDisk = new BaiyeHost.Disk(assets, profile(1, 1, 0))) {
                    call(resetDisk, "q7InventoryEditAsk", edit(op('c'),
                            BsonLite.document("k", "bulk", "m", "letters")));
                    check(inventory(resetDisk.read(), 519) == 1, "letters granted before reset");
                    call(resetDisk, "q7InventoryEditAsk", edit(op('d'),
                            BsonLite.document("k", "bulk", "m", "letters_reset")));
                    check(inventory(resetDisk.read(), 519) == 0, "reset drops a 2018 letter");
                    check(inventory(resetDisk.read(), 8005) == 0, "reset drops a 2019 letter");
                    check(inventory(resetDisk.read(), 8803) == 1, "reset keeps other years");
                    check(inventory(resetDisk.read(), 11527) == 99, "reset keeps the selectors");
                }
                List<ProtoLite.EntityMessage> bad = call(quick, "q7InventoryEditAsk", edit(op('a'),
                        BsonLite.document("k", "bulk", "m", "nothing")));
                check(!BsonLite.boolValue(reply(bad, "q7InventoryEditReply").parameters, "rs"),
                        "unknown bulk class rejected");
            }
            try (BaiyeHost.Disk crystal = new BaiyeHost.Disk(assets, profile(4253, 1, 0))) {
                List<ProtoLite.EntityMessage> cat = call(crystal, "q7InventoryCatalogAsk",
                        BsonLite.document("g", "item", "q", "4253", "n", 10, "_cbid_", 53));
                check(Boolean.TRUE.equals(BsonLite.boolValue(reply(cat, "q7InventoryCatalogReply").parameters, "rs")),
                        "memory crystal catalog accepted");
                callback(call(crystal, "q7InventoryEditAsk", edit(op('5'), row("item", 4253, "add", 1))));
                check(inventory(crystal.read(), 4253) == 2, "type17 memory crystal grant");
            }
            try (BaiyeHost.Disk furniture = new BaiyeHost.Disk(assets, profile(10036, 1, 0))) {
                callback(call(furniture, "q7InventoryEditAsk", edit(op('4'), row("item", 10036, "add", 1))));
                check(inventory(furniture.read(), 10036) == 2, "type20 furniture grant");
            }
            byte[] malformed = BsonLite.document("account", BaiyeHost.ACCOUNT, "an", BaiyeHost.ACCOUNT,
                    "st", 900999, "inv", BsonLite.document("items", Arrays.asList(1)), "unknown", "preserve");
            try (BaiyeHost.Disk bad = new BaiyeHost.Disk(assets, malformed)) {
                byte[] beforeBad = bad.read();
                List<ProtoLite.EntityMessage> rejected = call(bad, "q7InventoryCatalogAsk",
                        BsonLite.document("g", "item", "q", "1", "n", 50, "_cbid_", 54));
                check(!BsonLite.boolValue(reply(rejected, "q7InventoryCatalogReply").parameters, "rs"),
                        "non-document inventory array rejected");
                check(Arrays.equals(beforeBad, bad.read()), "malformed array no mutation");
            }
            try (BaiyeHost.Disk quality = new BaiyeHost.Disk(assets, profile(1, 1, 0))) {
                byte[] qualityOp = edit(op('0'), BsonLite.document("k", "treasure", "i", 1001,
                        "m", "create", "n", 1, "q", 999));
                byte[] beforeQuality = quality.read();
                int writes = Os.renames;
                List<ProtoLite.EntityMessage> badQuality = call(quality, "q7InventoryEditAsk", qualityOp);
                byte[] badReply = reply(badQuality, "q7InventoryEditReply").parameters;
                check(!BsonLite.boolValue(badReply, "rs"), "invalid quality rejected");
                check(BsonLite.intValue(badReply, "reason") == 1, "invalid quality reason1");
                check(op('0').equals(BsonLite.stringValue(badReply, "op")), "invalid quality op echo");
                check(Os.renames == writes, "invalid quality zero writes");
                check(Arrays.equals(beforeQuality, quality.read()), "invalid quality profile unchanged");
                callback(call(quality, "q7InventoryEditAsk", edit(op('1'), row("item", 1, "add", 1))));
                check(inventory(quality.read(), 1) == 2, "valid op after invalid quality");
            }
            try (BaiyeHost.Disk mixed = new BaiyeHost.Disk(assets, profile(1, 1, 0))) {
                byte[] mixedOp = edit(op('2'), row("item", 1, "add", 1),
                        BsonLite.document("k", "treasure", "i", 1001, "m", "create", "n", 1, "q", 999));
                byte[] beforeMixed = mixed.read();
                int writes = Os.renames;
                List<ProtoLite.EntityMessage> badMixed = call(mixed, "q7InventoryEditAsk", mixedOp);
                byte[] mixedReply = reply(badMixed, "q7InventoryEditReply").parameters;
                check(!BsonLite.boolValue(mixedReply, "rs"), "mixed invalid row rejected");
                check(BsonLite.intValue(mixedReply, "reason") == 1, "mixed reason1");
                check(Os.renames == writes, "mixed invalid row zero writes");
                check(Arrays.equals(beforeMixed, mixed.read()), "mixed invalid row unchanged");
                callback(call(mixed, "q7InventoryEditAsk", edit(op('3'), row("item", 1, "add", 1))));
                check(inventory(mixed.read(), 1) == 2, "valid op after mixed invalid row");
            }
            try (BaiyeHost.Disk deletion = new BaiyeHost.Disk(assets, profile(1, 2, 0))) {
                byte[] remove = edit(op('b'), row("item", 1, "set", 0));
                List<ProtoLite.EntityMessage> firstDelete = call(deletion, "q7InventoryEditAsk", remove);
                callback(firstDelete);
                check(inventory(deletion.read(), 1) == 0, "set zero removes stacks");
                check(lastMethod(firstDelete, "q7InventoryEditReply"), "initial success last");
                byte[] committedDelete = deletion.read();
                try (BaiyeHost.Disk retry = new BaiyeHost.Disk(assets, committedDelete)) {
                    List<ProtoLite.EntityMessage> replay = call(retry, "q7InventoryEditAsk", remove);
                    check(hasMethod(replay, "deleteItems"), "replay carries reliable deletion tombstone");
                    ProtoLite.EntityMessage delete = reply(replay, "deleteItems");
                    check(bsonFieldType(delete.parameters, "i") == 4, "deleteItems list field");
                    check(bsonArrayFirstType(delete.parameters, "i") == 7, "deleteItems ObjectId type");
                    check(lastMethod(replay, "q7InventoryEditReply"), "replay success after sync frames");
                    check(Arrays.equals(committedDelete, retry.read()), "retry absolute sync is read-only");
                }
            }
            List<ProtoLite.EntityMessage> catalog = call(disk, "q7InventoryCatalogAsk",
                    BsonLite.document("g", "item", "q", "1", "n", 10, "op", op('d'), "_cbid_", 44));
            callback(catalog);
            byte[] catalogReply = reply(catalog, "q7InventoryCatalogReply").parameters;
            check(BsonLite.boolValue(catalogReply, "rs"), "catalog read-only success reply");
            check(op('d').equals(BsonLite.stringValue(catalogReply, "op")), "catalog echoes raw query nonce");
            byte[] catalogRows = BsonLite.arrayValue(reply(catalog, "q7InventoryCatalogReply").parameters, "rows");
            byte[] firstRow = LocalResourceEngine.array(catalogRows).get(0);
            check(BsonLite.numericValue(firstRow, "n") instanceof Long, "catalog count is true int64");
            byte[] catalogImage = disk.read();
            List<ProtoLite.EntityMessage> badCatalog = call(disk, "q7InventoryCatalogAsk", BsonLite.document("g", "bogus", "n", 1, "_cbid_", 45));
            callback(badCatalog);
            check(!BsonLite.boolValue(reply(badCatalog, "q7InventoryCatalogReply").parameters, "rs"), "catalog failure uses catalog reply");
            check(Arrays.equals(catalogImage, disk.read()), "catalog no mutation");
            check(Arrays.equals(disk.read(), disk.read()), "catalog no mutation");
            System.out.println("PASS inventory editor: set/add/currency/treasure/catalog; callback-insensitive exact replay; conflict/cap/busy rejection; empty-battle/completed-week; stock receipt recovery; original Store image");
        }
    }
}
