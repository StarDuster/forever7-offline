package com.project7.localmanager;

import android.content.Context;
import java.io.IOException;
import java.io.OutputStream;
import java.util.Set;

/** Authenticated extension dispatch only. Original ACK/cache/replies stay stock. */
public final class OfflineMechanismGateway {
    private OfflineMechanismGateway() {}
    public static void prepare(Context context) throws IOException {
        BaiyeGateway.prepare(context);
        BaiyeShopGateway.prepare(context);
        StoryBasicsGateway.prepare(context);
        RequestEventGateway.prepare(context);
        DreamRequestGateway.prepare(context);
        EventResetWeekPolicy.prepare(context);
    }
    private static void recover(LocalGatewayServer gateway, String account,
            LocalTutorialStore.Progress progress, LocalEventEngine engine) throws IOException {
        if (account != null && progress != null && engine != null &&
                !LocalAccountStore.isTemplateAccount(account))
            DreamCoordinator.recover(gateway, account, progress, engine);
    }
    public static boolean handleDirect(LocalGatewayServer gateway, OutputStream out,
            byte[] entityId, byte[] methodDigest, byte[] parameters, String account,
            LocalTutorialStore.Progress progress, LocalEventEngine engine) throws IOException {
        if (WishGateway.handleDirect(gateway, out, entityId, methodDigest,
                parameters, account, progress, engine)) return true;
        // Recovery is reconciliation, not a new patrol admission: it selects no
        // events and consumes no action. The stock sequence cache still runs.
        if (BaiyeShopGateway.handleDirect(gateway, out, entityId, methodDigest,
                parameters, account, progress, engine)) return true;
        if (BaiyeGateway.handleDirect(gateway, out, entityId, methodDigest,
                parameters, account, progress, engine)) return true;
        if (StoryBasicsGateway.handleDirect(gateway, out, entityId, methodDigest,
                parameters, account, progress, engine)) return true;
        recover(gateway, account, progress, engine);
        if (DreamRequestGateway.handleDirect(gateway, out, entityId, methodDigest,
                parameters, account, progress, engine)) return true;
        return RequestEventGateway.handleDirect(gateway, out, entityId, methodDigest,
                parameters, account, progress, engine);
    }
    public static boolean handleRequest(LocalGatewayServer gateway, OutputStream out,
            byte[] entityId, String method, byte[] parameters, Integer callback,
            String account, LocalTutorialStore.Progress progress, LocalEventEngine engine)
            throws IOException {
        if (WishGateway.handleRequest(gateway, out, entityId, method,
                parameters, callback, account, progress, engine)) return true;
        if (BaiyeShopGateway.handleRequest(gateway, out, entityId, method,
                parameters, callback, account, progress, engine)) return true;
        if (InventoryEditorGateway.handleRequest(gateway, out, entityId, method,
                parameters, callback, account, progress, engine)) return true;
        if (BaiyeGateway.handleRequest(gateway, out, entityId, method,
                parameters, callback, account, progress, engine)) return true;
        if (StoryBasicsGateway.handleRequest(gateway, out, entityId, method,
                parameters, callback, account, progress, engine)) return true;
        recover(gateway, account, progress, engine);
        if (DreamRequestGateway.handleRequest(gateway, out, entityId, method,
                parameters, callback, account, progress, engine)) return true;
        return RequestEventGateway.handleRequest(gateway, out, entityId, method,
                parameters, callback, account, progress, engine);
    }
    /** Forward original connection admission only to its reviewed Wish handler.
     * Other handlers retain their own original sequence gate unchanged.
     */
    public static boolean handleSequencedRequest(LocalGatewayServer gateway, OutputStream out,
            byte[] entityId, String method, byte[] parameters, Integer callback,
            String account, LocalTutorialStore.Progress progress, LocalEventEngine engine,
            Integer sequence, Set<Integer> seen) throws IOException {
        if (WishGateway.handleSequencedRequest(gateway, out, entityId, method,
                parameters, callback, account, progress, engine, sequence, seen)) return true;
        return handleRequest(gateway, out, entityId, method, parameters, callback,
                account, progress, engine);
    }
}
