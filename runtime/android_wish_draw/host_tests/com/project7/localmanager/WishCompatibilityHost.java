package com.project7.localmanager;
import android.content.*;import android.content.res.*;import java.io.*;import java.util.*;
/** Installs the new decoder before exercising frozen old family/pending callers. */
public final class WishCompatibilityHost {
 public static void main(String[]args)throws Exception{Context c=new Context(new File(System.getProperty("java.io.tmpdir")),new AssetManager(new File(args[0]),new File(args[1]),new File(args[2]),new File(args[3]),new File(args[4])));CoreDrawPolicy.prepare(c);HistoryDrawPolicy.prepare(c);try(InputStream in=new FileInputStream(args[5])){SelectorPolicy.prepareStream(in);}try(InputStream in=new FileInputStream(args[6])){DynamicDrawPolicy.prepareStream(in);}WishGateway.prepare(c);if(args[7].equals("family"))DynamicFamilyHost.main(Arrays.copyOf(args,7));else if(args[7].equals("selector"))DynamicSelectorRegressionHost.main(Arrays.copyOf(args,7));else DynamicUpgradeHost.main(args);}
}
