import com.googlecode.d2j.*;
import com.googlecode.d2j.dex.writer.DexFileWriter;
import com.googlecode.d2j.node.*;
import com.googlecode.d2j.reader.*;
import com.googlecode.d2j.visitors.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

/** Shared chapter consumers; retain every original body for exact delegation. */
public final class Project7StoryMissionHook {
    static final String SOURCE="9506b09dc71f90e257ad99c371bb396d411e885a8dbc2dcc17a2d2e824aadd7b";
    static final String TARGET="9339898c6f7f6b3950ef06731b8e18d68fe6b84b5838670a792c4601527a371b";
    static final String R="Lcom/project7/localmanager/", CITY=R+"LocalCityProgress;", SERVER=R+"LocalGatewayServer;", BRIDGE=R+"StoryMissionBridge;";
    static final String P=R+"LocalTutorialStore$Progress;";
    static final Map<String,String> METHODS=new LinkedHashMap<>();
    static final Set<String> changed=new HashSet<>();
    static int admissions,partyChecks;
    static {
        METHODS.put("area(I)I","q7OriginalArea");
        METHODS.put("mapStages("+P+"I[B)[B","q7OriginalMapStages");
        METHODS.put("stages("+P+"I[B)[B","q7OriginalStages");
        METHODS.put("status("+P+"I[B)I","q7OriginalStatus");
        METHODS.put("consumeVictory("+P+"[BII)Z","q7OriginalConsumeVictory");
    }
    static void need(boolean ok,String message){if(!ok)throw new IllegalStateException(message);}
    static String sha(byte[] data)throws Exception {
        StringBuilder b=new StringBuilder();for(byte v:MessageDigest.getInstance("SHA-256").digest(data))b.append(String.format("%02x",v&255));return b.toString();
    }
    public static void main(String[] args)throws Exception {
        need(args.length==2&&!Files.exists(Paths.get(args[1])),"Pinned source and unused output required");
        byte[] source=Files.readAllBytes(Paths.get(args[0]));need(sha(source).equals(SOURCE),"Story mission source differs");
        DexFileReader reader=new DexFileReader(source);need(reader.getDexVersion()==DexConstants.DEX_038&&reader.getClassSize()==649,"Manager format differs");
        DexFileWriter writer=new DexFileWriter();writer.cp.dex038();
        reader.accept(new DexFileVisitor(writer){
            @Override public DexClassVisitor visit(int access,String name,String parent,String[] interfaces){
                DexClassVisitor cv=super.visit(access,name,parent,interfaces);
                if(SERVER.equals(name))return new DexClassVisitor(cv){
                    @Override public DexMethodVisitor visitMethod(int flags,Method method){
                        DexMethodVisitor mv=super.visitMethod(flags,method);
                        if(!method.getName().equals("handleCombatAdmission"))return mv;
                        need(++admissions==1&&method.getDesc().equals("(Ljava/io/OutputStream;[BLjava/lang/String;"+P+R+"LocalEventEngine;Ljava/util/Set;Ljava/util/Set;I[B)V"),"Combat admission ABI differs");
                        return new DexMethodVisitor(mv){
                            @Override public DexCodeVisitor visitCode(){return new DexCodeVisitor(super.visitCode()){
                                @Override public void visitRegister(int count){need(count==44,"Combat admission register layout differs");super.visitRegister(count);}
                                @Override public void visitFieldStmt(Op op,int a,int b,Field field){
                                    if(op==Op.SGET_OBJECT&&field.getOwner().equals("Ljava/lang/Boolean;")&&field.getName().equals("FALSE")){
                                        need(a==0&&++partyChecks==1,"Combat validity merge differs");
                                        // Source v1 remains the raw request, v17 is accumulated
                                        // validity, and v0 is overwritten by the next original
                                        // Boolean.FALSE load. Keep the existing failure path.
                                        super.visitMethodStmt(Op.INVOKE_STATIC,new int[]{1},new Method(BRIDGE,"partyAllowed",new String[]{"[B"},"Z"));
                                        super.visitStmt1R(Op.MOVE_RESULT,0);
                                        super.visitStmt3R(Op.AND_INT,17,17,0);
                                    }
                                    super.visitFieldStmt(op,a,b,field);
                                }
                            };}
                        };
                    }
                };
                if(!CITY.equals(name))return cv;
                return new DexClassVisitor(cv){
                    @Override public DexMethodVisitor visitMethod(int flags,Method method){
                        need(!method.getName().startsWith("q7Original"),"Unexpected existing city bridge");
                        String key=method.getName()+method.getDesc(),retained=METHODS.get(key);
                        if(retained==null)return super.visitMethod(flags,method);
                        need((flags&(DexConstants.ACC_STATIC|DexConstants.ACC_ABSTRACT|DexConstants.ACC_NATIVE))==DexConstants.ACC_STATIC&&changed.add(key),"Unexpected chapter method access/duplicate");
                        // Capture once; preserve all code, labels, debug and annotations.
                        return new DexMethodNode(flags,method){
                            @Override public void visitEnd(){
                                need(codeNode!=null,"Original body missing");
                                Method original=method;
                                DexMethodNode wrapper=new DexMethodNode(flags,original);
                                wrapper.anns=anns;wrapper.parameterAnns=parameterAnns;
                                wrapper.codeNode=new DexCodeNode();
                                String[] parameters=original.getParameterTypes();int[] registers=new int[parameters.length];
                                for(int i=0;i<parameters.length;i++){
                                    need(!parameters[i].equals("J")&&!parameters[i].equals("D"),"Unexpected wide chapter parameter");registers[i]=i+1;
                                }
                                wrapper.codeNode.visitRegister(parameters.length+1);
                                wrapper.codeNode.visitMethodStmt(Op.INVOKE_STATIC,registers,new Method(BRIDGE,original.getName(),parameters,original.getReturnType()));
                                boolean object=original.getReturnType().startsWith("[")||original.getReturnType().startsWith("L");
                                wrapper.codeNode.visitStmt1R(object?Op.MOVE_RESULT_OBJECT:Op.MOVE_RESULT,0);
                                wrapper.codeNode.visitStmt1R(object?Op.RETURN_OBJECT:Op.RETURN,0);
                                wrapper.accept(cv);
                                this.method=new Method(CITY,retained,parameters,original.getReturnType());
                                this.access=flags|DexConstants.ACC_SYNTHETIC;
                                this.accept(cv);
                            }
                        };
                    }
                };
            }
        });
        need(changed.equals(METHODS.keySet())&&admissions==1&&partyChecks==1,"Incomplete shared chapter/trial seam");byte[] target=writer.toByteArray();
        need(sha(target).equals(TARGET),"Story mission output differs: "+sha(target));
        Files.write(Paths.get(args[1]),target,StandardOpenOption.CREATE_NEW);
        System.out.println("sha256="+sha(target)+"; wrappers=5; retained_original_bodies=5; trial_party_guard=1; chapterScene_unchanged=true");
    }
}
