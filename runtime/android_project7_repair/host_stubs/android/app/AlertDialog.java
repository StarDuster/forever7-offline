package android.app;
import android.content.DialogInterface;
/** Dialog UI leaf seam; show/press are counters only. */
public final class AlertDialog implements DialogInterface {
 public static AlertDialog latest;public String message;public DialogInterface.OnClickListener positive;public boolean shown,dismissed;
 public void dismiss(){dismissed=true;}public void show(){shown=true;latest=this;}public void press(){if(positive!=null)positive.onClick(this,1);}
 public static final class Builder {private final AlertDialog value=new AlertDialog();public Builder(Activity a){}public Builder setTitle(String v){return this;}public Builder setCancelable(boolean v){return this;}public Builder setMessage(String v){value.message=v;return this;}public Builder setPositiveButton(String v,DialogInterface.OnClickListener p){value.positive=p;return this;}public AlertDialog create(){return value;}}
}
