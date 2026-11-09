package com.project7.localmanager;
import android.content.Context;
import java.io.*;
/** Descriptor declarations only; these names must never be program input. */
final class LocalGatewayServer {}
final class LocalTutorialStore {static final class Progress {}}
final class LocalEventEngine {}
final class LocalAccountStore {static boolean isTemplateAccount(String account){throw new UnsupportedOperationException();}}
final class DreamCoordinator {
    static void recover(LocalGatewayServer g,String a,LocalTutorialStore.Progress p,LocalEventEngine e)throws IOException {throw new UnsupportedOperationException();}
}
final class DreamRequestGateway {
    static void prepare(Context c)throws IOException {throw new UnsupportedOperationException();}
    static boolean handleDirect(LocalGatewayServer g,OutputStream o,byte[]id,byte[]m,byte[]p,String a,LocalTutorialStore.Progress s,LocalEventEngine e)throws IOException {throw new UnsupportedOperationException();}
    static boolean handleRequest(LocalGatewayServer g,OutputStream o,byte[]id,String m,byte[]p,Integer cb,String a,LocalTutorialStore.Progress s,LocalEventEngine e)throws IOException {throw new UnsupportedOperationException();}
}
final class RequestEventGateway {
    static void prepare(Context c)throws IOException {throw new UnsupportedOperationException();}
    static boolean handleDirect(LocalGatewayServer g,OutputStream o,byte[]id,byte[]m,byte[]p,String a,LocalTutorialStore.Progress s,LocalEventEngine e)throws IOException {throw new UnsupportedOperationException();}
    static boolean handleRequest(LocalGatewayServer g,OutputStream o,byte[]id,String m,byte[]p,Integer cb,String a,LocalTutorialStore.Progress s,LocalEventEngine e)throws IOException {throw new UnsupportedOperationException();}
}

final class EventResetWeekPolicy {
    static void prepare(Context c)throws IOException {throw new UnsupportedOperationException();}
}
final class BaiyeGateway {
    static void prepare(Context c)throws IOException {throw new UnsupportedOperationException();}
    static boolean handleDirect(LocalGatewayServer g,OutputStream o,byte[]id,byte[]m,byte[]p,String a,LocalTutorialStore.Progress s,LocalEventEngine e)throws IOException {throw new UnsupportedOperationException();}
    static boolean handleRequest(LocalGatewayServer g,OutputStream o,byte[]id,String m,byte[]p,Integer cb,String a,LocalTutorialStore.Progress s,LocalEventEngine e)throws IOException {throw new UnsupportedOperationException();}
}
final class BaiyeShopGateway {
    static void prepare(Context c)throws IOException {throw new UnsupportedOperationException();}
    static boolean handleDirect(LocalGatewayServer g,OutputStream o,byte[]id,byte[]m,byte[]p,String a,LocalTutorialStore.Progress s,LocalEventEngine e)throws IOException {throw new UnsupportedOperationException();}
    static boolean handleRequest(LocalGatewayServer g,OutputStream o,byte[]id,String m,byte[]p,Integer cb,String a,LocalTutorialStore.Progress s,LocalEventEngine e)throws IOException {throw new UnsupportedOperationException();}
}
final class StoryBasicsGateway {
    static void prepare(Context c)throws IOException {throw new UnsupportedOperationException();}
    static boolean handleDirect(LocalGatewayServer g,OutputStream o,byte[]id,byte[]m,byte[]p,String a,LocalTutorialStore.Progress s,LocalEventEngine e)throws IOException {throw new UnsupportedOperationException();}
    static boolean handleRequest(LocalGatewayServer g,OutputStream o,byte[]id,String m,byte[]p,Integer cb,String a,LocalTutorialStore.Progress s,LocalEventEngine e)throws IOException {throw new UnsupportedOperationException();}
}
final class WishGateway {
    static boolean handleDirect(LocalGatewayServer g,OutputStream o,byte[]id,byte[]m,byte[]p,String a,LocalTutorialStore.Progress s,LocalEventEngine e)throws IOException {throw new UnsupportedOperationException();}
    static boolean handleRequest(LocalGatewayServer g,OutputStream o,byte[]id,String m,byte[]p,Integer cb,String a,LocalTutorialStore.Progress s,LocalEventEngine e)throws IOException {throw new UnsupportedOperationException();}
    static boolean handleSequencedRequest(LocalGatewayServer g,OutputStream o,byte[]id,String m,byte[]p,Integer cb,String a,LocalTutorialStore.Progress s,LocalEventEngine e,Integer seq,java.util.Set<Integer>seen)throws IOException {throw new UnsupportedOperationException();}
}
final class InventoryEditorGateway {
    public static boolean handleRequest(LocalGatewayServer g,OutputStream o,byte[]id,String m,byte[]p,Integer cb,String a,LocalTutorialStore.Progress s,LocalEventEngine e)throws IOException {throw new UnsupportedOperationException();}
}
