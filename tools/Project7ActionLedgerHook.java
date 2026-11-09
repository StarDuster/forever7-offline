import com.googlecode.d2j.*;
import com.googlecode.d2j.dex.writer.DexFileWriter;
import com.googlecode.d2j.node.*;
import com.googlecode.d2j.node.insn.*;
import com.googlecode.d2j.reader.*;
import com.googlecode.d2j.visitors.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

/** Maintainer-only code20 ledger/provider seam over the b012 condition candidate.
 *
 * Input is the already-frozen 31/45/46/49 candidate (b012...).  The four proven
 * code branches and every original condition branch stay untouched.  This hook:
 *   - appends code 20 to LocalStoryConditions.SUPPORTED and dispatches it to the
 *     new LocalActionLedger.condition20 helper (fail closed without a ledger fact),
 *   - records the exact spendActions cost argument under a caller receipt id,
 *   - stages real event completion baselines and lands them in the atomic
 *     profile write, and advances the ledger generation on a real week reset.
 * A compiled LocalActionLedger class (provided as a one-class DEX) is merged
 * into the output.  No D8, APK, native, prepare, or v44 stage edit.
 */
public final class Project7ActionLedgerHook {
 static final String SOURCE="b012f019387db916846ee0531ba6518e1b84271db5fdf356e7af6bd1adbfcf53";
 static final String R="Lcom/project7/localmanager/",LSC=R+"LocalStoryConditions;",LAL=R+"LocalActionLedger;";
 static final String BYTES="[B",STR="Ljava/lang/String;",INT="I",VOID="V",BOOL="Z";
 static final String PROGRESS=R+"LocalTutorialStore$Progress;",CONTEXT=R+"LocalStoryConditions$Context;";
 static final String RESULT=R+"LocalEconomyEngine$Result;",ECON=R+"LocalEconomyEngine;";
 static final String CONS=R+"LocalConstructionEngine;",EVENT=R+"LocalEventEngine;";
 static final String STORE=R+"LocalProfileStore;",WEEK=R+"LocalWeekEngine;";
 static final Field PROFILE=new Field(RESULT,"profile","[B");
 static final Method RECORD=new Method(LAL,"record",new String[]{BYTES,INT,STR},BYTES);
 static final Method TAKE=new Method(LAL,"takeReceipt",new String[]{},STR);
 static final Method SET_ACTION=new Method(LAL,"setActionReceipt",new String[]{BYTES},VOID);
 static final Method SET_BATTLE=new Method(LAL,"setBattleReceipt",new String[]{BYTES,INT},VOID);
 static final Method SET_REST=new Method(LAL,"setRestReceipt",new String[]{STR},VOID);
 static final Method CLEAR=new Method(LAL,"clearReceipt",new String[]{},VOID);
 static final Method PENDING=new Method(LAL,"pending",new String[]{INT},VOID);
 static final Method PENDING_APPLY=new Method(LAL,"pendingApply",new String[]{BYTES},BYTES);
 static final Method PENDING_DONE=new Method(LAL,"pendingDone",new String[]{},VOID);
 static final Method WEEK_CARRY=new Method(LAL,"week",new String[]{BYTES},BYTES);
 static final Method CODE20=new Method(LAL,"condition20",new String[]{STR,BYTES,PROGRESS},BOOL);
 static int lscEdits,ledgerEdits,classes,copies;
 static void need(boolean v,String m){if(!v)throw new IllegalStateException(m);}
 static String sha(byte[]b)throws Exception{StringBuilder s=new StringBuilder();for(byte x:MessageDigest.getInstance("SHA-256").digest(b))s.append(String.format("%02x",x&255));return s.toString();}
 static int idxOfCall(DexCodeNode c, Method m, int from){for(int i=from;i<c.stmts.size();i++){DexStmtNode n=c.stmts.get(i);if(n instanceof MethodStmtNode&&m.equals(((MethodStmtNode)n).method))return i;}return -1;}
 /** Append one Integer.valueOf(code) at array index slot before Arrays.asList. */
 static void appendSupported(DexCodeNode node,int supported,int slot){
  int listAt=-1,sizeAt=-1;
  for(int i=0;i<node.stmts.size();i++){DexStmtNode n=node.stmts.get(i);
   if(n instanceof ConstStmtNode&&n.op==Op.CONST_16&&((ConstStmtNode)n).a==3&&Integer.valueOf(39).equals(((ConstStmtNode)n).value))sizeAt=i;
   if(n instanceof MethodStmtNode&&((MethodStmtNode)n).method.getOwner().equals("Ljava/util/Arrays;")
      &&((MethodStmtNode)n).method.getName().equals("asList")){listAt=i;break;}}
  need(sizeAt>=0&&listAt>sizeAt,"SUPPORTED clinit shape changed");
  node.stmts.set(sizeAt,new ConstStmtNode(Op.CONST_16,3,Integer.valueOf(40)));
  DexCodeNode add=new DexCodeNode();
  add.visitConstStmt(Op.CONST_16,1,Integer.valueOf(supported));
  add.visitMethodStmt(Op.INVOKE_STATIC,new int[]{1},new Method("Ljava/lang/Integer;","valueOf",new String[]{INT},"Ljava/lang/Integer;"));
  add.visitStmt1R(Op.MOVE_RESULT_OBJECT,1);
  add.visitConstStmt(Op.CONST_16,3,Integer.valueOf(slot));
  add.visitStmt3R(Op.APUT_OBJECT,1,2,3);
  node.stmts.addAll(listAt,add.stmts);
  lscEdits++;
 }
 /** Add code20 dispatch to the existing 31/45/46/49 prologue. */
 static void dispatch20(DexCodeNode code){
  int head=-1;
  for(int i=0;i<Math.min(code.stmts.size(),20);i++){DexStmtNode n=code.stmts.get(i);
   if(n instanceof ConstStmtNode&&n.op==Op.CONST_16&&((ConstStmtNode)n).a==5&&Integer.valueOf(31).equals(((ConstStmtNode)n).value)){head=i;break;}}
  need(head>=0,"matchesValue dispatch head changed");
  DexLabel code20=new DexLabel();
  DexCodeNode headBlock=new DexCodeNode();
  headBlock.visitConstStmt(Op.CONST_16,5,Integer.valueOf(20));
  headBlock.visitJumpStmt(Op.IF_EQ,0,5,code20);
  code.stmts.addAll(head,headBlock.stmts);
  int extraIdx=idxOfCall(code,new Method(LSC,"q7ExtraCondition",new String[]{INT,STR,BYTES},BOOL),head+2);
  need(extraIdx>head,"matchesValue extra call changed");
  int gotoIdx=-1;
  for(int i=extraIdx-1;i>=head+2;i--){DexStmtNode n=code.stmts.get(i);if(n instanceof JumpStmtNode&&(n.op==Op.GOTO_32||n.op==Op.GOTO_16||n.op==Op.GOTO)){gotoIdx=i;break;}}
  need(gotoIdx>head,"matchesValue dispatch tail changed");
  DexCodeNode tail=new DexCodeNode();
  tail.visitLabel(code20);
  tail.visitMethodStmt(Op.INVOKE_STATIC,new int[]{1,2,3},CODE20);
  tail.visitStmt1R(Op.MOVE_RESULT,0);
  tail.visitStmt1R(Op.RETURN,0);
  code.stmts.addAll(gotoIdx+1,tail.stmts);
  lscEdits++;
 }
 /** Exact cost owner: record the cost argument once per accepted spend. */
 static void spend(DexCodeNode code,int regs){ // args p0=regs-3,p1=regs-2,p2=regs-1
  int at=-1;
  for(int i=0;i<code.stmts.size();i++){DexStmtNode n=code.stmts.get(i);
   if(n instanceof FieldStmtNode&&n.op==Op.IPUT&&"remainingActions".equals(((FieldStmtNode)n).field.getName())){at=i;break;}}
  need(at>=0,"spendActions remainingActions write changed");
  int p0=regs-3,p2=regs-1;
  DexCodeNode add=new DexCodeNode();
  add.visitMethodStmt(Op.INVOKE_STATIC,new int[]{},TAKE);
  add.visitStmt1R(Op.MOVE_RESULT_OBJECT,1);
  add.visitFieldStmt(Op.IGET_OBJECT,3,p0,PROFILE);
  add.visitMethodStmt(Op.INVOKE_STATIC,new int[]{3,p2,1},RECORD);
  add.visitStmt1R(Op.MOVE_RESULT_OBJECT,3);
  add.visitFieldStmt(Op.IPUT_OBJECT,3,p0,PROFILE);
  code.stmts.addAll(at+1,add.stmts);
  ledgerEdits++;
 }
 /** apply: stage the reliable request payload as the construction receipt id. */
 static void apply(DexCodeNode code,int regs){ // args p0=regs-5..p4=regs-1
  DexCodeNode add=new DexCodeNode();
  add.visitStmt2R(Op.MOVE_OBJECT_16,0,regs-1);
  add.visitMethodStmt(Op.INVOKE_STATIC,new int[]{0},SET_ACTION);
  code.stmts.addAll(0,add.stmts);
  ledgerEdits++;
 }
 /** finish: week+stage is the existing q7BattleReceipts identity. */
 static void finish(DexCodeNode code,int regs){
  int at=idxOfCall(code,new Method(ECON,"spendActions",new String[]{RESULT,PROGRESS,INT},VOID),0);
  need(at>=0,"finish spendActions call changed");
  DexCodeNode add=new DexCodeNode();
  add.visitFieldStmt(Op.IGET_OBJECT,8,0,PROFILE);
  add.visitMethodStmt(Op.INVOKE_STATIC,new int[]{8,5},SET_BATTLE);
  code.stmts.addAll(at,add.stmts);
  ledgerEdits++;
 }
 /** rest: the committed day key is the existing q7Rest identity. */
 static void rest(DexCodeNode code){
  int at=idxOfCall(code,new Method(ECON,"spendActions",new String[]{RESULT,PROGRESS,INT},VOID),0);
  need(at>=0,"rest spendActions call changed");
  DexCodeNode add=new DexCodeNode();
  add.visitMethodStmt(Op.INVOKE_STATIC,new int[]{7},SET_REST);
  code.stmts.addAll(at,add.stmts);
  ledgerEdits++;
 }
 /** complete: stage one real completion after completedEvents/eventDays writes. */
 static void complete(DexCodeNode code,int regs){ // p1=regs-2
  int at=-1;
  for(int i=0;i<code.stmts.size();i++){DexStmtNode n=code.stmts.get(i);
   if(n instanceof ConstStmtNode&&n.op==Op.CONST_16&&Integer.valueOf(1047).equals(((ConstStmtNode)n).value)){at=i;break;}}
  need(at>=0,"complete eventDays tail changed");
  DexCodeNode add=new DexCodeNode();
  add.visitMethodStmt(Op.INVOKE_STATIC,new int[]{regs-2},PENDING);
  code.stmts.addAll(at,add.stmts);
  ledgerEdits++;
 }
 /** writeAtomic: apply staged baselines to the profile bytes and clear on success. */
 static void write(DexCodeNode code,int regs){ // p1=regs-1
  DexCodeNode add=new DexCodeNode();
  add.visitMethodStmt(Op.INVOKE_STATIC,new int[]{regs-1},PENDING_APPLY);
  add.visitStmt1R(Op.MOVE_RESULT_OBJECT,regs-1);
  code.stmts.addAll(0,add.stmts);
  int ret=-1;
  for(int i=code.stmts.size()-1;i>=0;i--){DexStmtNode n=code.stmts.get(i);if(n.op==Op.RETURN_VOID){ret=i;break;}}
  need(ret>=0,"writeAtomic success return changed");
  DexCodeNode done=new DexCodeNode();
  done.visitMethodStmt(Op.INVOKE_STATIC,new int[]{},PENDING_DONE);
  code.stmts.addAll(ret,done.stmts);
  ledgerEdits++;
 }
 /** updateEconomy: clear any stale per-request receipt before a new operation. */
 static void clear(DexCodeNode code){
  DexCodeNode add=new DexCodeNode();
  add.visitMethodStmt(Op.INVOKE_STATIC,new int[]{},CLEAR);
  code.stmts.addAll(0,add.stmts);
  ledgerEdits++;
 }
 /** resetProfile: carry spend, advance generation, drop old facts. */
 static void reset(DexCodeNode code){
  int ret=-1;
  for(int i=code.stmts.size()-1;i>=0;i--){DexStmtNode n=code.stmts.get(i);if(n.op==Op.RETURN_OBJECT){ret=i;break;}}
  need(ret>0,"resetProfile return changed");
  DexCodeNode add=new DexCodeNode();
  add.visitMethodStmt(Op.INVOKE_STATIC,new int[]{0},WEEK_CARRY);
  add.visitStmt1R(Op.MOVE_RESULT_OBJECT,0);
  code.stmts.addAll(ret,add.stmts);
  ledgerEdits++;
 }
 public static void main(String[]args)throws Exception{
  need(args.length==3&&!Files.exists(Paths.get(args[2])),"Source, ledger dex, unused output required");
  byte[]source=Files.readAllBytes(Paths.get(args[0]));need(SOURCE.equals(sha(source)),"Code20 base candidate differs");
  byte[]ledgerDex=Files.readAllBytes(Paths.get(args[1]));
  DexFileReader reader=new DexFileReader(source);need(reader.getDexVersion()==DexConstants.DEX_038&&reader.getClassSize()==649,"Manager format differs");
  classes=reader.getClassSize();
  DexFileWriter writer=new DexFileWriter();writer.cp.dex038();
  reader.accept(new DexFileVisitor(writer){
   @Override public DexClassVisitor visit(int flags,String owner,String parent,String[]interfaces){
    DexClassVisitor cv=super.visit(flags,owner,parent,interfaces);
    if(!owner.equals(LSC)&&!owner.equals(CONS)&&!owner.equals(EVENT)&&!owner.equals(STORE)&&!owner.equals(WEEK)&&!owner.equals(ECON))return cv;
    return new DexClassVisitor(cv){
     @Override public DexMethodVisitor visitMethod(int access,final Method method){
      final String n=method.getName(),d=method.getDesc();boolean target=false;
      if(owner.equals(LSC)&&n.equals("<clinit>")&&d.equals("()V"))target=true;
      if(owner.equals(LSC)&&n.equals("matchesValue")&&d.equals("(I"+STR+BYTES+PROGRESS+CONTEXT+")Z"))target=true;
      if(owner.equals(ECON)&&n.equals("spendActions")&&d.equals("("+RESULT+PROGRESS+INT+")V"))target=true;
      if(owner.equals(ECON)&&n.equals("finish")&&d.equals("("+RESULT+R+"LocalEconomyCatalog;"+R+"LocalResourceCatalog;"+PROGRESS+BYTES+")V"))target=true;
      if(owner.equals(ECON)&&n.equals("rest")&&d.equals("("+RESULT+R+"LocalEconomyCatalog;"+PROGRESS+")V"))target=true;
      if(owner.equals(CONS)&&n.equals("apply")&&d.equals("("+BYTES+R+"LocalConstructionCatalog;"+PROGRESS+STR+BYTES+")"+RESULT))target=true;
      if(owner.equals(EVENT)&&n.equals("complete")&&d.equals("(IZ)V"))target=true;
      if(owner.equals(STORE)&&n.equals("writeAtomic")&&d.equals("(Ljava/io/File;"+BYTES+")V"))target=true;
      if(owner.equals(STORE)&&n.equals("updateEconomy")&&d.equals("("+STR+STR+BYTES+PROGRESS+")"+RESULT))target=true;
      if(owner.equals(WEEK)&&n.equals("resetProfile")&&d.equals("("+BYTES+PROGRESS+INT+R+"LocalWeekCatalog;)"+BYTES))target=true;
      if(!target)return super.visitMethod(access,method);
      DexMethodVisitor mv=super.visitMethod(access,method);
      return new DexMethodVisitor(mv){
       @Override public DexCodeVisitor visitCode(){
        DexCodeVisitor out=super.visitCode();
        return new DexCodeNode(){
         @Override public void visitEnd(){
          int regs=totalRegister;
          if(owner.equals(LSC)&&n.equals("<clinit>"))appendSupported(this,20,39);
          else if(owner.equals(LSC))dispatch20(this);
          else if(owner.equals(ECON)&&n.equals("spendActions"))spend(this,regs);
          else if(owner.equals(ECON)&&n.equals("finish"))finish(this,regs);
          else if(owner.equals(ECON)&&n.equals("rest"))rest(this);
          else if(owner.equals(CONS))apply(this,regs);
          else if(owner.equals(EVENT))complete(this,regs);
          else if(owner.equals(STORE)&&n.equals("writeAtomic"))write(this,regs);
          else if(owner.equals(STORE))clear(this);
          else if(owner.equals(WEEK))reset(this);
          this.accept(out);out.visitEnd();
         }
        };
       }
      };
     }
    };
   }
  });
  // Merge the compiled helper class into the same DEX.
  DexFileReader ledger=new DexFileReader(ledgerDex);
  need(ledger.getClassSize()==1,"Ledger dex must contain exactly one class");
  ledger.accept(new DexFileVisitor(writer));
  copies++;
  byte[]target=writer.toByteArray();
  need(lscEdits==2&&ledgerEdits==8,"Incomplete code20 seam: "+lscEdits+"/"+ledgerEdits);
  Files.write(Paths.get(args[2]),target,StandardOpenOption.CREATE_NEW);
  System.out.println("sha256="+sha(target)+"; lsc="+lscEdits+" ledger="+ledgerEdits+" classes="+(classes+1)+" merge="+copies);
 }
}
