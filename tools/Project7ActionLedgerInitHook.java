import com.googlecode.d2j.*;
import com.googlecode.d2j.dex.writer.DexFileWriter;
import com.googlecode.d2j.node.*;
import com.googlecode.d2j.node.insn.*;
import com.googlecode.d2j.reader.*;
import com.googlecode.d2j.visitors.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

/** Code20 ledger initialization / request-scope repair over the v47 manager DEX.
 *
 * Input is the frozen v47 candidate (action-ledger-code20-v1 target, sha
 * 9f9b1fb5...).  The code20 provider dispatch, the exact spendActions record,
 * the battle/rest receipts and every 31/45/46/49 branch stay as v47 left them.
 * This hook only:
 *   - replaces LocalActionLedger with the v2 helper (new-save origin, request
 *     bound pending, construction seq identity, repeat move);
 *   - marks a profile template read by LocalProfileStore.load as a new save;
 *   - stages a completion only in the genuine eventCompletions branch;
 *   - aborts pending on a failed atomic profile write;
 *   - opens/closes the real reliable-RPC request scope.
 * No D8, APK, native, prepare, or v47 edit.
 */
public final class Project7ActionLedgerInitHook {
 static final String SOURCE="9f9b1fb5fea038dcb31f82e8766b68c0f356444a2591f82998952d46b9f8dcc0";
 static final String R="Lcom/project7/localmanager/",LSC=R+"LocalStoryConditions;",LAL=R+"LocalActionLedger;";
 static final String BYTES="[B",STR="Ljava/lang/String;",INT="I",VOID="V",BOOL="Z";
 static final String PROGRESS=R+"LocalTutorialStore$Progress;",CONTEXT=R+"LocalStoryConditions$Context;";
 static final String RESULT=R+"LocalEconomyEngine$Result;";
 static final String CONS=R+"LocalConstructionEngine;",EVENT=R+"LocalEventEngine;";
 static final String STORE=R+"LocalProfileStore;",SERVER=R+"LocalGatewayServer;";
 static final Method OLD_ACTION=new Method(LAL,"setActionReceipt",new String[]{BYTES},VOID);
 static final Method NEW_ACTION=new Method(LAL,"setActionReceipt",new String[]{BYTES,STR},VOID);
 static final Method OLD_PENDING=new Method(LAL,"pending",new String[]{INT},VOID);
 static final Method NEW_PENDING=new Method(LAL,"pending",new String[]{BYTES,INT},VOID);
 static final Method CLEAR_REQUEST=new Method(LAL,"clearRequest",new String[]{},VOID);
 static final Method END_REQUEST=new Method(LAL,"endRequest",new String[]{},VOID);
 static final Method BEGIN_REQUEST=new Method(LAL,"beginRequest",new String[]{BYTES,"Ljava/lang/Integer;",STR,BYTES,STR},VOID);
 static final Method INIT_NEW=new Method(LAL,"initNew",new String[]{BYTES},BYTES);
 static final Method PENDING_ABORT=new Method(LAL,"pendingAbort",new String[]{},VOID);
 static final Field EVENT_PROFILE=new Field(EVENT,"profile",BYTES);
 static final Method REPAIR=new Method(STORE,"repairRosterEncoding",new String[]{"Ljava/io/File;",BYTES,BOOL},BYTES);
 static int applied,completed,loaded,written,scoped,cleared,classes,skipped,copies;

 static void need(boolean v,String m){if(!v)throw new IllegalStateException(m);}
 static String sha(byte[]b)throws Exception{StringBuilder s=new StringBuilder();for(byte x:MessageDigest.getInstance("SHA-256").digest(b))s.append(String.format("%02x",x&255));return s.toString();}

 static MethodStmtNode methodAt(List<DexStmtNode> stmts, Method m) {
  for (DexStmtNode n : stmts) {
   if (n instanceof MethodStmtNode && m.equals(((MethodStmtNode) n).method)) return (MethodStmtNode) n;
  }
  return null;
 }
 static int indexOf(List<DexStmtNode> stmts, DexStmtNode target) {
  for (int i = 0; i < stmts.size(); i++) if (stmts.get(i) == target) return i;
  return -1;
 }

 /** apply: the real operation string accompanies the payload. */
 static void apply(DexCodeNode code, int regs) {
  MethodStmtNode old = methodAt(code.stmts, OLD_ACTION);
  need(old != null, "apply setActionReceipt call missing");
  int at = indexOf(code.stmts, old);
  DexCodeNode add = new DexCodeNode();
  add.visitStmt2R(Op.MOVE_OBJECT_16, 1, regs - 2);
  add.visitMethodStmt(Op.INVOKE_STATIC, new int[]{0, 1}, NEW_ACTION);
  code.stmts.remove(at);
  code.stmts.addAll(at, add.stmts);
  applied++;
 }

