package com.project7.localmanager;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
/** Real original LocalEventCatalog probe for the pinned puzzle-room-4 increment.
 * Args: base event_graph.tsv, merged event_graph.tsv, clues-only probe graph.
 * Covers room/clue bounds, base preservation, duplicate/orphan consumer semantics,
 * and the success/clear/fail event rows. */
public final class PuzzleRoom4Host {
 static int checks;
 static void check(boolean value,String why){checks++;if(!value)throw new AssertionError(why);}
 static LocalEventCatalog load(File path)throws IOException{return new LocalEventCatalog(new FileInputStream(path));}
 static Set<Integer> set(Integer...values){return new LinkedHashSet<>(Arrays.asList(values));}
 static File append(File base,String row)throws IOException{
  byte[] prefix=Files.readAllBytes(base.toPath());
  byte[] suffix=(row+"\n").getBytes(StandardCharsets.UTF_8);
  Path tmp=Files.createTempFile("puzzle-probe-",".tsv");
  byte[] all=new byte[prefix.length+suffix.length];
  System.arraycopy(prefix,0,all,0,prefix.length);System.arraycopy(suffix,0,all,prefix.length,suffix.length);
  Files.write(tmp,all);tmp.toFile().deleteOnExit();return tmp.toFile();
 }
 static IllegalArgumentException reject(File base,String row,String message)throws IOException{
  try{load(append(base,row));}
  catch(IllegalArgumentException expected){check(message.equals(expected.getMessage()),"expected "+message+" for "+row);return expected;}
  throw new AssertionError("original consumer accepted "+row);
 }
 static void checkBase(LocalEventCatalog c){
  LocalEventCatalog.Event trigger=c.get(3437);
  check(trigger!=null,"3437 event exists");
  check(trigger.release,"3437 released");
  check(trigger.autoTrigger&&trigger.repeatable&&!trigger.autoStart,"3437 patrol auto trigger");
  check(trigger.dialog==3437,"3437 dialog");
  check(trigger.completeConditions.get("ui").equals(set(1)),"3437 complete ui=1");
  check(trigger.completeConditions.get("dialog").equals(set(3437)),"3437 complete dialog");
  LocalEventCatalog.Trigger t=c.trigger(3437);
  check(t!=null,"3437 trigger");
  check(t.eventId==3437,"3437 trigger id");
  check(t.preAll.equals(set(3436)),"3437 requires 3436");
  check(t.mutex.equals(set(3444)),"3437 trigger mutex 3444");
  check(t.areas.equals(Collections.singletonMap(7,set(0))),"3437 area 7:0");
  check(Arrays.equals(t.date,new int[]{2,2}),"3437 date 2,2");
  check(t.patrolAreas.equals(set(7)),"3437 patrol area 7");
  check(t.clientOps.equals(set(2)),"3437 client op 2");
  check("27,27-2".equals(t.predicates.get(52)),"3437 route predicate 27,27-2");
  check(c.get(3444)!=null&&c.get(3444).release,"3444 clear released");
  check(c.get(3455)!=null&&c.get(3455).release,"3455 fail released");
  check(c.mutex(3444).equals(set(3455)),"3444 mutex 3455 (clear excludes fail)");
  check(c.mutex(3455).equals(set(3444)),"3455 mutex 3444 (fail excludes clear)");
  check(c.puzzleRooms.size()==3,"three reviewed puzzle rooms in base");
  check(c.puzzleRooms.get(4229).id==1&&c.puzzleRooms.get(6228).id==2&&c.puzzleRooms.get(7346).id==3,"base room ids 1..3");
  check(c.puzzleRooms.get(7346).clear==7347&&c.puzzleRooms.get(7346).incomplete==7348,"base room 3 clear/fail");
  check(c.puzzleClues.size()==16,"sixteen reviewed clues in base");
 }
 static void checkRoom4(LocalEventCatalog c){
  LocalPuzzleEngine.Room room=c.puzzleRooms.get(3437);
  check(room!=null,"room 4 keyed by 3437");
  check(room.id==4&&room.clear==3444&&room.incomplete==3455,"room 4 success/clear/fail events");
  check(room.routes.equals(Collections.singleton("27-2")),"room 4 route 27-2");
  check(room.clues.equals(set(17,18,19,20,21)),"room 4 clues 17..21");
  for(int clue:new int[]{17,18,19,20,21}){
   LocalPuzzleEngine.Clue row=c.puzzleClues.get(clue);
   check(row!=null,"clue "+clue+" present");
   check(row.room==4,"clue "+clue+" room 4");
   check(row.cg==0,"clue "+clue+" add_cg 0");
  }
  check(c.puzzleRooms.size()==4&&c.puzzleClues.size()==21,"room/clue counts 4/21 after increment");
  check(c.puzzleRooms.get(4229)!=null&&c.puzzleRooms.get(6228)!=null&&c.puzzleRooms.get(7346)!=null,"rooms 1..3 preserved");
  check(c.puzzleClues.get(17)!=null&&c.puzzleClues.get(18)!=null&&c.puzzleClues.get(19)!=null&&c.puzzleClues.get(20)!=null&&c.puzzleClues.get(21)!=null,"clues 17..21 present");
 }
 public static void main(String[]args)throws Exception{
  check(args.length==3,"usage: base merged clues-only");
  File base=new File(args[0]),merged=new File(args[1]),cluesOnly=new File(args[2]);
  checkBase(load(base));
  LocalEventCatalog c=load(merged);
  checkRoom4(c);
  reject(base,"@puzzleRoom\t4000\t0\t4001\t4002\t27-2\t1","invalid reviewed room");
  reject(base,"@puzzleRoom\t4000\t5\t4001\t4002\t27-2\t1","invalid reviewed room");
  reject(base,"@puzzleClue\t90\t0\t0","invalid reviewed clue");
  reject(base,"@puzzleClue\t90\t5\t0","invalid reviewed clue");
  reject(merged,"@puzzleClue\t90\t4\t-1","invalid reviewed clue");
  LocalEventCatalog dupClue=load(append(merged,"@puzzleClue\t17\t3\t0"));
  check(dupClue.puzzleClues.size()==21&&dupClue.puzzleClues.get(17).room==3,"duplicate clue key last-wins, no new rejection");
  LocalEventCatalog dupRoom=load(append(merged,"@puzzleRoom\t3437\t1\t3444\t3455\t27-2\t17"));
  check(dupRoom.puzzleRooms.size()==4&&dupRoom.puzzleRooms.get(3437).id==1,"duplicate room key last-wins, no new rejection");
  LocalEventCatalog orphan=load(append(merged,"@puzzleClue\t99\t4\t0"));
  check(orphan.puzzleClues.get(99)!=null&&orphan.puzzleRooms.get(3437).clues.equals(set(17,18,19,20,21)),"orphan clue accepted, room clue set unchanged");
  LocalEventCatalog clues=load(cluesOnly);
  check(clues.puzzleRooms.size()==3&&clues.puzzleClues.size()==21&&clues.puzzleClues.get(17).room==4,"clues-only probe accepted; no room/clue cross-check added");
  System.out.println("PASS "+checks+" actual LocalEventCatalog checks; room4 success/clear/fail accepted; bounds/negatives preserved");
 }
}
