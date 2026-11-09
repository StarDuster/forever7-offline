package com.project7.localmanager;
import java.util.*;
/** PRIVATE candidate: retain first AllLeft activity snapshot, remove later superseded ones.
 * Two-pass validation: no mutation until every candidate frame is known valid.
 * Conservative eligibility: intermediate 12-field payloads must match the first
 * except ct/cctd/tw; tw advancement requires independent syncTreasureWishInfo
 * pushes. If the invariant is not proven, return the original result unchanged. */
final class AllLeftActivitySyncCandidate {
    // wi is not a blanket exclusion: group Wish restores it through syncWishGroupInfo;
    // this helper does not generalize to the group family without an observer proof.
    private static final String[] SEMANTIC = {"iof","wi","lt","jzc","jzr","rc","ff","ch","ctr"};
    static LocalResourceEngine.Result apply(LocalResourceEngine.Result result) {
        if (result == null || result.replies == null || result.profile == null) return result;
        try {
            int terminal=-1, terminals=0;
            Integer terminalT=null;
            for (int i=0;i<result.replies.size();i++) {
                LocalResourceEngine.Reply r=result.replies.get(i);
                if (r == null) return result;
                if ("replyLuckyDrawAllLeftCard".equals(r.method)) {
                    terminals++; terminal=i;
                    byte[] p=r.parameters;
                    terminalT=BsonLite.intValue(p,"t");
                    Boolean rt=BsonLite.boolValue(p,"rt");
                    byte[] trwd=BsonLite.arrayValue(p,"trwd");
                    if (!Boolean.TRUE.equals(rt) || terminalT==null || terminalT<=0 || trwd==null ||
                        LocalResourceEngine.array(trwd).isEmpty()) return result;
                }
            }
            if (terminals != 1 || terminal < 0 || Integer.valueOf(1).equals(terminalT)) return result;

            int finalIdx=-1, finals=0, treasurePushes=0;
            for (int i=terminal+1;i<result.replies.size();i++) {
                LocalResourceEngine.Reply r=result.replies.get(i);
                if (r == null) return result;
                if ("syncLuckyDrawActivityData".equals(r.method) &&
                    terminalT.equals(BsonLite.intValue(r.parameters,"t"))) {
                    finals++; finalIdx=i;
                    if (BsonLite.documentValue(r.parameters,"d") == null) return result;
                }
            }
            for (int i=0;i<terminal;i++) {
                LocalResourceEngine.Reply r=result.replies.get(i);
                if (r == null) return result;
                if ("syncTreasureWishInfo".equals(r.method) &&
                    terminalT.equals(BsonLite.intValue(r.parameters,"t"))) treasurePushes++;
            }
            if (finals != 1 || finalIdx < 0) return result;

            int first=-1, intermediate=0;
            byte[] firstD=null;
            ArrayList<Integer> remove=new ArrayList<Integer>();
            for (int i=0;i<terminal;i++) {
                LocalResourceEngine.Reply r=result.replies.get(i);
                if (r == null) return result;
                if ("syncLuckyDrawActivityData".equals(r.method) &&
                    terminalT.equals(BsonLite.intValue(r.parameters,"t"))) {
                    byte[] d=BsonLite.documentValue(r.parameters,"d");
                    if (d == null) return result;
                    intermediate++;
                    if (first < 0) { first=i; firstD=d; }
                    else { if (!semanticEqual(firstD,d)) return result; remove.add(i); }
                }
            }
            if (first < 0 || treasurePushes < intermediate) return result;
            // Commit only after every candidate frame passed validation.
            for (int i=remove.size()-1;i>=0;i--) result.replies.remove((int)remove.get(i));
            return result;
        } catch (RuntimeException malformed) {
            return result; // malformed input is passed through unchanged
        }
    }
    private static boolean semanticEqual(byte[] a,byte[] b) {
        List<String> aKeys = BsonLite.keys(a);
        List<String> bKeys = BsonLite.keys(b);
        for (String k: SEMANTIC) {
            boolean aPresent = aKeys.contains(k);
            boolean bPresent = bKeys.contains(k);
            if (aPresent != bPresent) return false;
            if (!aPresent) continue;
            byte[] av = BsonLite.withCopiedValue(BsonLite.EMPTY_DOCUMENT, k, a, k);
            byte[] bv = BsonLite.withCopiedValue(BsonLite.EMPTY_DOCUMENT, k, b, k);
            if (!Arrays.equals(av, bv)) return false;
        }
        return true;
    }
}