 /** complete: only the eventCompletions increment is a genuine new occurrence. */
 static void complete(DexCodeNode code, int regs) {
  MethodStmtNode old = methodAt(code.stmts, OLD_PENDING);
  need(old != null, "complete pending call missing");
  code.stmts.remove(indexOf(code.stmts, old));
  MethodStmtNode addExact = new MethodStmtNode(Op.INVOKE_STATIC, new int[]{},
          new Method("Ljava/lang/Math;", "addExact", new String[]{INT, INT}, INT));
  int at = -1;
  for (int i = 0; i < code.stmts.size(); i++) {
   DexStmtNode n = code.stmts.get(i);
   if (n instanceof MethodStmtNode && "addExact".equals(((MethodStmtNode) n).method.getName())
           && "Ljava/lang/Math;".equals(((MethodStmtNode) n).method.getOwner())) {
    for (int j = i + 1; j < code.stmts.size(); j++) {
     DexStmtNode next = code.stmts.get(j);
     if (next instanceof MethodStmtNode
             && "put".equals(((MethodStmtNode) next).method.getName())
             && "Ljava/util/Map;".equals(((MethodStmtNode) next).method.getOwner())) {
      at = j + 1;
      break;
     }
    }
    break;
   }
  }
  need(at > 0, "complete eventCompletions put missing");
  DexCodeNode add = new DexCodeNode();
  add.visitFieldStmt(Op.IGET_OBJECT, 7, regs - 3, EVENT_PROFILE);
  add.visitMethodStmt(Op.INVOKE_STATIC, new int[]{7, regs - 2}, NEW_PENDING);
  code.stmts.addAll(at, add.stmts);
  completed++;
 }

 /** load: a template read because the profile file was missing is a new save. */
 static void load(DexCodeNode code) {
  MethodStmtNode repair = methodAt(code.stmts, REPAIR);
  need(repair != null, "load repairRosterEncoding call missing");
  int at = indexOf(code.stmts, repair);
  int move = -1;
  for (int i = at + 1; i < Math.min(at + 6, code.stmts.size()); i++) {
   DexStmtNode n = code.stmts.get(i);
   if (n instanceof Stmt1RNode && ((Stmt1RNode) n).op == Op.MOVE_RESULT_OBJECT
           && ((Stmt1RNode) n).a == 13) { move = i; break; }
  }
  need(move > at, "load repaired profile register missing");
  DexLabel skip = new DexLabel();
  DexCodeNode add = new DexCodeNode();
  add.visitJumpStmt(Op.IF_EQZ, 12, -1, skip);
  add.visitMethodStmt(Op.INVOKE_STATIC, new int[]{13}, INIT_NEW);
  add.visitStmt1R(Op.MOVE_RESULT_OBJECT, 13);
  add.visitLabel(skip);
  code.stmts.addAll(move + 1, add.stmts);
  loaded++;
 }

 /** writeAtomic: a failed atomic write must not keep the staged completion. */
 static void write(DexCodeNode code) {
  int count = 0;
  for (int i = code.stmts.size() - 1; i >= 0; i--) {
   DexStmtNode n = code.stmts.get(i);
   if (n.op == Op.THROW) {
    DexCodeNode add = new DexCodeNode();
    add.visitMethodStmt(Op.INVOKE_STATIC, new int[]{}, PENDING_ABORT);
    code.stmts.addAll(i, add.stmts);
    count++;
   }
  }
  need(count >= 2, "writeAtomic throw paths changed: " + count);
  written++;
 }

 /** handleReliableRpc: one real request scope around every completion/write. */
 static void reliable(DexCodeNode code) {
  DexCodeNode clear = new DexCodeNode();
  clear.visitMethodStmt(Op.INVOKE_STATIC, new int[]{}, CLEAR_REQUEST);
  code.stmts.addAll(0, clear.stmts);
  cleared++;
  int logAt = -1;
  for (int i = 0; i < code.stmts.size(); i++) {
   DexStmtNode n = code.stmts.get(i);
   if (n instanceof ConstStmtNode
           && "reliableRpcCall missing sequence".equals(((ConstStmtNode) n).value)) {
    logAt = i;
    break;
   }
  }
  need(logAt > 0, "handleReliableRpc sequence log missing");
  int labelAt = -1;
  for (int i = logAt - 1; i >= 0; i--) {
   if (code.stmts.get(i) instanceof JumpStmtNode) { labelAt = i; break; }
  }
  need(labelAt > 0, "handleReliableRpc sequence check missing");
  DexCodeNode begin = new DexCodeNode();
  begin.visitMethodStmt(Op.INVOKE_STATIC, new int[]{13, 4, 2, 1, 8}, BEGIN_REQUEST);
  code.stmts.addAll(labelAt, begin.stmts);
  scoped++;
  int returns = 0;
  for (int i = code.stmts.size() - 1; i >= 0; i--) {
   DexStmtNode n = code.stmts.get(i);
   if (n.op == Op.RETURN_VOID) {
    DexCodeNode end = new DexCodeNode();
    end.visitMethodStmt(Op.INVOKE_STATIC, new int[]{}, END_REQUEST);
    code.stmts.addAll(i, end.stmts);
    returns++;
   }
  }
  need(returns >= 5, "handleReliableRpc returns changed: " + returns);
 }

