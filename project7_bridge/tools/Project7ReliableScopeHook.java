import com.googlecode.d2j.*;
import com.googlecode.d2j.dex.writer.DexFileWriter;
import com.googlecode.d2j.reader.*;
import com.googlecode.d2j.visitors.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.Arrays;

/** Maintainer-only: expose the existing reliable sequence/connection scope. */
public final class Project7ReliableScopeHook {
    static final String SOURCE="bcffb77c8370f640ac6c9728855ba738b78029deacf8dd41fe1e3aa957df5515";
    static final String TARGET="9506b09dc71f90e257ad99c371bb396d411e885a8dbc2dcc17a2d2e824aadd7b";
    static final String R="Lcom/project7/localmanager/", SERVER=R+"LocalGatewayServer;";
    static final String OUTPUT="Ljava/io/OutputStream;", STRING="Ljava/lang/String;";
    static final String INTEGER="Ljava/lang/Integer;", SET="Ljava/util/Set;";
    static final String PROGRESS=R+"LocalTutorialStore$Progress;", ENGINE=R+"LocalEventEngine;";
    static final String[] OLD={SERVER,OUTPUT,"[B",STRING,"[B",INTEGER,STRING,PROGRESS,ENGINE};
    static int methods,calls,acks;
    static void need(boolean ok,String message){if(!ok)throw new IllegalStateException(message);}
    static String sha(byte[] data)throws Exception{
        StringBuilder out=new StringBuilder();
        for(byte b:MessageDigest.getInstance("SHA-256").digest(data))out.append(String.format("%02x",b&255));
        return out.toString();
    }
    public static void main(String[] args)throws Exception{
        need(args.length==2&&!Files.exists(Paths.get(args[1])),"Pinned source and unused output required");
        byte[] source=Files.readAllBytes(Paths.get(args[0]));need(sha(source).equals(SOURCE),"Reliable scope source differs");
        DexFileReader reader=new DexFileReader(source);
        need(reader.getDexVersion()==DexConstants.DEX_038&&reader.getClassSize()==649,"Manager format differs");
        DexFileWriter writer=new DexFileWriter();writer.cp.dex038();
        reader.accept(new DexFileVisitor(writer){
            @Override public DexClassVisitor visit(int access,String name,String parent,String[] interfaces){
                DexClassVisitor cv=super.visit(access,name,parent,interfaces);if(!name.equals(SERVER))return cv;
                return new DexClassVisitor(cv){
                    @Override public DexMethodVisitor visitMethod(int flags,Method method){
                        DexMethodVisitor mv=super.visitMethod(flags,method);
                        if(!method.getName().equals("handleReliableRpc"))return mv;
                        need(method.getDesc().equals("("+OUTPUT+"[B[B"+STRING+PROGRESS+ENGINE+SET+SET+"Ljava/util/Map;"+SET+")V"),"Reliable descriptor differs");
                        need((flags&DexConstants.ACC_STATIC)==0&&++methods==1,"Reliable dispatcher differs");
                        return new DexMethodVisitor(mv){
                            @Override public DexCodeVisitor visitCode(){return new DexCodeVisitor(super.visitCode()){
                                boolean ackLiteral;
                                @Override public void visitRegister(int count){need(count==58,"Register layout differs");super.visitRegister(count);}
                                @Override public void visitConstStmt(Op op,int reg,Object value){
                                    if("reliableRpcAck".equals(value)){need(reg==0&&!ackLiteral,"ACK literal differs");ackLiteral=true;}
                                    super.visitConstStmt(op,reg,value);
                                }
                                @Override public void visitMethodStmt(Op op,int[] regs,Method called){
                                    if(called.getOwner().equals(SERVER)&&called.getName().equals("writeFrame")&&acks==0){
                                        need(ackLiteral&&op==Op.INVOKE_DIRECT&&Arrays.equals(regs,new int[]{11,12,6,0}),"First frame is not ACK");acks++;
                                    }
                                    if(called.getOwner().equals(R+"OfflineMechanismGateway;")&&called.getName().equals("handleRequest")){
                                        need(acks==1&&++calls==1&&op==Op.INVOKE_STATIC_RANGE,"Missing ACK or repeated dispatch");
                                        need(Arrays.equals(regs,new int[]{21,22,23,24,25,26,27,28,29})&&Arrays.equals(called.getParameterTypes(),OLD)&&called.getReturnType().equals("Z"),"Dispatch layout differs");
                                        // v4 is the decoded Integer sequence. v47 is the actual
                                        // connection-local Set after the pinned entry relocation.
                                        // v6 is already overwritten by the ACK message type.
                                        super.visitStmt2R(Op.MOVE_OBJECT_FROM16,30,4);
                                        super.visitStmt2R(Op.MOVE_OBJECT_FROM16,31,47);
                                        String[] parameters=Arrays.copyOf(OLD,11);parameters[9]=INTEGER;parameters[10]=SET;
                                        super.visitMethodStmt(op,new int[]{21,22,23,24,25,26,27,28,29,30,31},new Method(R+"OfflineMechanismGateway;","handleSequencedRequest",parameters,"Z"));
                                        return;
                                    }
                                    super.visitMethodStmt(op,regs,called);
                                }
                            };}
                        };
                    }
                };
            }
        });
        need(methods==1&&calls==1&&acks==1,"Incomplete reliable scope seam");
        byte[] target=writer.toByteArray();need(sha(target).equals(TARGET),"Reliable scope output differs: "+sha(target));
        Files.write(Paths.get(args[1]),target,StandardOpenOption.CREATE_NEW);
        System.out.println("sha256="+sha(target)+"; changed_methods=1; registers=58; ack_and_seen_gate_preserved=true");
    }
}
