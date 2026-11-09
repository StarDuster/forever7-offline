package com.project7.localmanager;
public final class FullCollectionInitializer implements StableIdentityBootstrap.PostProfileInitializer {
    public static final String POLICY="p7-full-collection-v1";
    public interface Cancellation{boolean cancelled();}
    public FullCollectionInitializer(Cancellation cancellation){}
    public void initialize(android.content.Context app,StableIdentityBootstrap.Identity identity,StableIdentityBootstrap.Stores stores){throw new UnsupportedOperationException("No original collection engine in host coordinator model");}
}
