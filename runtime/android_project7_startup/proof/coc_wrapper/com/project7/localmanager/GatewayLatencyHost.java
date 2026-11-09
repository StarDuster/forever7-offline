package com.project7.localmanager;

import android.content.Context;
import android.content.res.AssetManager;
import java.io.*;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

/** Host-only latency probe: real Store, real 517KB profile + Progress; no account content logged. */
public final class GatewayLatencyHost {
  static final byte[] FRAME_ID = new byte[12];
  static final ByteArrayOutputStream transcript = new ByteArrayOutputStream();
  static Object call(Object owner, String name, Class<?>[] types, Object... args) throws Exception {
    Method method = owner.getClass().getDeclaredMethod(name, types);
    method.setAccessible(true);
    try { return method.invoke(owner, args); }
    catch (InvocationTargetException e) { throw (Exception) e.getCause(); }
  }
  static byte[] envelope(String method, byte[] parameters, int sequence, int callback) {
    return BsonLite.document("w", BsonLite.document("m", method, "p", parameters, "r", sequence), "_cbid_", callback);
  }
  static List<ProtoLite.EntityMessage> frames(byte[] wire) throws Exception {
    List<ProtoLite.EntityMessage> out = new ArrayList<>();
    java.nio.ByteBuffer buffer = java.nio.ByteBuffer.wrap(wire).order(java.nio.ByteOrder.LITTLE_ENDIAN);
    while (buffer.hasRemaining()) {
      int length = buffer.getInt();
      if (buffer.getShort() != 5) throw new AssertionError("frame opcode");
      byte[] data = new byte[length - 2];
      buffer.get(data);
      out.add(ProtoLite.parseEntityMessage(data));
    }
    return out;
  }
  static byte[] md5(String text) throws Exception {
    return MessageDigest.getInstance("MD5").digest(text.getBytes(StandardCharsets.UTF_8));
  }
  static ProtoLite.EntityMessage frame(List<ProtoLite.EntityMessage> frames, String name) throws Exception {
    byte[] md5 = md5(name);
    for (ProtoLite.EntityMessage frame : frames) if (Arrays.equals(frame.methodMd5, md5)) return frame;
    return null;
  }
  static long run(LocalGatewayServer gateway, String op, byte[] envelope, String account,
                  LocalTutorialStore.Progress progress, LocalEventEngine engine,
                  Set<Integer> started, Set<Integer> completed, Map<Integer, Object> map, Set<Integer> other,
                  ByteArrayOutputStream sink) throws Exception {
    long start = System.nanoTime();
    call(gateway, "handleReliableRpc", new Class<?>[] {OutputStream.class, byte[].class, byte[].class,
        String.class, LocalTutorialStore.Progress.class, LocalEventEngine.class,
        Set.class, Set.class, Map.class, Set.class},
        sink, FRAME_ID, envelope, account, progress, engine, started, completed, map, other);
    long nanos = System.nanoTime() - start;
    byte[] wire = sink.toByteArray();
    synchronized (transcript) {
      transcript.write((wire.length >>> 24) & 255); transcript.write((wire.length >>> 16) & 255);
      transcript.write((wire.length >>> 8) & 255); transcript.write(wire.length & 255);
      transcript.write(wire);
    }
    List<ProtoLite.EntityMessage> decoded = frames(wire);
    System.out.println("BENCH op=" + op + " ms=" + (nanos / 1000000L) + " bytes=" + sink.size() + " frames=" + decoded.size());
    return nanos;
  }
  public static void main(String[] args) throws Exception {
    Path assetsPath = Paths.get(args[0]);
    Path classes7 = Paths.get(args[1]);
    Path framesJar = Paths.get(args[2]);
    Path production = Paths.get(args[3]);
    Path profileFixture = Paths.get(args[4]);
    Path progressFixture = Paths.get(args[5]);
    Path captureDir = args.length > 6 ? Paths.get(args[6]) : null;
    File assets = assetsPath.toFile();
    Context prepareContext = new Context(assets, new AssetManager(assets));
    CoreDrawPolicy.prepare(prepareContext);
    HistoryDrawPolicy.prepare(prepareContext);
    SelectorPolicy.prepare(prepareContext);
    OfflineMechanismGateway.prepare(prepareContext);
    StoryMissionBridge.prepare(prepareContext);
    StoryCityPolicy.prepare(prepareContext);
    StoryCityCocPolicy.prepare(prepareContext);
    String account = profileFixture.getFileName().toString().replaceFirst("\\.bson$", "");
    Path root = Files.createTempDirectory("p7-gateway-latency-");
    try {
      Files.createDirectories(root.resolve("profiles"));
      Files.createDirectories(root.resolve("tutorials"));
      Files.copy(profileFixture, root.resolve("profiles").resolve(account + ".bson"));
      Files.copy(progressFixture, root.resolve("tutorials").resolve(account + ".properties"));
      Context context = new Context(root.toFile(), new AssetManager(assets));
      LocalProfileStore store = new LocalProfileStore(context);
      LocalTutorialStore tutorials = new LocalTutorialStore(context);
      LocalTutorialStore.Progress progress = tutorials.load(account);
      LocalEventCatalog events = new LocalEventCatalog(new FileInputStream(new File(assets, "event_graph.tsv")));
      LocalNewbeeCatalog newbees = new LocalNewbeeCatalog(new FileInputStream(new File(assets, "newbee_graph.tsv")));
      LocalPatrolCatalog patrols = new LocalPatrolCatalog(new FileInputStream(new File(assets, "patrol.tsv")));
      LocalCombatCatalog combat = new LocalCombatCatalog(
          new FileInputStream(new File(assets, "combat_skills.tsv")),
          new FileInputStream(new File(assets, "combat_attrs.tsv")),
          new FileInputStream(new File(assets, "suppression.tsv")),
          new FileInputStream(new File(assets, "growth.tsv")),
          new FileInputStream(new File(assets, "home.tsv")));
      byte[] profile = store.load(account, progress);
      LocalEventEngine engine = new LocalEventEngine(events, newbees, progress, 0, profile, true);
      LocalGatewayServer gateway = new LocalGatewayServer(0, null,
          new FailureSafeProfileProvider(store), tutorials, events, newbees, combat, patrols,
          (status, message) -> {});
      Set<Integer> started = new HashSet<>();
      Set<Integer> completed = new HashSet<>();
      Map<Integer, Object> map = new HashMap<>();
      Set<Integer> other = new HashSet<>();
      byte[] statusCityEnv = envelope("statusSwitch", BsonLite.document("s", "city"), 8001, 51);
      ByteArrayOutputStream out1 = new ByteArrayOutputStream();
      run(gateway, "statusSwitch", statusCityEnv, account, progress, engine, started, completed, map, other, out1);
      ProtoLite.EntityMessage s1 = frame(frames(out1.toByteArray()), "statusSwitchReply");
      if (s1 == null || !"ok".equals(BsonLite.stringValue(s1.parameters, "r"))) throw new AssertionError("statusSwitch not accepted");
      ByteArrayOutputStream out2 = new ByteArrayOutputStream();
      run(gateway, "statusSwitch-exact-retransmit", statusCityEnv, account, progress, engine, started, completed, map, other, out2);
      byte[] statusAreaEnv = envelope("statusSwitch", BsonLite.document("s", "area10000"), 8002, 52);
      ByteArrayOutputStream out3 = new ByteArrayOutputStream();
      run(gateway, "statusSwitch-new-seq", statusAreaEnv, account, progress, engine, started, completed, map, other, out3);
      ProtoLite.EntityMessage s3 = frame(frames(out3.toByteArray()), "statusSwitchReply");
      if (s3 == null || !"ok".equals(BsonLite.stringValue(s3.parameters, "r"))) throw new AssertionError("statusSwitch area not accepted");
      ByteArrayOutputStream out4 = new ByteArrayOutputStream();
      run(gateway, "statusSwitch-same-logic-retransmit", statusAreaEnv, account, progress, engine, started, completed, map, other, out4);
      byte[] cond = BsonLite.document("c", 100, "v", "\"3:1\"");
      byte[] condEnv = envelope("updateEventCondClient", cond, 8101, 61);
      ByteArrayOutputStream cond1 = new ByteArrayOutputStream();
      run(gateway, "updateEventCondClient", condEnv, account, progress, engine, started, completed, map, other, cond1);
      String focus = engine.queryState().getProperty("query.areaClick");
      if (!"3:1".equals(focus)) throw new AssertionError("condition not accepted: " + focus);
      ByteArrayOutputStream cond2 = new ByteArrayOutputStream();
      run(gateway, "updateEventCondClient-exact-retransmit", condEnv, account, progress, engine, started, completed, map, other, cond2);
      byte[] start = BsonLite.document("e", 1000);
      byte[] startEnv = envelope("startEvent", start, 8201, 71);
      ByteArrayOutputStream start1 = new ByteArrayOutputStream();
      run(gateway, "startEvent", startEnv, account, progress, engine, started, completed, map, other, start1);
      ProtoLite.EntityMessage r1 = frame(frames(start1.toByteArray()), "startEventReply");
      if (r1 == null || BsonLite.intValue(r1.parameters, "r") != 1) throw new AssertionError("startEvent not accepted");
      ByteArrayOutputStream start2 = new ByteArrayOutputStream();
      run(gateway, "startEvent-exact-retransmit", startEnv, account, progress, engine, started, completed, map, other, start2);
      ProtoLite.EntityMessage r2 = frame(frames(start2.toByteArray()), "startEventReply");
      if (r2 == null || BsonLite.intValue(r2.parameters, "r") != 1) throw new AssertionError("startEvent replay not success");
      byte[] trace = BsonLite.document("k", "ui", "d", BsonLite.document("c", 1));
      ByteArrayOutputStream traceOut = new ByteArrayOutputStream();
      run(gateway, "clientTraceProcessingEvent", envelope("clientTraceProcessingEvent", trace, 8301, 81), account, progress, engine, started, completed, map, other, traceOut);
      System.out.println("BENCH profileBytes=" + profile.length + " progressAvailable=" + progress.availableEvents + " progressProcessing=" + progress.processingEvents);
      if (captureDir != null) {
        Files.createDirectories(captureDir);
        Files.copy(root.resolve("profiles").resolve(account + ".bson"), captureDir.resolve("profile.bson"), StandardCopyOption.REPLACE_EXISTING);
        Files.copy(root.resolve("tutorials").resolve(account + ".properties"), captureDir.resolve("progress.properties"), StandardCopyOption.REPLACE_EXISTING);
        Files.write(captureDir.resolve("replies.bin"), transcript.toByteArray());
        Files.write(captureDir.resolve("result.txt"), (profile.length + " " + progress.availableEvents + " " + progress.processingEvents).getBytes(StandardCharsets.UTF_8));
      }
    } finally {
      try (java.util.stream.Stream<Path> walk = Files.walk(root)) {
        walk.sorted(Comparator.reverseOrder()).forEach(p -> { try { Files.deleteIfExists(p); } catch (Exception ignored) {} });
      }
    }
  }
}
