package android.system;
/** HOST ONLY type linkage for the original writer's catch handler; no Android behavior. */
public final class ErrnoException extends Exception {
    public ErrnoException(String operation,int errno){super(operation+": "+errno);}
}
