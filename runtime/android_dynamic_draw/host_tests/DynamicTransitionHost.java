import com.project7.localmanager.DynamicTransition.*;
import com.project7.localmanager.DynamicTransition;
import java.util.*;
public class DynamicTransitionHost {
 static void need(boolean value){if(!value)throw new AssertionError();}
 static State empty(){return new State(0,0,Collections.<Integer>emptyList(),Collections.<Integer>emptyList(),Collections.<Integer>emptyList());}
 public static void main(String[] args){
  List<Threshold> charge=Arrays.asList(new Threshold(274,12,false,"common",new int[]{62945,5844,5845,5846}),new Threshold(275,36,false,"common",new int[]{62946,5847,5848,5849}),new Threshold(276,90,false,"common",new int[]{62897}),new Threshold(277,180,false,"common",new int[]{62891}));
  List<Threshold> jiaozhi=Arrays.asList(new Threshold(133,1,false,"random",new int[]{17982}),new Threshold(134,2,false,"random",new int[]{17983}),new Threshold(135,3,false,"random",new int[]{17985}),new Threshold(136,4,true,"random",new int[]{23500}),new Threshold(137,5,false,"random",new int[]{23501,17987}),new Threshold(138,6,true,"random",new int[]{23505}));
  Rules r=new Rules(147,charge,jiaozhi);State s=empty();
  Step step=DynamicTransition.primary(r,s,147,true,false);need(step.state.draws==1&&step.state.points==3&&step.grants.isEmpty()&&s.draws==0);
  step=DynamicTransition.settle(r,step.state);need(step.grants.size()==3&&step.state.blessings.isEmpty());
  step=DynamicTransition.primary(r,step.state,147,false,true);step=DynamicTransition.settle(r,step.state);need(step.state.points==4&&step.state.blessings.equals(Arrays.asList(136)));
  DynamicTransition.Blessing b=DynamicTransition.memory(r,step.state,147,1,false,1,3,new Random(2));need(b.piece!=1&&b.state.blessings.isEmpty()&&step.state.blessings.size()==1);
  need(DynamicTransition.memory(r,step.state,147,1,true,1,3,new Random(2)).state==step.state);
  step=DynamicTransition.settle(r,DynamicTransition.primary(r,b.state,147,false,true).state);need(step.state.points==5&&step.grants.size()==1);
  step=DynamicTransition.settle(r,DynamicTransition.primary(r,step.state,147,false,true).state);need(step.state.points==6&&step.state.blessings.equals(Arrays.asList(138)));need(DynamicTransition.settle(r,step.state).grants.isEmpty());
  s=empty();int chargeCount=0;for(int i=1;i<=180;i++){step=DynamicTransition.primary(r,s,0,false,false);s=step.state;chargeCount+=step.grants.size();if(i==180)s=DynamicTransition.chargedHero(r,s,147);}
  need(chargeCount==4&&s.draws==180&&s.points==3);need(DynamicTransition.settle(r,s).grants.size()==3);
  try{new Rules(147,Arrays.asList(charge.get(0),charge.get(0)),jiaozhi);throw new AssertionError();}catch(IllegalArgumentException expected){}
  State blessing=new State(12,4,Collections.<Integer>emptyList(),Collections.<Integer>emptyList(),Arrays.asList(136));Random noDraw=new Random(){public int nextInt(int bound){throw new AssertionError("retained piece must not consume replacement entropy");}};
  DynamicTransition.Blessing retained=DynamicTransition.memoryArchive(r,blessing,147,1,false,2,3,noDraw);need(retained.piece==1&&retained.state.blessings.isEmpty());
  DynamicTransition.Blessing replacement=DynamicTransition.memoryArchive(r,blessing,147,2,false,2,3,new Random(7));need(replacement.piece!=2&&replacement.state.blessings.isEmpty());
  need(DynamicTransition.memoryArchive(r,blessing,147,1,true,7,3,noDraw).state==blessing);need(DynamicTransition.memoryArchive(r,blessing,147,1,false,7,3,noDraw).state==blessing);need(DynamicTransition.memoryArchive(r,blessing,122,1,false,2,3,noDraw).state==blessing);
  System.out.println("PASS dynamic reducer source-485 thresholds 12/36/90/180 and 1..6, immutable/replay/FIFO/final-memory/charge-not-draw; no stock grant claim");
 }
}
