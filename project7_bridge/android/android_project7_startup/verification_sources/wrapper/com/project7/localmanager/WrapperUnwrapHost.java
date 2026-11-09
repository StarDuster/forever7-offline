package com.project7.localmanager;
import android.content.Context;
import android.content.res.AssetManager;
import java.io.File;
import java.lang.reflect.Method;
import java.nio.file.Files;
/** Exercises each consumer unwrap helper with a real FailureSafeProfileProvider instance. */
public class WrapperUnwrapHost {
 static Object call(Class<?> owner,Object provider)throws Exception{Method m=owner.getDeclaredMethod("unwrapProvider",Object.class);m.setAccessible(true);return m.invoke(null,provider);}
 public static void main(String[] a)throws Exception{
  File root=Files.createTempDirectory("wrapper-unwrap-").toFile();
  Context c=new Context(root,new AssetManager(new File(a[0])));
  LocalProfileStore store=new LocalProfileStore(c);
  FailureSafeProfileProvider wrapper=new FailureSafeProfileProvider(store);
  Class<?>[] owners={DreamStorage.class,CoreGapBridge.class,BaiyeGateway.class,BaiyeShopGateway.class,StoryBasicsGateway.class,WishGateway.class};
  for(Class<?> owner:owners){Object got=call(owner,wrapper);if(got!=store)throw new AssertionError(owner.getName()+" unwrap mismatch: "+(got==null?null:got.getClass()));System.out.println("PASS "+owner.getSimpleName());}
  if(FailureSafeProfileProvider.unwrap(wrapper)!=store)throw new AssertionError("startup unwrap mismatch");
  System.out.println("PASS FailureSafeProfileProvider");
 }
}
