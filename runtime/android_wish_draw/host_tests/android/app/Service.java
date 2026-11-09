package android.app;
/** HOST platform type seam; no service lifecycle is executed. */
public class Service extends android.content.Context {
 public Service(){super(new java.io.File("."),new android.content.res.AssetManager(new java.io.File(".")));}
 public void onCreate(){throw new UnsupportedOperationException("host service not started");}
 public void onDestroy(){throw new UnsupportedOperationException("host service not started");}
}
