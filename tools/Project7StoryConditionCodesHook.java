import com.googlecode.d2j.*;
import com.googlecode.d2j.dex.writer.DexFileWriter;
import com.googlecode.d2j.node.*;
import com.googlecode.d2j.node.insn.*;
import com.googlecode.d2j.reader.*;
import com.googlecode.d2j.visitors.*;
import java.nio.file.*;import java.security.MessageDigest;import java.util.*;

/** Maintainer-only manager bytecode seam for original condition codes 31/45/46/49.
 *
 * The frozen manager owns every other condition branch.  This hook appends the
 * four proven codes to LocalStoryConditions.SUPPORTED and inserts one dispatch
 * block at the start of matchesValue.  The original clinit entries and every
 * original matchesValue branch are left byte-for-byte in place; unsupported
 * code 20 is not touched.
 */
public final class Project7StoryConditionCodesHook {
 static final String SOURCE="fee369231e8924923f774cdbda4961f91b6ab87cee237b249cff8229b535f1c6";
 static final String TARGET="b012f019387db916846ee0531ba6518e1b84271db5fdf356e7af6bd1adbfcf53";
 static final String R="Lcom/project7/localmanager/",LSC=R+"LocalStoryConditions;";
 static final String STR="Ljava/lang/String;",BYTES="[B",INT="Ljava/lang/Integer;",BOOL="Ljava/lang/Boolean;";
 static final String LIST="Ljava/util/List;",ITER="Ljava/util/Iterator;",OBJ="Ljava/lang/Object;",STRARR="[Ljava/lang/String;";
 static final String IAE="Ljava/lang/IllegalArgumentException;",ALIST="Ljava/util/ArrayList;";
 static final Method VALUE_OF=new Method(INT,"valueOf",new String[]{"I"},INT);
 static final Method PARSE_INT=new Method(INT,"parseInt",new String[]{STR},"I");
 static final Method INT_VALUE=new Method(INT,"intValue",new String[]{},"I");
 static final Method BOOL_VALUE=new Method(BOOL,"booleanValue",new String[]{},"Z");
 static final Method SPLIT=new Method(STR,"split",new String[]{STR,"I"},STRARR);
 static final Method IS_EMPTY=new Method(STR,"isEmpty",new String[]{},"Z");
 static final Method ITERATOR=new Method(LIST,"iterator",new String[]{},"Ljava/util/Iterator;");
 static final Method HAS_NEXT=new Method(ITER,"hasNext",new String[]{},"Z");
 static final Method NEXT=new Method(ITER,"next",new String[]{},"Ljava/lang/Object;");
 static final Method ADD=new Method(LIST,"add",new String[]{OBJ},"Z");
 static final Method CONTAINS=new Method(LIST,"contains",new String[]{OBJ},"Z");
 static final Method ALIST_INIT=new Method(ALIST,"<init>",new String[]{},"V");
 static final Method IAE_INIT=new Method(IAE,"<init>",new String[]{STR},"V");
 static final Method MATH_MUL=new Method("Ljava/lang/Math;","multiplyExact",new String[]{"I","I"},"I");
 static final Method MATH_ADD=new Method("Ljava/lang/Math;","addExact",new String[]{"I","I"},"I");
 static final String BS=R+"BsonLite;",RES=R+"LocalResourceEngine;";
 static final Method BSON_DOC=new Method(BS,"documentValue",new String[]{BYTES,STR},BYTES);
 static final Method BSON_INT=new Method(BS,"intValue",new String[]{BYTES,STR},INT);
 static final Method BSON_BOOL=new Method(BS,"boolValue",new String[]{BYTES,STR},BOOL);
 static final Method BSON_KEYS=new Method(BS,"keys",new String[]{BYTES},LIST);
 static final Method HERO_DOC=new Method(BS,"profileHeroDocument",new String[]{BYTES,"I"},BYTES);
 static final Method RES_ARRAY=new Method(RES,"array",new String[]{BYTES},LIST);
 static final Method OWNS=new Method(RES,"ownsHero",new String[]{BYTES,"I"},"Z");
 static final Method EXTRA=new Method(LSC,"q7ExtraCondition",new String[]{"I",STR,BYTES},"Z");
 static final Method STAR=new Method(LSC,"q7HeroStar",new String[]{STR,BYTES},"Z");
 static final Method HUO=new Method(LSC,"q7Huohaihua",new String[]{STR,BYTES},"Z");
 static final Method INTERVAL=new Method(LSC,"q7Interval",new String[]{STR,"I"},"Z");
 static final Method COUNT=new Method(LSC,"q7ThresholdCount",new String[]{BYTES,STR,"I","Z"},"I");
 static final Method DOCS=new Method(LSC,"q7HeroDocuments",new String[]{BYTES},LIST);
 static int added,dispatches,olds;
 static void need(boolean v,String m){if(!v)throw new IllegalStateException(m);}
 static String sha(byte[]b)throws Exception{StringBuilder s=new StringBuilder();for(byte x:MessageDigest.getInstance("SHA-256").digest(b))s.append(String.format("%02x",x&255));return s.toString();}
 static void ret(DexCodeNode c,boolean value){c.visitConstStmt(Op.CONST_4,0,Integer.valueOf(value?1:0));c.visitStmt1R(Op.RETURN,0);}
 static void fail(DexCodeNode c,int r,String message){c.visitTypeStmt(Op.NEW_INSTANCE,r,0,IAE);c.visitConstStmt(Op.CONST_STRING,r+1,message);c.visitMethodStmt(Op.INVOKE_DIRECT,new int[]{r,r+1},IAE_INIT);c.visitStmt1R(Op.THROW,r);}
 /** Half-open [min,max) over an original IntervalCondition count. Empty literal is true. */
 static DexMethodNode intervalMethod(){
  DexMethodNode m=new DexMethodNode(DexConstants.ACC_PRIVATE|DexConstants.ACC_STATIC,new Method(LSC,"q7Interval",new String[]{STR,"I"},"Z"));
  DexCodeNode c=new DexCodeNode();DexLabel notEmpty=new DexLabel(),shape=new DexLabel(),ordered=new DexLabel(),fals=new DexLabel(),bad=new DexLabel(),rev=new DexLabel();
  c.visitRegister(8);
  c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{6},IS_EMPTY);c.visitStmt1R(Op.MOVE_RESULT,0);c.visitJumpStmt(Op.IF_EQZ,0,0,notEmpty);ret(c,true);c.visitLabel(notEmpty);
  c.visitConstStmt(Op.CONST_STRING,0,",");c.visitConstStmt(Op.CONST_4,1,Integer.valueOf(-1));c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{6,0,1},SPLIT);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,0);
  c.visitStmt2R(Op.ARRAY_LENGTH,1,0);c.visitConstStmt(Op.CONST_4,2,Integer.valueOf(2));c.visitJumpStmt(Op.IF_EQ,1,2,shape);c.visitJumpStmt(Op.GOTO_32,-1,0,bad);
  c.visitLabel(shape);
  c.visitConstStmt(Op.CONST_4,1,Integer.valueOf(0));c.visitStmt3R(Op.AGET_OBJECT,3,0,1);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{3},PARSE_INT);c.visitStmt1R(Op.MOVE_RESULT,1);
  c.visitConstStmt(Op.CONST_4,2,Integer.valueOf(1));c.visitStmt3R(Op.AGET_OBJECT,3,0,2);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{3},PARSE_INT);c.visitStmt1R(Op.MOVE_RESULT,2);
  c.visitJumpStmt(Op.IF_LE,1,2,ordered);c.visitJumpStmt(Op.GOTO_32,-1,0,rev);c.visitLabel(ordered);
  c.visitJumpStmt(Op.IF_LT,7,1,fals);c.visitJumpStmt(Op.IF_GE,7,2,fals);ret(c,true);c.visitLabel(fals);ret(c,false);
  c.visitLabel(bad);fail(c,4,"invalid condition interval");
  c.visitLabel(rev);fail(c,4,"reversed condition interval");
  m.codeNode=c;return m;
 }
 /** Count owned hrs hero documents by a numeric field against a threshold. */
 static DexMethodNode countMethod(){
  DexMethodNode m=new DexMethodNode(DexConstants.ACC_PRIVATE|DexConstants.ACC_STATIC,new Method(LSC,"q7ThresholdCount",new String[]{BYTES,STR,"I","Z"},"I"));
  DexCodeNode c=new DexCodeNode();DexLabel loop=new DexLabel(),done=new DexLabel(),bad=new DexLabel(),below=new DexLabel(),hit=new DexLabel(),next=new DexLabel();
  c.visitRegister(12);
  c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{8},DOCS);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,0);c.visitMethodStmt(Op.INVOKE_INTERFACE,new int[]{0},ITERATOR);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,1);
  c.visitConstStmt(Op.CONST_4,2,Integer.valueOf(0));
  c.visitLabel(loop);c.visitMethodStmt(Op.INVOKE_INTERFACE,new int[]{1},HAS_NEXT);c.visitStmt1R(Op.MOVE_RESULT,3);c.visitJumpStmt(Op.IF_EQZ,3,0,done);
  c.visitMethodStmt(Op.INVOKE_INTERFACE,new int[]{1},NEXT);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,3);c.visitTypeStmt(Op.CHECK_CAST,3,3,BYTES);
  c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{3,9},BSON_INT);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,4);c.visitJumpStmt(Op.IF_EQZ,4,0,bad);
  c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{4},INT_VALUE);c.visitStmt1R(Op.MOVE_RESULT,5);
  c.visitJumpStmt(Op.IF_NEZ,11,0,below);c.visitJumpStmt(Op.IF_GE,5,10,hit);c.visitJumpStmt(Op.GOTO_32,-1,0,next);
  c.visitLabel(below);c.visitJumpStmt(Op.IF_LT,5,10,hit);c.visitJumpStmt(Op.GOTO_32,-1,0,next);
  c.visitLabel(hit);c.visitStmt2R1N(Op.ADD_INT_LIT8,2,2,1);c.visitLabel(next);c.visitJumpStmt(Op.GOTO_32,-1,0,loop);
  c.visitLabel(done);c.visitStmt1R(Op.RETURN,2);
  c.visitLabel(bad);fail(c,6,"invalid hero value");
  m.codeNode=c;return m;
 }
 /** Owned hero documents from the original profile heromgr.hrs array (never bhrs). */
 static DexMethodNode docsMethod(){
  DexMethodNode m=new DexMethodNode(DexConstants.ACC_PRIVATE|DexConstants.ACC_STATIC,new Method(LSC,"q7HeroDocuments",new String[]{BYTES},LIST));
  DexCodeNode c=new DexCodeNode();DexLabel loop=new DexLabel(),done=new DexLabel(),bad=new DexLabel();
  c.visitRegister(7);
  c.visitConstStmt(Op.CONST_STRING,0,"heromgr");c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{6,0},BSON_DOC);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,0);c.visitJumpStmt(Op.IF_EQZ,0,0,bad);
  c.visitConstStmt(Op.CONST_STRING,1,"hrs");c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{0,1},BSON_DOC);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,1);c.visitJumpStmt(Op.IF_EQZ,1,0,bad);
  c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{1},RES_ARRAY);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,1);
  c.visitTypeStmt(Op.NEW_INSTANCE,2,0,ALIST);c.visitMethodStmt(Op.INVOKE_DIRECT,new int[]{2},ALIST_INIT);c.visitMethodStmt(Op.INVOKE_INTERFACE,new int[]{1},ITERATOR);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,1);
  c.visitLabel(loop);c.visitMethodStmt(Op.INVOKE_INTERFACE,new int[]{1},HAS_NEXT);c.visitStmt1R(Op.MOVE_RESULT,3);c.visitJumpStmt(Op.IF_EQZ,3,0,done);
  c.visitMethodStmt(Op.INVOKE_INTERFACE,new int[]{1},NEXT);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,3);c.visitTypeStmt(Op.CHECK_CAST,3,3,BYTES);
  c.visitConstStmt(Op.CONST_STRING,4,"1");c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{3,4},BSON_DOC);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,3);c.visitJumpStmt(Op.IF_EQZ,3,0,bad);
  c.visitMethodStmt(Op.INVOKE_INTERFACE,new int[]{2,3},ADD);c.visitStmt1R(Op.MOVE_RESULT,4);c.visitJumpStmt(Op.GOTO_32,-1,0,loop);
  c.visitLabel(done);c.visitStmt1R(Op.RETURN_OBJECT,2);
  c.visitLabel(bad);fail(c,4,"invalid hero population");
  m.codeNode=c;return m;
 }
 /** Original code 45: count owned heroes whose per-hero hhh flag is true; missing hhh is false. */
 static DexMethodNode huohaihuaMethod(){
  DexMethodNode m=new DexMethodNode(DexConstants.ACC_PRIVATE|DexConstants.ACC_STATIC,new Method(LSC,"q7Huohaihua",new String[]{STR,BYTES},"Z"));
  DexCodeNode c=new DexCodeNode();DexLabel loop=new DexLabel(),done=new DexLabel(),missing=new DexLabel(),next=new DexLabel(),bad=new DexLabel();
  c.visitRegister(10);
  c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{9},DOCS);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,0);c.visitMethodStmt(Op.INVOKE_INTERFACE,new int[]{0},ITERATOR);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,1);
  c.visitConstStmt(Op.CONST_4,2,Integer.valueOf(0));
  c.visitLabel(loop);c.visitMethodStmt(Op.INVOKE_INTERFACE,new int[]{1},HAS_NEXT);c.visitStmt1R(Op.MOVE_RESULT,3);c.visitJumpStmt(Op.IF_EQZ,3,0,done);
  c.visitMethodStmt(Op.INVOKE_INTERFACE,new int[]{1},NEXT);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,3);c.visitTypeStmt(Op.CHECK_CAST,3,3,BYTES);
  c.visitConstStmt(Op.CONST_STRING,4,"hhh");c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{3,4},BSON_BOOL);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,4);c.visitJumpStmt(Op.IF_EQZ,4,0,missing);
  c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{4},BOOL_VALUE);c.visitStmt1R(Op.MOVE_RESULT,4);c.visitJumpStmt(Op.IF_EQZ,4,0,next);c.visitStmt2R1N(Op.ADD_INT_LIT8,2,2,1);c.visitJumpStmt(Op.GOTO_32,-1,0,next);
  c.visitLabel(missing);c.visitConstStmt(Op.CONST_STRING,4,"hhh");c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{3},BSON_KEYS);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,5);c.visitMethodStmt(Op.INVOKE_INTERFACE,new int[]{5,4},CONTAINS);c.visitStmt1R(Op.MOVE_RESULT,5);c.visitJumpStmt(Op.IF_EQZ,5,0,next);c.visitJumpStmt(Op.GOTO_32,-1,0,bad);
  c.visitLabel(next);c.visitJumpStmt(Op.GOTO_32,-1,0,loop);
  c.visitLabel(done);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{8,2},INTERVAL);c.visitStmt1R(Op.MOVE_RESULT,0);c.visitStmt1R(Op.RETURN,0);
  c.visitLabel(bad);fail(c,6,"invalid huohaihua flag");
  m.codeNode=c;return m;
 }
 /** Original code 31: every listed owned hero must satisfy min <= sl*4+so <= max. */
 static DexMethodNode starMethod(){
  DexMethodNode m=new DexMethodNode(DexConstants.ACC_PRIVATE|DexConstants.ACC_STATIC,new Method(LSC,"q7HeroStar",new String[]{STR,BYTES},"Z"));
  DexCodeNode c=new DexCodeNode();DexLabel notEmpty=new DexLabel(),loop=new DexLabel(),body=new DexLabel(),fields=new DexLabel(),shape=new DexLabel(),ordered=new DexLabel(),ge=new DexLabel(),inside=new DexLabel(),fals=new DexLabel(),bad=new DexLabel(),rev=new DexLabel(),invalid=new DexLabel();
  c.visitRegister(14);
  c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{12},IS_EMPTY);c.visitStmt1R(Op.MOVE_RESULT,0);c.visitJumpStmt(Op.IF_EQZ,0,0,notEmpty);ret(c,true);c.visitLabel(notEmpty);
  c.visitConstStmt(Op.CONST_STRING,0,"\\|");c.visitConstStmt(Op.CONST_4,1,Integer.valueOf(-1));c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{12,0,1},SPLIT);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,0);
  c.visitStmt2R(Op.ARRAY_LENGTH,1,0);c.visitConstStmt(Op.CONST_4,2,Integer.valueOf(0));
  c.visitLabel(loop);c.visitJumpStmt(Op.IF_LT,2,1,body);ret(c,true);
  c.visitLabel(body);c.visitStmt3R(Op.AGET_OBJECT,3,0,2);c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{3},IS_EMPTY);c.visitStmt1R(Op.MOVE_RESULT,4);c.visitJumpStmt(Op.IF_EQZ,4,0,fields);c.visitJumpStmt(Op.GOTO_32,-1,0,bad);
  c.visitLabel(fields);c.visitConstStmt(Op.CONST_STRING,4,":");c.visitConstStmt(Op.CONST_4,5,Integer.valueOf(-1));c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{3,4,5},SPLIT);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,3);c.visitStmt2R(Op.ARRAY_LENGTH,4,3);c.visitConstStmt(Op.CONST_4,5,Integer.valueOf(3));c.visitJumpStmt(Op.IF_EQ,4,5,shape);c.visitJumpStmt(Op.GOTO_32,-1,0,bad);
  c.visitLabel(shape);
  c.visitConstStmt(Op.CONST_4,4,Integer.valueOf(0));c.visitStmt3R(Op.AGET_OBJECT,5,3,4);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{5},PARSE_INT);c.visitStmt1R(Op.MOVE_RESULT,5);
  c.visitConstStmt(Op.CONST_4,4,Integer.valueOf(1));c.visitStmt3R(Op.AGET_OBJECT,6,3,4);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{6},PARSE_INT);c.visitStmt1R(Op.MOVE_RESULT,6);
  c.visitConstStmt(Op.CONST_4,4,Integer.valueOf(2));c.visitStmt3R(Op.AGET_OBJECT,7,3,4);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{7},PARSE_INT);c.visitStmt1R(Op.MOVE_RESULT,7);
  c.visitJumpStmt(Op.IF_LE,6,7,ordered);c.visitJumpStmt(Op.GOTO_32,-1,0,rev);
  c.visitLabel(ordered);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{13,5},OWNS);c.visitStmt1R(Op.MOVE_RESULT,8);c.visitJumpStmt(Op.IF_EQZ,8,0,fals);
  c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{13,5},HERO_DOC);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,8);
  c.visitConstStmt(Op.CONST_STRING,9,"sl");c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{8,9},BSON_INT);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,9);
  c.visitConstStmt(Op.CONST_STRING,10,"so");c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{8,10},BSON_INT);c.visitStmt1R(Op.MOVE_RESULT_OBJECT,10);
  c.visitJumpStmt(Op.IF_EQZ,9,0,invalid);c.visitJumpStmt(Op.IF_EQZ,10,0,invalid);
  c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{9},INT_VALUE);c.visitStmt1R(Op.MOVE_RESULT,9);c.visitMethodStmt(Op.INVOKE_VIRTUAL,new int[]{10},INT_VALUE);c.visitStmt1R(Op.MOVE_RESULT,10);
  c.visitConstStmt(Op.CONST_4,11,Integer.valueOf(4));c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{9,11},MATH_MUL);c.visitStmt1R(Op.MOVE_RESULT,9);
  c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{9,10},MATH_ADD);c.visitStmt1R(Op.MOVE_RESULT,9);
  c.visitJumpStmt(Op.IF_LT,9,6,fals);c.visitJumpStmt(Op.IF_GT,9,7,fals);c.visitJumpStmt(Op.GOTO_32,-1,0,inside);
  c.visitLabel(fals);ret(c,false);
  c.visitLabel(inside);c.visitStmt2R1N(Op.ADD_INT_LIT8,2,2,1);c.visitJumpStmt(Op.GOTO_32,-1,0,loop);
  c.visitLabel(bad);fail(c,0,"invalid hero star condition");
  c.visitLabel(rev);fail(c,0,"reversed hero star condition");
  c.visitLabel(invalid);fail(c,0,"invalid hero star");
  m.codeNode=c;return m;
 }
 /** Dispatch for the four added codes only; every other code returns to the original branch chain. */
 static DexMethodNode extraMethod(){
  DexMethodNode m=new DexMethodNode(DexConstants.ACC_PRIVATE|DexConstants.ACC_STATIC,new Method(LSC,"q7ExtraCondition",new String[]{"I",STR,BYTES},"Z"));
  DexCodeNode c=new DexCodeNode();DexLabel l45=new DexLabel(),l46=new DexLabel(),l49=new DexLabel(),unknown=new DexLabel();
  c.visitRegister(12);
  c.visitConstStmt(Op.CONST_16,0,Integer.valueOf(31));c.visitJumpStmt(Op.IF_NE,9,0,l45);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{10,11},STAR);c.visitStmt1R(Op.MOVE_RESULT,0);c.visitStmt1R(Op.RETURN,0);
  c.visitLabel(l45);c.visitConstStmt(Op.CONST_16,0,Integer.valueOf(45));c.visitJumpStmt(Op.IF_NE,9,0,l46);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{10,11},HUO);c.visitStmt1R(Op.MOVE_RESULT,0);c.visitStmt1R(Op.RETURN,0);
  c.visitLabel(l46);c.visitConstStmt(Op.CONST_16,0,Integer.valueOf(46));c.visitJumpStmt(Op.IF_NE,9,0,l49);
  c.visitConstStmt(Op.CONST_STRING,1,"ef");c.visitConstStmt(Op.CONST_16,2,Integer.valueOf(50));c.visitConstStmt(Op.CONST_4,3,Integer.valueOf(0));c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{11,1,2,3},COUNT);c.visitStmt1R(Op.MOVE_RESULT,1);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{10,1},INTERVAL);c.visitStmt1R(Op.MOVE_RESULT,0);c.visitStmt1R(Op.RETURN,0);
  c.visitLabel(l49);c.visitConstStmt(Op.CONST_16,0,Integer.valueOf(49));c.visitJumpStmt(Op.IF_NE,9,0,unknown);
  c.visitConstStmt(Op.CONST_STRING,1,"cf");c.visitConstStmt(Op.CONST_16,2,Integer.valueOf(20));c.visitConstStmt(Op.CONST_4,3,Integer.valueOf(1));c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{11,1,2,3},COUNT);c.visitStmt1R(Op.MOVE_RESULT,1);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{10,1},INTERVAL);c.visitStmt1R(Op.MOVE_RESULT,0);c.visitStmt1R(Op.RETURN,0);
  c.visitLabel(unknown);ret(c,false);
  m.codeNode=c;return m;
 }
 /** Append 31/45/46/49 after the original 35 SUPPORTED entries; the original instructions stay. */
 static void clinit(DexCodeNode code){
  int arrayAt=-1;
  for(int i=0;i<code.stmts.size();i++){DexStmtNode n=code.stmts.get(i);if(n instanceof TypeStmtNode&&n.op==Op.NEW_ARRAY&&((TypeStmtNode)n).a==2&&((TypeStmtNode)n).b==1)arrayAt=i;}
  need(arrayAt>=0,"SUPPORTED array shape changed");
  code.stmts.set(arrayAt,new ConstStmtNode(Op.CONST_16,3,Integer.valueOf(39)));
  code.stmts.add(arrayAt+1,new TypeStmtNode(Op.NEW_ARRAY,2,3,"[Ljava/lang/Integer;"));
  int listAt=-1;
  for(int i=0;i<code.stmts.size();i++){DexStmtNode n=code.stmts.get(i);if(n instanceof MethodStmtNode){MethodStmtNode c=(MethodStmtNode)n;if(c.method.getOwner().equals("Ljava/util/Arrays;")&&c.method.getName().equals("asList")){listAt=i;break;}}}
  need(listAt>arrayAt,"SUPPORTED list shape changed");
  DexCodeNode add=new DexCodeNode();
  int[] codes={31,45,46,49};
  for(int i=0;i<codes.length;i++){add.visitConstStmt(Op.CONST_16,1,Integer.valueOf(codes[i]));add.visitMethodStmt(Op.INVOKE_STATIC,new int[]{1},VALUE_OF);add.visitStmt1R(Op.MOVE_RESULT_OBJECT,1);add.visitConstStmt(Op.CONST_16,3,Integer.valueOf(35+i));add.visitStmt3R(Op.APUT_OBJECT,1,2,3);}
  code.stmts.addAll(listAt,add.stmts);
  olds=35;
 }
 /** One entry dispatch; all non-target codes fall through to the original 54/50/... chain. */
 static void dispatch(DexCodeNode code){
  int at=-1;
  for(int i=0;i<Math.min(code.stmts.size(),40);i++){DexStmtNode n=code.stmts.get(i);if(n instanceof ConstStmtNode){ConstStmtNode c=(ConstStmtNode)n;if(c.op==Op.CONST_16&&c.a==6&&Integer.valueOf(54).equals(c.value)){at=i;break;}}}
  need(at>0,"matchesValue branch head changed");
  DexLabel extra=new DexLabel(),orig=new DexLabel();DexCodeNode pre=new DexCodeNode();
  int[] codes={31,45,46,49};
  for(int value:codes){pre.visitConstStmt(Op.CONST_16,5,Integer.valueOf(value));pre.visitJumpStmt(Op.IF_EQ,0,5,extra);}
  pre.visitJumpStmt(Op.GOTO_32,-1,0,orig);
  pre.visitLabel(extra);pre.visitMethodStmt(Op.INVOKE_STATIC,new int[]{0,1,2},EXTRA);pre.visitStmt1R(Op.MOVE_RESULT,0);pre.visitStmt1R(Op.RETURN,0);
  pre.visitLabel(orig);pre.visitConstStmt(Op.CONST_4,5,Integer.valueOf(0));
  code.stmts.addAll(at,pre.stmts);
  dispatches++;
 }
 public static void main(String[]args)throws Exception{
  need(args.length==2&&!Files.exists(Paths.get(args[1])),"Pinned source and unused output required");
  byte[]source=Files.readAllBytes(Paths.get(args[0]));need(SOURCE.equals(sha(source)),"Condition source differs");
  DexFileReader reader=new DexFileReader(source);need(reader.getDexVersion()==DexConstants.DEX_038&&reader.getClassSize()==649,"Manager format differs");
  DexFileWriter writer=new DexFileWriter();writer.cp.dex038();
  reader.accept(new DexFileVisitor(writer){
   @Override public DexClassVisitor visit(int flags,String owner,String parent,String[]interfaces){DexClassVisitor cv=super.visit(flags,owner,parent,interfaces);
    if(!owner.equals(LSC))return cv;
    return new DexClassVisitor(cv){
     @Override public void visitEnd(){
      need(added==4||added==0,"Duplicate added methods");
      if(added==0){starMethod().accept(cv);huohaihuaMethod().accept(cv);intervalMethod().accept(cv);countMethod().accept(cv);docsMethod().accept(cv);extraMethod().accept(cv);added=4;}
      super.visitEnd();
     }
     @Override public DexMethodVisitor visitMethod(int access,Method method){String n=method.getName(),d=method.getDesc();
      need(!(n.startsWith("q7")),"Unexpected pre-existing q7 method");
      boolean init=n.equals("<clinit>")&&d.equals("()V"),value=n.equals("matchesValue")&&d.equals("(I"+STR+BYTES+R+"LocalTutorialStore$Progress;"+R+"LocalStoryConditions$Context;)Z");
      if(!init&&!value)return super.visitMethod(access,method);
      need(init?((access&DexConstants.ACC_STATIC)!=0):((access&DexConstants.ACC_STATIC)!=0&&(access&DexConstants.ACC_PRIVATE)!=0),"Condition method access changed");
      DexMethodVisitor mv=super.visitMethod(access,method);
      return new DexMethodVisitor(mv){@Override public DexCodeVisitor visitCode(){DexCodeVisitor out=super.visitCode();return new DexCodeNode(){@Override public void visitEnd(){need(totalRegister==(init?19:21),"Condition method registers changed: "+totalRegister);if(init)clinit(this);else dispatch(this);this.accept(out);out.visitEnd();}};}};
     }
    };
   }
  });
  need(added==4&&dispatches==1&&olds==35,"Incomplete condition seam");byte[]target=writer.toByteArray();
  if(!TARGET.isEmpty())need(TARGET.equals(sha(target)),"Condition output differs: "+sha(target));
  Files.write(Paths.get(args[1]),target,StandardOpenOption.CREATE_NEW);System.out.println("sha256="+sha(target)+"; supported=39 old=35 added=4 dispatch=1 methods=6");
 }
}
