import com.googlecode.d2j.*;
import com.googlecode.d2j.dex.writer.DexFileWriter;
import com.googlecode.d2j.node.*;
import com.googlecode.d2j.reader.*;
import com.googlecode.d2j.visitors.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

/** One source-family trial lifecycle, with unmatched original paths retained. */
public final class Project7TrialRetryHook {
 static final String SOURCE="9339898c6f7f6b3950ef06731b8e18d68fe6b84b5838670a792c4601527a371b",TARGET="7f13c24a613676ee520bf6ed2590a6bf33788cb6955c92f3e9f446dee89c0d82";
 static final String R="Lcom/project7/localmanager/",G=R+"LocalGatewayServer;",E=R+"LocalEventEngine;",P=R+"LocalTutorialStore$Progress;",B=R+"LocalEventBattleEngine;",T=R+"TrialRetryGateway;";
 static final String O="Ljava/io/OutputStream;",S="Ljava/lang/String;",SET="Ljava/util/Set;",RESULT=R+"LocalResourceEngine$Result;",CAT=R+"LocalEventCatalog;";
 static int begin,sync;static Set<String>prefixes=new HashSet<>();
 static void need(boolean value,String message){if(!value)throw new IllegalStateException(message);}
 static String sha(byte[]bytes)throws Exception{StringBuilder out=new StringBuilder();for(byte v:MessageDigest.getInstance("SHA-256").digest(bytes))out.append(String.format("%02x",v&255));return out.toString();}
 public static void main(String[]args)throws Exception{
  need(args.length==2&&!Files.exists(Paths.get(args[1])),"Pinned source and unused output required");
  byte[]source=Files.readAllBytes(Paths.get(args[0]));need(sha(source).equals(SOURCE),"Trial retry source differs");
  DexFileReader reader=new DexFileReader(source);need(reader.getDexVersion()==DexConstants.DEX_038&&reader.getClassSize()==649,"Manager format differs");
  DexFileWriter writer=new DexFileWriter();writer.cp.dex038();
  reader.accept(new DexFileVisitor(writer){
   @Override public DexClassVisitor visit(int flags,String name,String parent,String[]interfaces){
    DexClassVisitor cv=super.visit(flags,name,parent,interfaces);
    if(name.equals(B))return new DexClassVisitor(cv){
     @Override public DexMethodVisitor visitMethod(int access,Method method){
      need(!method.getName().equals("q7OriginalSync"),"Unexpected original-sync bridge");
      if(!method.getName().equals("sync"))return super.visitMethod(access,method);
      need(method.getDesc().equals("("+RESULT+CAT+P+")V")&&(access&DexConstants.ACC_STATIC)!=0&&++sync==1,"Battle sync ABI differs");
      return new DexMethodNode(access,method){
       @Override public void visitEnd(){
        need(codeNode!=null,"Original sync body missing");
        DexMethodNode wrapper=new DexMethodNode(access,method);wrapper.anns=anns;wrapper.parameterAnns=parameterAnns;wrapper.codeNode=new DexCodeNode();
        wrapper.codeNode.visitRegister(3);wrapper.codeNode.visitMethodStmt(Op.INVOKE_STATIC,new int[]{0,1,2},new Method(T,"sync",method.getParameterTypes(),"V"));wrapper.codeNode.visitStmt0R(Op.RETURN_VOID);wrapper.accept(cv);
        this.method=new Method(B,"q7OriginalSync",method.getParameterTypes(),"V");this.access=access|DexConstants.ACC_SYNTHETIC;this.accept(cv);
       }
      };
     }
    };
    if(!name.equals(G))return cv;
    return new DexClassVisitor(cv){
     @Override public DexMethodVisitor visitMethod(int access,Method method){
      DexMethodVisitor mv=super.visitMethod(access,method);String n=method.getName(),helper=null;int count=0;boolean handled=false;
      if(n.equals("handleCombatOfflineFinish")){need(method.getDesc().equals("("+O+"[B[B"+S+P+E+SET+SET+")V"),"Finish ABI differs");helper="handleFinish";count=32;handled=true;}
      else if(n.equals("finishAbandonedStory")){need(method.getDesc().equals("("+O+"[B[B"+S+P+E+"Z)V"),"Giveup ABI differs");helper="handleGiveup";count=21;handled=true;}
      else if(n.equals("prepareEventEffects")){need(method.getDesc().equals("("+S+P+E+")"+RESULT),"Recovery ABI differs");helper="recover";count=20;}
      else if(!n.equals("handleCombatAdmission"))return mv;
      final String prefix=helper;final int registers=count;final boolean terminal=handled;
      need((access&DexConstants.ACC_STATIC)==0,"Unexpected static Gateway lifecycle");
      return new DexMethodVisitor(mv){
       @Override public DexCodeVisitor visitCode(){return new DexCodeVisitor(super.visitCode()){
        @Override public void visitRegister(int actual){
         need(actual==(prefix==null?44:registers),"Trial lifecycle register layout differs");super.visitRegister(actual);
         if(prefix!=null){
          need(prefixes.add(prefix),"Duplicate lifecycle prefix");
          String[]parameters=new String[method.getParameterTypes().length+1];parameters[0]=G;System.arraycopy(method.getParameterTypes(),0,parameters,1,parameters.length-1);
          int[]args=new int[parameters.length];for(int i=0;i<args.length;i++){need(!parameters[i].equals("J")&&!parameters[i].equals("D"),"Unexpected wide lifecycle parameter");args[i]=actual-args.length+i;}
          super.visitMethodStmt(Op.INVOKE_STATIC_RANGE,args,new Method(T,prefix,parameters,terminal?"Z":"V"));
          if(terminal){super.visitStmt1R(Op.MOVE_RESULT,0);DexLabel original=new DexLabel();super.visitJumpStmt(Op.IF_EQZ,0,-1,original);super.visitStmt0R(Op.RETURN_VOID);super.visitLabel(original);}
         }
        }
        @Override public void visitMethodStmt(Op op,int[]args,Method called){
         if(prefix==null&&called.getOwner().equals(E)&&called.getName().equals("beginStoryBattle")){
          need(++begin==1&&op==Op.INVOKE_VIRTUAL&&Arrays.equals(args,new int[]{11,15})&&called.getDesc().equals("(I)Z"),"Trial begin caller differs");
          super.visitMethodStmt(Op.INVOKE_STATIC,new int[]{7,6,10,11,15},new Method(T,"begin",new String[]{G,S,P,E,"I"},"Z"));return;
         }
         super.visitMethodStmt(op,args,called);
        }
       };}
      };
     }
    };
   }
  });
  need(begin==1&&sync==1&&prefixes.equals(new HashSet<>(Arrays.asList("handleFinish","handleGiveup","recover"))),"Incomplete trial lifecycle seams");
  byte[]target=writer.toByteArray();need(sha(target).equals(TARGET),"Trial retry output differs: "+sha(target));Files.write(Paths.get(args[1]),target,StandardOpenOption.CREATE_NEW);System.out.println("sha256="+sha(target)+"; begin=1; prefixes=3; original_sync_retained=true");
 }
}
