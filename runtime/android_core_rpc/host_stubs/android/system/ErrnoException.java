package android.system;
/** HOST ONLY original catch-handler type. */
public final class ErrnoException extends Exception {public ErrnoException(String op,int n){super(op+":"+n);}}
