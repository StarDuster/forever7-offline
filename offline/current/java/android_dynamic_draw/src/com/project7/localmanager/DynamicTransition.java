package com.project7.localmanager;
import java.util.*;

/** Pure parameter-driven reducer. Caller alone owns original BSON/Result transaction.
 * RewardRef domains are explicit: charge common, interweave random; never show IDs.
 * This reducer does not grant, write UI fields, read a profile, or mark a pool ready.
 */
public final class DynamicTransition {
 public static final class Threshold {
  public final int id,at;public final boolean blessing;public final String domain;private final int[] rewards;
  public Threshold(int id,int at,boolean blessing,String domain,int[] rewards){
   if(id<=0||at<=0||!(domain.equals("common")||domain.equals("random"))||rewards==null||rewards.length==0)throw new IllegalArgumentException("dynamic threshold");
   this.id=id;this.at=at;this.blessing=blessing;this.domain=domain;this.rewards=rewards.clone();for(int r:this.rewards)if(r<=0)throw new IllegalArgumentException("dynamic reward ref");
  }
  public int[] rewards(){return rewards.clone();}
 }
 public static final class Rules {
  public final int target;public final List<Threshold> charge,jiaozhi;
  public Rules(int target,List<Threshold> charge,List<Threshold> jiaozhi){if(target<0||target==0&&!jiaozhi.isEmpty())throw new IllegalArgumentException("dynamic target");this.target=target;this.charge=ordered(charge,"common");this.jiaozhi=ordered(jiaozhi,"random");}
  private static List<Threshold> ordered(List<Threshold> input,String domain){
   List<Threshold> rows=new ArrayList<>(input);Collections.sort(rows,new Comparator<Threshold>(){public int compare(Threshold a,Threshold b){return Integer.compare(a.at,b.at);}});Set<Integer> ids=new HashSet<>();int prior=0;
   for(Threshold t:rows){if(!t.domain.equals(domain)||t.at<=prior||!ids.add(t.id))throw new IllegalArgumentException("dynamic duplicate/domain");prior=t.at;}
   return Collections.unmodifiableList(rows);
  }
 }
 public static final class State {
  public final int draws,points;public final Set<Integer> chargeReceipts,jiaozhiReceipts;public final List<Integer> blessings;
  public State(int draws,int points,Collection<Integer> c,Collection<Integer> j,Collection<Integer> b){
   if(draws<0||points<0||c.size()>1024||j.size()>1024||b.size()>1024)throw new IllegalArgumentException("dynamic state boundary");
   this.draws=draws;this.points=points;this.chargeReceipts=Collections.unmodifiableSet(new TreeSet<>(c));this.jiaozhiReceipts=Collections.unmodifiableSet(new TreeSet<>(j));this.blessings=Collections.unmodifiableList(new ArrayList<>(b));
   if(c.size()!=chargeReceipts.size()||j.size()!=jiaozhiReceipts.size()||new HashSet<>(b).size()!=b.size())throw new IllegalArgumentException("dynamic duplicate receipt");
  }
 }
 public static final class Step {
  public final State state;public final List<Threshold> grants;
  private Step(State state,List<Threshold> grants){this.state=state;this.grants=Collections.unmodifiableList(grants);}
 }
 /** Called exactly once after successful original primary reveal. Source is the
  * resolved primary, not get_hero: duplicate hero stays +3; final memory stays +1.
  */
 public static Step primary(Rules rules,State state,int sourceHero,boolean wholeHero,boolean memory){
  if(wholeHero&&memory)throw new IllegalArgumentException("ambiguous primary source");
  int points=Math.addExact(state.points,sourceHero==rules.target?(wholeHero?3:memory?1:0):0);
  int draws=Math.addExact(state.draws,1);Set<Integer> receipts=new TreeSet<>(state.chargeReceipts);List<Threshold> grants=new ArrayList<>();
  for(Threshold t:rules.charge)if(t.at<=draws&&!receipts.contains(t.id)){if(t.at<=state.draws)throw new IllegalArgumentException("missing historical charge receipt");receipts.add(t.id);grants.add(t);}
  return new Step(new State(draws,points,receipts,state.jiaozhiReceipts,state.blessings),grants);
 }
 /** Charge-awarded target hero adds points, never another actual draw/charge. */
 public static State chargedHero(Rules rules,State state,int hero){return new State(state.draws,Math.addExact(state.points,hero==rules.target?3:0),state.chargeReceipts,state.jiaozhiReceipts,state.blessings);}
 /** After primary and bounded charge grants, settle every newly crossed threshold
  * in source threshold order. New blessing is available only to later primaries.
  */
 public static Step settle(Rules rules,State state){
  Set<Integer> receipts=new TreeSet<>(state.jiaozhiReceipts);List<Integer> blessings=new ArrayList<>(state.blessings);List<Threshold> grants=new ArrayList<>();
  for(Threshold t:rules.jiaozhi)if(t.at<=state.points&&!receipts.contains(t.id)){receipts.add(t.id);grants.add(t);if(t.blessing)blessings.add(t.id);}
  return new Step(new State(state.draws,state.points,state.chargeReceipts,receipts,blessings),grants);
 }
 public static final class Blessing {
  public final int piece;public final State state;private Blessing(int piece,State state){this.piece=piece;this.state=state;}
 }
 /** Existing blessing can replace only a corresponding memory, uniform among
  * actual missing pieces is the explicit offline-v1 policy. No reroll otherwise.
  */
 public static Blessing memory(Rules rules,State state,int hero,int piece,boolean ownsHero,int ownedMask,int pieces,Random random){
  if(pieces<=0||pieces>30||piece<=0||piece>pieces||ownedMask<0||(ownedMask>>>pieces)!=0||random==null)throw new IllegalArgumentException("dynamic memory boundary");
  if(hero!=rules.target||ownsHero||state.blessings.isEmpty())return new Blessing(piece,state);
  List<Integer> missing=new ArrayList<>();for(int i=0;i<pieces;i++)if((ownedMask&(1<<i))==0)missing.add(i+1);
  if(missing.isEmpty())return new Blessing(piece,state);
  int chosen=missing.get(random.nextInt(missing.size()));List<Integer> remaining=new ArrayList<>(state.blessings);remaining.remove(0);
  return new Blessing(chosen,new State(state.draws,state.points,state.chargeReceipts,state.jiaozhiReceipts,remaining));
 }
 /** Archive v2 retains a naturally missing original piece; only a duplicate is
  * resampled uniformly. Legacy485 memory() remains byte/entropy compatible. */
 public static Blessing memoryArchive(Rules rules,State state,int hero,int piece,boolean owns,int mask,int pieces,Random random){
  if(pieces<=0||pieces>30||piece<=0||piece>pieces||mask<0||(mask>>>pieces)!=0||random==null)throw new IllegalArgumentException("dynamic memory boundary");
  if(hero!=rules.target||owns||state.blessings.isEmpty())return new Blessing(piece,state);
  List<Integer>missing=new ArrayList<>();for(int i=0;i<pieces;i++)if((mask&(1<<i))==0)missing.add(i+1);
  if(missing.isEmpty())return new Blessing(piece,state);
  int chosen=missing.contains(piece)?piece:missing.get(random.nextInt(missing.size()));List<Integer>remaining=new ArrayList<>(state.blessings);remaining.remove(0);
  return new Blessing(chosen,new State(state.draws,state.points,state.chargeReceipts,state.jiaozhiReceipts,remaining));
 }

}
