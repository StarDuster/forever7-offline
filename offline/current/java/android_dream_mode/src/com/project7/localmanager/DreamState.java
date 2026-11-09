package com.project7.localmanager;
import java.util.*;

/** Pure stock-BSON transformations. No new profile owner or event interpreter.
 * The coordinator must validate the real named request and commit these deltas
 * with its accepted original event/patrol result. A lookup is not authorization.
 */
public final class DreamState {
 public static final String CONTEXT="q7Dream";
 public static final int PATROL_LIMIT=3;
 private DreamState(){}
 public enum Reason { ENTERED, ALREADY_ACTIVE, LEFT, NO_PLAN, LEGACY_UNSCOPED,
  STALE_SCOPE, INVALID_STATE, NOT_ACTIVE, PATROL_ALLOWED, PATROL_LIMIT_REACHED,
  PATROL_APPLIED, PATROL_RETRY, NIGHT_PENDING, NIGHT_READY, EXITED, CALENDAR_CLEARED, UNCHANGED }
 public static final class Scope {
  public final String weekCommit,route;public final int week,day;
  public Scope(String commit,int week,String route,int day){
   if(commit==null||commit.isEmpty()||commit.length()>128||route==null||!route.matches("[0-9]+(?:-[0-9]+)*")||route.length()>64||week<0||day<0||day>6)throw new IllegalArgumentException("Dream scope");
   this.weekCommit=commit;this.week=week;this.route=route;this.day=day;
  }
 }
 public static final class Change {
  public final byte[] profile;public final Reason reason;public final boolean changed;
  private Change(byte[] p,Reason r,boolean changed){profile=p;reason=r;this.changed=changed;}
 }
 /** Accepted named request activates mode/budget, not any story event. In
  * particular entry completion is NOT a prerequisite for patrol availability. */
 public static Change enterAuthorized(byte[] profile,DreamCatalog catalog,Scope scope){
  DreamCatalog.Plan plan=catalog.lookup(scope.route,scope.day);
  if(plan==null||!plan.hasEvents())return same(profile,Reason.NO_PLAN);
  if(Boolean.TRUE.equals(BsonLite.boolValue(std(profile),"ff")))return same(profile,Reason.INVALID_STATE);
  byte[] std=std(profile),context=BsonLite.documentValue(profile,CONTEXT);
  if(context!=null){
   if(!matches(context,scope))return same(profile,Reason.STALE_SCOPE);
   if(Boolean.TRUE.equals(BsonLite.boolValue(std,"lhs")))return same(profile,Reason.LEFT);
   if(Boolean.TRUE.equals(BsonLite.boolValue(std,"hsf"))&&budget(std)>=0&&validReceiptCount(context,budget(std)))return same(profile,Reason.ALREADY_ACTIVE);
   return same(profile,Reason.INVALID_STATE);
  }
  if(Boolean.TRUE.equals(BsonLite.boolValue(std,"lhs")))return same(profile,Reason.LEFT);
  if(Boolean.TRUE.equals(BsonLite.boolValue(std,"hsf")))return same(profile,Reason.LEGACY_UNSCOPED);
  byte[] contextNew=BsonLite.document("v",1,"policy",DreamCatalog.POLICY,"catalog",DreamCatalog.SHA256,"wc",scope.weekCommit,"w",scope.week,"d",scope.day,"rt",scope.route,"patrolReceipts",Collections.emptyList());
  byte[] result=BsonLite.withProfileDocument(profile,CONTEXT,contextNew);
  return changed(project(result,true,0,false),Reason.ENTERED);
 }
 public static Change canPatrol(byte[]profile,DreamCatalog catalog,Scope scope){
  Reason guard=activeGuard(profile,catalog,scope);if(guard!=null)return same(profile,guard);
  return same(profile,budget(std(profile))>=PATROL_LIMIT?Reason.PATROL_LIMIT_REACHED:Reason.PATROL_ALLOWED);
 }
 /** The supplied ID is the coordinator's durable ACCEPTED original-patrol
  * receipt, NOT area/heroes, a random re-roll ID or q7EconomyCommit.id.
  * At most three references are retained; no duplicated budget/legacy admissions.
  * Coordinator writes this result + owned pending Progress recovery delta in one
  * original BSON commit, then applies/saves Progress. This method does no IO. */
 public static Change recordAcceptedPatrol(byte[]profile,DreamCatalog catalog,Scope scope,String patrolCommit){
  if(patrolCommit==null||patrolCommit.isEmpty()||patrolCommit.length()>128)throw new IllegalArgumentException("Accepted patrol receipt required");
  Reason guard=activeGuard(profile,catalog,scope);if(guard!=null)return same(profile,guard);
  byte[] context=BsonLite.documentValue(profile,CONTEXT);List<String> receipts=receipts(context);
  int used=budget(std(profile));
  if(receipts.contains(patrolCommit))return same(profile,Reason.PATROL_RETRY);
  if(used>=PATROL_LIMIT)return same(profile,Reason.PATROL_LIMIT_REACHED);
  if(receipts.size()!=used)return same(profile,Reason.INVALID_STATE);
  receipts.add(patrolCommit);context=BsonLite.withProfileArray(context,"patrolReceipts",receipts);
  byte[] result=BsonLite.withProfileDocument(profile,CONTEXT,context);
  result=BsonLite.withProfileDocument(result,"std",BsonLite.withProfileInt(std(result),"hst",used+1));
  return changed(result,Reason.PATROL_APPLIED);
 }
 /** Original runner owns start/select/trace and night completion; this checks
  * only its real completion/pending facts. It never completes events or emits
  * NEXTDAY_CLICK, and never requires spending all three actions before rest. */
 public static Change nightGuard(byte[]profile,DreamCatalog catalog,Scope scope,Collection<Integer>completed,Collection<Integer>processing){
  Reason guard=activeGuard(profile,catalog,scope);if(guard!=null)return same(profile,guard);
  DreamCatalog.Plan plan=catalog.lookup(scope.route,scope.day);
  if(completed==null||processing==null||!completed.contains(plan.night))return same(profile,Reason.NIGHT_PENDING);
  return same(profile,Reason.NIGHT_READY);
 }
 /** Called only with the real runner's completion facts, in the existing
  * transaction before its committed day transition. Inventory/effects remain. */
 public static Change exitAfterNight(byte[]profile,DreamCatalog catalog,Scope scope,Collection<Integer>completed,Collection<Integer>processing){
  Change gate=nightGuard(profile,catalog,scope,completed,processing);
  if(gate.reason!=Reason.NIGHT_READY)return gate;
  return changed(project(profile,false,0,true),Reason.EXITED);
 }
 /** Input is the original calendar/route writer's ALREADY COMMITTED scope.
  * Only owned dream fields are reset; no whole-profile rollback on exit. */
 public static Change afterCalendarCommit(byte[]profile,Scope committed){
  byte[]context=BsonLite.documentValue(profile,CONTEXT);
  if(context==null)return same(profile,Reason.UNCHANGED);
  if(matches(context,committed))return same(profile,Reason.UNCHANGED);
  if(!validContext(context))return same(profile,Reason.INVALID_STATE);
  return changed(project(BsonLite.withoutProfileKey(profile,CONTEXT),false,0,false),Reason.CALENDAR_CLEARED);
 }
 /** Called only for a new original q7WeekTransition.id candidate, before its
  * original atomic writer and Week.recover. The day number may remain equal. */
 public static byte[] afterWeekTransition(byte[]profile){
  return project(BsonLite.withoutProfileKey(BsonLite.withoutProfileKey(profile,CONTEXT),"q7DreamPatrolCommit"),false,0,false);
 }
 /** Existing syncHuiSuData(d) shape. Caller emits original syncRoute first to
  * retain its false->true animation edge, and preserves route35 fbd untouched. */
 public static byte[] huiSuProjection(byte[]profile){byte[]s=std(profile);Integer used=BsonLite.intValue(s,"hst");return BsonLite.document("hs",BsonLite.intArrayValues(s,"hsu"),"hsf",Boolean.TRUE.equals(BsonLite.boolValue(s,"hsf")),"hst",used==null?0:used,"lhs",Boolean.TRUE.equals(BsonLite.boolValue(s,"lhs")));}
 private static Reason activeGuard(byte[]profile,DreamCatalog catalog,Scope scope){
  DreamCatalog.Plan plan=catalog.lookup(scope.route,scope.day);if(plan==null||!plan.hasEvents())return Reason.NO_PLAN;
  byte[]context=BsonLite.documentValue(profile,CONTEXT);if(context==null)return Boolean.TRUE.equals(BsonLite.boolValue(std(profile),"hsf"))?Reason.LEGACY_UNSCOPED:Reason.NOT_ACTIVE;
  if(!matches(context,scope))return Reason.STALE_SCOPE;
  if(Boolean.TRUE.equals(BsonLite.boolValue(std(profile),"lhs")))return Reason.LEFT;
  if(!Boolean.TRUE.equals(BsonLite.boolValue(std(profile),"hsf")))return Reason.NOT_ACTIVE;
  if(Boolean.TRUE.equals(BsonLite.boolValue(std(profile),"ff"))||budget(std(profile))<0||!validReceiptCount(context,budget(std(profile))))return Reason.INVALID_STATE;
  return null;
 }
 private static boolean validReceiptCount(byte[]context,int budget){try{return receipts(context).size()==budget;}catch(IllegalArgumentException invalid){return false;}}
 private static int budget(byte[]std){Integer value=BsonLite.intValue(std,"hst");return value==null||value<0||value>PATROL_LIMIT?-1:value;}
 private static boolean validContext(byte[]context){return Integer.valueOf(1).equals(BsonLite.intValue(context,"v"))&&DreamCatalog.POLICY.equals(BsonLite.stringValue(context,"policy"))&&DreamCatalog.SHA256.equals(BsonLite.stringValue(context,"catalog"));}
 private static boolean matches(byte[]context,Scope scope){return validContext(context)&&scope.weekCommit.equals(BsonLite.stringValue(context,"wc"))&&Integer.valueOf(scope.week).equals(BsonLite.intValue(context,"w"))&&Integer.valueOf(scope.day).equals(BsonLite.intValue(context,"d"))&&scope.route.equals(BsonLite.stringValue(context,"rt"));}
 private static List<String> receipts(byte[]context){
  byte[]raw=BsonLite.arrayValue(context,"patrolReceipts");if(raw==null)throw new IllegalArgumentException("Dream receipts missing");
  List<String> keys=BsonLite.keys(raw),out=new ArrayList<>();if(keys.size()>PATROL_LIMIT)throw new IllegalArgumentException("Dream receipts bound");
  for(int i=0;i<keys.size();i++){String value=BsonLite.stringValue(raw,Integer.toString(i));if(value==null||value.isEmpty()||value.length()>128||out.contains(value))throw new IllegalArgumentException("Dream receipt shape");out.add(value);}return out;
 }
 private static byte[] std(byte[]profile){byte[]s=BsonLite.documentValue(profile,"std");return s==null?BsonLite.EMPTY_DOCUMENT:s;}
 private static byte[] project(byte[]profile,boolean active,int used,boolean left){byte[]s=std(profile);s=BsonLite.withProfileBool(s,"hsf",active);s=BsonLite.withProfileInt(s,"hst",used);s=BsonLite.withProfileArray(s,"hsu",Collections.emptyList());s=BsonLite.withProfileBool(s,"lhs",left);return BsonLite.withProfileDocument(profile,"std",s);}
 private static Change same(byte[]profile,Reason reason){return new Change(profile,reason,false);}
 private static Change changed(byte[]profile,Reason reason){return new Change(profile,reason,true);}
}