 /** handleClientException: an exception report closes any stale request scope. */
 static void clientException(DexCodeNode code) {
  DexCodeNode clear = new DexCodeNode();
  clear.visitMethodStmt(Op.INVOKE_STATIC, new int[]{}, CLEAR_REQUEST);
  code.stmts.addAll(0, clear.stmts);
  cleared++;
 }

 public static void main(String[]args)throws Exception{
  need(args.length==3&&!Files.exists(Paths.get(args[2])),"Source, ledger dex, unused output required");
  byte[]source=Files.readAllBytes(Paths.get(args[0]));
  need(SOURCE.equals(sha(source)),"Code20 v47 base differs");
  byte[]ledgerDex=Files.readAllBytes(Paths.get(args[1]));
  DexFileReader reader=new DexFileReader(source);
  need(reader.getDexVersion()==DexConstants.DEX_038&&reader.getClassSize()==650,"Manager format differs");
  classes=reader.getClassSize();
  DexFileWriter writer=new DexFileWriter();writer.cp.dex038();
  reader.accept(new DexFileVisitor(writer){
   @Override public DexClassVisitor visit(int flags,final String owner,String parent,String[]interfaces){
    if(owner.equals(LAL)){skipped++;return null;}
    DexClassVisitor cv=super.visit(flags,owner,parent,interfaces);
    if(!owner.equals(CONS)&&!owner.equals(EVENT)&&!owner.equals(STORE)&&!owner.equals(SERVER))return cv;
    return new DexClassVisitor(cv){
     @Override public DexMethodVisitor visitMethod(int access,final Method method){
      final String n=method.getName(),d=method.getDesc();boolean target=false;
      if(owner.equals(CONS)&&n.equals("apply")&&d.equals("("+BYTES+R+"LocalConstructionCatalog;"+PROGRESS+STR+BYTES+")"+RESULT))target=true;
      if(owner.equals(EVENT)&&n.equals("complete")&&d.equals("(IZ)"+VOID))target=true;
      if(owner.equals(STORE)&&n.equals("load")&&d.equals("("+STR+PROGRESS+")"+BYTES))target=true;
      if(owner.equals(STORE)&&n.equals("writeAtomic")&&d.equals("(Ljava/io/File;"+BYTES+")"+VOID))target=true;
      if(owner.equals(SERVER)&&n.equals("handleReliableRpc")&&d.equals("(Ljava/io/OutputStream;"+BYTES+BYTES+STR+PROGRESS+R+"LocalEventEngine;Ljava/util/Set;Ljava/util/Set;Ljava/util/Map;Ljava/util/Set;)"+VOID))target=true;
      if(owner.equals(SERVER)&&n.equals("handleClientException")&&d.equals("("+BYTES+")"+VOID))target=true;
      if(!target)return super.visitMethod(access,method);
      DexMethodVisitor mv=super.visitMethod(access,method);
      return new DexMethodVisitor(mv){
       @Override public DexCodeVisitor visitCode(){
        DexCodeVisitor out=super.visitCode();
        return new DexCodeNode(){
         @Override public void visitEnd(){
          int regs=totalRegister;
          if(owner.equals(CONS))apply(this,regs);
          else if(owner.equals(EVENT))complete(this,regs);
          else if(owner.equals(STORE)&&n.equals("load"))load(this);
          else if(owner.equals(STORE))write(this);
          else if(n.equals("handleReliableRpc"))reliable(this);
          else clientException(this);
          this.accept(out);out.visitEnd();
         }
        };
       }
      };
     }
    };
   }
  });
  DexFileReader ledger=new DexFileReader(ledgerDex);
  need(ledger.getClassSize()==1,"Ledger dex must contain exactly one class");
  ledger.accept(new DexFileVisitor(writer));
  copies++;
  byte[]target=writer.toByteArray();
  need(applied==1&&completed==1&&loaded==1&&written==1&&scoped==1&&cleared==2,
          "Incomplete v2 seam: apply="+applied+" complete="+completed+" load="+loaded
                  +" write="+written+" scope="+scoped+" clear="+cleared);
  need(skipped==1,"old ledger class not replaced");
  Files.write(Paths.get(args[2]),target,StandardOpenOption.CREATE_NEW);
  System.out.println("sha256="+sha(target)+"; replaced="+skipped+" v2="+applied+"/"+completed
          +"/"+loaded+"/"+written+"/"+scoped+"/"+cleared+" classes="+(classes-skipped+copies));
 }
}
