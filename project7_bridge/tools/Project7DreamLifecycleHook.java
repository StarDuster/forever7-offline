import com.googlecode.d2j.*;
import com.googlecode.d2j.dex.writer.DexFileWriter;
import com.googlecode.d2j.reader.*;
import com.googlecode.d2j.visitors.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.Arrays;

/** Maintainer-only: original Week writer and patrol cache/callback boundaries. */
public final class Project7DreamLifecycleHook {
    static final String SOURCE="74e2a7bdc71b1b1d1f3989fe44dc27d47cad433ecd0eccf9168d1d288efb744c";
    static final String TARGET="523aa97f00b098694437f88d46821a3c9fbbfb60c5ed78213c2b16ccd976170b";
    static final String R="Lcom/project7/localmanager/", SERVER=R+"LocalGatewayServer;", STORE=R+"LocalProfileStore;";
    static final String PROGRESS=R+"LocalTutorialStore$Progress;", ENGINE=R+"LocalEventEngine;";
    static final String STRING="Ljava/lang/String;", OUT="Ljava/io/OutputStream;", INTEGER="Ljava/lang/Integer;";
    static int methods,recover,week,callbacks,claim,claimGuard;
    static void need(boolean ok,String message){if(!ok)throw new IllegalStateException(message);}
    static String sha(byte[]data)throws Exception{StringBuilder b=new StringBuilder();for(byte x:MessageDigest.getInstance("SHA-256").digest(data))b.append(String.format("%02x",x&255));return b.toString();}
    public static void main(String[]args)throws Exception{
        need(args.length==2&&!Files.exists(Paths.get(args[1])),"Pinned input and unused output required");
        byte[] source=Files.readAllBytes(Paths.get(args[0]));need(sha(source).equals(SOURCE),"Lifecycle source differs");
        DexFileReader reader=new DexFileReader(source);need(reader.getDexVersion()==DexConstants.DEX_038&&reader.getClassSize()==649,"Manager format differs");
        DexFileWriter writer=new DexFileWriter();writer.cp.dex038();
        reader.accept(new DexFileVisitor(writer){
            @Override public DexClassVisitor visit(int access,String name,String parent,String[]interfaces){
                DexClassVisitor cv=super.visit(access,name,parent,interfaces);
                if(!name.equals(SERVER)&&!name.equals(STORE))return cv;
                return new DexClassVisitor(cv){
                    @Override public DexMethodVisitor visitMethod(int flags,Method m){
                        DexMethodVisitor mv=super.visitMethod(flags,m);
                        boolean rel=name.equals(SERVER)&&m.getName().equals("handleReliableRpc");
                        boolean wrpc=name.equals(SERVER)&&m.getName().equals("handleWeekRpc");
                        boolean services=name.equals(STORE)&&m.getName().equals("updateServices");
                        if(!rel&&!wrpc&&!services)return mv;methods++;
                        return new DexMethodVisitor(mv){
                            @Override public DexCodeVisitor visitCode(){return new DexCodeVisitor(super.visitCode()){
                                boolean claimResult;
                                void object(int target,int from){super.visitStmt2R(Op.MOVE_OBJECT_FROM16,target,from);}
                                @Override public void visitRegister(int n){need(!rel||n==58,"Reliable register baseline differs");super.visitRegister(n);}
                                @Override public void visitFieldStmt(Op op,int a,int b,Field f){
                                    if(wrpc&&op==Op.IGET_OBJECT&&a==3&&b==5&&f.getOwner().equals(PROGRESS)&&f.getName().equals("weekCommit")){
                                        need(++recover==1,"Ambiguous matched Week boundary");
                                        super.visitMethodStmt(Op.INVOKE_STATIC,new int[]{0,4,5,6},new Method(R+"DreamCoordinator;","recover",new String[]{SERVER,STRING,PROGRESS,ENGINE},"V"));
                                    }
                                    super.visitFieldStmt(op,a,b,f);
                                }
                                @Override public void visitMethodStmt(Op op,int[]rs,Method called){
                                    if(services&&called.getOwner().equals(R+"LocalWeekEngine;")&&called.getName().equals("apply")){
                                        need(op==Op.INVOKE_STATIC&&Arrays.equals(rs,new int[]{14,2,8,10,7})&&++week==1,"Week apply baseline differs");
                                        super.visitMethodStmt(op,rs,new Method(R+"DreamWeekPolicy;","apply",called.getParameterTypes(),called.getReturnType()));return;
                                    }
                                    if(rel&&called.getOwner().equals(R+"DreamPatrolGatewayHooks;")&&called.getName().equals("claim")){need(++claim==1,"Ambiguous claim");claimResult=true;}
                                    if(rel&&called.getOwner().equals(SERVER)&&called.getName().equals("completeCallback")){
                                        need(op==Op.INVOKE_DIRECT&&rs.length==5&&rs[0]==11&&rs[1]==12&&rs[2]==13,"Callback baseline differs");callbacks++;
                                        object(48,11);object(49,12);object(50,13);super.visitStmt2R(Op.MOVE_FROM16,51,rs[3]);object(52,rs[4]);object(53,41);object(54,42);object(55,43);
                                        super.visitMethodStmt(Op.INVOKE_STATIC_RANGE,new int[]{48,49,50,51,52,53,54,55},new Method(R+"DreamPatrolReply;","complete",new String[]{SERVER,OUT,"[B","I",STRING,STRING,PROGRESS,ENGINE},"V"));return;
                                    }
                                    super.visitMethodStmt(op,rs,called);
                                }
                                @Override public void visitStmt1R(Op op,int a){
                                    super.visitStmt1R(op,a);
                                    if(claimResult){
                                        need(op==Op.MOVE_RESULT_OBJECT&&a==0,"Claim result baseline differs");claimResult=false;claimGuard++;
                                        DexLabel accepted=new DexLabel();super.visitJumpStmt(Op.IF_NEZ,0,-1,accepted);
                                        object(48,11);object(49,12);object(50,13);object(51,40);
                                        super.visitMethodStmt(Op.INVOKE_STATIC_RANGE,new int[]{48,49,50,51},new Method(R+"DreamPatrolReply;","rejectClaim",new String[]{SERVER,OUT,"[B",INTEGER},"V"));
                                        super.visitStmt0R(Op.RETURN_VOID);super.visitLabel(accepted);
                                    }
                                }
                                @Override public void visitEnd(){need(!claimResult,"Unfinished claim guard");super.visitEnd();}
                            };}
                        };
                    }
                };
            }
        });
        need(methods==3&&recover==1&&week==1&&callbacks==11&&claim==1&&claimGuard==1,"Incomplete lifecycle seams");
        byte[] target=writer.toByteArray();need(sha(target).equals(TARGET),"Lifecycle output differs");
        Files.write(Paths.get(args[1]),target,StandardOpenOption.CREATE_NEW);
        System.out.println("sha256="+sha(target)+"; changed_methods=3; week_recovery=1; week_apply=1; callbacks=11; claim_guard=1");
    }
}
