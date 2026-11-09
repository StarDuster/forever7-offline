import com.googlecode.d2j.*;
import com.googlecode.d2j.dex.writer.DexFileWriter;
import com.googlecode.d2j.reader.*;
import com.googlecode.d2j.visitors.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.Arrays;

/** Maintainer-only same-shape selector admission; original choose stays private. */
public final class Project7SelectorHook {
    static final String SOURCE="b461f49531efd2ab7fb09eb71e22ade0085e92f7567d5fddcff1c534fc68b257";
    static final String TARGET="bcffb77c8370f640ac6c9728855ba738b78029deacf8dd41fe1e3aa957df5515";
    static final String R="Lcom/project7/localmanager/",DRAW=R+"LocalDrawEngine;";
    static int methods,calls;
    static void need(boolean ok,String text){if(!ok)throw new IllegalStateException(text);}
    static String sha(byte[]data)throws Exception{StringBuilder b=new StringBuilder();for(byte x:MessageDigest.getInstance("SHA-256").digest(data))b.append(String.format("%02x",x&255));return b.toString();}
    public static void main(String[]args)throws Exception{
        need(args.length==2&&!Files.exists(Paths.get(args[1])),"Pinned input and unused output required");
        byte[]source=Files.readAllBytes(Paths.get(args[0]));need(sha(source).equals(SOURCE),"Selector source differs");
        DexFileReader reader=new DexFileReader(source);need(reader.getDexVersion()==DexConstants.DEX_038&&reader.getClassSize()==649,"Manager format differs");DexFileWriter writer=new DexFileWriter();writer.cp.dex038();
        reader.accept(new DexFileVisitor(writer){
            @Override public DexClassVisitor visit(int access,String name,String parent,String[]interfaces){
                DexClassVisitor cv=super.visit(access,name,parent,interfaces);if(!name.equals(DRAW))return cv;
                return new DexClassVisitor(cv){
                    @Override public DexMethodVisitor visitMethod(int flags,Method m){
                        DexMethodVisitor mv=super.visitMethod(flags,m);if(!m.getName().equals("applyCurrent"))return mv;methods++;
                        return new DexMethodVisitor(mv){
                            @Override public DexCodeVisitor visitCode(){return new DexCodeVisitor(super.visitCode()){
                                @Override public void visitMethodStmt(Op op,int[]regs,Method called){
                                    if(called.getOwner().equals(DRAW)&&called.getName().equals("choose")){
                                        need(op==Op.INVOKE_STATIC&&Arrays.equals(regs,new int[]{1,8,2,4})&&++calls==1,"Original choose caller differs");
                                        need(Arrays.equals(called.getParameterTypes(),new String[]{"[B",R+"LocalResourceCatalog;","[B","I"})&&called.getReturnType().equals(R+"LocalResourceEngine$Result;"),"Original choose descriptor differs");
                                        super.visitMethodStmt(op,regs,new Method(R+"SelectorPolicy;","choose",called.getParameterTypes(),called.getReturnType()));return;
                                    }
                                    super.visitMethodStmt(op,regs,called);
                                }
                            };}
                        };
                    }
                };
            }
        });
        need(methods==1&&calls==1,"Incomplete selector seam");byte[]target=writer.toByteArray();need(sha(target).equals(TARGET),"Selector output differs");
        Files.write(Paths.get(args[1]),target,StandardOpenOption.CREATE_NEW);System.out.println("sha256="+sha(target)+"; changed_methods=1; original_private_choose_retained=true");
    }
}
