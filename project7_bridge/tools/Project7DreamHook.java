import com.googlecode.d2j.*;
import com.googlecode.d2j.dex.writer.DexFileWriter;
import com.googlecode.d2j.reader.*;
import com.googlecode.d2j.visitors.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.Arrays;

/** Maintainer-only: preserve stock RPC sequence cache and Store commit points. */
public final class Project7DreamHook {
    static final String SOURCE="5e0e6220e63e04fda492608f34ff16230d010b2f8641fd37a7e4aa7fce80eb19";
    static final String TARGET="74e2a7bdc71b1b1d1f3989fe44dc27d47cad433ecd0eccf9168d1d288efb744c";
    static final String R="Lcom/project7/localmanager/", SERVER=R+"LocalGatewayServer;", STORE=R+"LocalProfileStore;";
    static final String PROGRESS=R+"LocalTutorialStore$Progress;", ENGINE=R+"LocalEventEngine;", PATROL=R+"LocalPatrolEngine;";
    static final String COORD=R+"DreamCoordinator;", HOOKS=R+"DreamPatrolGatewayHooks;", POLICY=R+"DreamEconomyPolicy;";
    static final String ECONOMY=R+"LocalEconomyEngine;", ECONRESULT=R+"LocalEconomyEngine$Result;", RESULT=R+"LocalPatrolEngine$Result;";
    static final String STRING="Ljava/lang/String;", LIST="Ljava/util/List;", OUTPUT="Ljava/io/OutputStream;";
    static int methods,copies,direct,reliable,begin,claim,saves,pending,resume,economy,calendar;
    static void need(boolean ok,String message){if(!ok)throw new IllegalStateException(message);}
    static String sha(byte[] data)throws Exception{StringBuilder b=new StringBuilder();for(byte x:MessageDigest.getInstance("SHA-256").digest(data))b.append(String.format("%02x",x&255));return b.toString();}
    static boolean call(Method m,String owner,String name){return m.getOwner().equals(owner)&&m.getName().equals(name);}
    public static void main(String[]args)throws Exception{
        need(args.length==2&&!Files.exists(Paths.get(args[1])),"Require pinned source and unused output");byte[] source=Files.readAllBytes(Paths.get(args[0]));need(sha(source).equals(SOURCE),"Dream source differs");
        DexFileReader reader=new DexFileReader(source);need(reader.getDexVersion()==DexConstants.DEX_038&&reader.getClassSize()==649,"Manager format differs");DexFileWriter writer=new DexFileWriter();writer.cp.dex038();
        reader.accept(new DexFileVisitor(writer){
            @Override public DexClassVisitor visit(int access,String name,String parent,String[]interfaces){
                DexClassVisitor cv=super.visit(access,name,parent,interfaces);if(!name.equals(SERVER)&&!name.equals(STORE))return cv;
                return new DexClassVisitor(cv){
                    @Override public DexMethodVisitor visitMethod(int flags,Method m){
                        DexMethodVisitor mv=super.visitMethod(flags,m);
                        boolean rel=name.equals(SERVER)&&m.getName().equals("handleReliableRpc");
                        boolean svc=name.equals(SERVER)&&m.getName().equals("handleServiceRpc");
                        boolean cal=name.equals(SERVER)&&m.getName().equals("handleCalendar");
                        boolean eco=name.equals(STORE)&&m.getName().equals("updateEconomy");
                        if(!rel&&!svc&&!cal&&!eco)return mv;methods++;
                        return new DexMethodVisitor(mv){
                            @Override public DexCodeVisitor visitCode(){return new DexCodeVisitor(super.visitCode()){
                                int saveState;
                                @Override public void visitRegister(int count){
                                    if(rel){need(count==48,"Reliable register baseline differs");super.visitRegister(58);
                                        // Copy object parameters before reusing their high slots.
                                        // Increasing the register file moves incoming words by ten.
                                        // Low-to-high copying preserves the one-word overlap at47.
                                        for(int i=0;i<11;i++){super.visitStmt2R(Op.MOVE_OBJECT_FROM16,37+i,47+i);copies++;}
                                    }else super.visitRegister(count);
                                }
                                void objects(int... from){for(int i=0;i<from.length;i++)super.visitStmt2R(Op.MOVE_OBJECT_FROM16,48+i,from[i]);}
                                @Override public void visitMethodStmt(Op op,int[]rs,Method called){
                                    if(rel&&saveState==3){need(call(called,R+"LocalTutorialStore;","save")&&op==Op.INVOKE_VIRTUAL&&Arrays.equals(rs,new int[]{1,7,9}),"Patrol save span differs");saveState=0;saves++;return;}
                                    if((rel||svc)&&called.getOwner().equals(R+"RequestEventGateway;")){
                                        need((rel&&called.getName().equals("handleRequest"))||(svc&&called.getName().equals("handleDirect")),"Unexpected extension prefix");
                                        super.visitMethodStmt(op,rs,new Method(R+"OfflineMechanismGateway;",called.getName(),called.getParameterTypes(),called.getReturnType()));if(rel)reliable++;else direct++;return;
                                    }
                                    if(rel&&call(called,PATROL,"hasPendingChoice")){need(++pending==1,"Ambiguous pending guard");super.visitMethodStmt(op,rs,new Method(COORD,called.getName(),called.getParameterTypes(),called.getReturnType()));return;}
                                    if(rel&&call(called,PATROL,"canResume")){need(++resume==1,"Ambiguous resume guard");super.visitMethodStmt(op,rs,new Method(COORD,called.getName(),called.getParameterTypes(),called.getReturnType()));return;}
                                    if(rel&&call(called,PATROL,"begin")){
                                        need(op==Op.INVOKE_STATIC_RANGE&&Arrays.equals(rs,new int[]{0,1,2,3,4,5})&&++begin==1,"Patrol begin differs");
                                        objects(0,1,2,3);super.visitStmt2R(Op.MOVE_FROM16,52,4);super.visitStmt2R(Op.MOVE_OBJECT_FROM16,53,5);super.visitStmt2R(Op.MOVE_OBJECT_FROM16,54,11);super.visitStmt2R(Op.MOVE_OBJECT_FROM16,55,7);
                                        super.visitMethodStmt(Op.INVOKE_STATIC_RANGE,new int[]{48,49,50,51,52,53,54,55},new Method(HOOKS,"begin",new String[]{R+"LocalPatrolCatalog;",PROGRESS,ENGINE,"[B","I",LIST,SERVER,STRING},RESULT));saveState=1;return;
                                    }
                                    if(rel&&call(called,PATROL,"claim")){
                                        need(op==Op.INVOKE_STATIC&&Arrays.equals(rs,new int[]{9,0})&&++claim==1,"Patrol claim differs");objects(9,0,11,7,43);
                                        super.visitMethodStmt(Op.INVOKE_STATIC_RANGE,new int[]{48,49,50,51,52},new Method(HOOKS,"claim",new String[]{PROGRESS,"[B",SERVER,STRING,ENGINE},"Ljava/util/Map;"));saveState=1;return;
                                    }
                                    if(eco&&call(called,ECONOMY,"apply")){need(++economy==1,"Ambiguous economy apply");super.visitMethodStmt(op,rs,new Method(POLICY,"apply",called.getParameterTypes(),called.getReturnType()));return;}
                                    if(cal&&call(called,ENGINE,"refreshProfile")){need(op==Op.INVOKE_VIRTUAL&&rs.length==2&&rs[0]==14&&++calendar==1,"Calendar refresh differs");super.visitMethodStmt(Op.INVOKE_STATIC,new int[]{rs[0],rs[1],0},new Method(POLICY,"refreshCalendarEngine",new String[]{ENGINE,"[B",ECONRESULT},"V"));return;}
                                    super.visitMethodStmt(op,rs,called);
                                }
                                @Override public void visitStmt1R(Op op,int a){if(rel&&saveState==1){need(op==Op.MOVE_RESULT_OBJECT&&a==0,"Patrol result register differs");saveState=2;}super.visitStmt1R(op,a);}
                                @Override public void visitFieldStmt(Op op,int a,int b,Field field){
                                    if(rel&&saveState==2){need(op==Op.IGET_OBJECT&&a==1&&b==11&&field.getOwner().equals(SERVER)&&field.getName().equals("tutorialStore"),"Patrol store field differs");saveState=3;}
                                    super.visitFieldStmt(op,a,b,field);
                                }
                                @Override public void visitEnd(){need(saveState==0,"Unfinished patrol save replacement");super.visitEnd();}
                            };}
                        };
                    }
                };
            }
        });
        need(methods==4&&copies==11&&direct==1&&reliable==1&&begin==1&&claim==1&&saves==2&&pending==1&&resume==1&&economy==1&&calendar==1,"Incomplete dream seams");
        byte[] target=writer.toByteArray();need(sha(target).equals(TARGET),"Dream output differs from reviewed seams");Files.write(Paths.get(args[1]),target,StandardOpenOption.CREATE_NEW);System.out.println("sha256="+sha(target)+"; changed_methods=4; added_methods=0; reliable_registers=58; original_sequence_cache_retained=true");
    }
}
