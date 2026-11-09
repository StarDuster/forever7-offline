import com.project7.localmanager.DynamicSlotPlan;
import java.util.Random;
public class DynamicSlotPlanHost {
 public static void main(String[] args){
  String hash="845e146b5fd19fc119ff79ebee6671755c35cfad9a41743003e1898e987b7c5e";
  Random source=new Random(71),oracle=new Random(71);DynamicSlotPlan[] plans=DynamicSlotPlan.group(485,1631084400,1,hash,source);
  for(int i=0;i<6;i++){
   DynamicSlotPlan p=plans[i];if(p.slot!=i||p.ordinal!=i+1||p.entropy!=oracle.nextLong())throw new AssertionError();
   DynamicSlotPlan restored=DynamicSlotPlan.restore(p.pool,p.epoch,p.slot,p.ordinal,p.entropy,p.catalogHash,DynamicSlotPlan.POLICY);
   for(int j=0;j<3;j++)if(p.resolutionEntropy().nextLong()!=restored.resolutionEntropy().nextLong())throw new AssertionError();
  }
  Random untouched=new Random(18),same=new Random(18);
  try{DynamicSlotPlan.group(485,1,Long.MAX_VALUE-4,hash,untouched);throw new AssertionError();}catch(IllegalArgumentException expected){}
  if(untouched.nextLong()!=same.nextLong())throw new AssertionError();
  try{DynamicSlotPlan.restore(485,1,0,1,0,hash,"unknown");throw new AssertionError();}catch(IllegalArgumentException expected){}
  System.out.println("PASS slot-plan immutable6 entropy/reload/overflow-before-entropy/version; no profile/count mutations");
 }
}
