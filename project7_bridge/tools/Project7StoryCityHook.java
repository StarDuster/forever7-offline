import com.googlecode.d2j.*;
import com.googlecode.d2j.dex.writer.DexFileWriter;
import com.googlecode.d2j.node.*;
import com.googlecode.d2j.node.insn.*;
import com.googlecode.d2j.reader.*;
import com.googlecode.d2j.visitors.*;
import java.nio.file.*;import java.security.MessageDigest;import java.util.*;
/** Maintainer-only fixed core city seams plus a profile-gated, non-mutating Gateway area query seam. */
public final class Project7StoryCityHook {
 static final String SOURCE="7f13c24a613676ee520bf6ed2590a6bf33788cb6955c92f3e9f446dee89c0d82";
 static final String TARGET="fee369231e8924923f774cdbda4961f91b6ab87cee237b249cff8229b535f1c6";
 static final String R="Lcom/project7/localmanager/",HELP=R+"StoryCityPolicy;",CITY=R+"LocalCityProgress;",CHAPTER=R+"LocalChapterCityEngine;",ENTRY=R+"LocalStoryEntryPolicy;",WEEK=R+"LocalWeekEngine;",BSON=R+"BsonLite;",G=R+"LocalGatewayServer;",THUNK=R+"LocalStoryRuleRegistry$$ExternalSyntheticLambda4;",P=R+"LocalTutorialStore$Progress;",RESULT=R+"LocalResourceEngine$Result;",CAT=R+"LocalEventCatalog;",ROOM=R+"LocalPuzzleEngine$Room;",CLUE=R+"LocalPuzzleEngine$Clue;";
 static final String QUERY="q7QueryAreaId",ALLOWED="q7QueryAreaAllowed",RESOLVE="resolveAreaId",RESOLVE_DESC="(Ljava/lang/Integer;Z)I",MSG="\u8be5\u5730\u533a\u6682\u4e0d\u652f\u6301\u67e5\u8be2";
 static final String COC=R+"StoryCityCocPolicy;",ADMISSION=R+"StoryCityCocPolicy$Admission;",SETTLEMENT=R+"StoryCityCocPolicy$Settlement;",PROVIDER=R+"LocalGatewayServer$ProfileProvider;",STORE=R+"LocalProfileStore;",TUTORIAL=R+"LocalTutorialStore;",ECORESULT=R+"LocalEconomyEngine$Result;";
 static final Method TUTORIAL_SAVE=new Method(TUTORIAL,"save",new String[]{"Ljava/lang/String;",P},"V");
 static final Method RECOVERABLE=new Method(COC,"recoverableProgress",new String[]{P,"[B","I","[B"},"Z");
 static final Field TUTORIAL_STORE=new Field(G,"tutorialStore",TUTORIAL);
 static final Field ALREADY_SETTLED_FIELD=new Field(COC,"ALREADY_SETTLED","Ljava/lang/String;"),P_PATROL=new Field(P,"patrolActions","I");
 static final Method ADMIT=new Method(COC,"admit",new String[]{P,"[B","I","[B"},ADMISSION);
 static final Method COC_BEGIN=new Method(COC,"begin",new String[]{STORE,"Ljava/lang/String;",P,"[B","I","[B"},SETTLEMENT);
 static final Method COC_SETTLE=new Method(COC,"settle",new String[]{STORE,"Ljava/lang/String;",P,"[B","I","[B","I",R+"LocalEventEngine;"},SETTLEMENT);
 static final Method SNAPSHOT=new Method(PROVIDER,"snapshot",new String[]{"Ljava/lang/String;",P},"[B");
 static final Method LOAD=new Method(PROVIDER,"load",new String[]{"Ljava/lang/String;",P},"[B");
 static final Method UPDATE_ECONOMY=new Method(PROVIDER,"updateEconomy",new String[]{"Ljava/lang/String;","Ljava/lang/String;","[B",P},ECORESULT);
 static final Method COMBAT_WIN=new Method(BSON,"combatWinValue",new String[]{"[B"},"I");
 static final Method BSON_INT=new Method(BSON,"intValue",new String[]{"[B","Ljava/lang/String;"},"Ljava/lang/Integer;");
 static final Method EC_INIT=new Method(ECORESULT,"<init>",new String[]{"[B"},"V");
 static final Method STRING_EQUALS=new Method("Ljava/lang/String;","equals",new String[]{"Ljava/lang/Object;"},"Z");
 static final Field ADM_ALLOWED=new Field(ADMISSION,"allowed","Z"),ADM_REASON=new Field(ADMISSION,"reason","Ljava/lang/String;"),ADM_SCENE=new Field(ADMISSION,"scene","I");
 static final Field SET_ACCEPTED=new Field(SETTLEMENT,"accepted","Z"),SET_REPLAY=new Field(SETTLEMENT,"replay","Z"),SET_REASON=new Field(SETTLEMENT,"reason","Ljava/lang/String;"),SET_REWARD=new Field(SETTLEMENT,"reward","[B"),SET_REMAIN=new Field(SETTLEMENT,"remainingActions","I"),SET_STORE_RESULT=new Field(SETTLEMENT,"storeResult",ECORESULT);
 static final Field EC_ACCEPTED=new Field(ECORESULT,"accepted","Z"),EC_REPLAY=new Field(ECORESULT,"replay","Z"),EC_REASON=new Field(ECORESULT,"reason","Ljava/lang/String;"),EC_REWARD=new Field(ECORESULT,"reward","[B"),EC_REMAIN=new Field(ECORESULT,"remainingActions","I"),EC_WIN=new Field(ECORESULT,"win","I");
 static final Field UNKNOWN_SCENE=new Field(COC,"UNKNOWN_SCENE","Ljava/lang/String;"),NOT_PREPARED=new Field(COC,"NOT_PREPARED","Ljava/lang/String;");
 static final Map<String,String> REDIRECT=new LinkedHashMap<>();static final Set<String>changed=new HashSet<>();static int refresh,party,resets,querySites,queryBlocks,queryAdded,puzzleRooms,puzzleClues,cocBeginCalls,cocFinishCalls;static Set<String>prefixes=new HashSet<>(),wrappers=new HashSet<>();
 static{REDIRECT.put("area(I)I","area");REDIRECT.put("mapStages("+P+"I[B)[B","mapStages");REDIRECT.put("stages("+P+"I[B)[B","stages");REDIRECT.put("status("+P+"I[B)I","status");REDIRECT.put("consumeVictory("+P+"[BII)Z","consumeVictory");}
 static void need(boolean v,String m){if(!v)throw new IllegalStateException(m);}
 static String sha(byte[]b)throws Exception{StringBuilder s=new StringBuilder();for(byte x:MessageDigest.getInstance("SHA-256").digest(b))s.append(String.format("%02x",x&255));return s.toString();}
 static final Method KNOWN=new Method(HELP,"knownArea",new String[]{"I"},"Z");
 static final Method OWN=new Method(HELP,"owns",new String[]{"[B"},"Z");
 static final Method INT_VALUE=new Method("Ljava/lang/Integer;","intValue",new String[]{},"I");
 static final Method DOCUMENT=new Method(BSON,"document",new String[]{"[Ljava/lang/Object;"},"[B");
 static final Method ENTITY=new Method(R+"ProtoLite;","entityMessage",new String[]{"[B","[B","[B"},"[B");
 static final Method MD5=new Method(G,"md5",new String[]{"Ljava/lang/String;"},"[B");
 static final Method WRITEFRAME=new Method(G,"writeFrame",new String[]{"Ljava/io/OutputStream;","I","[B"},"V");
 static final Method ALLOW=new Method(G,ALLOWED,new String[]{"Ljava/lang/Integer;","[B"},"Z");
 static final Method UNWRAP_STORE=new Method(R+"FailureSafeProfileProvider;","unwrapStore",new String[]{"Ljava/lang/Object;"},STORE);
 /** Non-owned delegates; owned resolves legacy 1..8 and catalog areas; unreachable unknown returns itself, never a sentinel. */
 static DexMethodNode queryMethod(){
  DexMethodNode m=new DexMethodNode(DexConstants.ACC_PRIVATE|DexConstants.ACC_STATIC,new Method(G,QUERY,new String[]{"Ljava/lang/Integer;","Z","[B"},"I"));
  DexCodeNode c=new DexCodeNode();DexLabel owned=new DexLabel(),legacy=new DexLabel(),nonStrict=new DexLabel(),known=new DexLabel(),zero=new DexLabel(),one=new DexLabel();
  c.visitRegister(5);
  c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{4},OWN);c.visitStmt1R(Op.MOVE_RESULT,0);
  c.visitJumpStmt(Op.IF_NEZ,0,0,owned);c.visitJumpStmt(Op.GOTO_32,-1,0,legacy);c.visitLabel(owned);
  c.visitJumpStmt(Op.IF_EQZ,3,0,nonStrict);c.visitJumpStmt(Op.IF_EQZ,2,0,one);
  c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{2},INT_VALUE);c.visitStmt1R(Op.MOVE_RESULT,0);
  c.visitConstStmt(Op.CONST_4,1,Integer.valueOf(1));c.visitJumpStmt(Op.IF_LT,0,1,one);
  c.visitConstStmt(Op.CONST_16,1,Integer.valueOf(8));c.visitJumpStmt(Op.IF_GT,0,1,known);c.visitStmt1R(Op.RETURN,0);
  c.visitLabel(known);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{0},KNOWN);c.visitStmt1R(Op.MOVE_RESULT,1);c.visitStmt1R(Op.RETURN,0);
  c.visitLabel(nonStrict);c.visitJumpStmt(Op.IF_EQZ,2,0,zero);c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{2},INT_VALUE);c.visitStmt1R(Op.MOVE_RESULT,0);c.visitStmt1R(Op.RETURN,0);
  c.visitLabel(zero);c.visitConstStmt(Op.CONST_4,0,Integer.valueOf(0));c.visitStmt1R(Op.RETURN,0);
  c.visitLabel(one);c.visitConstStmt(Op.CONST_4,0,Integer.valueOf(1));c.visitStmt1R(Op.RETURN,0);
  c.visitLabel(legacy);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{2,3},new Method(G,RESOLVE,new String[]{"Ljava/lang/Integer;","Z"},"I"));c.visitStmt1R(Op.MOVE_RESULT,0);c.visitStmt1R(Op.RETURN,0);
  m.codeNode=c;return m;
 }
 /** Non-owned, null, legacy 1..8 and catalog areas are allowed; owned unknown is not. */
 static DexMethodNode allowedMethod(){
  DexMethodNode m=new DexMethodNode(DexConstants.ACC_PRIVATE|DexConstants.ACC_STATIC,new Method(G,ALLOWED,new String[]{"Ljava/lang/Integer;","[B"},"Z"));
  DexCodeNode c=new DexCodeNode();DexLabel allow=new DexLabel(),deny=new DexLabel(),known=new DexLabel();
  c.visitRegister(4);
  c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{3},OWN);c.visitStmt1R(Op.MOVE_RESULT,0);
  c.visitJumpStmt(Op.IF_EQZ,0,0,allow);c.visitJumpStmt(Op.IF_EQZ,2,0,allow);
  c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{2},INT_VALUE);c.visitStmt1R(Op.MOVE_RESULT,0);
  c.visitConstStmt(Op.CONST_4,1,Integer.valueOf(1));c.visitJumpStmt(Op.IF_LT,0,1,deny);
  c.visitConstStmt(Op.CONST_16,1,Integer.valueOf(8));c.visitJumpStmt(Op.IF_GT,0,1,known);c.visitJumpStmt(Op.GOTO_32,-1,0,allow);
  c.visitLabel(known);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{0},KNOWN);c.visitStmt1R(Op.MOVE_RESULT,1);c.visitJumpStmt(Op.IF_EQZ,1,0,deny);
  c.visitLabel(allow);c.visitConstStmt(Op.CONST_4,0,Integer.valueOf(1));c.visitStmt1R(Op.RETURN,0);
  c.visitLabel(deny);c.visitConstStmt(Op.CONST_4,0,Integer.valueOf(0));c.visitStmt1R(Op.RETURN,0);
  m.codeNode=c;return m;
 }
 /** Real admission seam: delegate only COC-catalog scenes; non-COC/foreign providers fall through to the original Store call. */
 static DexMethodNode cocBeginMethod(){
  DexMethodNode m=new DexMethodNode(DexConstants.ACC_PRIVATE|DexConstants.ACC_STATIC,new Method(G,"q7StoryCityCocBegin",new String[]{PROVIDER,"Ljava/lang/String;",TUTORIAL,"[B",P},ECORESULT));
  DexCodeNode c=new DexCodeNode();DexLabel fallback=new DexLabel(),reject=new DexLabel(),nullStore=new DexLabel(),returnResult=new DexLabel();
  c.visitRegister(16);
  c.visitStmt2R(Op.MOVE_OBJECT,0,11);c.visitStmt2R(Op.MOVE_OBJECT,1,12);c.visitStmt2R(Op.MOVE_OBJECT,2,14);c.visitStmt2R(Op.MOVE_OBJECT,3,15);
  c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{0},UNWRAP_STORE);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,5);c.visitJumpStmt(Op.IF_EQZ,5,0,fallback);c.visitStmt1R(Op.NOP,0);
  c.visitStmt2R(Op.MOVE_OBJECT,8,0);c.visitStmt2R(Op.MOVE_OBJECT,9,1);c.visitStmt2R(Op.MOVE_OBJECT,10,3);c.visitMethodStmt(Op.INVOKE_INTERFACE,new int[]{8,9,10},SNAPSHOT);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,6);
  c.visitStmt2R(Op.MOVE_OBJECT,9,2);c.visitConstStmt(Op.CONST_STRING,10,"s");c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{9,10},BSON_INT);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,7);
  c.visitJumpStmt(Op.IF_EQZ,7,0,fallback);
  c.visitStmt2R(Op.MOVE_OBJECT,9,7);c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{9},INT_VALUE);c.visitStmt1R(Op.MOVE_RESULT,4);
  c.visitStmt2R(Op.MOVE_OBJECT,7,3);c.visitStmt2R(Op.MOVE_OBJECT,8,6);c.visitStmt2R(Op.MOVE,9,4);c.visitStmt2R(Op.MOVE_OBJECT,10,2);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{7,8,9,10},ADMIT);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,7);
  c.visitFieldStmt(Op.IGET_OBJECT,9,7,ADM_REASON);c.visitFieldStmt(Op.SGET_OBJECT,10,0,UNKNOWN_SCENE);c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{9,10},STRING_EQUALS);c.visitStmt1R(Op.MOVE_RESULT,8);c.visitJumpStmt(Op.IF_NEZ,8,0,fallback);
  c.visitFieldStmt(Op.IGET_OBJECT,9,7,ADM_REASON);c.visitFieldStmt(Op.SGET_OBJECT,10,0,NOT_PREPARED);c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{9,10},STRING_EQUALS);c.visitStmt1R(Op.MOVE_RESULT,8);c.visitJumpStmt(Op.IF_NEZ,8,0,fallback);
  c.visitFieldStmt(Op.IGET_BOOLEAN,8,7,ADM_ALLOWED);c.visitJumpStmt(Op.IF_EQZ,8,0,reject);
  c.visitStmt2R(Op.MOVE_OBJECT,10,6);c.visitStmt2R(Op.MOVE_OBJECT,6,1);c.visitStmt2R(Op.MOVE_OBJECT,7,3);c.visitStmt2R(Op.MOVE_OBJECT,8,10);c.visitStmt2R(Op.MOVE,9,4);c.visitStmt2R(Op.MOVE_OBJECT,10,2);c.visitMethodStmt(Op.INVOKE_STATIC_RANGE,new int[]{5,6,7,8,9,10},COC_BEGIN);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,5);
  c.visitFieldStmt(Op.IGET_OBJECT,6,5,SET_STORE_RESULT);c.visitJumpStmt(Op.IF_EQZ,6,0,nullStore);c.visitFieldStmt(Op.IGET_BOOLEAN,8,5,SET_ACCEPTED);c.visitJumpStmt(Op.IF_EQZ,8,0,returnResult);c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{13,1,3},TUTORIAL_SAVE);c.visitLabel(returnResult);c.visitStmt2R(Op.MOVE_OBJECT,9,6);c.visitStmt1R(Op.RETURN_OBJECT,9);
  c.visitLabel(reject);
  c.visitStmt2R(Op.MOVE_OBJECT,10,7);c.visitTypeStmt(Op.NEW_INSTANCE,9,0,ECORESULT);c.visitStmt2R(Op.MOVE_OBJECT,5,9);c.visitMethodStmt(Op.INVOKE_DIRECT,new int[]{5,6},EC_INIT);c.visitConstStmt(Op.CONST_4,8,Integer.valueOf(0));c.visitFieldStmt(Op.IPUT_BOOLEAN,8,9,EC_ACCEPTED);c.visitFieldStmt(Op.IGET_OBJECT,8,10,ADM_REASON);c.visitFieldStmt(Op.IPUT_OBJECT,8,9,EC_REASON);c.visitStmt1R(Op.RETURN_OBJECT,9);
  c.visitLabel(nullStore);
  c.visitStmt2R(Op.MOVE_OBJECT,8,0);c.visitStmt2R(Op.MOVE_OBJECT,9,1);c.visitStmt2R(Op.MOVE_OBJECT,10,3);c.visitMethodStmt(Op.INVOKE_INTERFACE,new int[]{8,9,10},SNAPSHOT);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,6);
  c.visitStmt2R(Op.MOVE_OBJECT,10,5);c.visitTypeStmt(Op.NEW_INSTANCE,9,0,ECORESULT);c.visitStmt2R(Op.MOVE_OBJECT,5,9);c.visitMethodStmt(Op.INVOKE_DIRECT,new int[]{5,6},EC_INIT);c.visitConstStmt(Op.CONST_4,8,Integer.valueOf(0));c.visitFieldStmt(Op.IPUT_BOOLEAN,8,9,EC_ACCEPTED);c.visitFieldStmt(Op.IGET_OBJECT,8,10,SET_REASON);c.visitFieldStmt(Op.IPUT_OBJECT,8,9,EC_REASON);c.visitStmt1R(Op.RETURN_OBJECT,9);
  c.visitLabel(fallback);
  c.visitConstStmt(Op.CONST_STRING,13,"begin");c.visitMethodStmt(Op.INVOKE_INTERFACE,new int[]{11,12,13,14,15},UPDATE_ECONOMY);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,9);c.visitStmt1R(Op.RETURN_OBJECT,9);
  m.codeNode=c;return m;
 }
 /** Real settlement seam: delegate only COC-catalog scenes; the original finishStoryCombat still owns the event trace and Progress save. */
 static DexMethodNode cocFinishMethod(){
  DexMethodNode m=new DexMethodNode(DexConstants.ACC_PRIVATE|DexConstants.ACC_STATIC,new Method(G,"q7StoryCityCocFinish",new String[]{PROVIDER,"Ljava/lang/String;","Ljava/lang/String;","[B",P},ECORESULT));
  DexCodeNode c=new DexCodeNode();DexLabel fallback=new DexLabel(),reject=new DexLabel(),rejectCheck=new DexLabel(),nullStore=new DexLabel();
  c.visitRegister(16);
  c.visitStmt2R(Op.MOVE_OBJECT,0,11);c.visitStmt2R(Op.MOVE_OBJECT,1,12);c.visitStmt2R(Op.MOVE_OBJECT,2,14);c.visitStmt2R(Op.MOVE_OBJECT,3,15);
  c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{0},UNWRAP_STORE);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,5);c.visitJumpStmt(Op.IF_EQZ,5,0,fallback);c.visitStmt1R(Op.NOP,0);
  c.visitStmt2R(Op.MOVE_OBJECT,8,0);c.visitStmt2R(Op.MOVE_OBJECT,9,1);c.visitStmt2R(Op.MOVE_OBJECT,10,3);c.visitMethodStmt(Op.INVOKE_INTERFACE,new int[]{8,9,10},SNAPSHOT);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,6);
  c.visitStmt2R(Op.MOVE_OBJECT,9,2);c.visitConstStmt(Op.CONST_STRING,10,"s");c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{9,10},BSON_INT);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,9);
  c.visitJumpStmt(Op.IF_EQZ,9,0,fallback);
  c.visitStmt2R(Op.MOVE_OBJECT,10,9);c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{10},INT_VALUE);c.visitStmt1R(Op.MOVE_RESULT,4);
  c.visitStmt2R(Op.MOVE_OBJECT,7,3);c.visitStmt2R(Op.MOVE_OBJECT,8,6);c.visitStmt2R(Op.MOVE,9,4);c.visitStmt2R(Op.MOVE_OBJECT,10,2);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{7,8,9,10},ADMIT);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,7);
  c.visitFieldStmt(Op.IGET_OBJECT,9,7,ADM_REASON);c.visitFieldStmt(Op.SGET_OBJECT,10,0,UNKNOWN_SCENE);c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{9,10},STRING_EQUALS);c.visitStmt1R(Op.MOVE_RESULT,8);c.visitJumpStmt(Op.IF_NEZ,8,0,fallback);
  c.visitFieldStmt(Op.IGET_OBJECT,9,7,ADM_REASON);c.visitFieldStmt(Op.SGET_OBJECT,10,0,NOT_PREPARED);c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{9,10},STRING_EQUALS);c.visitStmt1R(Op.MOVE_RESULT,8);c.visitJumpStmt(Op.IF_NEZ,8,0,fallback);
  c.visitFieldStmt(Op.IGET_BOOLEAN,8,7,ADM_ALLOWED);c.visitJumpStmt(Op.IF_EQZ,8,0,rejectCheck);
  c.visitStmt2R(Op.MOVE_OBJECT,9,2);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{9},COMBAT_WIN);c.visitStmt1R(Op.MOVE_RESULT,8);
  c.visitStmt2R(Op.MOVE,14,8);c.visitStmt2R(Op.MOVE_OBJECT,8,5);c.visitStmt2R(Op.MOVE_OBJECT,9,1);c.visitStmt2R(Op.MOVE_OBJECT,10,3);c.visitStmt2R(Op.MOVE_OBJECT,11,6);c.visitStmt2R(Op.MOVE,12,4);c.visitStmt2R(Op.MOVE_OBJECT,13,2);c.visitConstStmt(Op.CONST_4,15,Integer.valueOf(0));
  c.visitMethodStmt(Op.INVOKE_STATIC_RANGE,new int[]{8,9,10,11,12,13,14,15},COC_SETTLE);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,10);
  c.visitFieldStmt(Op.IGET_OBJECT,9,10,SET_STORE_RESULT);c.visitJumpStmt(Op.IF_EQZ,9,0,nullStore);c.visitStmt1R(Op.RETURN_OBJECT,9);
  c.visitLabel(rejectCheck);
  c.visitStmt2R(Op.MOVE_OBJECT,9,2);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{9},COMBAT_WIN);c.visitStmt1R(Op.MOVE_RESULT,8);c.visitConstStmt(Op.CONST_4,10,Integer.valueOf(1));c.visitJumpStmt(Op.IF_NE,8,10,reject);
  c.visitFieldStmt(Op.IGET_OBJECT,9,7,ADM_REASON);c.visitFieldStmt(Op.SGET_OBJECT,10,0,ALREADY_SETTLED_FIELD);c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{9,10},STRING_EQUALS);c.visitStmt1R(Op.MOVE_RESULT,8);c.visitJumpStmt(Op.IF_EQZ,8,0,reject);
  c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{3,6,4,2},RECOVERABLE);c.visitStmt1R(Op.MOVE_RESULT,8);c.visitJumpStmt(Op.IF_EQZ,8,0,reject);
  c.visitTypeStmt(Op.NEW_INSTANCE,9,0,ECORESULT);c.visitStmt2R(Op.MOVE_OBJECT,8,9);c.visitStmt2R(Op.MOVE_OBJECT,9,6);c.visitMethodStmt(Op.INVOKE_DIRECT,new int[]{8,9},EC_INIT);c.visitConstStmt(Op.CONST_4,9,Integer.valueOf(1));c.visitFieldStmt(Op.IPUT_BOOLEAN,9,8,EC_ACCEPTED);c.visitFieldStmt(Op.IPUT_BOOLEAN,9,8,EC_REPLAY);c.visitFieldStmt(Op.IPUT,9,8,EC_WIN);c.visitFieldStmt(Op.IGET,9,3,P_PATROL);c.visitFieldStmt(Op.IPUT,9,8,EC_REMAIN);c.visitFieldStmt(Op.SGET_OBJECT,10,0,ALREADY_SETTLED_FIELD);c.visitFieldStmt(Op.IPUT_OBJECT,10,8,EC_REASON);c.visitStmt1R(Op.RETURN_OBJECT,8);
  c.visitLabel(reject);
  c.visitStmt2R(Op.MOVE_OBJECT,10,7);c.visitTypeStmt(Op.NEW_INSTANCE,9,0,ECORESULT);c.visitStmt2R(Op.MOVE_OBJECT,8,9);c.visitStmt2R(Op.MOVE_OBJECT,9,6);c.visitMethodStmt(Op.INVOKE_DIRECT,new int[]{8,9},EC_INIT);c.visitConstStmt(Op.CONST_4,5,Integer.valueOf(0));c.visitFieldStmt(Op.IPUT_BOOLEAN,5,8,EC_ACCEPTED);c.visitFieldStmt(Op.IPUT,5,8,EC_WIN);c.visitFieldStmt(Op.IGET_OBJECT,10,7,ADM_REASON);c.visitFieldStmt(Op.IPUT_OBJECT,10,8,EC_REASON);c.visitStmt1R(Op.RETURN_OBJECT,8);
  c.visitLabel(nullStore);
  c.visitStmt2R(Op.MOVE_OBJECT,12,10);c.visitStmt2R(Op.MOVE_OBJECT,8,0);c.visitStmt2R(Op.MOVE_OBJECT,9,1);c.visitStmt2R(Op.MOVE_OBJECT,10,3);c.visitMethodStmt(Op.INVOKE_INTERFACE,new int[]{8,9,10},SNAPSHOT);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,6);
  c.visitTypeStmt(Op.NEW_INSTANCE,9,0,ECORESULT);c.visitStmt2R(Op.MOVE_OBJECT,8,9);c.visitStmt2R(Op.MOVE_OBJECT,9,6);c.visitMethodStmt(Op.INVOKE_DIRECT,new int[]{8,9},EC_INIT);c.visitConstStmt(Op.CONST_4,5,Integer.valueOf(0));c.visitFieldStmt(Op.IPUT_BOOLEAN,5,8,EC_ACCEPTED);c.visitFieldStmt(Op.IPUT,5,8,EC_WIN);c.visitFieldStmt(Op.IGET_OBJECT,10,12,SET_REASON);c.visitFieldStmt(Op.IPUT_OBJECT,10,8,EC_REASON);c.visitStmt1R(Op.RETURN_OBJECT,8);
  c.visitLabel(fallback);
  c.visitMethodStmt(Op.INVOKE_INTERFACE,new int[]{11,12,13,14,15},UPDATE_ECONOMY);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,9);c.visitStmt1R(Op.RETURN_OBJECT,9);
  m.codeNode=c;return m;
 }
 /** Raise only the reviewed room/clue upper bound 3 -> 4; preserve lower bounds and all other checks. */
 static void puzzleMutate(DexCodeNode code,boolean room){
  List<Integer> pos=instructionPositions(code);int n=code.stmts.size();
  if(room){
   need(pos.size()==69,"Room constructor instructions changed");
   ConstStmtNode c11=(ConstStmtNode)code.stmts.get(pos.get(11));JumpStmtNode lb=(JumpStmtNode)code.stmts.get(pos.get(53));JumpStmtNode ub=(JumpStmtNode)code.stmts.get(pos.get(54));
   need(c11.op==Op.CONST_4&&c11.a==1&&((Integer)c11.value).intValue()==3,"Room clear index changed");
   need(lb.op==Op.IF_LT&&lb.a==7&&lb.b==0,"Room lower bound changed");
   need(ub.op==Op.IF_GT&&ub.a==7&&ub.b==1,"Room upper bound changed");
   code.stmts.set(pos.get(54),new JumpStmtNode(Op.IF_GT,7,4,ub.label));
   code.stmts.add(pos.get(54),new ConstStmtNode(Op.CONST_4,4,Integer.valueOf(4)));
  }else{
   need(pos.size()==25,"Clue constructor instructions changed");
   ConstStmtNode c11=(ConstStmtNode)code.stmts.get(pos.get(11));JumpStmtNode lb=(JumpStmtNode)code.stmts.get(pos.get(17));JumpStmtNode ub=(JumpStmtNode)code.stmts.get(pos.get(18));JumpStmtNode cg=(JumpStmtNode)code.stmts.get(pos.get(19));
   need(c11.op==Op.CONST_4&&c11.a==3&&((Integer)c11.value).intValue()==3,"Clue cg index changed");
   need(lb.op==Op.IF_LT&&lb.a==2&&lb.b==0,"Clue lower bound changed");
   need(ub.op==Op.IF_GT&&ub.a==2&&ub.b==3,"Clue upper bound changed");
   need(cg.op==Op.IF_LTZ&&cg.a==5,"Clue cg lower bound changed");
   code.stmts.add(pos.get(16),new ConstStmtNode(Op.CONST_4,3,Integer.valueOf(4)));
  }
  if(room)puzzleRooms++;else puzzleClues++;
 }
 static List<Integer> instructionPositions(DexCodeNode code){List<Integer> p=new ArrayList<>();for(int i=0;i<code.stmts.size();i++)if(!(code.stmts.get(i) instanceof DexLabelStmtNode))p.add(i);return p;}
 static void queryMutate(DexCodeNode code,boolean client){
  List<Integer> pos=instructionPositions(code);int resolve=client?1362:2494,normal=client?1364:2496,loadAt=client?1368:2500,replyAt=client?1371:2503,logAt=client?1379:2509,tailAt=logAt+8;
  DexStmtNode rn=code.stmts.get(pos.get(resolve));need(rn instanceof MethodStmtNode&&((MethodStmtNode)rn).method.getOwner().equals(G)&&((MethodStmtNode)rn).method.getName().equals(RESOLVE)&&((MethodStmtNode)rn).method.getDesc().equals(RESOLVE_DESC)&&rn.op==Op.INVOKE_STATIC&&((MethodStmtNode)rn).args.length==2,"Query resolver source changed");
  MethodStmtNode rm=(MethodStmtNode)rn;need(rm.args[0]==(client?1:0)&&rm.args[1]==(client?3:1),"Query resolver registers changed");
  FieldStmtNode lf=(FieldStmtNode)code.stmts.get(pos.get(loadAt));MethodStmtNode lm=(MethodStmtNode)code.stmts.get(pos.get(loadAt+1));Stmt1RNode lr=(Stmt1RNode)code.stmts.get(pos.get(loadAt+2));
  String provider=R+"LocalGatewayServer$ProfileProvider;";int pReg=lr.a;
  need(lf.op==Op.IGET_OBJECT&&lf.a==pReg&&lf.b==(client?12:11)&&lf.field.getOwner().equals(G)&&lf.field.getName().equals("profileProvider")&&lm.op==Op.INVOKE_INTERFACE&&lm.method.getOwner().equals(provider)&&lm.method.getName().equals(client?"load":"snapshot")&&lm.method.getDesc().equals("(Ljava/lang/String;"+P+")[B")&&Arrays.equals(lm.args,client?new int[]{5,10,8}:new int[]{2,7,9})&&lr.op==Op.MOVE_RESULT_OBJECT,"Query profile load shape changed");
  MethodStmtNode reply=(MethodStmtNode)code.stmts.get(pos.get(replyAt));need(reply.op==Op.INVOKE_STATIC&&reply.method.getOwner().equals(BSON)&&reply.method.getName().equals(client?"areaInfoReplyDocument":"areaStagesReplyDocument")&&Arrays.equals(reply.args,client?new int[]{1,3,8,pReg}:new int[]{0,9,pReg}),"Query reply profile reuse changed");
  code.stmts.set(pos.get(resolve),new MethodStmtNode(Op.INVOKE_STATIC,new int[]{rm.args[0],pReg},ALLOW));code.stmts.set(pos.get(resolve+1),new Stmt1RNode(Op.MOVE_RESULT,client?4:3));
  List<DexStmtNode>load=Arrays.asList(new FieldStmtNode(lf.op,lf.a,lf.b,lf.field),new MethodStmtNode(lm.op,lm.args.clone(),lm.method),new Stmt1RNode(lr.op,lr.a));List<DexStmtNode>originals=Arrays.asList(lf,lm,lr);
  DexLabel reject=new DexLabel(),resolved=new DexLabel(),log=new DexLabel();List<DexStmtNode> block=new ArrayList<>();
  block.add(new JumpStmtNode(Op.IF_EQZ,client?4:3,0,reject));
  block.add(new MethodStmtNode(Op.INVOKE_STATIC,new int[]{client?1:0,client?3:1,pReg},new Method(G,QUERY,new String[]{"Ljava/lang/Integer;","Z","[B"},"I")));block.add(new Stmt1RNode(Op.MOVE_RESULT,client?1:0));
  block.add(new JumpStmtNode(Op.GOTO_32,-1,0,resolved));block.add(new DexLabelStmtNode(reject));
  block.add(new MethodStmtNode(Op.INVOKE_VIRTUAL,new int[]{client?1:0},INT_VALUE));block.add(new Stmt1RNode(Op.MOVE_RESULT,client?1:0));
  block.add(new ConstStmtNode(Op.CONST_STRING,client?5:1,"showMessageStr"));block.add(new MethodStmtNode(Op.INVOKE_STATIC,new int[]{client?5:1},MD5));block.add(new Stmt1RNode(Op.MOVE_RESULT_OBJECT,client?4:1));
  block.add(new ConstStmtNode(Op.CONST_STRING,client?5:3,"m"));block.add(new ConstStmtNode(Op.CONST_STRING,client?0:4,MSG));
  block.add(new FilledNewArrayStmtNode(Op.FILLED_NEW_ARRAY,client?new int[]{5,0}:new int[]{3,4},"[Ljava/lang/Object;"));block.add(new Stmt1RNode(Op.MOVE_RESULT_OBJECT,client?5:3));
  block.add(new MethodStmtNode(Op.INVOKE_STATIC,new int[]{client?5:3},DOCUMENT));block.add(new Stmt1RNode(Op.MOVE_RESULT_OBJECT,client?3:2));
  block.add(new MethodStmtNode(Op.INVOKE_STATIC,client?new int[]{14,4,3}:new int[]{13,1,2},ENTITY));block.add(new Stmt1RNode(Op.MOVE_RESULT_OBJECT,client?3:2));
  if(client){block.add(new MethodStmtNode(Op.INVOKE_DIRECT,new int[]{12,15,2,3},WRITEFRAME));}
  else{block.add(new ConstStmtNode(Op.CONST_4,3,Integer.valueOf(5)));block.add(new MethodStmtNode(Op.INVOKE_DIRECT,new int[]{11,12,3,2},WRITEFRAME));}
  block.add(new JumpStmtNode(Op.GOTO_32,-1,0,log));block.add(new DexLabelStmtNode(resolved));
  code.stmts.add(pos.get(tailAt),new DexLabelStmtNode(log));
  code.stmts.addAll(pos.get(normal),block);
  code.stmts.addAll(pos.get(resolve),load);
  for(DexStmtNode n:originals)need(code.stmts.remove(n),"Query duplicate profile load");
  MethodStmtNode an=null;for(DexStmtNode n:code.stmts)if(n instanceof MethodStmtNode&&((MethodStmtNode)n).method.getOwner().equals(G)&&((MethodStmtNode)n).method.getName().equals(ALLOWED))an=(MethodStmtNode)n;
  need(an!=null,"Missing allowed invoke");int ai=code.stmts.indexOf(an),ri=code.stmts.indexOf(reply);need(ai>=0&&ri>ai,"Allowed/reply order changed");
  int calls=0;for(int i=ai+1;i<ri;i++)if(code.stmts.get(i) instanceof MethodStmtNode){Method c=((MethodStmtNode)code.stmts.get(i)).method;if(c.getOwner().equals(provider)&&(c.getName().equals("load")||c.getName().equals("snapshot")))calls++;}
  need(calls==0,"Single profile load must be reused by the reply");
  querySites++;queryBlocks++;
 }
 public static void main(String[]args)throws Exception{
  need(args.length==2&&!Files.exists(Paths.get(args[1])),"Pinned source and unused output required");byte[]source=Files.readAllBytes(Paths.get(args[0]));need(SOURCE.equals(sha(source)),"Story city source differs");DexFileReader reader=new DexFileReader(source);need(reader.getDexVersion()==DexConstants.DEX_038&&reader.getClassSize()==649,"Manager format differs");DexFileWriter writer=new DexFileWriter();writer.cp.dex038();
  reader.accept(new DexFileVisitor(writer){
   @Override public DexClassVisitor visit(int flags,String owner,String parent,String[]interfaces){DexClassVisitor cv=super.visit(flags,owner,parent,interfaces);
    if(!Arrays.asList(CITY,CHAPTER,ENTRY,WEEK,BSON,G,THUNK,ROOM,CLUE).contains(owner))return cv;
    return new DexClassVisitor(cv){
     @Override public void visitEnd(){if(owner.equals(G)){need(queryAdded++==0,"Duplicate query methods");queryMethod().accept(cv);allowedMethod().accept(cv);cocBeginMethod().accept(cv);cocFinishMethod().accept(cv);queryAdded++;}super.visitEnd();}
     @Override public DexMethodVisitor visitMethod(int access,Method method){String n=method.getName(),d=method.getDesc();
      need(!(owner.equals(ENTRY)&&n.equals("q7OriginalSupports"))&&!(owner.equals(BSON)&&n.equals("q7OriginalAllAreaInfoReplyDocument"))&&!(owner.equals(G)&&(n.equals(QUERY)||n.equals(ALLOWED))),"Unexpected core wrapper");
      boolean supports=owner.equals(ENTRY)&&n.equals("supports")&&d.equals("(I)Z"),area=owner.equals(BSON)&&n.equals("allAreaInfoReplyDocument")&&d.equals("(Z"+P+"[B)[B");
      if(supports||area){need((access&(DexConstants.ACC_STATIC|DexConstants.ACC_ABSTRACT|DexConstants.ACC_NATIVE))==DexConstants.ACC_STATIC&&wrappers.add(n),"Core wrapper static/body ABI changed");
       return new DexMethodNode(access,method){@Override public void visitEnd(){need(codeNode!=null,"Missing original core body");DexMethodNode wrapper=new DexMethodNode(access,method);wrapper.anns=anns;wrapper.parameterAnns=parameterAnns;wrapper.codeNode=new DexCodeNode();String[]params=method.getParameterTypes();int[]rs=new int[params.length];for(int i=0;i<rs.length;i++){need(!params[i].equals("J")&&!params[i].equals("D"),"Unexpected wide core parameter");rs[i]=i+1;}wrapper.codeNode.visitRegister(rs.length+1);wrapper.codeNode.visitMethodStmt(Op.INVOKE_STATIC,rs,new Method(HELP,n,params,method.getReturnType()));wrapper.codeNode.visitStmt1R(area?Op.MOVE_RESULT_OBJECT:Op.MOVE_RESULT,0);wrapper.codeNode.visitStmt1R(area?Op.RETURN_OBJECT:Op.RETURN,0);wrapper.accept(cv);this.method=new Method(owner,supports?"q7OriginalSupports":"q7OriginalAllAreaInfoReplyDocument",params,method.getReturnType());this.access=access|DexConstants.ACC_SYNTHETIC;this.accept(cv);}};
      }
      boolean puzzleRoom=owner.equals(ROOM)&&n.equals("<init>")&&d.equals("([Ljava/lang/String;)V"),puzzleClue=owner.equals(CLUE)&&n.equals("<init>")&&d.equals("([Ljava/lang/String;)V");
      if(puzzleRoom||puzzleClue){DexMethodVisitor pmv=super.visitMethod(access,method);need((access&(DexConstants.ACC_STATIC|DexConstants.ACC_ABSTRACT|DexConstants.ACC_NATIVE))==0,"Puzzle constructor access changed");
       return new DexMethodVisitor(pmv){@Override public DexCodeVisitor visitCode(){DexCodeVisitor out=super.visitCode();return new DexCodeNode(){@Override public void visitEnd(){need(totalRegister==(puzzleRoom?8:6),"Puzzle constructor registers changed");puzzleMutate(this,puzzleRoom);this.accept(out);out.visitEnd();}};}};
      }
      boolean client=owner.equals(G)&&n.equals("handleClient"),reliable=owner.equals(G)&&n.equals("handleReliableRpc");
      if(client||reliable){DexMethodVisitor qmv=super.visitMethod(access,method);need((access&(DexConstants.ACC_STATIC|DexConstants.ACC_ABSTRACT|DexConstants.ACC_NATIVE))==0,"Query method access changed");
       return new DexMethodVisitor(qmv){@Override public DexCodeVisitor visitCode(){DexCodeVisitor out=super.visitCode();return new DexCodeNode(){@Override public void visitEnd(){need(totalRegister==(client?50:58),"Query method registers changed");queryMutate(this,client);this.accept(out);out.visitEnd();}};}};
      }
      DexMethodVisitor mv=super.visitMethod(access,method);boolean city=owner.equals(CITY)&&REDIRECT.containsKey(n+d),thunk=owner.equals(THUNK)&&n.equals("apply")&&d.equals("("+RESULT+CAT+P+")V"),admission=owner.equals(G)&&n.equals("handleCombatAdmission"),finish=owner.equals(G)&&n.equals("handleCombatOfflineFinish"),prefix=owner.equals(CHAPTER)&&(n.equals("state")&&d.equals("([BI)Ljava/lang/Integer;")||n.equals("locked")&&d.equals("([BI)Z")),reset=owner.equals(WEEK)&&n.equals("resetProfile")&&d.equals("([B"+P+"I"+R+"LocalWeekCatalog;)[B");
      if(!city&&!thunk&&!admission&&!finish&&!prefix&&!reset)return mv;
      if(city)need(changed.add(n+d),"Duplicate city redirect");if(prefix)need(prefixes.add(n)&&(access&DexConstants.ACC_STATIC)!=0,"State prefix access/duplicate");if(reset)need(access==(DexConstants.ACC_PRIVATE|DexConstants.ACC_STATIC),"Week reset access changed");
      return new DexMethodVisitor(mv){@Override public DexCodeVisitor visitCode(){return new DexCodeVisitor(super.visitCode()){
       int cityCalls;
       @Override public void visitRegister(int count){if(prefix)need(count==(n.equals("state")?3:4),"State prefix registers changed");if(reset)need(count==38,"Week reset registers changed");super.visitRegister(count);
        if(prefix){int[]rs=n.equals("state")?new int[]{1,2}:new int[]{2,3};super.visitMethodStmt(Op.INVOKE_STATIC,rs,new Method(HELP,"handlesState",new String[]{"[B","I"},"Z"));super.visitStmt1R(Op.MOVE_RESULT,0);DexLabel original=new DexLabel();super.visitJumpStmt(Op.IF_EQZ,0,-1,original);super.visitMethodStmt(Op.INVOKE_STATIC,rs,new Method(HELP,n,new String[]{"[B","I"},method.getReturnType()));super.visitStmt1R(n.equals("state")?Op.MOVE_RESULT_OBJECT:Op.MOVE_RESULT,0);super.visitStmt1R(n.equals("state")?Op.RETURN_OBJECT:Op.RETURN,0);super.visitLabel(original);}
       }
       @Override public void visitMethodStmt(Op op,int[]rs,Method called){
        if(city&&called.getOwner().equals(R+"StoryMissionBridge;")&&called.getName().equals(n)&&called.getDesc().equals(d)){need(++cityCalls==1&&op==Op.INVOKE_STATIC,"City wrapper invoke changed");super.visitMethodStmt(op,rs,new Method(HELP,n,called.getParameterTypes(),called.getReturnType()));return;}
        if(thunk&&called.getOwner().equals(CHAPTER)&&called.getName().equals("refresh")){need(++refresh==1&&op==Op.INVOKE_STATIC&&Arrays.equals(rs,new int[]{1,2,3})&&called.getDesc().equals(d),"Chapter refresh thunk changed");super.visitMethodStmt(op,rs,new Method(HELP,"refresh",called.getParameterTypes(),"V"));return;}
        if(admission&&called.getOwner().equals(R+"StoryMissionBridge;")&&called.getName().equals("partyAllowed")){need(++party==1&&op==Op.INVOKE_STATIC&&Arrays.equals(rs,new int[]{1})&&called.getDesc().equals("([B)Z"),"Party guard call changed");super.visitMethodStmt(op,rs,new Method(HELP,"partyAllowed",new String[]{"[B"},"Z"));return;}
        if((admission||finish)&&called.getOwner().equals(PROVIDER)&&called.getName().equals("updateEconomy")){need(op==Op.INVOKE_INTERFACE&&called.getDesc().equals("(Ljava/lang/String;Ljava/lang/String;[B"+P+")"+ECORESULT),"COC Store call shape changed");
         if(admission){need(++cocBeginCalls==1,"Duplicate COC begin store call");need(rs.length==5&&Arrays.equals(rs,new int[]{0,6,2,1,10}),"COC begin argument registers changed");super.visitFieldStmt(Op.IGET_OBJECT,rs[2],7,TUTORIAL_STORE);super.visitMethodStmt(Op.INVOKE_STATIC,rs,new Method(G,"q7StoryCityCocBegin",new String[]{PROVIDER,"Ljava/lang/String;",TUTORIAL,"[B",P},called.getReturnType()));}
         else{need(++cocFinishCalls==1,"Duplicate COC finish store call");super.visitMethodStmt(Op.INVOKE_STATIC,rs,new Method(G,"q7StoryCityCocFinish",new String[]{PROVIDER,"Ljava/lang/String;","Ljava/lang/String;","[B",P},called.getReturnType()));}
         return;}
        super.visitMethodStmt(op,rs,called);
       }
       @Override public void visitStmt1R(Op op,int reg){if(reset&&op==Op.RETURN_OBJECT){need(reg==0&&++resets==1,"Week reset sole return changed");super.visitMethodStmt(Op.INVOKE_STATIC,new int[]{0},new Method(HELP,"resetProfile",new String[]{"[B"},"[B"));super.visitStmt1R(Op.MOVE_RESULT_OBJECT,0);}super.visitStmt1R(op,reg);}
       @Override public void visitEnd(){if(city)need(cityCalls==1,"Missing city wrapper invoke");super.visitEnd();}
      };}};
     }
    };
   }
  });
  need(changed.containsAll(REDIRECT.keySet())&&refresh==1&&party==1&&resets==1&&prefixes.equals(new HashSet<>(Arrays.asList("state","locked")))&&wrappers.equals(new HashSet<>(Arrays.asList("supports","allAreaInfoReplyDocument"))),"Incomplete core city seams");need(queryAdded==2&&querySites==2&&queryBlocks==2&&cocBeginCalls==1&&cocFinishCalls==1&&puzzleRooms==1&&puzzleClues==1,"Incomplete Gateway/puzzle seam");byte[]target=writer.toByteArray();need(TARGET.equals(sha(target)),"Story city output differs: "+sha(target));Files.write(Paths.get(args[1]),target,StandardOpenOption.CREATE_NEW);System.out.println("sha256="+sha(target)+"; redirected=7; prefixes=2; reset_tail=1; wrappers=2; bridges=2; query_sites=2; query_method=2; coc_begin=1; coc_finish=1; puzzle_rooms=1; puzzle_clues=1");
 }
}
