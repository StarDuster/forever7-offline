package com.project7.localmanager;
import java.io.*;
/** Runs the frozen original selector proof with dynamic metadata prepared too. */
public final class DynamicSelectorRegressionHost {
 public static void main(String[] args)throws Exception{
  try(InputStream in=new FileInputStream(args[6])){DynamicDrawPolicy.prepareStream(in);}
  SelectorEngineHost.main(args);
 }
}
