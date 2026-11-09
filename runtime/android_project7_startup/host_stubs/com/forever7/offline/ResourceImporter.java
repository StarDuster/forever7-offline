package com.forever7.offline;
public class ResourceImporter {
    public static final class Entry { public final String name="synthetic"; }
    public static final class Cancelled extends java.io.IOException { public Cancelled(){super("cancelled");} }
    public interface Progress { void update(String name,long done,long total); }
}
