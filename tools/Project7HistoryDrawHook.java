import com.googlecode.d2j.*;
import com.googlecode.d2j.dex.writer.DexFileWriter;
import com.googlecode.d2j.reader.*;
import com.googlecode.d2j.visitors.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.Arrays;

/** Maintainer-only generic history seams; not an APK builder. */
public final class Project7HistoryDrawHook {
    static final String SOURCE = "d16990dff71677c55ecd54225cd1fdc82f06c3785c3258e5053e069f24df341f";
    static final String TARGET = "a71aa19649feaa262332ec03ff1c42254fb21886c1a73767b336f0dbd0c23d3b";
    static final String ROOT = "Lcom/project7/localmanager/";
    static final String CATALOG=ROOT+"LocalResourceCatalog;", POOL=ROOT+"LocalResourceCatalog$Pool;";
    static final String DRAW=ROOT+"LocalDrawEngine;", NORMAL=ROOT+"CoreDrawPolicy;", HISTORY=ROOT+"HistoryDrawPolicy;";
    static final String RESULT=ROOT+"LocalResourceEngine$Result;", RANDOM="Ljava/util/Random;", LIST="Ljava/util/List;";
    static int catalogCtor, catalogReturn, poolCtor, apply, save, guard, factory, spends, reveals, states;
    static void need(boolean ok,String message){if(!ok)throw new IllegalStateException(message);}
    static String sha(byte[] data)throws Exception{StringBuilder b=new StringBuilder();for(byte x:MessageDigest.getInstance("SHA-256").digest(data))b.append(String.format("%02x",x&255));return b.toString();}
    static boolean called(Method m,String owner,String name,String desc){return owner.equals(m.getOwner())&&name.equals(m.getName())&&desc.equals(m.getDesc());}
    public static void main(String[] args)throws Exception{
        if(args.length!=2||Files.exists(Paths.get(args[1])))throw new IllegalArgumentException("Require pinned source and unused output");
        byte[] input=Files.readAllBytes(Paths.get(args[0]));need(sha(input).equals(SOURCE),"History source differs");
        DexFileReader reader=new DexFileReader(input);need(reader.getDexVersion()==DexConstants.DEX_038&&reader.getClassSize()==649,"Manager format differs");
        DexFileWriter writer=new DexFileWriter();writer.cp.dex038();
        reader.accept(new DexFileVisitor(writer){
            @Override public DexClassVisitor visit(int flags,String name,String parent,String[] interfaces){
                DexClassVisitor target=super.visit(flags,name,parent,interfaces);
                if(!name.equals(CATALOG)&&!name.equals(POOL)&&!name.equals(DRAW))return target;
                return new DexClassVisitor(target){
                    @Override public DexMethodVisitor visitMethod(int access,Method method){
                        need(!method.getName().equals("q7OriginalSpend"),"Spend bridge already installed");
                        if(name.equals(POOL))need(!method.getDesc().equals("(III"+LIST+LIST+LIST+")V"),"Typed pool constructor already installed");
                        DexMethodVisitor original=super.visitMethod(access,method);
                        boolean ctor=called(method,CATALOG,"<init>","(Ljava/io/InputStream;)V");
                        boolean current=called(method,DRAW,"applyCurrent","([B"+CATALOG+"Ljava/lang/String;[B"+RANDOM+")"+RESULT);
                        boolean saving=called(method,DRAW,"saveState","("+RESULT+"[BI)V");
                        if(!ctor&&!current&&!saving)return original;
                        if(ctor)need(++catalogCtor==1,"Duplicate catalog ctor");
                        if(current)need(++apply==1,"Duplicate draw dispatcher");
                        if(saving)need(++save==1,"Duplicate state saver");
                        return new DexMethodVisitor(original){
                            @Override public DexCodeVisitor visitCode(){
                                return new DexCodeVisitor(super.visitCode()){
                                    @Override public void visitRegister(int count){need(count==(ctor?12:current?47:14),"Pinned registers differ");super.visitRegister(count);}
                                    @Override public void visitStmt0R(Op op){
                                        if(ctor&&op==Op.RETURN_VOID){need(++catalogReturn==1,"Multiple normal constructor exits");super.visitMethodStmt(Op.INVOKE_STATIC,new int[]{10},new Method(HISTORY,"augmentCatalog",new String[]{CATALOG},"V"));}
                                        super.visitStmt0R(op);
                                    }
                                    @Override public void visitJumpStmt(Op op,int a,int b,DexLabel label){
                                        super.visitJumpStmt(op,a,b,label);
                                        if(current&&op==Op.IF_EQZ&&a==11){
                                            need(++guard==1,"Ambiguous pool-null guard");
                                            // v13's first original use after this skip target is a
                                            // move-result-object; it is dead across the guard.
                                            super.visitMethodStmt(Op.INVOKE_STATIC,new int[]{11,5,4},new Method(HISTORY,"requiresStockChoice",new String[]{POOL,"[B","I"},"Z"));
                                            super.visitStmt1R(Op.MOVE_RESULT,13);
                                            super.visitJumpStmt(Op.IF_EQZ,13,-1,label);
                                        }
                                    }
                                    @Override public void visitMethodStmt(Op op,int[] regs,Method m){
                                        if(current&&called(m,DRAW,"makeActivityFile","("+CATALOG+POOL+"[B"+RANDOM+")[B")){
                                            need(op==Op.INVOKE_STATIC&&Arrays.equals(regs,new int[]{8,11,5,3})&&++factory==1,"History factory call differs");
                                            super.visitMethodStmt(op,regs,new Method(HISTORY,"makeFile",new String[]{CATALOG,POOL,"[B",RANDOM},"[B"));return;
                                        }
                                        if(current&&called(m,DRAW,"spend","("+RESULT+"I"+POOL+"I)V")){
                                            need(op==Op.INVOKE_STATIC&&(Arrays.equals(regs,new int[]{7,10,11,4})||Arrays.equals(regs,new int[]{7,3,11,4})),"Spend registers differ");spends++;
                                            super.visitMethodStmt(op,regs,new Method(HISTORY,"spend",new String[]{RESULT,"I",POOL,"I"},"V"));return;
                                        }
                                        if(current&&called(m,NORMAL,"reveal","("+RESULT+CATALOG+"[B)[B")){
                                            need(op==Op.INVOKE_STATIC&&++reveals==1,"Reveal seam differs");super.visitMethodStmt(op,regs,new Method(HISTORY,"reveal",new String[]{RESULT,CATALOG,"[B"},"[B"));return;
                                        }
                                        if(saving&&called(m,NORMAL,"stateForSave","([BI)[B")){
                                            need(op==Op.INVOKE_STATIC&&Arrays.equals(regs,new int[]{12,13})&&++states==1,"State seam differs");super.visitMethodStmt(op,regs,new Method(HISTORY,"stateForSave",new String[]{"[B","I"},"[B"));return;
                                        }
                                        super.visitMethodStmt(op,regs,m);
                                    }
                                };
                            }
                        };
                    }
                    @Override public void visitEnd(){
                        if(name.equals(POOL)){
                            DexMethodVisitor mv=super.visitMethod(DexConstants.ACC_CONSTRUCTOR|DexConstants.ACC_SYNTHETIC,new Method(POOL,"<init>",new String[]{"I","I","I",LIST,LIST,LIST},"V"));
                            DexCodeVisitor c=mv.visitCode();c.visitRegister(9);
                            c.visitMethodStmt(Op.INVOKE_DIRECT,new int[]{2},new Method("Ljava/lang/Object;","<init>",new String[]{},"V"));
                            String[] ints={"id","stamp","ticket"};for(int i=0;i<3;i++)c.visitFieldStmt(Op.IPUT,3+i,2,new Field(POOL,ints[i],"I"));
                            String[] lists={"s","a","drops"};for(int i=0;i<3;i++){
                                c.visitTypeStmt(Op.NEW_INSTANCE,0,-1,"Ljava/util/ArrayList;");
                                c.visitMethodStmt(Op.INVOKE_DIRECT,new int[]{0,6+i},new Method("Ljava/util/ArrayList;","<init>",new String[]{"Ljava/util/Collection;"},"V"));
                                c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{0},new Method("Ljava/util/Collections;","unmodifiableList",new String[]{LIST},LIST));
                                c.visitStmt1R(Op.MOVE_RESULT_OBJECT,0);c.visitFieldStmt(Op.IPUT_OBJECT,0,2,new Field(POOL,lists[i],LIST));
                            }
                            c.visitStmt0R(Op.RETURN_VOID);c.visitEnd();mv.visitEnd();poolCtor++;
                        }
                        if(name.equals(DRAW)){
                            DexMethodVisitor mv=super.visitMethod(DexConstants.ACC_PUBLIC|DexConstants.ACC_STATIC|DexConstants.ACC_SYNTHETIC,new Method(DRAW,"q7OriginalSpend",new String[]{RESULT,"I",POOL,"I"},"V"));
                            DexCodeVisitor c=mv.visitCode();c.visitRegister(4);c.visitMethodStmt(Op.INVOKE_STATIC,new int[]{0,1,2,3},new Method(DRAW,"spend",new String[]{RESULT,"I",POOL,"I"},"V"));c.visitStmt0R(Op.RETURN_VOID);c.visitEnd();mv.visitEnd();
                        }
                        super.visitEnd();
                    }
                };
            }
        });
        need(catalogCtor==1&&catalogReturn==1&&poolCtor==1&&apply==1&&save==1&&guard==1&&factory==1&&spends==2&&reveals==1&&states==1,"Missing exact history seam");
        byte[] output=writer.toByteArray();need(sha(output).equals(TARGET),"History producer output differs");
        Files.write(Paths.get(args[1]),output,StandardOpenOption.CREATE_NEW);
        System.out.println("history_seams=typed-pool,catalog-tail,choice-guard,factory,two-spends,reveal,state; unchanged_registers=true");
    }
}
