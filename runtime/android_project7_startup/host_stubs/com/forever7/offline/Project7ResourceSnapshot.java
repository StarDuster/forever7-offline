package com.forever7.offline;
public final class Project7ResourceSnapshot {
    public interface Assets {java.io.InputStream open(String name)throws java.io.IOException;}
    public static final class Asset { public String sha256; }
    public static final class TrustedContract { public int entryCount;public Asset snapshot,binding; }
    public static final class Receipt {public int verifiedEntries;public String snapshotSha256,bindingSha256;}
    public static Receipt publish(java.io.File docs,java.util.List<ResourceImporter.Entry> entries,TrustedContract contract,
                                  Assets assets,java.util.concurrent.atomic.AtomicBoolean flag,ResourceImporter.Progress progress) {
        throw new UnsupportedOperationException("Host coordinator uses explicit publication seam, never fake verification");
    }
}
