package com.project7.localmanager;

import android.content.Context;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import org.json.JSONArray;
import org.json.JSONObject;

/** Pinned original mainline_week_info failed-rule admission for ending triggers.
 *
 * <p>The asset is regenerated only from the original literal table by
 * tools/project7_ending_trigger_catalog.py. Current original 640 data has no
 * nonzero false_event, so production authorizes no event; the consumer still
 * evaluates future nonzero rows without accepting a client-supplied ID.
 */
final class EndingTriggerCatalog {
    static final String ASSET = "offline/ending-trigger-v1.json";
    static final String SHA256 = "1792a804aba72c806a7bb73dce3a42baf52695ff0edc5b476fbbe05c89095431";
    private static final int MAX_BYTES = 128 * 1024;
    static final class Rule {
        final List<int[]> requires;
        final int trueClientEvent, falseClientEvent, falseEvent;
        final List<Integer> openChapters;
        Rule(List<int[]> requires, int trueClientEvent, int falseClientEvent, int falseEvent,
                List<Integer> openChapters) {
            this.requires = requires;
            this.trueClientEvent = trueClientEvent;
            this.falseClientEvent = falseClientEvent;
            this.falseEvent = falseEvent;
            this.openChapters = openChapters;
        }
    }
    static final class Authorized {
        static final Authorized AMBIGUOUS = new Authorized(-1, -1);
        final int event, rule;
        Authorized(int event, int rule) { this.event = event; this.rule = rule; }
    }
    private final Map<Integer,List<Rule>> weeks;
    private final Map<Integer,int[]> endings;
    private EndingTriggerCatalog(Map<Integer,List<Rule>> weeks, Map<Integer,int[]> endings) {
        this.weeks = Collections.unmodifiableMap(weeks);
        this.endings = Collections.unmodifiableMap(endings);
    }
    static EndingTriggerCatalog prepare(Context context)throws IOException {
        return prepare(context, SHA256);
    }
    /** Host verification only: callers pass an independently computed hash for
     * a synthetic fixture. Production always uses the pinned prepare(context). */
    static EndingTriggerCatalog prepare(Context context,String expectedSha)throws IOException {
        byte[] bytes;
        try (InputStream in = context.getAssets().open(ASSET)) { bytes = read(in); }
        if (!expectedSha.equals(RequestEventCatalog.hex(RequestEventCatalog.hash("SHA-256", bytes))))
            throw new IOException("Ending-trigger catalog hash");
        Map<Integer,List<Rule>> weeks = parse(bytes);
        LocalWeekCatalog catalog;
        try (InputStream in = context.getAssets().open("weeks.tsv")) { catalog = new LocalWeekCatalog(in); }
        if (catalog.endings == null || catalog.endings.isEmpty())
            throw new IOException("Original week ending contract missing");
        Map<Integer,int[]> endings = new LinkedHashMap<>();
        for (Map.Entry<Integer,int[]> row : catalog.endings.entrySet()) {
            int[] value = row.getValue();
            if (row.getKey() == null || row.getKey() <= 0 || value == null || value.length < 3)
                throw new IOException("Original week ending row invalid");
            endings.put(row.getKey(), value.clone());
        }
        return new EndingTriggerCatalog(weeks, endings);
    }
    int[] ending(int event) {
        int[] row = endings.get(event);
        return row == null ? null : row.clone();
    }
    /** Original WeekNumMember.getMainLineWeekEvent: AND groups of OR endings.
     * Only failed rows with both client and server failure events are eligible;
     * multiple matches stay ambiguous instead of choosing one. */
    Authorized authorize(int sourceWeek, Collection<Integer> endings) {
        List<Rule> rules = weeks.get(sourceWeek + 1);
        if (rules == null) return null;
        Set<Integer> known = new HashSet<>(endings);
        Authorized found = null;
        for (int index = 0; index < rules.size(); index++) {
            Rule rule = rules.get(index);
            boolean satisfied = true;
            for (int[] group : rule.requires) {
                boolean any = false;
                for (int ending : group) if (known.contains(ending)) { any = true; break; }
                if (!any) { satisfied = false; break; }
            }
            if (satisfied || rule.falseClientEvent == 0 || rule.falseEvent == 0) continue;
            if (found != null) return Authorized.AMBIGUOUS;
            found = new Authorized(rule.falseEvent, index);
        }
        return found;
    }
    private static Map<Integer,List<Rule>> parse(byte[] bytes)throws IOException {
        Object rootValue;
        try { rootValue = json(new JSONObject(new String(bytes, StandardCharsets.UTF_8))); }
        catch (Exception failure) { throw new IOException("Ending-trigger catalog JSON", failure); }
        if (!(rootValue instanceof Map)) throw new IOException("Ending-trigger catalog root");
        Map<?,?> root = (Map<?,?>) rootValue;
        if (!"project7-ending-trigger-v1".equals(root.get("schema")) ||
                !"open-new-enter-failed-rule-v1".equals(root.get("policy")))
            throw new IOException("Ending-trigger catalog schema");
        Object source = root.get("source");
        if (!(source instanceof Map) || !"mainline_week_info".equals(((Map<?,?>) source).get("table")) ||
                !"4a14531712d43d9b006c716a6364fbec0620f2b765ceb3a68505f8db4540b844".equals(
                        ((Map<?,?>) source).get("sha256")))
            throw new IOException("Ending-trigger source pin");
        Object weeksValue = root.get("weeks");
        if (!(weeksValue instanceof Map)) throw new IOException("Ending-trigger weeks");
        Map<Integer,List<Rule>> weeks = new LinkedHashMap<>();
        for (Map.Entry<?,?> entry : ((Map<?,?>) weeksValue).entrySet()) {
            int week;
            try { week = Integer.parseInt(String.valueOf(entry.getKey())); }
            catch (RuntimeException failure) { throw new IOException("Ending-trigger week", failure); }
            if (week <= 0 || week > 100000 || !(entry.getValue() instanceof List))
                throw new IOException("Ending-trigger week row");
            List<Rule> rules = new ArrayList<>();
            for (Object raw : (List<?>) entry.getValue()) {
                if (!(raw instanceof Map)) throw new IOException("Ending-trigger rule");
                Map<?,?> rule = (Map<?,?>) raw;
                if (!rule.keySet().equals(new HashSet<>(Arrays.asList("requires", "true_client_event",
                        "false_client_event", "false_event", "open_chapters"))))
                    throw new IOException("Ending-trigger rule fields");
                Object requires = rule.get("requires");
                if (!(requires instanceof List)) throw new IOException("Ending-trigger requires");
                List<int[]> groups = new ArrayList<>();
                for (Object group : (List<?>) requires) {
                    if (!(group instanceof List) || ((List<?>) group).isEmpty())
                        throw new IOException("Ending-trigger requirement group");
                    List<?> members = (List<?>) group;
                    int[] ids = new int[members.size()];
                    for (int i = 0; i < ids.length; i++) ids[i] = positive(members.get(i));
                    groups.add(ids);
                }
                int trueEvent = nonnegative(rule.get("true_client_event"));
                int falseClient = nonnegative(rule.get("false_client_event"));
                int falseEvent = nonnegative(rule.get("false_event"));
                Object chapters = rule.get("open_chapters");
                if (!(chapters instanceof List)) throw new IOException("Ending-trigger chapters");
                List<Integer> chapterIds = new ArrayList<>();
                for (Object chapter : (List<?>) chapters) chapterIds.add(positive(chapter));
                rules.add(new Rule(groups, trueEvent, falseClient, falseEvent, chapterIds));
            }
            if (rules.isEmpty() || weeks.put(week, rules) != null) throw new IOException("Ending-trigger week duplicate");
        }
        if (weeks.isEmpty()) throw new IOException("Ending-trigger weeks empty");
        return weeks;
    }
    private static Object json(Object value)throws IOException {
        if (value == null || value == JSONObject.NULL) return null;
        if (value instanceof JSONObject) {
            Map<String,Object> result = new LinkedHashMap<>();
            JSONObject object = (JSONObject) value;
            Iterator<String> keys = object.keys();
            while (keys.hasNext()) {
                String key = keys.next();
                result.put(key, json(object.opt(key)));
            }
            return result;
        }
        if (value instanceof JSONArray) {
            List<Object> result = new ArrayList<>();
            JSONArray array = (JSONArray) value;
            for (int i = 0; i < array.length(); i++) result.add(json(array.opt(i)));
            return result;
        }
        return value;
    }
    private static int positive(Object value)throws IOException {
        int result = nonnegative(value);
        if (result == 0) throw new IOException("Ending-trigger positive integer");
        return result;
    }
    private static int nonnegative(Object value)throws IOException {
        if (!(value instanceof Number) || value instanceof Double || value instanceof Float)
            throw new IOException("Ending-trigger integer");
        long number = ((Number) value).longValue();
        if (number < 0 || number > Integer.MAX_VALUE) throw new IOException("Ending-trigger integer range");
        return (int) number;
    }
    private static byte[] read(InputStream in)throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] block = new byte[4096]; int count;
        while ((count = in.read(block)) != -1) {
            if (out.size() + count > MAX_BYTES) throw new IOException("Ending-trigger catalog bound");
            out.write(block, 0, count);
        }
        return out.toByteArray();
    }
}
