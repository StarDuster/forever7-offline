import com.googlecode.d2j.*;
import com.googlecode.d2j.dex.writer.DexFileWriter;
import com.googlecode.d2j.reader.*;
import com.googlecode.d2j.visitors.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.Arrays;

/** Maintainer-only scoped furniture sampling/admission. Stock award loop stays. */
public final class Project7FurnitureHook {
    static final String SOURCE="075edbaaf62c1d777c1982850fad4b68db518eae9e75ec4e50fc80a7ab7d0863";
    static final String TARGET="5e0e6220e63e04fda492608f34ff16230d010b2f8641fd37a7e4aa7fce80eb19";
    static final String ROOT="Lcom/project7/localmanager/", HOME=ROOT+"LocalHomeEngine;";
    static final String POLICY=ROOT+"HistoryFurniturePolicy;", FEATURE=ROOT+"LocalFeatureCatalog;";
    static final String RESOURCE=ROOT+"LocalResourceCatalog;", RESULT=ROOT+"LocalResourceEngine$Result;";
    static final String LIST="Ljava/util/List;", RANDOM="Ljava/util/Random;", STRING="Ljava/lang/String;", OBJECT="Ljava/lang/Object;";
    static int draws,applies,pools,gates,constants,defaults,outer,inner,bridges,messages,skins,rewards,selections;
    static void need(boolean ok,String message){if(!ok)throw new IllegalStateException(message);}
    static String sha(byte[] data)throws Exception{StringBuilder s=new StringBuilder();for(byte x:MessageDigest.getInstance("SHA-256").digest(data))s.append(String.format("%02x",x&255));return s.toString();}
    static boolean call(Method m,String owner,String name,String desc){return m.getOwner().equals(owner)&&m.getName().equals(name)&&m.getDesc().equals(desc);}
    // Seven scratch locals inserted before eight original incoming words.
    static int reg(int r){return r<31?r:r+7;}
    static int[] regs(int[] input){int[] out=input.clone();for(int i=0;i<out.length;i++)out[i]=reg(out[i]);return out;}
    static void wide(Op op,int... input){
        if(op.name().contains("WIDE")||op.name().contains("LONG")||op.name().contains("DOUBLE"))
            for(int r:input)need(r!=30,"Wide pair crosses inserted-local boundary");
    }
    static void range(Op op,int[] rs){if(op.name().endsWith("_RANGE"))for(int i=1;i<rs.length;i++)need(rs[i]==rs[i-1]+1,"Range crosses inserted locals");}
    public static void main(String[] args)throws Exception{
        need(args.length==2&&!Files.exists(Paths.get(args[1])),"Require pinned source and unused output");
        byte[] input=Files.readAllBytes(Paths.get(args[0]));need(sha(input).equals(SOURCE),"Furniture source differs");
        DexFileReader reader=new DexFileReader(input);need(reader.getDexVersion()==DexConstants.DEX_038&&reader.getClassSize()==649,"Manager format differs");
        DexFileWriter writer=new DexFileWriter();writer.cp.dex038();
        reader.accept(new DexFileVisitor(writer){
            @Override public DexClassVisitor visit(int access,String name,String parent,String[] interfaces){
                DexClassVisitor original=super.visit(access,name,parent,interfaces);if(!name.equals(HOME))return original;
                return new DexClassVisitor(original){
                    @Override public DexMethodVisitor visitMethod(int flags,Method method){
                        need(!method.getName().equals("q7OriginalChoose")&&!method.getName().equals("q7OriginalSkinCopies"),"Furniture bridge already exists");
                        DexMethodVisitor mv=super.visitMethod(flags,method);
                        boolean draw=method.getName().equals("draw")&&method.getDesc().equals("("+RESULT+FEATURE+RESOURCE+STRING+"[BJ"+RANDOM+")V");
                        boolean apply=method.getName().equals("apply")&&method.getDesc().equals("([B"+FEATURE+RESOURCE+STRING+"[BJ"+RANDOM+")"+RESULT);
                        if(!draw&&!apply)return mv;
                        if(draw)need(++draws==1,"Duplicate furniture draw");else need(++applies==1,"Duplicate furniture apply");
                        return new DexMethodVisitor(mv){
                            @Override public DexCodeVisitor visitCode(){
                                return new DexCodeVisitor(super.visitCode()){
                                    boolean waitingGate,waitingSelection;
                                    int r(int x){return draw?reg(x):x;}
                                    @Override public void visitRegister(int count){need(count==(draw?39:45),"Pinned registers differ");super.visitRegister(count+(draw?7:0));}
                                    @Override public DexDebugVisitor visitDebug(){
                                        DexDebugVisitor dv=super.visitDebug();if(!draw)return dv;
                                        return new DexDebugVisitor(dv){
                                            @Override public void visitStartLocal(int r,DexLabel l,String n,String t,String s){super.visitStartLocal(reg(r),l,n,t,s);}
                                            @Override public void visitEndLocal(int r,DexLabel l){super.visitEndLocal(reg(r),l);}
                                            @Override public void visitRestartLocal(int r,DexLabel l){super.visitRestartLocal(reg(r),l);}
                                        };
                                    }
                                    @Override public void visitConstStmt(Op op,int a,Object value){
                                        if(draw&&a==9&&Integer.valueOf(162).equals(value)){need(!waitingGate&&++constants==1,"Ambiguous constant gate");waitingGate=true;return;}
                                        if(draw&&"仅常驻都市配送已接入".equals(value)){need(++messages==1,"Ambiguous refusal text");value="该配送池尚未开放或角色等级不足。";}
                                        if(draw)wide(op,a);super.visitConstStmt(op,r(a),value);
                                    }
                                    @Override public void visitJumpStmt(Op op,int a,int b,DexLabel label){
                                        if(draw&&waitingGate){need(op==Op.IF_NE&&a==4&&b==9&&++gates==1,"Pinned admission branch differs");waitingGate=false;
                                            super.visitMethodStmt(Op.INVOKE_STATIC,new int[]{4},new Method(POLICY,"acceptsPool",new String[]{"I"},"Z"));super.visitStmt1R(Op.MOVE_RESULT,9);super.visitJumpStmt(Op.IF_EQZ,9,-1,label);return;}
                                        super.visitJumpStmt(op,r(a),r(b),label);
                                    }
                                    void sample(String name,int source){
                                        super.visitStmt2R(Op.MOVE_OBJECT_FROM16,31,source);super.visitStmt2R(Op.MOVE_OBJECT_FROM16,32,2);super.visitStmt2R(Op.MOVE_FROM16,33,19);
                                        super.visitMethodStmt(Op.INVOKE_STATIC_RANGE,new int[]{31,32,33},new Method(POLICY,name,new String[]{LIST,RANDOM,"I"},"[B"));
                                    }
                                    @Override public void visitMethodStmt(Op op,int[] input,Method method){
                                        if(draw&&call(method,HOME,"skinCopies","("+RESULT+RESOURCE+"IIJ)V")){
                                            need(op==Op.INVOKE_STATIC_RANGE&&Arrays.equals(input,new int[]{22,23,24,25,26,27})&&++skins==1,"Skin copies call differs");
                                            super.visitStmt2R(Op.MOVE_OBJECT_FROM16,31,22);super.visitStmt2R(Op.MOVE_OBJECT_FROM16,32,23);
                                            super.visitStmt2R(Op.MOVE_FROM16,33,24);super.visitStmt2R(Op.MOVE_FROM16,34,25);super.visitStmt2R(Op.MOVE_WIDE_FROM16,35,26);super.visitStmt2R(Op.MOVE_FROM16,37,19);
                                            super.visitMethodStmt(Op.INVOKE_STATIC_RANGE,new int[]{31,32,33,34,35,36,37},new Method(POLICY,"skinCopies",new String[]{RESULT,RESOURCE,"I","I","J","I"},"V"));return;
                                        }
                                        if(draw&&call(method,RESULT,"reward","()[B")){
                                            need(op==Op.INVOKE_VIRTUAL&&Arrays.equals(input,new int[]{12})&&++rewards==1,"Child reward projection differs");
                                            super.visitStmt2R(Op.MOVE_OBJECT_FROM16,31,12);super.visitStmt2R(Op.MOVE_FROM16,32,19);super.visitStmt2R(Op.MOVE_OBJECT_FROM16,33,42);
                                            super.visitMethodStmt(Op.INVOKE_STATIC_RANGE,new int[]{31,32,33},new Method(POLICY,"reward",new String[]{RESULT,"I","[B"},"[B"));return;
                                        }
                                        if(call(method,HOME,"rule","("+FEATURE+STRING+OBJECT+")[B")){
                                            need(op==Op.INVOKE_STATIC&&Arrays.equals(input,draw?new int[]{1,9,8}:new int[]{6,1,2}),"Pool rule call differs");pools++;
                                            super.visitMethodStmt(op,input,new Method(POLICY,"poolRule",new String[]{FEATURE,STRING,OBJECT},"[B"));return;
                                        }
                                        if(draw&&call(method,FEATURE,"get","("+STRING+OBJECT+")[B")){
                                            need(op==Op.INVOKE_VIRTUAL&&Arrays.equals(input,new int[]{1,6,12})&&++defaults==1,"Default lookup differs");
                                            super.visitStmt2R(Op.MOVE_OBJECT_FROM16,31,1);super.visitStmt2R(Op.MOVE_OBJECT_FROM16,32,6);super.visitStmt2R(Op.MOVE_OBJECT_FROM16,33,12);super.visitStmt2R(Op.MOVE_FROM16,34,19);
                                            super.visitMethodStmt(Op.INVOKE_STATIC_RANGE,new int[]{31,32,33,34},new Method(POLICY,"defaultRow",new String[]{FEATURE,STRING,OBJECT,"I"},"[B"));return;
                                        }
                                        if(draw&&call(method,HOME,"choose","("+LIST+RANDOM+")[B")){
                                            need(op==Op.INVOKE_STATIC,"Chooser opcode differs");
                                            if(Arrays.equals(input,new int[]{3,2})){need(++outer==1,"Duplicate outer choice");sample("chooseOuter",3);return;}
                                            need(Arrays.equals(input,new int[]{6,2})&&++inner==1,"Inner choice differs");sample("chooseInner",6);waitingSelection=true;return;
                                        }
                                        int[] mapped=draw?regs(input):input;range(op,mapped);super.visitMethodStmt(op,mapped,method);
                                    }
                                    @Override public void visitMethodStmt(Op op,int[] rs,CallSite site){throw new IllegalStateException("Unexpected custom invocation");}
                                    @Override public void visitMethodStmt(Op op,int[] rs,Method method,Proto proto){throw new IllegalStateException("Unexpected polymorphic invocation");}
                                    @Override public void visitStmt1R(Op op,int a){
                                        if(draw)wide(op,a);super.visitStmt1R(op,r(a));
                                        if(waitingSelection){need(draw&&op==Op.MOVE_RESULT_OBJECT&&a==6&&++selections==1,"Inner selection result differs");
                                            // Original input params v35 is read only by the entry
                                            // copy. Its mapped v42 is dead for the whole draw loop.
                                            super.visitStmt2R(Op.MOVE_OBJECT_FROM16,42,6);waitingSelection=false;}
                                    }
                                    @Override public void visitStmt2R(Op op,int a,int b){if(draw)wide(op,a,b);super.visitStmt2R(op,r(a),r(b));}
                                    @Override public void visitStmt3R(Op op,int a,int b,int c){if(draw)wide(op,a,b,c);super.visitStmt3R(op,r(a),r(b),r(c));}
                                    @Override public void visitStmt2R1N(Op op,int a,int b,int n){if(draw)wide(op,a,b);super.visitStmt2R1N(op,r(a),r(b),n);}
                                    @Override public void visitFieldStmt(Op op,int a,int b,Field f){if(draw)wide(op,a,b);super.visitFieldStmt(op,r(a),r(b),f);}
                                    @Override public void visitTypeStmt(Op op,int a,int b,String t){super.visitTypeStmt(op,r(a),r(b),t);}
                                    @Override public void visitFillArrayDataStmt(Op op,int a,Object data){super.visitFillArrayDataStmt(op,r(a),data);}
                                    @Override public void visitFilledNewArrayStmt(Op op,int[] rs,String t){int[] mapped=draw?regs(rs):rs;range(op,mapped);super.visitFilledNewArrayStmt(op,mapped,t);}
                                    @Override public void visitSparseSwitchStmt(Op op,int a,int[] cases,DexLabel[] labels){super.visitSparseSwitchStmt(op,r(a),cases,labels);}
                                    @Override public void visitPackedSwitchStmt(Op op,int a,int first,DexLabel[] labels){super.visitPackedSwitchStmt(op,r(a),first,labels);}
                                    @Override public void visitEnd(){need(!waitingGate&&!waitingSelection,"Unfinished furniture replacement");super.visitEnd();}
                                };
                            }
                        };
                    }
                    @Override public void visitEnd(){
                        DexMethodVisitor mv=super.visitMethod(DexConstants.ACC_PUBLIC|DexConstants.ACC_STATIC|DexConstants.ACC_SYNTHETIC,new Method(HOME,"q7OriginalChoose",new String[]{LIST,RANDOM},"[B"));
                        DexCodeVisitor code=mv.visitCode();code.visitRegister(2);code.visitMethodStmt(Op.INVOKE_STATIC,new int[]{0,1},new Method(HOME,"choose",new String[]{LIST,RANDOM},"[B"));code.visitStmt1R(Op.MOVE_RESULT_OBJECT,0);code.visitStmt1R(Op.RETURN_OBJECT,0);code.visitEnd();mv.visitEnd();bridges++;
                        mv=super.visitMethod(DexConstants.ACC_PUBLIC|DexConstants.ACC_STATIC|DexConstants.ACC_SYNTHETIC,new Method(HOME,"q7OriginalSkinCopies",new String[]{RESULT,RESOURCE,"I","I","J"},"V"));
                        code=mv.visitCode();code.visitRegister(6);code.visitMethodStmt(Op.INVOKE_STATIC_RANGE,new int[]{0,1,2,3,4,5},new Method(HOME,"skinCopies",new String[]{RESULT,RESOURCE,"I","I","J"},"V"));code.visitStmt0R(Op.RETURN_VOID);code.visitEnd();mv.visitEnd();bridges++;super.visitEnd();
                    }
                };
            }
        });
        need(draws==1&&applies==1&&pools==2&&gates==1&&constants==1&&defaults==1&&outer==1&&inner==1&&bridges==2&&messages==1&&skins==1&&rewards==1&&selections==1,"Incomplete furniture seams");
        byte[] target=writer.toByteArray();need(sha(target).equals(TARGET),"Furniture output differs from reviewed seams");Files.write(Paths.get(args[1]),target,StandardOpenOption.CREATE_NEW);
        System.out.println("sha256="+sha(target)+"; original_draw_registers=39; mapped_draw_registers=46; added_methods=2; existing_changed_methods=2");
    }
}
