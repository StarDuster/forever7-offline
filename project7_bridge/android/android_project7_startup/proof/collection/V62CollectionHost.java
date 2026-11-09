package com.project7.localmanager;

import android.content.Context;
import android.content.res.AssetManager;
import java.io.File;

/** Reuses the published RealCollectionHost body after the exact v62 production prepare order.
 *  Why: current v62 LocalResourceCatalog construction augments the history/dynamic/selector pools
 *  and fails closed unless those production policies have loaded their staged assets first.
 *  No production source, engine or asset is modified; the prepare calls are the same nine calls
 *  already proven by root-v62-prepare-all-independent.json.
 */
public final class V62CollectionHost {
    public static void main(String[] args) throws Exception {
        File assets = new File(args[0]);
        Context context = new Context(assets, new AssetManager(assets));
        CoreDrawPolicy.prepare(context);          System.out.println("PREPARE PASS CoreDrawPolicy");
        HistoryDrawPolicy.prepare(context);       System.out.println("PREPARE PASS HistoryDrawPolicy");
        SelectorPolicy.prepare(context);          System.out.println("PREPARE PASS SelectorPolicy");
        DynamicDrawPolicy.prepare(context);       System.out.println("PREPARE PASS DynamicDrawPolicy");
        WishGateway.prepare(context);             System.out.println("PREPARE PASS WishGateway");
        StoryMissionBridge.prepare(context);      System.out.println("PREPARE PASS StoryMissionBridge");
        StoryCityBootstrap.prepare(context);      System.out.println("PREPARE PASS StoryCityBootstrap");
        TrialRetryGateway.prepare(context);       System.out.println("PREPARE PASS TrialRetryGateway");
        OfflineMechanismGateway.prepare(context); System.out.println("PREPARE PASS OfflineMechanismGateway");
        // Source identity for this run: manager classes must be the translated f81b frame,
        // production bridge/validator/initializer must be the v62 OWN tree supplied on the classpath.
        for (Class<?> c : new Class<?>[]{BsonLite.class, LocalResourceEngine.class, LocalLevelAdmin.class,
                LocalCollectionEngine.class, LocalSharedLiberateEngine.class, LocalResourceCatalog.class,
                LocalFeatureCatalog.class, LocalProfileStore.class}) {
            System.out.println("MANAGER_CLASS " + c.getName() + " " + c.getProtectionDomain().getCodeSource().getLocation());
        }
        for (Class<?> c : new Class<?>[]{CollectionBson.class, CollectionStockBridge.class, CollectionTargets.class,
                CollectionValidator.class, FullCollectionInitializer.class}) {
            System.out.println("OWN_CLASS " + c.getName() + " " + c.getProtectionDomain().getCodeSource().getLocation());
        }
        RealCollectionHost.main(args);
    }
}
