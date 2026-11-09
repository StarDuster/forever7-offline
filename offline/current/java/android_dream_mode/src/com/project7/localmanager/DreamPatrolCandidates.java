package com.project7.localmanager;
import java.util.*;
/** Qualification only, NOT patrol admission or completion. The coordinator first
 * checks active scope/budget and original area/hero facts. Original engine still
 * evaluates every prerequisite/mutex/route/calendar/area/hero/client-op predicate.
 * The selected pending result must then be committed with its budget receipt.
 */
public final class DreamPatrolCandidates {
 private DreamPatrolCandidates(){}
 public static List<Integer> eligible(LocalEventEngine engine,LocalPatrolCatalog patrol,DreamCatalog catalog,int area,Collection<Integer>heroes){
  if(engine==null||catalog==null||heroes==null)throw new IllegalArgumentException("Dream selector inputs");
  List<Integer> original=engine.patrolEvents(area,heroes,patrol);List<Integer> result=new ArrayList<>();
  for(Integer event:original){DreamCatalog.Rule rule=catalog.rule(event);
   if(rule!=null&&rule.dreamSentinel&&rule.hasCondition&&rule.contentRelease&&rule.conditionRelease)result.add(event);
  }
  return Collections.unmodifiableList(result);
 }
}
