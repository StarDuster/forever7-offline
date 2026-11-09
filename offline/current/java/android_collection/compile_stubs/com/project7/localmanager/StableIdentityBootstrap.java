package com.project7.localmanager;
import android.content.Context;
// COMPILE ONLY. Never package these identity/manager type stubs.
public final class StableIdentityBootstrap {
    public interface PostProfileInitializer {void initialize(Context app,Identity identity,Stores stores)throws Exception;}
    public static final class Identity {public String username(){throw new UnsupportedOperationException();}public int numericId(){throw new UnsupportedOperationException();}}
    public static final class Stores {final LocalProfileStore profiles=null;}
}
final class LocalProfileStore { }
