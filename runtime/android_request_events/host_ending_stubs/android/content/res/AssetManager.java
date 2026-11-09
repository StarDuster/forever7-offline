package android.content.res;

import java.io.*;

/** Host-only full stage asset reader; never packaged. */
public final class AssetManager {
    private final File root;
    public AssetManager(File root) { this.root = root; }
    public InputStream open(String name) throws IOException { return new FileInputStream(new File(root, name)); }
}
