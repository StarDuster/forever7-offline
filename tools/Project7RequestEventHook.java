import com.googlecode.d2j.*;
import com.googlecode.d2j.dex.writer.DexFileWriter;
import com.googlecode.d2j.reader.*;
import com.googlecode.d2j.visitors.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.Arrays;

/** Maintainer-only: shared request-event admission on authenticated stock paths. */
public final class Project7RequestEventHook {
    static final String SOURCE="a71aa19649feaa262332ec03ff1c42254fb21886c1a73767b336f0dbd0c23d3b";
    static final String TARGET="075edbaaf62c1d777c1982850fad4b68db518eae9e75ec4e50fc80a7ab7d0863";
    static final String ROOT="Lcom/project7/localmanager/", SERVER=ROOT+"LocalGatewayServer;";
    static final String BRIDGE=ROOT+"RequestEventGateway;", PROGRESS=ROOT+"LocalTutorialStore$Progress;", ENGINE=ROOT+"LocalEventEngine;";
    static final String OUTPUT="Ljava/io/OutputStream;", STRING="Ljava/lang/String;";
    static int directMethods,reliableMethods,ackCalls,reliableHooks;
    static void need(boolean condition,String message){if(!condition)throw new IllegalStateException(message);}
    static String sha(byte[] data)throws Exception{StringBuilder out=new StringBuilder();for(byte b:MessageDigest.getInstance("SHA-256").digest(data))out.append(String.format("%02x",b&255));return out.toString();}
    public static void main(String[] args)throws Exception{
        need(args.length==2&&!Files.exists(Paths.get(args[1])),"Require pinned source and unused destination");
        byte[] source=Files.readAllBytes(Paths.get(args[0]));need(sha(source).equals(SOURCE),"Request-event source differs");
        DexFileReader reader=new DexFileReader(source);need(reader.getDexVersion()==DexConstants.DEX_038&&reader.getClassSize()==649,"Manager format differs");
        DexFileWriter writer=new DexFileWriter();writer.cp.dex038();
        reader.accept(new DexFileVisitor(writer){
            @Override public DexClassVisitor visit(int access,String name,String parent,String[] interfaces){
                DexClassVisitor original=super.visit(access,name,parent,interfaces);if(!SERVER.equals(name))return original;
                return new DexClassVisitor(original){
                    @Override public DexMethodVisitor visitMethod(int flags,Method method){
                        DexMethodVisitor mv=super.visitMethod(flags,method);
                        boolean direct=method.getName().equals("handleServiceRpc")&&method.getDesc().equals("("+OUTPUT+"[B[B[B"+STRING+PROGRESS+ENGINE+")Z");
                        boolean reliable=method.getName().equals("handleReliableRpc")&&method.getDesc().equals("("+OUTPUT+"[B[B"+STRING+PROGRESS+ENGINE+"Ljava/util/Set;Ljava/util/Set;Ljava/util/Map;Ljava/util/Set;)V");
                        if(!direct&&!reliable)return mv;
                        need((flags&DexConstants.ACC_STATIC)==0,"Unexpected static dispatcher");if(direct)need(++directMethods==1,"Duplicate direct path");else need(++reliableMethods==1,"Duplicate reliable path");
                        return new DexMethodVisitor(mv){
                            @Override public DexCodeVisitor visitCode(){
                                return new DexCodeVisitor(super.visitCode()){
                                    boolean ackName;
                                    @Override public void visitRegister(int count){
                                        need(count==(direct?42:48),"Pinned register layout differs");super.visitRegister(count);
                                        if(direct){
                                            // Existing parameters form an eight-word contiguous range.
                                            super.visitMethodStmt(Op.INVOKE_STATIC_RANGE,new int[]{34,35,36,37,38,39,40,41},new Method(BRIDGE,"handleDirect",new String[]{SERVER,OUTPUT,"[B","[B","[B",STRING,PROGRESS,ENGINE},"Z"));
                                            super.visitStmt1R(Op.MOVE_RESULT,0);DexLabel resume=new DexLabel();super.visitJumpStmt(Op.IF_EQZ,0,-1,resume);super.visitStmt1R(Op.RETURN,0);super.visitLabel(resume);
                                        }
                                    }
                                    @Override public void visitConstStmt(Op op,int register,Object value){
                                        if(reliable&&"reliableRpcAck".equals(value)){need(register==0&&!ackName,"ACK literal changed");ackName=true;}
                                        super.visitConstStmt(op,register,value);
                                    }
                                    @Override public void visitMethodStmt(Op op,int[] regs,Method called){
                                        super.visitMethodStmt(op,regs,called);
                                        if(!reliable||!called.getOwner().equals(SERVER)||!called.getName().equals("writeFrame")||!called.getDesc().equals("("+OUTPUT+"I[B)V"))return;
                                        if(++ackCalls!=1)return;
                                        need(ackName&&op==Op.INVOKE_DIRECT&&Arrays.equals(regs,new int[]{11,12,6,0}),"First reliable frame is not pinned ACK");
                                        // v21..v29 have no definitions before ACK and are overwritten
                                        // before their original uses. Parameter registers stay intact.
                                        int[] from={11,12,13,2,1,3,8,9,10};int[] to=new int[9];
                                        for(int i=0;i<9;i++){to[i]=21+i;super.visitStmt2R(Op.MOVE_OBJECT_FROM16,to[i],from[i]);}
                                        super.visitMethodStmt(Op.INVOKE_STATIC_RANGE,to,new Method(BRIDGE,"handleRequest",new String[]{SERVER,OUTPUT,"[B",STRING,"[B","Ljava/lang/Integer;",STRING,PROGRESS,ENGINE},"Z"));
                                        super.visitStmt1R(Op.MOVE_RESULT,0);DexLabel resume=new DexLabel();super.visitJumpStmt(Op.IF_EQZ,0,-1,resume);super.visitStmt0R(Op.RETURN_VOID);super.visitLabel(resume);reliableHooks++;
                                    }
                                };
                            }
                        };
                    }
                };
            }
        });
        need(directMethods==1&&reliableMethods==1&&reliableHooks==1&&ackCalls>1,"Missing request-event dispatch seam");
        byte[] target=writer.toByteArray();need(sha(target).equals(TARGET),"Request-event producer output differs");Files.write(Paths.get(args[1]),target,StandardOpenOption.CREATE_NEW);
        System.out.println("sha256="+sha(target)+"; direct_prefix=1; reliable_after_ack=1; register_counts_unchanged=true");
    }
}
