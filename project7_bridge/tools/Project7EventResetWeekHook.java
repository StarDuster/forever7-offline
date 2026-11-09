import com.googlecode.d2j.*;
import com.googlecode.d2j.dex.writer.DexFileWriter;
import com.googlecode.d2j.reader.*;
import com.googlecode.d2j.visitors.*;
import java.nio.file.*;
import java.security.MessageDigest;

/** Maintainer-only: extend the original shared Week method family once. */
public final class Project7EventResetWeekHook {
    static final String SOURCE="523aa97f00b098694437f88d46821a3c9fbbfb60c5ed78213c2b16ccd976170b";
    static final String TARGET="b461f49531efd2ab7fb09eb71e22ade0085e92f7567d5fddcff1c534fc68b257";
    static final String R="Lcom/project7/localmanager/", WEEK=R+"LocalWeekEngine;", SERVER=R+"LocalGatewayServer;", ARRAY="[Ljava/lang/String;";
    static int methods,stores,recover,copies;
    static void need(boolean ok,String message){if(!ok)throw new IllegalStateException(message);}
    static String sha(byte[]data)throws Exception{StringBuilder b=new StringBuilder();for(byte x:MessageDigest.getInstance("SHA-256").digest(data))b.append(String.format("%02x",x&255));return b.toString();}
    public static void main(String[]args)throws Exception{
        need(args.length==2&&!Files.exists(Paths.get(args[1])),"Pinned input and unused output required");
        byte[] source=Files.readAllBytes(Paths.get(args[0]));need(sha(source).equals(SOURCE),"Event-reset source differs");
        DexFileReader reader=new DexFileReader(source);need(reader.getDexVersion()==DexConstants.DEX_038&&reader.getClassSize()==649,"Manager format differs");
        DexFileWriter writer=new DexFileWriter();writer.cp.dex038();
        reader.accept(new DexFileVisitor(writer){
            @Override public DexClassVisitor visit(int access,String name,String parent,String[]interfaces){
                DexClassVisitor cv=super.visit(access,name,parent,interfaces);if(!name.equals(WEEK)&&!name.equals(SERVER))return cv;
                return new DexClassVisitor(cv){
                    @Override public DexMethodVisitor visitMethod(int flags,Method m){
                        DexMethodVisitor mv=super.visitMethod(flags,m);
                        boolean init=name.equals(WEEK)&&m.getName().equals("<clinit>");
                        boolean rpc=name.equals(SERVER)&&m.getName().equals("handleWeekRpc");
                        if(!init&&!rpc)return mv;methods++;
                        return new DexMethodVisitor(mv){
                            @Override public DexCodeVisitor visitCode(){return new DexCodeVisitor(super.visitCode()){
                                @Override public void visitRegister(int n){
                                    if(init){need(n==6,"Week initializer registers differ");super.visitRegister(n);}
                                    else{need(n==24,"Week RPC registers differ");super.visitRegister(32);
                                        for(int i=0;i<8;i++){super.visitStmt2R(Op.MOVE_OBJECT_FROM16,16+i,24+i);copies++;}
                                    }
                                }
                                void object(int to,int from){super.visitStmt2R(Op.MOVE_OBJECT_FROM16,to,from);}
                                @Override public void visitMethodStmt(Op op,int[]rs,Method called){
                                    if(rpc&&called.getOwner().equals(R+"DreamCoordinator;")&&called.getName().equals("recover")){
                                        need(op==Op.INVOKE_STATIC&&java.util.Arrays.equals(rs,new int[]{0,4,5,6})&&++recover==1,"Week recovery boundary differs");
                                        object(24,0);object(25,1);object(26,2);object(27,4);object(28,5);object(29,6);object(30,14);
                                        super.visitMethodStmt(Op.INVOKE_STATIC_RANGE,new int[]{24,25,26,27,28,29,30},new Method(R+"EventResetWeekGateway;","beforeWeek",new String[]{SERVER,"Ljava/io/OutputStream;","[B","Ljava/lang/String;",R+"LocalTutorialStore$Progress;",R+"LocalEventEngine;","Ljava/lang/String;"},"Z"));
                                        super.visitStmt1R(Op.MOVE_RESULT,7);DexLabel ready=new DexLabel();super.visitJumpStmt(Op.IF_NEZ,7,-1,ready);
                                        super.visitConstStmt(Op.CONST_4,7,1);super.visitStmt1R(Op.RETURN,7);super.visitLabel(ready);return;
                                    }
                                    super.visitMethodStmt(op,rs,called);
                                }
                                @Override public void visitFieldStmt(Op op,int a,int b,Field field){
                                    if(init&&field.getOwner().equals(WEEK)&&field.getName().equals("METHODS")){
                                        need(op==Op.SPUT_OBJECT&&a==0&&field.getType().equals(ARRAY)&&++stores==1,"Week method-family store differs");
                                        super.visitMethodStmt(Op.INVOKE_STATIC,new int[]{0},new Method(R+"EventResetWeekPolicy;","weekMethods",new String[]{ARRAY},ARRAY));
                                        super.visitStmt1R(Op.MOVE_RESULT_OBJECT,0);
                                    }
                                    super.visitFieldStmt(op,a,b,field);
                                }
                            };}
                        };
                    }
                };
            }
        });
        need(methods==2&&stores==1&&recover==1&&copies==8,"Incomplete event-reset routing seam");byte[]target=writer.toByteArray();
        need(sha(target).equals(TARGET),"Event-reset output differs");
        Files.write(Paths.get(args[1]),target,StandardOpenOption.CREATE_NEW);
        System.out.println("sha256="+sha(target)+"; changed_methods=2; shared_method_family=1; guarded_week_effects=1; definitions_unchanged=true");
    }
}
