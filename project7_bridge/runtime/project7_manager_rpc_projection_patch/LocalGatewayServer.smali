.class final Lcom/project7/localmanager/LocalGatewayServer;
.super Ljava/lang/Object;
.implements Ljava/lang/Runnable;
.implements Ljava/lang/AutoCloseable;
.source "LocalGatewayServer.java"

.annotation system Ldalvik/annotation/MemberClasses;
  value = {
    Lcom/project7/localmanager/LocalGatewayServer$Frame;,
    Lcom/project7/localmanager/LocalGatewayServer$ClientSession;,
    Lcom/project7/localmanager/LocalGatewayServer$CombatReplies;,
    Lcom/project7/localmanager/LocalGatewayServer$CombatReply;,
    Lcom/project7/localmanager/LocalGatewayServer$EventQueryCache;,
    Lcom/project7/localmanager/LocalGatewayServer$HomeCallbacks;,
    Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;,
    Lcom/project7/localmanager/LocalGatewayServer$StatusListener;
  }
.end annotation

.field private final static CHECK_GAMEPLAY_SWITCH:[B

.field private final static CLIENT_CONNECT_REPLY:I = 2

.field private final static CLIENT_CREATE_ENTITY:I = 3

.field private final static CLIENT_ENTITY_MESSAGE:I = 5

.field private final static COMBAT_OFFLINE_FINISH:[B

.field private final static COMBAT_OFFLINE_RESET:[B

.field private final static ENTER_PLACE:[B

.field private final static GET_ALL_AREA_INFO_REQUEST:[B

.field private final static GET_AREA_INFO_REQUEST:[B

.field private final static HEARTBEAT_SERVER:[B

.field private final static LOGIN:[B

.field private final static LOGIN_WITH_URS:[B

.field private final static MAX_FRAME:I = 67108864

.field private final static RELIABLE_RPC_CALL:[B

.field private final static REQUEST_FILE:[B

.field private final static REQUEST_LUCKY_DRAW_CARD:[B

.field private final static REQUEST_QUIT_FILE:[B

.field private final static REQUEST_TRIGGER_DA_XUAN_WO:[B

.field private final static SERVICE_CONNECT_SERVER:I = 0

.field private final static SERVICE_ENTITY_MESSAGE:I = 1

.field private final static SET_PLAYER_NAME:[B

.field private final static TAG:Ljava/lang/String; = "Project7Gateway"

.field private final static TUTORIAL_BEGIN:[B

.field private final static TUTORIAL_END:[B

.field private final accountStore:Lcom/project7/localmanager/LocalAccountStore;

.field private volatile activeSession:Lcom/project7/localmanager/LocalGatewayServer$ClientSession;

.field private final clients:Ljava/util/Set;
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "Ljava/util/Set<",
      "Lcom/project7/localmanager/LocalGatewayServer$ClientSession;",
      ">;"
    }
  .end annotation
.end field

.field private volatile closed:Z

.field private final combatCatalog:Lcom/project7/localmanager/LocalCombatCatalog;

.field private final combatReplies:Ljava/lang/ThreadLocal;
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "Ljava/lang/ThreadLocal<",
      "Lcom/project7/localmanager/LocalGatewayServer$CombatReplies;",
      ">;"
    }
  .end annotation
.end field

.field private final connections:Ljava/util/concurrent/ThreadPoolExecutor;

.field private final eventCatalog:Lcom/project7/localmanager/LocalEventCatalog;

.field private final eventQueries:Ljava/lang/ThreadLocal;
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "Ljava/lang/ThreadLocal<",
      "Lcom/project7/localmanager/LocalGatewayServer$EventQueryCache;",
      ">;"
    }
  .end annotation
.end field

.field private final homeCallbacks:Ljava/lang/ThreadLocal;
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "Ljava/lang/ThreadLocal<",
      "Lcom/project7/localmanager/LocalGatewayServer$HomeCallbacks;",
      ">;"
    }
  .end annotation
.end field

.field private final listener:Lcom/project7/localmanager/LocalGatewayServer$StatusListener;

.field private final newbeeCatalog:Lcom/project7/localmanager/LocalNewbeeCatalog;

.field private final patrolCatalog:Lcom/project7/localmanager/LocalPatrolCatalog;

.field private final port:I

.field private final preparedQuery:Ljava/lang/ThreadLocal;
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "Ljava/lang/ThreadLocal<",
      "Lcom/project7/localmanager/LocalEventEngine;",
      ">;"
    }
  .end annotation
.end field

.field private final profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;

.field private final random:Ljava/security/SecureRandom;

.field private final sessionLock:Ljava/lang/Object;

.field private volatile socket:Ljava/net/ServerSocket;

.field private final storyClosureIncomplete:Ljava/lang/ThreadLocal;
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "Ljava/lang/ThreadLocal<",
      "Ljava/lang/Boolean;",
      ">;"
    }
  .end annotation
.end field

.field private final tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;

.field private final unimplementedReliableRpc:Ljava/lang/ThreadLocal;
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "Ljava/lang/ThreadLocal<",
      "Ljava/lang/Boolean;",
      ">;"
    }
  .end annotation
.end field

.method static constructor <clinit>()V
  .registers 1
  .line 68
    const-string v0, "login"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    sput-object v0, Lcom/project7/localmanager/LocalGatewayServer;->LOGIN:[B
  .line 69
    const-string v0, "loginWithUrs"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    sput-object v0, Lcom/project7/localmanager/LocalGatewayServer;->LOGIN_WITH_URS:[B
  .line 70
    const-string v0, "heartbeatServer"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    sput-object v0, Lcom/project7/localmanager/LocalGatewayServer;->HEARTBEAT_SERVER:[B
  .line 71
    const-string v0, "reliableRpcCall"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    sput-object v0, Lcom/project7/localmanager/LocalGatewayServer;->RELIABLE_RPC_CALL:[B
  .line 72
    const-string v0, "requestTriggerDaXuanWo"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    sput-object v0, Lcom/project7/localmanager/LocalGatewayServer;->REQUEST_TRIGGER_DA_XUAN_WO:[B
  .line 73
    const-string v0, "setPlayerName"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    sput-object v0, Lcom/project7/localmanager/LocalGatewayServer;->SET_PLAYER_NAME:[B
  .line 74
    const-string v0, "enterPlace"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    sput-object v0, Lcom/project7/localmanager/LocalGatewayServer;->ENTER_PLACE:[B
  .line 75
    const-string v0, "tutorialBegin"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    sput-object v0, Lcom/project7/localmanager/LocalGatewayServer;->TUTORIAL_BEGIN:[B
  .line 76
    const-string v0, "tutorialEnd"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    sput-object v0, Lcom/project7/localmanager/LocalGatewayServer;->TUTORIAL_END:[B
  .line 77
    const-string v0, "checkGamePlaySwitch"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    sput-object v0, Lcom/project7/localmanager/LocalGatewayServer;->CHECK_GAMEPLAY_SWITCH:[B
  .line 78
    const-string v0, "requestFile"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    sput-object v0, Lcom/project7/localmanager/LocalGatewayServer;->REQUEST_FILE:[B
  .line 79
    const-string v0, "requestQuitFile"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    sput-object v0, Lcom/project7/localmanager/LocalGatewayServer;->REQUEST_QUIT_FILE:[B
  .line 80
    const-string v0, "requestLuckyDrawCard"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    sput-object v0, Lcom/project7/localmanager/LocalGatewayServer;->REQUEST_LUCKY_DRAW_CARD:[B
  .line 81
    const-string v0, "getAllAreaInfoRequest"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    sput-object v0, Lcom/project7/localmanager/LocalGatewayServer;->GET_ALL_AREA_INFO_REQUEST:[B
  .line 82
    const-string v0, "getAreaInfoRequest"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    sput-object v0, Lcom/project7/localmanager/LocalGatewayServer;->GET_AREA_INFO_REQUEST:[B
  .line 83
    const-string v0, "combatOfflineFinish"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    sput-object v0, Lcom/project7/localmanager/LocalGatewayServer;->COMBAT_OFFLINE_FINISH:[B
  .line 84
    const-string v0, "combatOfflineReset"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    sput-object v0, Lcom/project7/localmanager/LocalGatewayServer;->COMBAT_OFFLINE_RESET:[B
    return-void
.end method

.method constructor <init>(ILcom/project7/localmanager/LocalAccountStore;Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;Lcom/project7/localmanager/LocalTutorialStore;Lcom/project7/localmanager/LocalEventCatalog;Lcom/project7/localmanager/LocalNewbeeCatalog;Lcom/project7/localmanager/LocalCombatCatalog;Lcom/project7/localmanager/LocalPatrolCatalog;Lcom/project7/localmanager/LocalGatewayServer$StatusListener;)V
  .registers 20
  .line 202
    move-object v0, p0
    invoke-direct { p0 }, Ljava/lang/Object;-><init>()V
  .line 95
    new-instance v1, Ljava/security/SecureRandom;
    invoke-direct { v1 }, Ljava/security/SecureRandom;-><init>()V
    iput-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->random:Ljava/security/SecureRandom;
  .line 101
    sget-object v1, Lcom/project7/localmanager/LocalGatewayServer$$ExternalSyntheticLambda4;->INSTANCE:Lcom/project7/localmanager/LocalGatewayServer$$ExternalSyntheticLambda4;
    invoke-static { v1 }, Ljava/lang/ThreadLocal;->withInitial(Ljava/util/function/Supplier;)Ljava/lang/ThreadLocal;
    move-result-object v1
    iput-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->homeCallbacks:Ljava/lang/ThreadLocal;
  .line 102
    sget-object v1, Lcom/project7/localmanager/LocalGatewayServer$$ExternalSyntheticLambda5;->INSTANCE:Lcom/project7/localmanager/LocalGatewayServer$$ExternalSyntheticLambda5;
    invoke-static { v1 }, Ljava/lang/ThreadLocal;->withInitial(Ljava/util/function/Supplier;)Ljava/lang/ThreadLocal;
    move-result-object v1
    iput-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->storyClosureIncomplete:Ljava/lang/ThreadLocal;
  .line 123
    sget-object v1, Lcom/project7/localmanager/LocalGatewayServer$$ExternalSyntheticLambda6;->INSTANCE:Lcom/project7/localmanager/LocalGatewayServer$$ExternalSyntheticLambda6;
    invoke-static { v1 }, Ljava/lang/ThreadLocal;->withInitial(Ljava/util/function/Supplier;)Ljava/lang/ThreadLocal;
    move-result-object v1
    iput-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->eventQueries:Ljava/lang/ThreadLocal;
  .line 124
    new-instance v1, Ljava/lang/ThreadLocal;
    invoke-direct { v1 }, Ljava/lang/ThreadLocal;-><init>()V
    iput-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->preparedQuery:Ljava/lang/ThreadLocal;
  .line 124
    new-instance v1, Ljava/lang/ThreadLocal;
    invoke-direct { v1 }, Ljava/lang/ThreadLocal;-><init>()V
    iput-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->unimplementedReliableRpc:Ljava/lang/ThreadLocal;
  .line 167
    sget-object v1, Lcom/project7/localmanager/LocalGatewayServer$$ExternalSyntheticLambda7;->INSTANCE:Lcom/project7/localmanager/LocalGatewayServer$$ExternalSyntheticLambda7;
    invoke-static { v1 }, Ljava/lang/ThreadLocal;->withInitial(Ljava/util/function/Supplier;)Ljava/lang/ThreadLocal;
    move-result-object v1
    iput-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->combatReplies:Ljava/lang/ThreadLocal;
  .line 170
    new-instance v1, Ljava/lang/Object;
    invoke-direct { v1 }, Ljava/lang/Object;-><init>()V
    iput-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->sessionLock:Ljava/lang/Object;
  .line 171
    invoke-static { }, Ljava/util/concurrent/ConcurrentHashMap;->newKeySet()Ljava/util/concurrent/ConcurrentHashMap$KeySetView;
    move-result-object v1
    iput-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->clients:Ljava/util/Set;
  .line 173
    new-instance v1, Ljava/util/concurrent/ThreadPoolExecutor;
    sget-object v7, Ljava/util/concurrent/TimeUnit;->MILLISECONDS:Ljava/util/concurrent/TimeUnit;
    new-instance v8, Ljava/util/concurrent/ArrayBlockingQueue;
    const/4 v2, 4
    invoke-direct { v8, v2 }, Ljava/util/concurrent/ArrayBlockingQueue;-><init>(I)V
    sget-object v9, Lcom/project7/localmanager/LocalGatewayServer$$ExternalSyntheticLambda1;->INSTANCE:Lcom/project7/localmanager/LocalGatewayServer$$ExternalSyntheticLambda1;
    const/4 v3, 4
    const/4 v4, 4
    const-wide/16 v5, 0
    move-object v2, v1
    invoke-direct/range { v2 .. v9 }, Ljava/util/concurrent/ThreadPoolExecutor;-><init>(IIJLjava/util/concurrent/TimeUnit;Ljava/util/concurrent/BlockingQueue;Ljava/util/concurrent/ThreadFactory;)V
    iput-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->connections:Ljava/util/concurrent/ThreadPoolExecutor;
  .line 203
    move v1, p1
    iput v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->port:I
  .line 204
    move-object v1, p2
    iput-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->accountStore:Lcom/project7/localmanager/LocalAccountStore;
  .line 205
    move-object v1, p3
    iput-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
  .line 206
    move-object v1, p4
    iput-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
  .line 207
    move-object v1, p5
    iput-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->eventCatalog:Lcom/project7/localmanager/LocalEventCatalog;
  .line 208
    move-object/from16 v1, p6
    iput-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->newbeeCatalog:Lcom/project7/localmanager/LocalNewbeeCatalog;
  .line 209
    move-object/from16 v1, p7
    iput-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->combatCatalog:Lcom/project7/localmanager/LocalCombatCatalog;
  .line 210
    move-object/from16 v1, p8
    iput-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->patrolCatalog:Lcom/project7/localmanager/LocalPatrolCatalog;
  .line 211
    move-object/from16 v1, p9
    iput-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->listener:Lcom/project7/localmanager/LocalGatewayServer$StatusListener;
  .line 212
    return-void
.end method

.method private acknowledgeCgNotices(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalResourceEngine$Result;)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 8
  .line 995
    invoke-direct { p0, p3 }, Lcom/project7/localmanager/LocalGatewayServer;->deliveredCgs(Lcom/project7/localmanager/LocalResourceEngine$Result;)Ljava/util/List;
    move-result-object p3
  .line 996
    invoke-interface { p3 }, Ljava/util/List;->isEmpty()Z
    move-result v0
    if-nez v0, :L0
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    const/4 v1, 2
    new-array v1, v1, [Ljava/lang/Object;
    const/4 v2, 0
    const-string v3, "c"
    aput-object v3, v1, v2
    const/4 v2, 1
    aput-object p3, v1, v2
    invoke-static { v1 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object p3
    const-string v1, "q7AckCgNotice"
    invoke-interface { v0, p1, v1, p3, p2 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
  :L0
  .line 997
    return-void
.end method

.method private claimSession(Lcom/project7/localmanager/LocalGatewayServer$ClientSession;)Z
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .catchall { :L0 .. :L2 } :L10
  .catch Ljava/lang/InterruptedException; { :L2 .. :L3 } :L6
  .catchall { :L2 .. :L3 } :L10
  .catchall { :L4 .. :L11 } :L10
  .registers 9
  .line 2565
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->sessionLock:Ljava/lang/Object;
    monitor-enter v0
  :L0
  .line 2566
    iget-boolean v1, p0, Lcom/project7/localmanager/LocalGatewayServer;->closed:Z
    const/4 v2, 0
    if-eqz v1, :L1
    monitor-exit v0
    return v2
  :L1
  .line 2567
    iget-object v1, p0, Lcom/project7/localmanager/LocalGatewayServer;->activeSession:Lcom/project7/localmanager/LocalGatewayServer$ClientSession;
  .line 2568
    if-eqz v1, :L7
    if-eq v1, p1, :L7
    iget-object v3, v1, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;->done:Ljava/util/concurrent/CountDownLatch;
    invoke-virtual { v3 }, Ljava/util/concurrent/CountDownLatch;->getCount()J
    move-result-wide v3
    const-wide/16 v5, 0
    cmp-long v3, v3, v5
    if-eqz v3, :L7
  .line 2569
    invoke-virtual { v1 }, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;->close()V
  :L2
  .line 2572
    iget-object v1, v1, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;->done:Ljava/util/concurrent/CountDownLatch;
    const-wide/16 v3, 15
    sget-object v5, Ljava/util/concurrent/TimeUnit;->SECONDS:Ljava/util/concurrent/TimeUnit;
    invoke-virtual { v1, v3, v4, v5 }, Ljava/util/concurrent/CountDownLatch;->await(JLjava/util/concurrent/TimeUnit;)Z
    move-result v1
  :L3
    if-nez v1, :L5
  :L4
    monitor-exit v0
    return v2
  :L5
  .line 2576
    goto :L7
  :L6
  .line 2573
    move-exception p1
  .line 2574
    invoke-static { }, Ljava/lang/Thread;->currentThread()Ljava/lang/Thread;
    move-result-object p1
    invoke-virtual { p1 }, Ljava/lang/Thread;->interrupt()V
  .line 2575
    monitor-exit v0
    return v2
  :L7
  .line 2578
    iget-boolean v1, p0, Lcom/project7/localmanager/LocalGatewayServer;->closed:Z
    if-nez v1, :L9
    iget-object v1, p1, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;->client:Ljava/net/Socket;
    invoke-virtual { v1 }, Ljava/net/Socket;->isClosed()Z
    move-result v1
    if-eqz v1, :L8
    goto :L9
  :L8
  .line 2579
    iput-object p1, p0, Lcom/project7/localmanager/LocalGatewayServer;->activeSession:Lcom/project7/localmanager/LocalGatewayServer$ClientSession;
  .line 2580
    const/4 p1, 1
    monitor-exit v0
    return p1
  :L9
  .line 2578
    monitor-exit v0
    return v2
  :L10
  .line 2581
    move-exception p1
    monitor-exit v0
  :L11
    throw p1
.end method

.method private closePuzzleBeforeTrace(Ljava/lang/String;Ljava/util/List;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Ljava/lang/String;",
      "Ljava/util/List<",
      "Ljava/lang/Integer;",
      ">;",
      "Ljava/lang/String;",
      "Lcom/project7/localmanager/LocalTutorialStore$Progress;",
      "Lcom/project7/localmanager/LocalEventEngine;",
      ")V"
    }
  .end annotation
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 11
  .line 922
    const-string v0, "ui"
    invoke-virtual { v0, p1 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result p1
    if-eqz p1, :L4
    const/4 p1, 1
    invoke-static { p1 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v0
    invoke-interface { p2, v0 }, Ljava/util/List;->contains(Ljava/lang/Object;)Z
    move-result p2
    if-eqz p2, :L4
    iget-object p2, p0, Lcom/project7/localmanager/LocalGatewayServer;->eventCatalog:Lcom/project7/localmanager/LocalEventCatalog;
    if-nez p2, :L0
    goto :L4
  :L0
  .line 923
    new-instance p2, Ljava/util/ArrayList;
    iget-object v0, p4, Lcom/project7/localmanager/LocalTutorialStore$Progress;->processingEvents:Ljava/util/Set;
    invoke-direct { p2, v0 }, Ljava/util/ArrayList;-><init>(Ljava/util/Collection;)V
    invoke-virtual { p2 }, Ljava/util/ArrayList;->iterator()Ljava/util/Iterator;
    move-result-object p2
  :L1
    invoke-interface { p2 }, Ljava/util/Iterator;->hasNext()Z
    move-result v0
    if-eqz v0, :L3
    invoke-interface { p2 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Ljava/lang/Integer;
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v0
  .line 924
    iget-object v1, p0, Lcom/project7/localmanager/LocalGatewayServer;->eventCatalog:Lcom/project7/localmanager/LocalEventCatalog;
    iget-object v1, v1, Lcom/project7/localmanager/LocalEventCatalog;->puzzleRooms:Ljava/util/Map;
    invoke-static { v0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v2
    invoke-interface { v1, v2 }, Ljava/util/Map;->containsKey(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L2
    goto :L1
  :L2
  .line 925
    iget-object v1, p0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    const/4 v2, 2
    new-array v2, v2, [Ljava/lang/Object;
    const/4 v3, 0
    const-string v4, "e"
    aput-object v4, v2, v3
  .line 926
    invoke-static { v0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v0
    aput-object v0, v2, p1
    invoke-static { v2 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v0
  .line 925
    const-string v2, "q7PuzzleExit"
    invoke-interface { v1, p3, v2, v0, p4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v0
  .line 927
    iget-object v0, v0, Lcom/project7/localmanager/LocalResourceEngine$Result;->profile:[B
    invoke-virtual { p5, v0 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  .line 928
    goto :L1
  :L3
  .line 929
    return-void
  :L4
  .line 922
    return-void
.end method

.method private static combatHash([B)[B
  .catch Ljava/security/NoSuchAlgorithmException; { :L0 .. :L2 } :L3
  .registers 2
  :L0
  .line 1889
    const-string v0, "SHA-256"
    invoke-static { v0 }, Ljava/security/MessageDigest;->getInstance(Ljava/lang/String;)Ljava/security/MessageDigest;
    move-result-object v0
    if-nez p0, :L1
    sget-object p0, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
  :L1
    invoke-virtual { v0, p0 }, Ljava/security/MessageDigest;->digest([B)[B
    move-result-object p0
  :L2
    return-object p0
  :L3
  .line 1890
    move-exception p0
    new-instance v0, Ljava/lang/IllegalStateException;
    invoke-direct { v0, p0 }, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/Throwable;)V
    throw v0
.end method

.method private completeCallback(Ljava/io/OutputStream;[BILjava/lang/String;)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 7
  .line 2470
    nop
  .line 2475
    const-string v0, "serverCallbackCarrier"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
  .line 2476
    invoke-static { p3 }, Lcom/project7/localmanager/BsonLite;->callbackDocument(I)[B
    move-result-object v1
  .line 2473
    invoke-static { p2, v0, v1 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object p2
  .line 2470
    const/4 v0, 5
    invoke-direct { p0, p1, v0, p2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2479
    new-instance p1, Ljava/lang/StringBuilder;
    invoke-direct { p1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string p2, "reliable RPC callback completed id="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, p3 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string p2, " method="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, p4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p1
    const-string p2, "Project7Gateway"
    invoke-static { p2, p1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 2480
    return-void
.end method

.method private completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 9
  .line 2501
    const-string v0, "_cbid_"
    invoke-static { p3, v0 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object p3
  .line 2502
    const-string v0, "Project7Gateway"
    if-nez p3, :L0
  .line 2503
    new-instance p1, Ljava/lang/StringBuilder;
    invoke-direct { p1 }, Ljava/lang/StringBuilder;-><init>()V
    invoke-virtual { p1, p4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string p2, " completed without callback id"
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p1
    invoke-static { v0, p1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 2504
    return-void
  :L0
  .line 2506
    const/4 v1, 5
  .line 2511
    const-string v2, "serverCallbackCarrier"
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
  .line 2512
    invoke-virtual { p3 }, Ljava/lang/Integer;->intValue()I
    move-result v3
    invoke-static { v3 }, Lcom/project7/localmanager/BsonLite;->callbackDocument(I)[B
    move-result-object v3
  .line 2509
    invoke-static { p2, v2, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object p2
  .line 2506
    invoke-direct { p0, p1, v1, p2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2515
    new-instance p1, Ljava/lang/StringBuilder;
    invoke-direct { p1 }, Ljava/lang/StringBuilder;-><init>()V
    invoke-virtual { p1, p4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string p2, " callback completed id="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, p3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { p1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p1
    invoke-static { v0, p1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 2516
    iget-object p1, p0, Lcom/project7/localmanager/LocalGatewayServer;->listener:Lcom/project7/localmanager/LocalGatewayServer$StatusListener;
    const/4 p2, 1
    new-instance p3, Ljava/lang/StringBuilder;
    invoke-direct { p3 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v0, "\u5df2\u5b8c\u6210\u542f\u52a8\u56de\u8c03\uff1a"
    invoke-virtual { p3, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p3, p4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p3 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p3
    invoke-interface { p1, p2, p3 }, Lcom/project7/localmanager/LocalGatewayServer$StatusListener;->onStatus(ZLjava/lang/String;)V
  .line 2517
    return-void
.end method

.method private currentCombatReply(Lcom/project7/localmanager/LocalGatewayServer$CombatReply;Lcom/project7/localmanager/LocalGatewayServer$CombatReplies;I[BLcom/project7/localmanager/LocalEventEngine;)Z
  .registers 11
  .line 1895
    const-string v0, "weeknum"
    invoke-static { p4, v0 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v0
  .line 1896
    iget v1, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->week:I
    const-string v2, "w"
    invoke-static { v0, v2 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v2
    const/4 v3, 0
    if-ne v1, v2, :L18
    iget v1, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->day:I
  .line 1897
    const-string v2, "d"
    invoke-static { v0, v2 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v0
    if-eq v1, v0, :L0
    goto/16 :L18
  :L0
  .line 1898
    iget v0, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->type:I
    const-string v1, "q7Battle"
    const/4 v2, 2
    const/4 v4, 1
    if-nez v0, :L4
  .line 1899
    iget-object p3, p2, Lcom/project7/localmanager/LocalGatewayServer$CombatReplies;->values:Ljava/util/Map;
    iget-object v0, p2, Lcom/project7/localmanager/LocalGatewayServer$CombatReplies;->latestAccepted:Ljava/lang/Integer;
    invoke-interface { p3, v0 }, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object p3
    check-cast p3, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;
  .line 1900
    invoke-static { p4 }, Lcom/project7/localmanager/LocalDailyEngine;->active([B)Z
    move-result v0
    if-nez v0, :L2
  .line 1901
    invoke-static { p4, v1 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object p4
    invoke-static { p4 }, Lcom/project7/localmanager/BsonLite;->keys([B)Ljava/util/List;
    move-result-object p4
    invoke-interface { p4 }, Ljava/util/List;->isEmpty()Z
    move-result p4
    if-eqz p4, :L2
    iget-object p2, p2, Lcom/project7/localmanager/LocalGatewayServer$CombatReplies;->latestAccepted:Ljava/lang/Integer;
    iget-object p1, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->acceptedAtPreparation:Ljava/lang/Integer;
  .line 1902
    invoke-static { p2, p1 }, Ljava/util/Objects;->equals(Ljava/lang/Object;Ljava/lang/Object;)Z
    move-result p1
    if-eqz p1, :L2
    if-eqz p3, :L1
    iget p1, p3, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->type:I
    if-ne p1, v2, :L1
    if-eqz p5, :L1
    iget p1, p3, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->scene:I
  .line 1903
    invoke-virtual { p5, p1 }, Lcom/project7/localmanager/LocalEventEngine;->hasPendingStoryBattle(I)Z
    move-result p1
    if-nez p1, :L2
  :L1
    move v3, v4
    goto :L3
  :L2
    nop
  :L3
  .line 1900
    return v3
  :L4
  .line 1905
    invoke-static { p3 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object p3
    iget-object p2, p2, Lcom/project7/localmanager/LocalGatewayServer$CombatReplies;->latestAccepted:Ljava/lang/Integer;
    invoke-virtual { p3, p2 }, Ljava/lang/Integer;->equals(Ljava/lang/Object;)Z
    move-result p2
    if-nez p2, :L5
    return v3
  :L5
  .line 1906
    iget p2, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->type:I
    const-string p3, "f"
    const-string v0, "h"
    if-ne p2, v2, :L11
  .line 1907
    if-eqz p5, :L10
    iget-object p2, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->owners:Ljava/util/Set;
    invoke-interface { p2 }, Ljava/util/Set;->isEmpty()Z
    move-result p2
    if-nez p2, :L10
    iget-object p2, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->owners:Ljava/util/Set;
    iget v1, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->scene:I
    invoke-virtual { p5, v1 }, Lcom/project7/localmanager/LocalEventEngine;->pendingStoryBattleOwners(I)Ljava/util/Set;
    move-result-object p5
    invoke-interface { p2, p5 }, Ljava/util/Set;->equals(Ljava/lang/Object;)Z
    move-result p2
    if-nez p2, :L6
    goto :L10
  :L6
  .line 1908
    iget p2, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->scene:I
    const/16 p5, 291
    if-eq p2, p5, :L7
    return v4
  :L7
  .line 1909
    const-string p2, "q7WingBattle"
    invoke-static { p4, p2 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object p2
  .line 1910
    sget-object p4, Ljava/lang/Boolean;->FALSE:Ljava/lang/Boolean;
    const-string p5, "done"
    invoke-static { p2, p5 }, Lcom/project7/localmanager/BsonLite;->boolValue([BLjava/lang/String;)Ljava/lang/Boolean;
    move-result-object p5
    invoke-virtual { p4, p5 }, Ljava/lang/Boolean;->equals(Ljava/lang/Object;)Z
    move-result p4
    if-eqz p4, :L8
    iget-object p4, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->fight:Ljava/lang/String;
    if-eqz p4, :L8
    iget-object p4, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->fight:Ljava/lang/String;
  .line 1911
    invoke-static { p2, p3 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object p3
    invoke-virtual { p4, p3 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result p3
    if-eqz p3, :L8
  .line 1912
    invoke-static { p2, v0 }, Lcom/project7/localmanager/BsonLite;->intArrayValues([BLjava/lang/String;)Ljava/util/List;
    move-result-object p2
    iget-object p1, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->parameters:[B
    invoke-static { p1, v0 }, Lcom/project7/localmanager/BsonLite;->intArrayValues([BLjava/lang/String;)Ljava/util/List;
    move-result-object p1
    invoke-interface { p2, p1 }, Ljava/util/List;->equals(Ljava/lang/Object;)Z
    move-result p1
    if-eqz p1, :L8
    move v3, v4
    goto :L9
  :L8
    nop
  :L9
  .line 1910
    return v3
  :L10
  .line 1907
    return v3
  :L11
  .line 1914
    iget p2, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->type:I
    if-ne p2, v4, :L12
    goto :L13
  :L12
    const-string v1, "q7DailyBattle"
  :L13
    invoke-static { p4, v1 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object p2
  .line 1915
    iget p5, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->type:I
    if-eq p5, v4, :L14
    invoke-static { p4 }, Lcom/project7/localmanager/LocalDailyEngine;->active([B)Z
    move-result p4
    if-eqz p4, :L16
  :L14
    iget p4, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->type:I
    if-eq p4, v4, :L15
    iget p4, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->type:I
  .line 1916
    const-string p5, "t"
    invoke-static { p2, p5 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result p5
    if-ne p4, p5, :L16
  :L15
    iget p4, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->scene:I
  .line 1917
    const-string p5, "s"
    invoke-static { p2, p5 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result p5
    if-ne p4, p5, :L16
  .line 1918
    invoke-static { p2, v0 }, Lcom/project7/localmanager/BsonLite;->intArrayValues([BLjava/lang/String;)Ljava/util/List;
    move-result-object p4
    iget-object p5, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->parameters:[B
    invoke-static { p5, v0 }, Lcom/project7/localmanager/BsonLite;->intArrayValues([BLjava/lang/String;)Ljava/util/List;
    move-result-object p5
    invoke-interface { p4, p5 }, Ljava/util/List;->equals(Ljava/lang/Object;)Z
    move-result p4
    if-eqz p4, :L16
    iget-object p4, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->fight:Ljava/lang/String;
    if-eqz p4, :L16
    iget-object p1, p1, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->fight:Ljava/lang/String;
  .line 1919
    invoke-static { p2, p3 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object p2
    invoke-virtual { p1, p2 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result p1
    if-eqz p1, :L16
    move v3, v4
    goto :L17
  :L16
    nop
  :L17
  .line 1915
    return v3
  :L18
  .line 1897
    return v3
.end method

.method private deliveredCgs(Lcom/project7/localmanager/LocalResourceEngine$Result;)Ljava/util/List;
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Lcom/project7/localmanager/LocalResourceEngine$Result;",
      ")",
      "Ljava/util/List<",
      "Ljava/lang/Integer;",
      ">;"
    }
  .end annotation
  .registers 6
  .line 1000
    new-instance v0, Ljava/util/LinkedHashSet;
    invoke-direct { v0 }, Ljava/util/LinkedHashSet;-><init>()V
  .line 1001
    iget-object p1, p1, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { p1 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object p1
  :L0
    invoke-interface { p1 }, Ljava/util/Iterator;->hasNext()Z
    move-result v1
    if-eqz v1, :L2
    invoke-interface { p1 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;
  .line 1002
    iget-object v2, v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    const-string v3, "procRewardSettlementCommon"
    invoke-virtual { v3, v2 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v2
    if-nez v2, :L1
    goto :L0
  :L1
  .line 1003
    iget-object v1, v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    const-string v2, "r"
    invoke-static { v1, v2 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v1
    const-string v2, "cg"
    invoke-static { v1, v2 }, Lcom/project7/localmanager/BsonLite;->intArrayValues([BLjava/lang/String;)Ljava/util/List;
    move-result-object v1
    invoke-interface { v0, v1 }, Ljava/util/Set;->addAll(Ljava/util/Collection;)Z
  .line 1004
    goto :L0
  :L2
  .line 1005
    new-instance p1, Ljava/util/ArrayList;
    invoke-direct { p1, v0 }, Ljava/util/ArrayList;-><init>(Ljava/util/Collection;)V
    return-object p1
.end method

.method private static digest(Ljava/lang/String;)[B
  .catch Ljava/security/NoSuchAlgorithmException; { :L0 .. :L1 } :L2
  .registers 3
  :L0
  .line 2620
    const-string v0, "MD5"
    invoke-static { v0 }, Ljava/security/MessageDigest;->getInstance(Ljava/lang/String;)Ljava/security/MessageDigest;
    move-result-object v0
    sget-object v1, Ljava/nio/charset/StandardCharsets;->US_ASCII:Ljava/nio/charset/Charset;
  .line 2621
    invoke-virtual { p0, v1 }, Ljava/lang/String;->getBytes(Ljava/nio/charset/Charset;)[B
    move-result-object p0
  .line 2620
    invoke-virtual { v0, p0 }, Ljava/security/MessageDigest;->digest([B)[B
    move-result-object p0
  :L1
    return-object p0
  :L2
  .line 2623
    move-exception p0
  .line 2624
    new-instance v0, Ljava/lang/ExceptionInInitializerError;
    invoke-direct { v0, p0 }, Ljava/lang/ExceptionInInitializerError;-><init>(Ljava/lang/Throwable;)V
    throw v0
.end method

.method private dispatchReliableRpc(Ljava/io/OutputStream;[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;Ljava/util/Set;Ljava/util/Map;Ljava/util/Set;)V
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Ljava/io/OutputStream;",
      "[B[B",
      "Ljava/lang/String;",
      "Lcom/project7/localmanager/LocalTutorialStore$Progress;",
      "Lcom/project7/localmanager/LocalEventEngine;",
      "Ljava/util/Set<",
      "Ljava/lang/Integer;",
      ">;",
      "Ljava/util/Set<",
      "Ljava/lang/Integer;",
      ">;",
      "Ljava/util/Map<",
      "Ljava/lang/Integer;",
      "Lcom/project7/localmanager/LocalPatrolEngine$Result;",
      ">;",
      "Ljava/util/Set<",
      "Ljava/lang/Integer;",
      ">;)V"
    }
  .end annotation
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .catchall { :L0 .. :L15 } :L16
  .registers 28
  .line 1225
    move-object/from16 v7, p0
    move-object/from16 v0, p4
    move-object/from16 v8, p5
    move-object/from16 v9, p6
    invoke-static { }, Ljava/lang/System;->nanoTime()J
    move-result-wide v10
  .line 1226
    iget-object v1, v7, Lcom/project7/localmanager/LocalGatewayServer;->storyClosureIncomplete:Ljava/lang/ThreadLocal;
    const/4 v2, 0
    invoke-static { v2 }, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
    move-result-object v3
    invoke-virtual { v1, v3 }, Ljava/lang/ThreadLocal;->set(Ljava/lang/Object;)V
    iget-object v1, v7, Lcom/project7/localmanager/LocalGatewayServer;->unimplementedReliableRpc:Ljava/lang/ThreadLocal;
    invoke-virtual { v1 }, Ljava/lang/ThreadLocal;->remove()V
  :L0
  .line 1228
    const-string v1, "w"
    move-object/from16 v3, p3
    invoke-static { v3, v1 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v1
  .line 1229
    const/4 v4, 0
    if-nez v1, :L1
    move-object v12, v4
    goto :L2
  :L1
    const-string v5, "m"
    invoke-static { v1, v5 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v1
    move-object v12, v1
  :L2
  .line 1230
    const/4 v1, 1
    if-eqz v9, :L4
    const-string v5, "pullEvents"
    invoke-virtual { v5, v12 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v5
    if-nez v5, :L3
    const-string v5, "updateEventCondClient"
    invoke-virtual { v5, v12 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v5
    if-nez v5, :L3
    const-string v5, "checkProcessingEvent"
  .line 1231
    invoke-virtual { v5, v12 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v5
    if-nez v5, :L3
    const-string v5, "statusSwitch"
    invoke-virtual { v5, v12 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v5
    if-eqz v5, :L4
  :L3
    move v13, v1
    goto :L5
  :L4
    move v13, v2
  :L5
  .line 1232
    nop
  .line 1233
    iget-object v5, v7, Lcom/project7/localmanager/LocalGatewayServer;->eventQueries:Ljava/lang/ThreadLocal;
    invoke-virtual { v5 }, Ljava/lang/ThreadLocal;->get()Ljava/lang/Object;
    move-result-object v5
    move-object v14, v5
    check-cast v14, Lcom/project7/localmanager/LocalGatewayServer$EventQueryCache;
  .line 1234
    nop
  .line 1235
    if-eqz v13, :L7
  .line 1238
    iget-object v5, v7, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v5, v0, v8 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v5
  .line 1239
    invoke-virtual { v14, v9, v5 }, Lcom/project7/localmanager/LocalGatewayServer$EventQueryCache;->matches(Lcom/project7/localmanager/LocalEventEngine;[B)Z
    move-result v6
  .line 1240
    if-nez v6, :L6
    invoke-virtual { v9, v5 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  :L6
  .line 1241
    iget-object v15, v7, Lcom/project7/localmanager/LocalGatewayServer;->preparedQuery:Ljava/lang/ThreadLocal;
    invoke-virtual { v15, v9 }, Ljava/lang/ThreadLocal;->set(Ljava/lang/Object;)V
    move-object v15, v5
    goto :L8
  :L7
  .line 1235
    move v6, v2
    move-object v15, v4
  :L8
  .line 1243
    invoke-direct/range { p0 .. p10 }, Lcom/project7/localmanager/LocalGatewayServer;->handleReliableRpc(Ljava/io/OutputStream;[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;Ljava/util/Set;Ljava/util/Map;Ljava/util/Set;)V
  .line 1245
    if-eqz v13, :L9
    if-eqz v6, :L9
    invoke-virtual { v14, v9, v15 }, Lcom/project7/localmanager/LocalGatewayServer$EventQueryCache;->matches(Lcom/project7/localmanager/LocalEventEngine;[B)Z
    move-result v3
    if-eqz v3, :L9
    move v2, v1
  :L9
  .line 1250
    # Post projection: skip generic post effects only for A (the exact pure area
    # query) or U (this dispatch hit the explicit unimplemented sink). When both
    # are false, execution continues into the unmodified v9 post condition below.
    const-string v1, "getAreaStagesRequest"
    invoke-virtual { v1, v12 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L9_check_unimplemented
    goto/16 :L13
  :L9_check_unimplemented
    iget-object v1, v7, Lcom/project7/localmanager/LocalGatewayServer;->unimplementedReliableRpc:Ljava/lang/ThreadLocal;
    invoke-virtual { v1 }, Ljava/lang/ThreadLocal;->get()Ljava/lang/Object;
    move-result-object v1
    sget-object v3, Ljava/lang/Boolean;->TRUE:Ljava/lang/Boolean;
    invoke-virtual { v3, v1 }, Ljava/lang/Boolean;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L9_original_post
    goto/16 :L13
  :L9_original_post
    if-nez v2, :L13
    const-string v1, "reliableEcho"
    invoke-virtual { v1, v12 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L13
    const-string v1, "clientTraceProcessingEvent"
  .line 1251
    invoke-virtual { v1, v12 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L11
    if-eqz v9, :L11
    iget-object v1, v7, Lcom/project7/localmanager/LocalGatewayServer;->storyClosureIncomplete:Ljava/lang/ThreadLocal;
    invoke-virtual { v1 }, Ljava/lang/ThreadLocal;->get()Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Ljava/lang/Boolean;
    invoke-virtual { v1 }, Ljava/lang/Boolean;->booleanValue()Z
    move-result v1
    if-eqz v1, :L10
    goto :L11
  :L10
    move-object/from16 v16, v12
    goto :L14
  :L11
  .line 1253
    if-eqz v13, :L12
    invoke-virtual/range { p6 .. p6 }, Lcom/project7/localmanager/LocalEventEngine;->queryState()Ljava/util/Properties;
    move-result-object v4
  :L12
    move-object v6, v4
  .line 1254
    move-object/from16 v1, p0
    move-object/from16 v2, p1
    move-object/from16 v3, p2
    move-object/from16 v4, p4
    move-object/from16 v5, p5
    move-object/from16 v16, v12
    move-object v12, v6
    move-object/from16 v6, p6
    invoke-direct/range { v1 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->syncEventEffects(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 1258
    if-eqz v13, :L14
    iget-object v1, v7, Lcom/project7/localmanager/LocalGatewayServer;->storyClosureIncomplete:Ljava/lang/ThreadLocal;
    invoke-virtual { v1 }, Ljava/lang/ThreadLocal;->get()Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Ljava/lang/Boolean;
    invoke-virtual { v1 }, Ljava/lang/Boolean;->booleanValue()Z
    move-result v1
    if-nez v1, :L14
    invoke-virtual/range { p6 .. p6 }, Lcom/project7/localmanager/LocalEventEngine;->queryState()Ljava/util/Properties;
    move-result-object v1
    invoke-virtual { v12, v1 }, Ljava/util/Properties;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L14
  .line 1259
    iget-object v1, v7, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v1, v0, v8 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v0
  .line 1260
    invoke-static { v15 }, Lcom/project7/localmanager/LocalGatewayServer$EventQueryCache;->storySnapshot([B)[B
    move-result-object v1
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer$EventQueryCache;->storySnapshot([B)[B
    move-result-object v2
    invoke-static { v1, v2 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L14
  .line 1261
    invoke-virtual { v14, v9, v0 }, Lcom/project7/localmanager/LocalGatewayServer$EventQueryCache;->settle(Lcom/project7/localmanager/LocalEventEngine;[B)V
    goto :L14
  :L13
  .line 1250
    move-object/from16 v16, v12
  :L14
  .line 1264
    invoke-static { }, Ljava/lang/System;->nanoTime()J
    move-result-wide v0
    sub-long/2addr v0, v10
    const-wide/32 v2, 1000000
    div-long/2addr v0, v2
  .line 1265
    const-wide/16 v2, 250
    cmp-long v2, v0, v2
    if-ltz v2, :L15
    const-string v2, "Project7Gateway"
    new-instance v3, Ljava/lang/StringBuilder;
    invoke-direct { v3 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v4, "slow reliable dispatch method="
    invoke-virtual { v3, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-object/from16 v4, v16
    invoke-virtual { v3, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v4, " elapsedMs="
    invoke-virtual { v3, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v3, v0, v1 }, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;
    invoke-virtual { v3 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v2, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;)I
  :L15
  .line 1268
    iget-object v0, v7, Lcom/project7/localmanager/LocalGatewayServer;->preparedQuery:Ljava/lang/ThreadLocal;
    invoke-virtual { v0 }, Ljava/lang/ThreadLocal;->remove()V
  .line 1269
    iget-object v0, v7, Lcom/project7/localmanager/LocalGatewayServer;->storyClosureIncomplete:Ljava/lang/ThreadLocal;
    invoke-virtual { v0 }, Ljava/lang/ThreadLocal;->remove()V
  .line 1269
    iget-object v0, v7, Lcom/project7/localmanager/LocalGatewayServer;->unimplementedReliableRpc:Ljava/lang/ThreadLocal;
    invoke-virtual { v0 }, Ljava/lang/ThreadLocal;->remove()V
  .line 1270
    nop
  .line 1271
    return-void
  :L16
  .line 1268
    move-exception v0
    iget-object v1, v7, Lcom/project7/localmanager/LocalGatewayServer;->preparedQuery:Ljava/lang/ThreadLocal;
    invoke-virtual { v1 }, Ljava/lang/ThreadLocal;->remove()V
  .line 1269
    iget-object v1, v7, Lcom/project7/localmanager/LocalGatewayServer;->storyClosureIncomplete:Ljava/lang/ThreadLocal;
    invoke-virtual { v1 }, Ljava/lang/ThreadLocal;->remove()V
  .line 1269
    iget-object v1, v7, Lcom/project7/localmanager/LocalGatewayServer;->unimplementedReliableRpc:Ljava/lang/ThreadLocal;
    invoke-virtual { v1 }, Ljava/lang/ThreadLocal;->remove()V
  .line 1270
    throw v0
.end method

.method private emitCombatControls(Ljava/io/OutputStream;[BLcom/project7/localmanager/LocalGatewayServer$CombatReply;[BZ)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 15
  .line 1924
    iget-object v0, p3, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->profileHash:[B
    invoke-static { p4 }, Lcom/project7/localmanager/LocalGatewayServer;->combatHash([B)[B
    move-result-object v1
    invoke-static { v0, v1 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v0
  .line 1925
    iget-object p3, p3, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->controls:Ljava/util/List;
    invoke-interface { p3 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object p3
  :L0
    invoke-interface { p3 }, Ljava/util/Iterator;->hasNext()Z
    move-result v1
    if-eqz v1, :L4
    invoke-interface { p3 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;
  .line 1926
    iget-object v2, v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
  .line 1927
    const/4 v3, 5
    const/4 v4, 2
    const/4 v5, 1
    const/4 v6, 0
    if-eqz p5, :L1
    iget-object v7, v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    const-string v8, "syncJingshenliPower"
    invoke-virtual { v8, v7 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v7
    if-eqz v7, :L1
  .line 1928
    const-string v2, "city"
    invoke-static { p4, v2 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v2
  .line 1929
    const/4 v7, 6
    new-array v7, v7, [Ljava/lang/Object;
    const-string v8, "p"
    aput-object v8, v7, v6
    const-string v6, "jpv"
    invoke-static { v2, v6 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v6
    invoke-static { v6 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v6
    aput-object v6, v7, v5
    const-string v5, "t"
    aput-object v5, v7, v4
    const/4 v4, 3
  .line 1930
    const-string v5, "jpvt"
    invoke-static { v2, v5 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v5
    invoke-static { v5 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v5
    aput-object v5, v7, v4
    const/4 v4, 4
    const-string v5, "cjsla"
    aput-object v5, v7, v4
    invoke-static { v2, v5 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v2
    invoke-static { v2 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v2
    aput-object v2, v7, v3
  .line 1929
    invoke-static { v7 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v2
  .line 1931
    goto :L3
  :L1
    if-eqz p5, :L2
    iget-object v7, v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    const-string v8, "syncMazeData"
    invoke-virtual { v8, v7 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v7
    if-eqz v7, :L2
  .line 1932
    new-array v2, v4, [Ljava/lang/Object;
    const-string v4, "d"
    aput-object v4, v2, v6
    const-string v4, "ifm"
    invoke-static { p4, v4 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v4
    aput-object v4, v2, v5
    invoke-static { v2 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v2
    goto :L3
  :L2
  .line 1933
    if-eqz p5, :L3
    if-nez v0, :L3
    iget-object v4, v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    const-string v5, "enterManeuverBattleReply"
    invoke-virtual { v5, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v4
    if-nez v4, :L3
    iget-object v4, v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 1934
    const-string v5, "showMessageStr"
    invoke-virtual { v5, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v4
    if-nez v4, :L3
  .line 1936
    goto/16 :L0
  :L3
  .line 1938
    iget-object v1, v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    invoke-static { p2, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
    invoke-direct { p0, p1, v3, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1939
    goto/16 :L0
  :L4
  .line 1940
    return-void
.end method

.method private emitCombatCores(Ljava/io/OutputStream;[BLcom/project7/localmanager/LocalGatewayServer$CombatReply;)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 7
  .line 1943
    iget-object p3, p3, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->cores:Ljava/util/List;
    invoke-interface { p3 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object p3
  :L0
    invoke-interface { p3 }, Ljava/util/Iterator;->hasNext()Z
    move-result v0
    if-eqz v0, :L1
    invoke-interface { p3 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    const/4 v1, 5
    iget-object v2, v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 1944
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
    iget-object v0, v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { p2, v2, v0 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
  .line 1943
    invoke-direct { p0, p1, v1, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L0
  :L1
  .line 1945
    return-void
.end method

.method private emitEventEffects(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Lcom/project7/localmanager/LocalResourceEngine$Result;)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 14
  .line 973
    iget-object p5, p6, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { p5 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object p5
  :L0
    invoke-interface { p5 }, Ljava/util/Iterator;->hasNext()Z
    move-result v0
    const/4 v1, 5
    if-eqz v0, :L1
    invoke-interface { p5 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v2, v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 974
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
    iget-object v0, v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { p2, v2, v0 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
  .line 973
    invoke-direct { p0, p1, v1, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L0
  :L1
  .line 975
    iget-object p5, p6, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { p5 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object p5
  :L2
    invoke-interface { p5 }, Ljava/util/Iterator;->hasNext()Z
    move-result v0
    const-string v2, "c"
    if-eqz v0, :L4
    invoke-interface { p5 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v3, v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    const-string v4, "addCenterConfidence"
    invoke-virtual { v4, v3 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v3
    if-eqz v3, :L3
  .line 976
    new-instance v3, Ljava/lang/StringBuilder;
    invoke-direct { v3 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v4, "story confidence delivered delta="
    invoke-virtual { v3, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-object v4, v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    const-string v5, "v"
    invoke-static { v4, v5 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v4
    invoke-virtual { v3, v4 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v4, " total="
    invoke-virtual { v3, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-object v0, v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
  .line 977
    invoke-static { v0, v2 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v0
    invoke-virtual { v3, v0 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v3 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
  .line 976
    const-string v2, "Project7Gateway"
    invoke-static { v2, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  :L3
  .line 975
    goto :L2
  :L4
  .line 978
    invoke-static { p6 }, Lcom/project7/localmanager/LocalStoryProgressDelivery;->sent(Lcom/project7/localmanager/LocalResourceEngine$Result;)[B
    move-result-object p5
  .line 979
    invoke-direct { p0, p6 }, Lcom/project7/localmanager/LocalGatewayServer;->deliveredCgs(Lcom/project7/localmanager/LocalResourceEngine$Result;)Ljava/util/List;
    move-result-object v0
  .line 980
    invoke-static { p5 }, Lcom/project7/localmanager/BsonLite;->keys([B)Ljava/util/List;
    move-result-object v3
    invoke-interface { v3 }, Ljava/util/List;->isEmpty()Z
    move-result v3
    if-eqz v3, :L5
    invoke-interface { v0 }, Ljava/util/List;->isEmpty()Z
    move-result v3
    if-nez v3, :L6
  :L5
  .line 981
    iget-object v3, p0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    const/4 v4, 4
    new-array v4, v4, [Ljava/lang/Object;
    const/4 v5, 0
    const-string v6, "s"
    aput-object v6, v4, v5
    const/4 v5, 1
    aput-object p5, v4, v5
    const/4 p5, 2
    aput-object v2, v4, p5
    const/4 p5, 3
    aput-object v0, v4, p5
  .line 982
    invoke-static { v4 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object p5
  .line 981
    const-string v0, "q7AckStoryDelivery"
    invoke-interface { v3, p3, v0, p5, p4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
  :L6
  .line 983
    iget-object p3, p6, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { p3 }, Ljava/util/List;->stream()Ljava/util/stream/Stream;
    move-result-object p3
    sget-object p5, Lcom/project7/localmanager/LocalGatewayServer$$ExternalSyntheticLambda2;->INSTANCE:Lcom/project7/localmanager/LocalGatewayServer$$ExternalSyntheticLambda2;
    invoke-interface { p3, p5 }, Ljava/util/stream/Stream;->anyMatch(Ljava/util/function/Predicate;)Z
    move-result p3
  .line 984
    iget-object p5, p6, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { p5 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object p5
  :L7
    invoke-interface { p5 }, Ljava/util/Iterator;->hasNext()Z
    move-result v0
    if-eqz v0, :L8
    invoke-interface { p5 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    if-nez p3, :L7
    iget-object v0, v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    const-string v2, "updateBlackCore"
    invoke-virtual { v2, v0 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L7
  .line 985
    const-string p3, "get_all_area_info_reply"
    invoke-static { p3 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object p3
  .line 986
    invoke-static { p4 }, Lcom/project7/localmanager/LocalGatewayServer;->isHighSchoolUnlocked(Lcom/project7/localmanager/LocalTutorialStore$Progress;)Z
    move-result p5
    iget-object p6, p6, Lcom/project7/localmanager/LocalResourceEngine$Result;->profile:[B
    invoke-static { p5, p4, p6 }, Lcom/project7/localmanager/BsonLite;->allAreaInfoReplyDocument(ZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
    move-result-object p4
  .line 985
    invoke-static { p2, p3, p4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object p2
    invoke-direct { p0, p1, v1, p2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L8
  .line 991
    return-void
.end method

.method private emitHomeResult(Ljava/io/OutputStream;[BLcom/project7/localmanager/LocalResourceEngine$Result;Ljava/lang/Integer;)[B
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 10
  .line 732
    sget-object v0, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
  .line 733
    iget-object p3, p3, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { p3 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object p3
  :L0
    invoke-interface { p3 }, Ljava/util/Iterator;->hasNext()Z
    move-result v1
    const/4 v2, 5
    if-eqz v1, :L2
    invoke-interface { p3 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;
  .line 734
    iget-object v3, v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    const-string v4, "q7HomeCallback"
    invoke-virtual { v4, v3 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v3
    if-eqz v3, :L1
    iget-object v0, v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    goto :L0
  :L1
  .line 735
    iget-object v3, v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    invoke-static { v3 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v3
    iget-object v1, v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { p2, v3, v1 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
    invoke-direct { p0, p1, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 736
    goto :L0
  :L2
  .line 737
    if-eqz p4, :L3
  .line 738
    const-string p3, "serverCallbackCarrier"
    invoke-static { p3 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object p3
    const/4 v1, 4
    new-array v1, v1, [Ljava/lang/Object;
    const/4 v3, 0
    const-string v4, "_r_"
    aput-object v4, v1, v3
    const/4 v3, 1
    aput-object v0, v1, v3
    const/4 v3, 2
    const-string v4, "_cbid_"
    aput-object v4, v1, v3
    const/4 v3, 3
    aput-object p4, v1, v3
    invoke-static { v1 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object p4
  .line 737
    invoke-static { p2, p3, p4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object p2
    invoke-direct { p0, p1, v2, p2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L3
  .line 739
    return-object v0
.end method

.method private finishAbandonedStory(Ljava/io/OutputStream;[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Z)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 21
    invoke-static/range { p0 .. p7 }, Lcom/project7/localmanager/TrialRetryGateway;->handleGiveup(Lcom/project7/localmanager/LocalGatewayServer;Ljava/io/OutputStream;[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Z)Z
    move-result v0
    if-eqz v0, :L0
    return-void
  :L0
  .line 2104
    move-object v6, p0
    move-object v7, p1
    move-object v8, p2
    move-object/from16 v3, p4
    move-object/from16 v4, p5
    move-object/from16 v9, p6
    if-eqz v9, :L6
    iget-object v0, v6, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v0, v3, v4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v0
    invoke-static { v0 }, Lcom/project7/localmanager/LocalDailyEngine;->active([B)Z
    move-result v0
    if-eqz v0, :L1
    goto/16 :L6
  :L1
  .line 2105
    const-string v0, "s"
    move-object/from16 v1, p3
    invoke-static { v1, v0 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v10
  .line 2106
    if-gtz v10, :L2
    return-void
  :L2
  .line 2107
    move/from16 v0, p7
    invoke-virtual { v9, v10, v0 }, Lcom/project7/localmanager/LocalEventEngine;->abandonStoryBattle(IZ)Ljava/util/List;
    move-result-object v11
  .line 2108
    invoke-interface { v11 }, Ljava/util/List;->isEmpty()Z
    move-result v0
    if-eqz v0, :L3
    return-void
  :L3
  .line 2109
    iget-object v0, v6, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v0, v3, v4 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 2110
    invoke-interface { v11 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v0
  :L4
    invoke-interface { v0 }, Ljava/util/Iterator;->hasNext()Z
    move-result v1
    const/4 v12, 5
    if-eqz v1, :L5
    invoke-interface { v0 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Ljava/lang/Integer;
    invoke-virtual { v1 }, Ljava/lang/Integer;->intValue()I
    move-result v1
  .line 2111
    const-string v2, "completeEventReplyStart"
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
    invoke-static { v1 }, Lcom/project7/localmanager/BsonLite;->eventRewardDocument(I)[B
    move-result-object v5
    invoke-static { p2, v2, v5 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
    invoke-direct { p0, p1, v12, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2112
    const-string v2, "completeEventReplyEnd"
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
    invoke-static { v1 }, Lcom/project7/localmanager/BsonLite;->eventDocument(I)[B
    move-result-object v1
    invoke-static { p2, v2, v1 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
    invoke-direct { p0, p1, v12, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2113
    goto :L4
  :L5
  .line 2114
    move-object v0, p0
    move-object v1, p1
    move-object v2, p2
    move-object/from16 v3, p4
    move-object/from16 v4, p5
    move-object/from16 v5, p6
    invoke-direct/range { v0 .. v5 }, Lcom/project7/localmanager/LocalGatewayServer;->syncEventEffects(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 2115
    const-string v0, "pushEvents"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
  .line 2116
    invoke-virtual/range { p6 .. p6 }, Lcom/project7/localmanager/LocalEventEngine;->availableEvents()Ljava/util/Set;
    move-result-object v1
    invoke-virtual/range { p6 .. p6 }, Lcom/project7/localmanager/LocalEventEngine;->processingEvents()Ljava/util/Set;
    move-result-object v2
    invoke-static { v1, v2 }, Lcom/project7/localmanager/BsonLite;->eventListsDocument(Ljava/lang/Iterable;Ljava/lang/Iterable;)[B
    move-result-object v1
  .line 2115
    invoke-static { p2, v0, v1 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
    invoke-direct { p0, p1, v12, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2117
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "confirmed story abandonment scene="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v10 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v1, " events="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v11 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    const-string v1, "Project7Gateway"
    invoke-static { v1, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 2118
    return-void
  :L6
  .line 2104
    return-void
.end method

.method private finishStoryCombat(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;Ljava/util/Set;IIILcom/project7/localmanager/LocalEconomyEngine$Result;)V
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Ljava/io/OutputStream;",
      "[B",
      "Ljava/lang/String;",
      "Lcom/project7/localmanager/LocalTutorialStore$Progress;",
      "Lcom/project7/localmanager/LocalEventEngine;",
      "Ljava/util/Set<",
      "Ljava/lang/Integer;",
      ">;",
      "Ljava/util/Set<",
      "Ljava/lang/Integer;",
      ">;III",
      "Lcom/project7/localmanager/LocalEconomyEngine$Result;",
      ")V"
    }
  .end annotation
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 28
  .line 2228
    move-object/from16 v0, p0
    move-object/from16 v1, p1
    move-object/from16 v2, p2
    move-object/from16 v3, p3
    move-object/from16 v4, p4
    move-object/from16 v5, p5
    move/from16 v6, p8
    move/from16 v7, p9
    move-object/from16 v8, p11
    const/4 v9, 0
    const/4 v10, 1
    if-ne v6, v10, :L0
    invoke-static/range { p9 .. p9 }, Lcom/project7/localmanager/LocalCityProgress;->area(I)I
    move-result v11
    if-eqz v11, :L0
    move v11, v10
    goto :L1
  :L0
    move v11, v9
  :L1
  .line 2230
    if-eqz v5, :L13
    if-nez p10, :L2
    goto/16 :L13
  :L2
  .line 2233
    if-eqz v11, :L3
    if-eqz v8, :L3
    iget v8, v8, Lcom/project7/localmanager/LocalEconomyEngine$Result;->remainingActions:I
    if-ltz v8, :L3
    move v8, v10
    goto :L4
  :L3
    move v8, v9
  :L4
  .line 2234
    if-eqz v5, :L5
    iget-object v11, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v11, v3, v4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v11
    invoke-virtual { v5, v11 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  :L5
  .line 2235
    const/4 v11, 2
    if-ne v6, v11, :L7
  .line 2236
    if-eqz p10, :L6
    move v9, v10
  :L6
    invoke-virtual { v5, v7, v9 }, Lcom/project7/localmanager/LocalEventEngine;->finishStoryBattle(IZ)Ljava/util/List;
    move-result-object v9
    goto :L8
  :L7
  .line 2237
    invoke-static/range { p9 .. p9 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v9
    invoke-static { v9 }, Ljava/util/Collections;->singletonList(Ljava/lang/Object;)Ljava/util/List;
    move-result-object v9
    const-string v11, "battle"
    invoke-virtual { v5, v11, v9 }, Lcom/project7/localmanager/LocalEventEngine;->trace(Ljava/lang/String;Ljava/util/Collection;)Ljava/util/List;
    move-result-object v9
  :L8
  .line 2238
    iget-object v11, v0, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v11, v3, v4 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 2239
    invoke-interface { v9 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v9
  :L9
    invoke-interface { v9 }, Ljava/util/Iterator;->hasNext()Z
    move-result v11
    const-string v12, "Project7Gateway"
    const/4 v13, 5
    if-eqz v11, :L10
    invoke-interface { v9 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v11
    check-cast v11, Ljava/lang/Integer;
  .line 2240
    nop
  .line 2245
    const-string v14, "completeEventReplyStart"
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v14
  .line 2246
    invoke-virtual { v11 }, Ljava/lang/Integer;->intValue()I
    move-result v15
    invoke-static { v15 }, Lcom/project7/localmanager/BsonLite;->eventRewardDocument(I)[B
    move-result-object v15
  .line 2243
    invoke-static { v2, v14, v15 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v14
  .line 2240
    invoke-direct { v0, v1, v13, v14 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2249
    nop
  .line 2254
    const-string v14, "completeEventReplyEnd"
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v14
  .line 2255
    invoke-virtual { v11 }, Ljava/lang/Integer;->intValue()I
    move-result v15
    invoke-static { v15 }, Lcom/project7/localmanager/BsonLite;->eventDocument(I)[B
    move-result-object v15
  .line 2252
    invoke-static { v2, v14, v15 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v14
  .line 2249
    invoke-direct { v0, v1, v13, v14 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2258
    move-object/from16 v14, p6
    invoke-interface { v14, v11 }, Ljava/util/Set;->remove(Ljava/lang/Object;)Z
  .line 2259
    new-instance v13, Ljava/lang/StringBuilder;
    invoke-direct { v13 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v15, "event completed event="
    invoke-virtual { v13, v15 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v13, v11 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v11, " condition=battle["
    invoke-virtual { v13, v11 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v13, v7 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v11, "]"
    invoke-virtual { v13, v11 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v13 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v11
    invoke-static { v12, v11 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 2260
    goto :L9
  :L10
  .line 2262
    invoke-direct/range { p0 .. p5 }, Lcom/project7/localmanager/LocalGatewayServer;->syncEventEffects(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 2263
    if-eqz v8, :L11
  .line 2264
    nop
  .line 2265
    const-string v8, "get_city_data_reply"
    invoke-static { v8 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v8
    iget-object v9, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v9, v3, v4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v9
    invoke-static { v4, v9 }, Lcom/project7/localmanager/BsonLite;->cityDataReplyDocument(Lcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
    move-result-object v9
  .line 2264
    invoke-static { v2, v8, v9 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v8
    invoke-direct { v0, v1, v13, v8 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2266
    new-instance v8, Ljava/lang/StringBuilder;
    invoke-direct { v8 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v9, "combat action consumed scene="
    invoke-virtual { v8, v9 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v8, v7 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v9, " remaining="
    invoke-virtual { v8, v9 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget v9, v4, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolActions:I
    invoke-virtual { v8, v9 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v8 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v8
    invoke-static { v12, v8 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  :L11
  .line 2268
    if-ne v6, v10, :L12
    invoke-static/range { p9 .. p9 }, Lcom/project7/localmanager/LocalCityProgress;->area(I)I
    move-result v6
    if-eqz v6, :L12
  .line 2269
    nop
  .line 2270
    const-string v6, "get_all_area_info_reply"
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v6
  .line 2271
    invoke-static/range { p4 .. p4 }, Lcom/project7/localmanager/LocalGatewayServer;->isHighSchoolUnlocked(Lcom/project7/localmanager/LocalTutorialStore$Progress;)Z
    move-result v8
    iget-object v9, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v9, v3, v4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v9
    invoke-static { v8, v4, v9 }, Lcom/project7/localmanager/BsonLite;->allAreaInfoReplyDocument(ZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
    move-result-object v8
  .line 2269
    invoke-static { v2, v6, v8 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v6
    invoke-direct { v0, v1, v13, v6 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2272
    new-instance v6, Ljava/lang/StringBuilder;
    invoke-direct { v6 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v8, "post-battle city state refreshed scene="
    invoke-virtual { v6, v8 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v6, v7 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v6 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v6
    invoke-static { v12, v6 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  :L12
  .line 2274
    move-object/from16 v6, p7
    invoke-direct { v0, v1, v2, v5, v6 }, Lcom/project7/localmanager/LocalGatewayServer;->triggerPendingNewbees(Ljava/io/OutputStream;[BLcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;)V
  .line 2275
    iget-object v6, v0, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v6, v3, v4 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 2276
    invoke-direct/range { p0 .. p5 }, Lcom/project7/localmanager/LocalGatewayServer;->syncEventEffects(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 2277
    nop
  .line 2278
    const-string v3, "pushEvents"
    invoke-static { v3 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v3
  .line 2279
    invoke-virtual/range { p5 .. p5 }, Lcom/project7/localmanager/LocalEventEngine;->availableEvents()Ljava/util/Set;
    move-result-object v4
    invoke-virtual/range { p5 .. p5 }, Lcom/project7/localmanager/LocalEventEngine;->processingEvents()Ljava/util/Set;
    move-result-object v5
  .line 2278
    invoke-static { v4, v5 }, Lcom/project7/localmanager/BsonLite;->eventListsDocument(Ljava/lang/Iterable;Ljava/lang/Iterable;)[B
    move-result-object v4
  .line 2277
    invoke-static { v2, v3, v4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
    invoke-direct { v0, v1, v13, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2280
    return-void
  :L13
  .line 2231
    return-void
.end method

.method private handleBasicRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;)Z
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 48
  .line 1010
    move-object/from16 v0, p0
    move-object/from16 v1, p1
    move-object/from16 v2, p2
    move-object/from16 v3, p3
    move-object/from16 v4, p4
    move-object/from16 v5, p5
    const-string v6, "uploadDeviceInfo"
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v6
    invoke-static { v3, v6 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v6
    const/4 v7, 1
    if-nez v6, :L30
  .line 1011
    const-string v6, "logCheckCheat"
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v6
    invoke-static { v3, v6 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v6
    if-nez v6, :L30
  .line 1012
    const-string v6, "uploadTouchHistory"
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v6
    invoke-static { v3, v6 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v6
    if-eqz v6, :L0
    goto/16 :L30
  :L0
  .line 1018
    const-string v6, "teamOnLoginAsk"
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v6
    invoke-static { v3, v6 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v6
    if-nez v6, :L29
  .line 1019
    const-string v6, "limitTeamOnLoginAsk"
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v6
    invoke-static { v3, v6 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v6
    if-nez v6, :L29
  .line 1020
    const-string v6, "multiTeamOnLoginAsk"
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v6
    invoke-static { v3, v6 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v6
    if-eqz v6, :L1
    goto/16 :L29
  :L1
  .line 1026
    const-string v6, "remove_chat_channel_listener"
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v6
    invoke-static { v3, v6 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v6
    if-eqz v6, :L2
  .line 1028
    return v7
  :L2
  .line 1030
    const-string v6, "evalEcho"
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v6
    invoke-static { v3, v6 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v6
    const-string v8, "m"
    const-string v9, "Project7Gateway"
    if-eqz v6, :L3
  .line 1031
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "client data sync: "
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-static { v4, v8 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v2
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-static { v9, v1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 1032
    return v7
  :L3
  .line 1034
    const-string v6, "checkGamePlaySwitchAsk"
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v6
    invoke-static { v3, v6 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v6
    const/4 v10, 4
    const/4 v11, 3
    const/4 v12, 2
    const/4 v13, 0
    const/4 v14, 5
    if-eqz v6, :L13
  .line 1035
    const-string v3, "g"
    invoke-static { v4, v3 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v4
  .line 1036
    const-string v5, "friendsummon"
    invoke-virtual { v5, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    const-string v15, "summon"
    if-nez v6, :L5
    invoke-virtual { v15, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    if-nez v6, :L5
  .line 1037
    const-string v6, "itemStore"
    invoke-virtual { v6, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    if-nez v6, :L5
    const-string v6, "huodongMain_2"
    invoke-virtual { v6, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    if-nez v6, :L5
    const-string v6, "huodongMain_42"
    invoke-virtual { v6, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    if-nez v6, :L5
  .line 1038
    const-string v6, "huodongMain_215"
    invoke-virtual { v6, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    if-nez v6, :L5
    const-string v6, "memoryPalace"
    invoke-virtual { v6, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    if-nez v6, :L5
  .line 1039
    const-string v6, "exchange"
    invoke-virtual { v6, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    if-nez v6, :L5
    const-string v6, "dancengxunluo"
    invoke-virtual { v6, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    if-nez v6, :L5
    const-string v6, "lunhuizhijing"
    invoke-virtual { v6, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    if-nez v6, :L5
  .line 1040
    const-string v6, "furnitureSummon"
    invoke-virtual { v6, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    if-nez v6, :L5
    const-string v6, "funitureSummonLianchou"
    invoke-virtual { v6, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    if-nez v6, :L5
  .line 1041
    const-string v6, "heroliberate"
    invoke-virtual { v6, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    if-nez v6, :L5
    const-string v6, "treasureExp"
    invoke-virtual { v6, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    if-eqz v6, :L4
    goto :L5
  :L4
    move v6, v13
    goto :L6
  :L5
    move v6, v7
  :L6
  .line 1042
    invoke-virtual { v5, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v5
    if-nez v5, :L7
    invoke-virtual { v15, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v5
    if-eqz v5, :L8
  :L7
    invoke-direct/range { p0 .. p2 }, Lcom/project7/localmanager/LocalGatewayServer;->syncDrawCalendar(Ljava/io/OutputStream;[B)V
  :L8
  .line 1043
    nop
  .line 1044
    const-string v5, "checkGamePlaySwitchReply"
    invoke-static { v5 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v5
    const/4 v15, 6
    new-array v15, v15, [Ljava/lang/Object;
    aput-object v3, v15, v13
    const-string v3, ""
    if-nez v4, :L9
    move-object v13, v3
    goto :L10
  :L9
    move-object v13, v4
  :L10
    aput-object v13, v15, v7
    const-string v13, "s"
    aput-object v13, v15, v12
  .line 1045
    invoke-static { v6 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v12
    aput-object v12, v15, v11
    aput-object v8, v15, v10
    if-eqz v6, :L11
    goto :L12
  :L11
    const-string v3, "\u6b64\u73a9\u6cd5\u5c1a\u672a\u63a5\u5165\u672c\u5730\u7f51\u5173"
  :L12
    aput-object v3, v15, v14
  .line 1044
    invoke-static { v15 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v3
  .line 1043
    invoke-static { v2, v5, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
    invoke-direct { v0, v1, v14, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1046
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "gameplay switch="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v2, " enabled="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v6 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-static { v9, v1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 1047
    return v7
  :L13
  .line 1049
    const/4 v6, 7
    const-string v15, "buyMoney"
    const-string v16, "buyCardMallItem"
    const-string v17, "setSkinRequest"
    const-string v18, "queryItemDetail"
    const-string v19, "yuanbaoExchangeCrystal"
    const-string v20, "crystalExchangeSkinCoin"
    const-string v21, "buySkinRequest"
    filled-new-array/range { v15 .. v21 }, [Ljava/lang/String;
    move-result-object v8
    move v15, v13
  :L14
    const-string v11, " method="
    if-ge v15, v6, :L18
    aget-object v6, v8, v15
  .line 1051
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v12
    invoke-static { v3, v12 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v12
    if-nez v12, :L15
  .line 1049
    add-int/lit8 v15, v15, 1
    const/4 v6, 7
    const/4 v11, 3
    const/4 v12, 2
    goto :L14
  :L15
  .line 1052
    iget-object v3, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v3, v5, v6, v4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateCommerce(Ljava/lang/String;Ljava/lang/String;[B)Lcom/project7/localmanager/LocalCommerceEngine$Result;
    move-result-object v3
  .line 1053
    iget-object v4, v3, Lcom/project7/localmanager/LocalCommerceEngine$Result;->replies:Ljava/util/Map;
    invoke-interface { v4 }, Ljava/util/Map;->entrySet()Ljava/util/Set;
    move-result-object v4
    invoke-interface { v4 }, Ljava/util/Set;->iterator()Ljava/util/Iterator;
    move-result-object v4
  :L16
    invoke-interface { v4 }, Ljava/util/Iterator;->hasNext()Z
    move-result v8
    if-eqz v8, :L17
    invoke-interface { v4 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v8
    check-cast v8, Ljava/util/Map$Entry;
  .line 1054
    nop
  .line 1055
    invoke-interface { v8 }, Ljava/util/Map$Entry;->getKey()Ljava/lang/Object;
    move-result-object v10
    check-cast v10, Ljava/lang/String;
    invoke-static { v10 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v10
    invoke-interface { v8 }, Ljava/util/Map$Entry;->getValue()Ljava/lang/Object;
    move-result-object v8
    check-cast v8, [B
  .line 1054
    invoke-static { v2, v10, v8 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v8
    invoke-direct { v0, v1, v14, v8 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1056
    goto :L16
  :L17
  .line 1057
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "commerce RPC completed account="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v5 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v11 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v6 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v2, " success="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-object v2, v3, Lcom/project7/localmanager/LocalCommerceEngine$Result;->replies:Ljava/util/Map;
  .line 1058
    const-string v3, "showMessageStr"
    invoke-interface { v2, v3 }, Ljava/util/Map;->containsKey(Ljava/lang/Object;)Z
    move-result v2
    xor-int/2addr v2, v7
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
  .line 1057
    invoke-static { v9, v1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 1059
    return v7
  :L18
  .line 1061
    const-string v6, "syncServerTime"
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v6
    invoke-static { v3, v6 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v6
    if-eqz v6, :L19
  .line 1062
    nop
  .line 1063
    const-string v3, "onSyncServerTime"
    invoke-static { v3 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v3
  .line 1064
    invoke-static { }, Ljava/lang/System;->currentTimeMillis()J
    move-result-wide v4
    const-wide/16 v8, 1000
    div-long/2addr v4, v8
    long-to-int v4, v4
    const-string v5, "t"
    invoke-static { v5, v4 }, Lcom/project7/localmanager/BsonLite;->intDocument(Ljava/lang/String;I)[B
    move-result-object v4
  .line 1062
    invoke-static { v2, v3, v4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
    invoke-direct { v0, v1, v14, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1065
    return v7
  :L19
  .line 1067
    const/16 v6, 23
    const-string v19, "setPlayerBirthday"
    const-string v20, "setRoleIdRequest"
    const-string v21, "setDescribeRequest"
    const-string v22, "setBbsSkin"
    const-string v23, "read_cg"
    const-string v24, "changeName"
    const-string v25, "setHeadImage"
    const-string v26, "setImgState"
    const-string v27, "unlockCollectMark"
    const-string v28, "setHeroEmojiUsed"
    const-string v29, "requestEmojiRead"
    const-string v30, "addRecentEmoji"
    const-string v31, "setAssistHero"
    const-string v32, "requestNameCardChange"
    const-string v33, "setNameCardFirstSee"
    const-string v34, "setTitleShowList"
    const-string v35, "setBadgeShowList"
    const-string v36, "updateTitleNewState"
    const-string v37, "updateBadgeNewState"
    const-string v38, "updateTitleExchange"
    const-string v39, "requestUpdateCollectCover"
    const-string v40, "clearFirstGetFlag"
    const-string v41, "set_hero_shoucang"
    filled-new-array/range { v19 .. v41 }, [Ljava/lang/String;
    move-result-object v8
    move v12, v13
  :L20
    if-ge v12, v6, :L28
    aget-object v15, v8, v12
  .line 1072
    invoke-static { v15 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v6
    invoke-static { v3, v6 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v6
    if-nez v6, :L21
  .line 1067
    add-int/lit8 v12, v12, 1
    const/16 v6, 23
    goto :L20
  :L21
  .line 1073
    iget-object v3, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v3, v5, v15, v4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateProfile(Ljava/lang/String;Ljava/lang/String;[B)Lcom/project7/localmanager/LocalProfileEngine$Result;
    move-result-object v3
  .line 1075
    iget-object v6, v3, Lcom/project7/localmanager/LocalProfileEngine$Result;->callback:Ljava/lang/String;
    if-eqz v6, :L22
  .line 1076
    iget-object v6, v3, Lcom/project7/localmanager/LocalProfileEngine$Result;->callback:Ljava/lang/String;
  .line 1077
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v6
    iget-object v8, v3, Lcom/project7/localmanager/LocalProfileEngine$Result;->reply:[B
  .line 1076
    invoke-static { v2, v6, v8 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v6
    invoke-direct { v0, v1, v14, v6 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L22
  .line 1079
    iget-object v6, v3, Lcom/project7/localmanager/LocalProfileEngine$Result;->extras:Ljava/util/List;
    invoke-interface { v6 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v6
  :L23
    invoke-interface { v6 }, Ljava/util/Iterator;->hasNext()Z
    move-result v8
    if-eqz v8, :L24
    invoke-interface { v6 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v8
    check-cast v8, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v12, v8, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 1080
    invoke-static { v12 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v12
    iget-object v8, v8, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v2, v12, v8 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v8
  .line 1079
    invoke-direct { v0, v1, v14, v8 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L23
  :L24
  .line 1081
    const-string v6, "changeName"
    invoke-virtual { v6, v15 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    if-eqz v6, :L25
    iget-object v6, v3, Lcom/project7/localmanager/LocalProfileEngine$Result;->profile:[B
    if-eqz v6, :L25
  .line 1082
    nop
  .line 1083
    const-string v6, "updateCrystal"
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v6
    new-array v8, v10, [Ljava/lang/Object;
    const-string v10, "v"
    aput-object v10, v8, v13
    iget-object v10, v3, Lcom/project7/localmanager/LocalProfileEngine$Result;->profile:[B
    const-string v12, "crystal"
    invoke-static { v10, v12 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v10
    invoke-static { v10 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v10
    aput-object v10, v8, v7
    const-string v10, "bv"
    const/4 v12, 2
    aput-object v10, v8, v12
    iget-object v10, v3, Lcom/project7/localmanager/LocalProfileEngine$Result;->profile:[B
  .line 1084
    const-string v12, "bind_crystal"
    invoke-static { v10, v12 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v10
    invoke-static { v10 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v10
    const/4 v12, 3
    aput-object v10, v8, v12
  .line 1083
    invoke-static { v8 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v8
  .line 1082
    invoke-static { v2, v6, v8 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
    invoke-direct { v0, v1, v14, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L25
  .line 1086
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "profile RPC completed account="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v5 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v11 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v15 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v2, " parameters="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  .line 1087
    const-string v2, "setHeadImage"
    invoke-virtual { v2, v15 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v2
    if-eqz v2, :L26
    const-string v2, "<avatar metadata/image redacted>"
    goto :L27
  :L26
    invoke-static/range { p4 .. p4 }, Lcom/project7/localmanager/BsonLite;->debugDocument([B)Ljava/lang/String;
    move-result-object v2
  :L27
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v2, " role="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-object v2, v3, Lcom/project7/localmanager/LocalProfileEngine$Result;->profile:[B
  .line 1088
    const-string v3, "role"
    invoke-static { v2, v3 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v2
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
  .line 1086
    invoke-static { v9, v1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 1089
    return v7
  :L28
  .line 1091
    return v13
  :L29
  .line 1024
    return v7
  :L30
  .line 1016
    return v7
.end method

.method private handleCalendar(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/lang/String;)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 16
  .line 2359
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    sget-object v1, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    invoke-interface { v0, p3, p6, v1, p4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateEconomy(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalEconomyEngine$Result;
    move-result-object v0
  .line 2360
    if-eqz p5, :L0
    iget-object v1, p0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v1, p3, p4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->load(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v1
    invoke-static { p5, v1, v0 }, Lcom/project7/localmanager/DreamEconomyPolicy;->refreshCalendarEngine(Lcom/project7/localmanager/LocalEventEngine;[BLcom/project7/localmanager/LocalEconomyEngine$Result;)V
  :L0
  .line 2361
    iget-object v1, p0, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v1, p3, p4 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 2362
    iget-object p3, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->replies:Ljava/util/List;
    invoke-interface { p3 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object p3
  :L1
    invoke-interface { p3 }, Ljava/util/Iterator;->hasNext()Z
    move-result v1
    const/4 v2, 5
    if-eqz v1, :L2
    invoke-interface { p3 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v3, v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 2363
    invoke-static { v3 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v3
    iget-object v1, v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { p2, v3, v1 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
  .line 2362
    invoke-direct { p0, p1, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L1
  :L2
  .line 2364
    iget-boolean p3, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->accepted:Z
    if-nez p3, :L3
    const-string p3, "incDayWhenNoActionVal"
    invoke-virtual { p3, p6 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result p3
    if-eqz p3, :L3
  .line 2365
    iget-object v7, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->profile:[B
    move-object v3, p0
    move-object v4, p1
    move-object v5, p2
    move-object v6, p4
    move-object v8, p5
    invoke-direct/range { v3 .. v8 }, Lcom/project7/localmanager/LocalGatewayServer;->restorePendingPatrol(Ljava/io/OutputStream;[BLcom/project7/localmanager/LocalTutorialStore$Progress;[BLcom/project7/localmanager/LocalEventEngine;)V
  :L3
  .line 2366
    iget-boolean p3, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->accepted:Z
    if-eqz p3, :L4
    if-eqz p5, :L4
  .line 2367
    const-string p3, "pullEventsReply"
    invoke-static { p3 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object p3
  .line 2368
    invoke-virtual { p5 }, Lcom/project7/localmanager/LocalEventEngine;->availableEvents()Ljava/util/Set;
    move-result-object p4
    invoke-virtual { p5 }, Lcom/project7/localmanager/LocalEventEngine;->processingEvents()Ljava/util/Set;
    move-result-object p5
    invoke-static { p4, p5 }, Lcom/project7/localmanager/BsonLite;->eventListsDocument(Ljava/lang/Iterable;Ljava/lang/Iterable;)[B
    move-result-object p4
  .line 2367
    invoke-static { p2, p3, p4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object p2
  .line 2366
    invoke-direct { p0, p1, v2, p2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L4
  .line 2369
    new-instance p1, Ljava/lang/StringBuilder;
    invoke-direct { p1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string p2, "calendar method="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, p6 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string p2, " accepted="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-boolean p2, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->accepted:Z
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    const-string p2, " reason="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-object p2, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->reason:Ljava/lang/String;
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p1
    const-string p2, "Project7Gateway"
    invoke-static { p2, p1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 2370
    return-void
.end method

.method private handleClient(Ljava/net/Socket;Lcom/project7/localmanager/LocalGatewayServer$ClientSession;)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .catch Ljava/io/EOFException; { :L1 .. :L2 } :L125
  .catch Ljava/io/IOException; { :L4 .. :L5 } :L119
  .catch Ljava/io/IOException; { :L7 .. :L8 } :L20
  .registers 50
  .line 263
    move-object/from16 v12, p0
    move-object/from16 v13, p2
    new-instance v14, Ljava/io/BufferedInputStream;
    invoke-virtual/range { p1 .. p1 }, Ljava/net/Socket;->getInputStream()Ljava/io/InputStream;
    move-result-object v0
    invoke-direct { v14, v0 }, Ljava/io/BufferedInputStream;-><init>(Ljava/io/InputStream;)V
  .line 264
    new-instance v15, Ljava/io/BufferedOutputStream;
    invoke-virtual/range { p1 .. p1 }, Ljava/net/Socket;->getOutputStream()Ljava/io/OutputStream;
    move-result-object v0
    invoke-direct { v15, v0 }, Ljava/io/BufferedOutputStream;-><init>(Ljava/io/OutputStream;)V
  .line 265
    invoke-direct/range { p0 .. p0 }, Lcom/project7/localmanager/LocalGatewayServer;->objectId()[B
    move-result-object v11
  .line 266
    invoke-direct/range { p0 .. p0 }, Lcom/project7/localmanager/LocalGatewayServer;->objectId()[B
    move-result-object v10
  .line 267
    nop
  .line 268
    nop
  .line 269
    nop
  .line 270
    new-instance v16, Ljava/util/HashSet;
    invoke-direct/range { v16 .. v16 }, Ljava/util/HashSet;-><init>()V
  .line 271
    new-instance v17, Ljava/util/HashSet;
    invoke-direct/range { v17 .. v17 }, Ljava/util/HashSet;-><init>()V
  .line 272
    new-instance v18, Ljava/util/LinkedHashMap;
    invoke-direct/range { v18 .. v18 }, Ljava/util/LinkedHashMap;-><init>()V
  .line 273
    new-instance v19, Ljava/util/HashSet;
    invoke-direct/range { v19 .. v19 }, Ljava/util/HashSet;-><init>()V
  .line 274
    new-instance v9, Ljava/util/HashSet;
    invoke-direct { v9 }, Ljava/util/HashSet;-><init>()V
  .line 275
    nop
  .line 276
    nop
  .line 277
    nop
  .line 278
    nop
  .line 279
    nop
  .line 280
    nop
  .line 281
    nop
  .line 282
    const-string v8, "Project7Gateway"
    const-string v0, "client connected; awaiting local authentication"
    invoke-static { v8, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
    const-string v7, ""
    const/16 v20, 0
    move-object/from16 v21, v7
    move-object/from16 v3, v20
    move-object v4, v3
    move-object v5, v4
    move-object/from16 v22, v5
    move-object/from16 v23, v22
    move-object/from16 v24, v23
    move-object/from16 v25, v24
    const/4 v1, 0
    const/4 v2, 0
  :L0
  .line 284
    iget-boolean v0, v12, Lcom/project7/localmanager/LocalGatewayServer;->closed:Z
    if-nez v0, :L127
  :L1
  .line 287
    invoke-direct { v12, v14 }, Lcom/project7/localmanager/LocalGatewayServer;->readFrame(Ljava/io/InputStream;)Lcom/project7/localmanager/LocalGatewayServer$Frame;
    move-result-object v0
  :L2
  .line 292
    nop
  .line 293
    iget v6, v0, Lcom/project7/localmanager/LocalGatewayServer$Frame;->method:I
    move-object/from16 v28, v3
    const/4 v3, 2
    if-nez v6, :L3
  .line 294
    invoke-static { }, Lcom/project7/localmanager/ProtoLite;->connectReply()[B
    move-result-object v0
    invoke-direct { v12, v15, v3, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 295
    nop
  .line 298
    const-string v0, "ClientAccount"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
    sget-object v3, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    invoke-static { v0, v11, v3 }, Lcom/project7/localmanager/ProtoLite;->entityInfo([B[B[B)[B
    move-result-object v0
  .line 295
    const/4 v3, 3
    invoke-direct { v12, v15, v3, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    move-object/from16 v27, v7
    move-object/from16 v30, v9
    move-object/from16 v31, v11
    move-object/from16 v32, v14
    move-object/from16 v29, v23
    const/16 v26, 0
    move/from16 v23, v1
    move-object v9, v4
    move-object v11, v8
    move-object v14, v10
    move-object v10, v5
    move-object/from16 v46, v24
    move/from16 v24, v2
    move-object/from16 v2, v28
    move-object/from16 v28, v22
    move-object/from16 v22, v25
    move-object/from16 v25, v46
    goto/16 :L121
  :L3
  .line 300
    iget v6, v0, Lcom/project7/localmanager/LocalGatewayServer$Frame;->method:I
    const/4 v3, 1
    if-ne v6, v3, :L120
  :L4
  .line 303
    iget-object v0, v0, Lcom/project7/localmanager/LocalGatewayServer$Frame;->payload:[B
    invoke-static { v0 }, Lcom/project7/localmanager/ProtoLite;->parseEntityMessage([B)Lcom/project7/localmanager/ProtoLite$EntityMessage;
    move-result-object v0
  :L5
  .line 308
    nop
  .line 309
    iget-object v3, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v3, v11 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v3
    const-string v6, "mails"
    move-object/from16 v31, v7
    const-string v7, "mailbox"
    move-object/from16 v32, v14
    const-string v14, "ldd"
    move/from16 v33, v1
    const-string v1, "id"
    move/from16 v34, v2
    const-string v2, "fd"
    move-object/from16 v35, v4
    if-eqz v3, :L21
    iget-object v3, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    sget-object v4, Lcom/project7/localmanager/LocalGatewayServer;->LOGIN:[B
  .line 310
    invoke-static { v3, v4 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v3
    if-nez v3, :L6
    iget-object v3, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    sget-object v4, Lcom/project7/localmanager/LocalGatewayServer;->LOGIN_WITH_URS:[B
  .line 311
    invoke-static { v3, v4 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v3
    if-eqz v3, :L21
  :L6
  .line 312
    iget-object v3, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const-string v4, "name"
    invoke-static { v3, v4 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v3
  .line 313
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const-string v4, "psw"
    invoke-static { v0, v4 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v0
  :L7
  .line 316
    iget-object v4, v12, Lcom/project7/localmanager/LocalGatewayServer;->accountStore:Lcom/project7/localmanager/LocalAccountStore;
    invoke-virtual { v4, v3, v0 }, Lcom/project7/localmanager/LocalAccountStore;->authenticate(Ljava/lang/String;Ljava/lang/String;)Lcom/project7/localmanager/LocalAccountStore$Result;
    move-result-object v0
  :L8
  .line 321
    nop
  .line 322
    iget-boolean v3, v0, Lcom/project7/localmanager/LocalAccountStore$Result;->accepted:Z
    if-nez v3, :L9
  .line 323
    const-string v1, "\u8d26\u53f7\u6216\u5bc6\u7801\u9519\u8bef"
    invoke-direct { v12, v15, v11, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->sendLoginFailure(Ljava/io/OutputStream;[BLjava/lang/String;)V
  .line 324
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "local login rejected account="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-object v0, v0, Lcom/project7/localmanager/LocalAccountStore$Result;->username:Ljava/lang/String;
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v8, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;)I
  .line 326
    return-void
  :L9
  .line 328
    invoke-direct { v12, v13 }, Lcom/project7/localmanager/LocalGatewayServer;->claimSession(Lcom/project7/localmanager/LocalGatewayServer$ClientSession;)Z
    move-result v3
    if-nez v3, :L10
  .line 329
    const-string v0, "\u4e0a\u4e00\u6b21\u8fde\u63a5\u4ecd\u5728\u4fdd\u5b58\uff0c\u8bf7\u7a0d\u540e\u91cd\u65b0\u767b\u5f55"
    invoke-direct { v12, v15, v11, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->sendLoginFailure(Ljava/io/OutputStream;[BLjava/lang/String;)V
  .line 330
    return-void
  :L10
  .line 334
    move-object/from16 v4, p1
    const/4 v3, 0
    invoke-virtual { v4, v3 }, Ljava/net/Socket;->setSoTimeout(I)V
  .line 335
    iget-object v5, v0, Lcom/project7/localmanager/LocalAccountStore$Result;->username:Ljava/lang/String;
  .line 336
    iget-object v3, v12, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v3, v5 }, Lcom/project7/localmanager/LocalTutorialStore;->load(Ljava/lang/String;)Lcom/project7/localmanager/LocalTutorialStore$Progress;
    move-result-object v3
  .line 337
    iget-object v4, v12, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v4, v5, v3 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->load(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v4
  .line 338
    invoke-static { v4 }, Lcom/project7/localmanager/LocalHomeDailyEngine;->payload([B)[B
    move-result-object v21
  .line 339
    invoke-static { v4 }, Lcom/project7/localmanager/LocalDrawDailyEngine;->payload([B)[B
    move-result-object v22
  .line 340
    move-object/from16 v42, v11
    sget-object v11, Ljava/lang/Boolean;->TRUE:Ljava/lang/Boolean;
    invoke-static { v4, v14 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v14
    invoke-static { v14, v2 }, Lcom/project7/localmanager/BsonLite;->boolValue([BLjava/lang/String;)Ljava/lang/Boolean;
    move-result-object v2
    invoke-virtual { v11, v2 }, Ljava/lang/Boolean;->equals(Ljava/lang/Object;)Z
    move-result v2
  .line 341
    invoke-static { v4 }, Lcom/project7/localmanager/LocalAchievementFreeDraw;->used([B)Z
    move-result v11
  .line 342
    invoke-static { v4 }, Lcom/project7/localmanager/LocalGuildShopEngine;->dayAnchor([B)Ljava/lang/String;
    move-result-object v14
  .line 343
    invoke-static { v4 }, Lcom/project7/localmanager/LocalHomeWishDailyEngine;->generation([B)Ljava/lang/String;
    move-result-object v23
  .line 344
    nop
  .line 345
    invoke-static { v4, v7 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v7
  .line 344
    invoke-static { v7, v6 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v6
    invoke-static { v6 }, Lcom/project7/localmanager/LocalResourceEngine;->array([B)Ljava/util/List;
    move-result-object v6
    invoke-interface { v6 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v6
  :L11
    invoke-interface { v6 }, Ljava/util/Iterator;->hasNext()Z
    move-result v7
    if-eqz v7, :L12
    invoke-interface { v6 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v7
    check-cast v7, [B
  .line 346
    invoke-static { v7, v1 }, Lcom/project7/localmanager/BsonLite;->uuidValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v7
    invoke-interface { v9, v7 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
  .line 347
    goto :L11
  :L12
  .line 348
    invoke-static { v5 }, Lcom/project7/localmanager/LocalGatewayServer;->starterHeroForUsername(Ljava/lang/String;)I
    move-result v1
  .line 349
    new-instance v6, Lcom/project7/localmanager/LocalEventEngine;
    iget-object v7, v12, Lcom/project7/localmanager/LocalGatewayServer;->eventCatalog:Lcom/project7/localmanager/LocalEventCatalog;
    move/from16 v24, v2
    iget-object v2, v12, Lcom/project7/localmanager/LocalGatewayServer;->newbeeCatalog:Lcom/project7/localmanager/LocalNewbeeCatalog;
  .line 353
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->starterEventForHero(I)I
    move-result v40
    move-object/from16 v36, v6
    move-object/from16 v37, v7
    move-object/from16 v38, v2
    move-object/from16 v39, v3
    move-object/from16 v41, v4
    invoke-direct/range { v36 .. v41 }, Lcom/project7/localmanager/LocalEventEngine;-><init>(Lcom/project7/localmanager/LocalEventCatalog;Lcom/project7/localmanager/LocalNewbeeCatalog;Lcom/project7/localmanager/LocalTutorialStore$Progress;I[B)V
  .line 356
    iget-object v1, v12, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v1, v5, v3 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 357
    invoke-static { v4, v3 }, Lcom/project7/localmanager/BsonLite;->withTutorialProgress([BLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v1
  .line 359
    invoke-static { v5 }, Lcom/project7/localmanager/LocalAccountStore;->isTemplateAccount(Ljava/lang/String;)Z
    move-result v2
    if-nez v2, :L13
  .line 360
    invoke-static { v1, v3 }, Lcom/project7/localmanager/BsonLite;->withLocalCityState([BLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v1
  :L13
  .line 362
    nop
  .line 365
    const-string v2, "ClientAvatar"
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
    invoke-static { v2, v10, v1 }, Lcom/project7/localmanager/ProtoLite;->entityInfo([B[B[B)[B
    move-result-object v1
  .line 362
    const/4 v2, 3
    invoke-direct { v12, v15, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 367
    nop
  .line 370
    const-string v1, "become_player"
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    sget-object v2, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    invoke-static { v10, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
  .line 367
    const/4 v2, 5
    invoke-direct { v12, v15, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 372
    invoke-direct { v12, v15, v10 }, Lcom/project7/localmanager/LocalGatewayServer;->syncClientCompatibility(Ljava/io/OutputStream;[B)V
  .line 373
    invoke-virtual { v12, v15, v10, v4 }, Lcom/project7/localmanager/LocalGatewayServer;->syncFurnitureLogin(Ljava/io/OutputStream;[B[B)V
  .line 374
    const-string v1, "syncAllNote"
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    const/4 v2, 2
    new-array v2, v2, [Ljava/lang/Object;
    const-string v7, "nd"
    const/16 v25, 0
    aput-object v7, v2, v25
  .line 375
    const-string v7, "np"
    invoke-static { v4, v7 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v7
    const/16 v25, 1
    aput-object v7, v2, v25
    invoke-static { v2 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v2
  .line 374
    invoke-static { v10, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
    const/4 v2, 5
    invoke-direct { v12, v15, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 376
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "diary login account="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v5 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v2, " "
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  .line 377
    invoke-static { v4, v3 }, Lcom/project7/localmanager/LocalDiaryEngine;->diagnostic([BLcom/project7/localmanager/LocalTutorialStore$Progress;)Ljava/lang/String;
    move-result-object v2
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
  .line 376
    invoke-static { v8, v1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 378
    invoke-static { v4 }, Lcom/project7/localmanager/LocalImageAvatar;->cache([B)Ljava/util/List;
    move-result-object v1
    invoke-interface { v1 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v1
  :L14
    invoke-interface { v1 }, Ljava/util/Iterator;->hasNext()Z
    move-result v2
    if-eqz v2, :L15
    invoke-interface { v1 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Lcom/project7/localmanager/LocalResourceEngine$Reply;
  .line 379
    iget-object v4, v2, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    invoke-static { v4 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v4
    iget-object v2, v2, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v10, v4, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
    const/4 v4, 5
    invoke-direct { v12, v15, v4, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L14
  :L15
  .line 380
    iget-object v1, v3, Lcom/project7/localmanager/LocalTutorialStore$Progress;->weekCommit:Ljava/lang/String;
  .line 381
    iget-object v2, v12, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    sget-object v4, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    const-string v7, "q7ResumeWeekResult"
    invoke-interface { v2, v5, v7, v4, v3 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v2
  .line 383
    iget-object v4, v2, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v4 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v4
  :L16
    invoke-interface { v4 }, Ljava/util/Iterator;->hasNext()Z
    move-result v7
    if-eqz v7, :L17
    invoke-interface { v4 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v7
    check-cast v7, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    move-object/from16 v25, v1
    iget-object v1, v7, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 384
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    iget-object v7, v7, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v10, v1, v7 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
  .line 383
    const/4 v7, 5
    invoke-direct { v12, v15, v7, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    move-object/from16 v1, v25
    goto :L16
  :L17
  .line 385
    move-object/from16 v25, v1
    invoke-direct { v12, v5, v3, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->acknowledgeCgNotices(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalResourceEngine$Result;)V
  .line 386
    iput-object v5, v13, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;->username:Ljava/lang/String;
  .line 387
    iget-object v1, v12, Lcom/project7/localmanager/LocalGatewayServer;->listener:Lcom/project7/localmanager/LocalGatewayServer$StatusListener;
    new-instance v2, Ljava/lang/StringBuilder;
    invoke-direct { v2 }, Ljava/lang/StringBuilder;-><init>()V
  .line 389
    iget-boolean v0, v0, Lcom/project7/localmanager/LocalAccountStore$Result;->registered:Z
    if-eqz v0, :L18
    const-string v0, "\u5df2\u6ce8\u518c\u5e76\u767b\u5f55\uff1a"
    goto :L19
  :L18
    const-string v0, "\u672c\u5730\u8d26\u53f7\u5df2\u767b\u5f55\uff1a"
  :L19
    invoke-virtual { v2, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v2, v5 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v0, "\n\u4e1a\u52a1 RPC \u7b49\u5f85\u5b9e\u73b0"
    invoke-virtual { v2, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v2 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
  .line 387
    const/4 v2, 1
    invoke-interface { v1, v2, v0 }, Lcom/project7/localmanager/LocalGatewayServer$StatusListener;->onStatus(ZLjava/lang/String;)V
  .line 392
    move-object v4, v3
    move-object v3, v6
    move-object/from16 v30, v9
    move v2, v11
    move/from16 v1, v24
    move-object/from16 v27, v31
    move-object/from16 v31, v42
    const/16 v26, 0
    move-object v11, v8
    move-object/from16 v24, v23
    move-object/from16 v23, v14
    move-object v14, v10
    move-object/from16 v46, v25
    move-object/from16 v25, v21
    move-object/from16 v21, v46
    goto/16 :L118
  :L20
  .line 317
    move-exception v0
    move-object/from16 v42, v11
  .line 318
    invoke-virtual { v0 }, Ljava/io/IOException;->getMessage()Ljava/lang/String;
    move-result-object v1
    move-object/from16 v11, v42
    invoke-direct { v12, v15, v11, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->sendLoginFailure(Ljava/io/OutputStream;[BLjava/lang/String;)V
  .line 319
    const-string v1, "local login rejected"
    invoke-static { v8, v1, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
  .line 320
    return-void
  :L21
  .line 392
    iget-object v3, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v3, v10 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v3
    const-string v4, "p"
    move-object/from16 v42, v11
    const-string v11, "t"
    if-eqz v3, :L48
    iget-object v3, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    sget-object v13, Lcom/project7/localmanager/LocalGatewayServer;->HEARTBEAT_SERVER:[B
  .line 393
    invoke-static { v3, v13 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v3
    if-eqz v3, :L47
  .line 394
    nop
  .line 397
    const-string v0, "on_heartbeat"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
    sget-object v3, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    invoke-static { v10, v0, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
  .line 394
    const/4 v3, 5
    invoke-direct { v12, v15, v3, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 399
    const-string v0, "heartbeat acknowledged"
    invoke-static { v8, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 400
    if-eqz v5, :L46
  .line 401
    iget-object v0, v12, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    move-object/from16 v13, v35
    invoke-interface { v0, v5, v13 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v0
  .line 402
    invoke-static { v0 }, Lcom/project7/localmanager/LocalDrawDailyEngine;->payload([B)[B
    move-result-object v3
  .line 403
    move-object/from16 v35, v5
    invoke-static { v0 }, Lcom/project7/localmanager/LocalAchievementFreeDraw;->used([B)Z
    move-result v5
  .line 404
    move-object/from16 v36, v8
    move/from16 v8, v34
    if-eq v5, v8, :L22
  .line 405
    nop
  .line 406
    const-string v8, "replyUseNewAchievementChouka"
    invoke-static { v8 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v8
    move-object/from16 v37, v9
    move-object/from16 v34, v13
    const/4 v13, 2
    new-array v9, v13, [Ljava/lang/Object;
    const-string v13, "ic"
    const/16 v26, 0
    aput-object v13, v9, v26
    invoke-static { v5 }, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
    move-result-object v13
    const/16 v27, 1
    aput-object v13, v9, v27
    invoke-static { v9 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v9
  .line 405
    invoke-static { v10, v8, v9 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v8
    const/4 v9, 5
    invoke-direct { v12, v15, v9, v8 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 407
    goto :L23
  :L22
  .line 404
    move-object/from16 v37, v9
    move-object/from16 v34, v13
    move v5, v8
  :L23
  .line 409
    sget-object v8, Ljava/lang/Boolean;->TRUE:Ljava/lang/Boolean;
    invoke-static { v0, v14 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v9
    invoke-static { v9, v2 }, Lcom/project7/localmanager/BsonLite;->boolValue([BLjava/lang/String;)Ljava/lang/Boolean;
    move-result-object v9
    invoke-virtual { v8, v9 }, Ljava/lang/Boolean;->equals(Ljava/lang/Object;)Z
    move-result v8
  .line 410
    move/from16 v9, v33
    if-eq v8, v9, :L24
  .line 411
    nop
  .line 412
    const-string v9, "updateFriendDraw"
    invoke-static { v9 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v9
    const/4 v13, 2
    new-array v14, v13, [Ljava/lang/Object;
    const/4 v13, 0
    aput-object v2, v14, v13
    invoke-static { v8 }, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
    move-result-object v2
    const/4 v13, 1
    aput-object v2, v14, v13
    invoke-static { v14 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v2
  .line 411
    invoke-static { v10, v9, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
    const/4 v9, 5
    invoke-direct { v12, v15, v9, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 413
    goto :L25
  :L24
  .line 410
    move v8, v9
  :L25
  .line 415
    move-object/from16 v13, v22
    invoke-static { v3, v13 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v2
    if-nez v2, :L26
  .line 416
    nop
  .line 417
    const-string v2, "updateCurTimesDay"
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
  .line 416
    invoke-static { v10, v2, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
    const/4 v9, 5
    invoke-direct { v12, v15, v9, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 418
    move-object/from16 v22, v3
    goto :L27
  :L26
  .line 415
    move-object/from16 v22, v13
  :L27
  .line 420
    invoke-static { v0 }, Lcom/project7/localmanager/LocalHomeWishDailyEngine;->generation([B)Ljava/lang/String;
    move-result-object v2
  .line 421
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGuildShopEngine;->dayAnchor([B)Ljava/lang/String;
    move-result-object v3
  .line 422
    if-eqz v3, :L30
    move-object/from16 v14, v23
    invoke-virtual { v3, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v9
    if-nez v9, :L31
  .line 423
    new-instance v9, Lcom/project7/localmanager/LocalResourceEngine$Result;
    invoke-direct { v9, v0 }, Lcom/project7/localmanager/LocalResourceEngine$Result;-><init>([B)V
  .line 424
    invoke-static { v9 }, Lcom/project7/localmanager/LocalGuildShopEngine;->syncDaily(Lcom/project7/localmanager/LocalResourceEngine$Result;)V
  .line 425
    iget-object v9, v9, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v9 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v9
  :L28
    invoke-interface { v9 }, Ljava/util/Iterator;->hasNext()Z
    move-result v13
    if-eqz v13, :L29
    invoke-interface { v9 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v13
    check-cast v13, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v14, v13, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 426
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v14
    iget-object v13, v13, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v10, v14, v13 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v13
  .line 425
    const/4 v14, 5
    invoke-direct { v12, v15, v14, v13 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L28
  :L29
  .line 427
    move-object/from16 v23, v3
    goto :L32
  :L30
  .line 422
    move-object/from16 v14, v23
  :L31
  .line 429
    move-object/from16 v23, v14
  :L32
    if-eqz v2, :L35
    invoke-virtual { v2 }, Ljava/lang/String;->isEmpty()Z
    move-result v3
    if-nez v3, :L35
    move-object/from16 v3, v24
    invoke-virtual { v2, v3 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v9
    if-nez v9, :L36
  .line 430
    new-instance v3, Lcom/project7/localmanager/LocalResourceEngine$Result;
    invoke-direct { v3, v0 }, Lcom/project7/localmanager/LocalResourceEngine$Result;-><init>([B)V
  .line 431
    sget-object v9, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    invoke-static { v3, v9 }, Lcom/project7/localmanager/LocalHomeWishDailyEngine;->sync(Lcom/project7/localmanager/LocalResourceEngine$Result;[B)V
  .line 432
    iget-object v3, v3, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v3 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v3
  :L33
    invoke-interface { v3 }, Ljava/util/Iterator;->hasNext()Z
    move-result v9
    if-eqz v9, :L34
    invoke-interface { v3 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v9
    check-cast v9, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v13, v9, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 433
    invoke-static { v13 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v13
    iget-object v9, v9, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v10, v13, v9 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v9
  .line 432
    const/4 v13, 5
    invoke-direct { v12, v15, v13, v9 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L33
  :L34
  .line 434
    move-object/from16 v24, v2
    goto :L37
  :L35
  .line 429
    move-object/from16 v3, v24
  :L36
  .line 436
    move-object/from16 v24, v3
  :L37
    invoke-static { v0 }, Lcom/project7/localmanager/LocalHomeDailyEngine;->payload([B)[B
    move-result-object v2
  .line 437
    if-eqz v2, :L38
    move-object/from16 v3, v25
    invoke-static { v2, v3 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v9
    if-nez v9, :L39
  .line 438
    nop
  .line 439
    const-string v3, "syncHeroXinqing"
    invoke-static { v3 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v3
  .line 438
    invoke-static { v10, v3, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v3
    const/4 v9, 5
    invoke-direct { v12, v15, v9, v3 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 440
    move-object/from16 v25, v2
    goto :L40
  :L38
  .line 437
    move-object/from16 v3, v25
  :L39
  .line 442
    move-object/from16 v25, v3
  :L40
    const-string v2, "city"
    invoke-static { v0, v2 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v2
  .line 443
    const-string v3, "syncJingshenliPower"
    invoke-static { v3 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v3
    const/4 v9, 6
    new-array v9, v9, [Ljava/lang/Object;
    const/4 v13, 0
    aput-object v4, v9, v13
  .line 444
    const-string v4, "jpv"
    invoke-static { v2, v4 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v4
    invoke-static { v4 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v4
    const/4 v13, 1
    aput-object v4, v9, v13
    const/4 v4, 2
    aput-object v11, v9, v4
  .line 445
    const-string v4, "jpvt"
    invoke-static { v2, v4 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v4
    invoke-static { v4 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v4
    const/4 v11, 3
    aput-object v4, v9, v11
    const/4 v4, 4
    const-string v11, "cjsla"
    aput-object v11, v9, v4
  .line 446
    invoke-static { v2, v11 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v2
    invoke-static { v2 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v2
    const/4 v4, 5
    aput-object v2, v9, v4
  .line 444
    invoke-static { v9 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v2
  .line 443
    invoke-static { v10, v3, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
    invoke-direct { v12, v15, v4, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 447
    nop
  .line 448
    invoke-static { v0, v7 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v0
  .line 447
    invoke-static { v0, v6 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v0
    invoke-static { v0 }, Lcom/project7/localmanager/LocalResourceEngine;->array([B)Ljava/util/List;
    move-result-object v0
    invoke-interface { v0 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v0
  :L41
    invoke-interface { v0 }, Ljava/util/Iterator;->hasNext()Z
    move-result v2
    if-eqz v2, :L45
    invoke-interface { v0 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v2
    check-cast v2, [B
  .line 449
    invoke-static { v2, v1 }, Lcom/project7/localmanager/BsonLite;->uuidValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v3
  .line 450
    if-eqz v3, :L42
    move-object/from16 v7, v37
    invoke-interface { v7, v3 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
    move-result v3
    if-eqz v3, :L43
  .line 452
    const-string v3, "addMailRep"
    invoke-static { v3 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v3
    const/4 v4, 2
    new-array v6, v4, [Ljava/lang/Object;
    const-string v9, "m"
    const/16 v26, 0
    aput-object v9, v6, v26
    const/16 v27, 1
    aput-object v2, v6, v27
    invoke-static { v6 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v2
  .line 451
    invoke-static { v10, v3, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
  .line 450
    const/4 v6, 5
    invoke-direct { v12, v15, v6, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L44
  :L42
    move-object/from16 v7, v37
  :L43
    const/4 v4, 2
    const/4 v6, 5
    const/16 v26, 0
    const/16 v27, 1
  :L44
  .line 453
    move-object/from16 v37, v7
    goto :L41
  :L45
  .line 454
    move-object/from16 v7, v37
    const/16 v26, 0
    move v2, v5
    move-object/from16 v30, v7
    move v1, v8
    move-object v14, v10
    move-object/from16 v3, v28
    move-object/from16 v27, v31
    move-object/from16 v4, v34
    move-object/from16 v5, v35
    move-object/from16 v11, v36
    move-object/from16 v31, v42
    goto/16 :L118
  :L46
  .line 400
    move-object/from16 v36, v8
    move-object v7, v9
    move-object/from16 v13, v22
    move-object/from16 v14, v23
    move-object/from16 v3, v24
    move-object/from16 v22, v25
    move/from16 v9, v33
    move/from16 v8, v34
    move-object/from16 v34, v35
    const/16 v26, 0
    move-object/from16 v35, v5
    move-object/from16 v25, v3
    move-object/from16 v30, v7
    move/from16 v24, v8
    move/from16 v23, v9
    move-object/from16 v29, v14
    move-object/from16 v2, v28
    move-object/from16 v27, v31
    move-object/from16 v9, v34
    move-object/from16 v11, v36
    move-object/from16 v31, v42
    move-object v14, v10
    move-object/from16 v28, v13
    move-object/from16 v10, v35
    goto/16 :L117
  :L47
  .line 393
    move-object/from16 v36, v8
    move-object v7, v9
    move-object/from16 v13, v22
    move-object/from16 v14, v23
    move-object/from16 v3, v24
    move-object/from16 v22, v25
    move/from16 v9, v33
    move/from16 v8, v34
    move-object/from16 v34, v35
    const/4 v6, 5
    const/16 v26, 0
    const/16 v27, 1
    move-object/from16 v35, v5
    goto :L49
  :L48
  .line 392
    move-object/from16 v36, v8
    move-object v7, v9
    move-object/from16 v13, v22
    move-object/from16 v14, v23
    move-object/from16 v3, v24
    move-object/from16 v22, v25
    move/from16 v9, v33
    move/from16 v8, v34
    move-object/from16 v34, v35
    const/4 v6, 5
    const/16 v26, 0
    const/16 v27, 1
    move-object/from16 v35, v5
  :L49
  .line 455
    iget-object v2, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v2, v10 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v2
    if-eqz v2, :L51
    iget-object v2, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    sget-object v5, Lcom/project7/localmanager/LocalGatewayServer;->RELIABLE_RPC_CALL:[B
  .line 456
    invoke-static { v2, v5 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v2
    if-eqz v2, :L50
  .line 457
    iget-object v4, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    move/from16 v23, v9
    move-object/from16 v1, p0
    move/from16 v24, v8
    move-object v2, v15
    move-object/from16 v25, v3
    move-object/from16 v11, v28
    move-object v3, v10
    move-object/from16 v9, v34
    move-object/from16 v8, v35
    move-object v5, v8
    move-object v6, v9
    move-object/from16 v27, v7
    move-object/from16 v28, v13
    move-object/from16 v13, v31
    move-object v7, v11
    move-object/from16 v29, v14
    move-object/from16 v14, v36
    move-object/from16 v8, v16
    move-object/from16 v30, v27
    move-object/from16 v9, v17
    move-object v14, v10
    move-object/from16 v10, v18
    move-object/from16 v33, v11
    move-object/from16 v31, v42
    move-object/from16 v11, v19
    invoke-direct/range { v1 .. v11 }, Lcom/project7/localmanager/LocalGatewayServer;->dispatchReliableRpc(Ljava/io/OutputStream;[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;Ljava/util/Set;Ljava/util/Map;Ljava/util/Set;)V
    move-object/from16 v27, v13
    move-object/from16 v2, v33
    move-object/from16 v9, v34
    move-object/from16 v10, v35
    move-object/from16 v11, v36
    goto/16 :L117
  :L50
  .line 456
    move-object/from16 v25, v3
    move-object/from16 v30, v7
    move/from16 v24, v8
    move/from16 v23, v9
    move-object/from16 v29, v14
    move-object/from16 v33, v28
    move-object v14, v10
    move-object/from16 v28, v13
    move-object/from16 v13, v31
    move-object/from16 v31, v42
    goto :L52
  :L51
  .line 455
    move-object/from16 v25, v3
    move-object/from16 v30, v7
    move/from16 v24, v8
    move/from16 v23, v9
    move-object/from16 v29, v14
    move-object/from16 v33, v28
    move-object v14, v10
    move-object/from16 v28, v13
    move-object/from16 v13, v31
    move-object/from16 v31, v42
  :L52
  .line 469
    iget-object v2, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v2, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v2
    if-eqz v2, :L53
    iget-object v5, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    iget-object v7, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
  .line 470
    move-object v10, v1
    move-object/from16 v1, p0
    move-object v2, v15
    move-object v3, v14
    move-object v9, v4
    move v8, v6
    move-object v4, v5
    move-object v5, v7
    move/from16 v7, v27
    move-object/from16 v6, v35
    move-object/from16 v27, v11
    move v11, v7
    move-object/from16 v7, v34
    move-object/from16 v8, v33
    move-object/from16 v43, v9
    move-object/from16 v9, v16
    move-object/from16 v44, v10
    move-object/from16 v10, v17
    invoke-direct/range { v1 .. v10 }, Lcom/project7/localmanager/LocalGatewayServer;->handleSuppressionRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;Ljava/util/Set;)Z
    move-result v1
    if-eqz v1, :L54
  .line 472
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const-string v1, "battleYazhiAsk"
    invoke-direct { v12, v15, v14, v0, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
    move-object/from16 v27, v13
    move-object/from16 v2, v33
    move-object/from16 v9, v34
    move-object/from16 v10, v35
    move-object/from16 v11, v36
    goto/16 :L117
  :L53
  .line 469
    move-object/from16 v44, v1
    move-object/from16 v43, v4
    move/from16 v46, v27
    move-object/from16 v27, v11
    move/from16 v11, v46
  :L54
  .line 473
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L55
    iget-object v4, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    iget-object v5, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
  .line 474
    move-object/from16 v1, p0
    move-object v2, v15
    move-object v3, v14
    move-object/from16 v6, v35
    move-object/from16 v7, v34
    invoke-direct/range { v1 .. v7 }, Lcom/project7/localmanager/LocalGatewayServer;->handleDailyRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)Z
    move-result v1
    if-eqz v1, :L55
    move-object/from16 v27, v13
    move-object/from16 v2, v33
    move-object/from16 v9, v34
    move-object/from16 v10, v35
    move-object/from16 v11, v36
    goto/16 :L117
  :L55
  .line 476
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L56
    iget-object v4, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    iget-object v5, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
  .line 477
    move-object/from16 v1, p0
    move-object v2, v15
    move-object v3, v14
    move-object/from16 v6, v35
    move-object/from16 v7, v34
    move-object/from16 v8, v33
    invoke-direct/range { v1 .. v8 }, Lcom/project7/localmanager/LocalGatewayServer;->handleSpecialItemRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)Z
    move-result v1
    if-eqz v1, :L56
  .line 478
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const-string v1, "specialItemRpc"
    invoke-direct { v12, v15, v14, v0, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
    move-object/from16 v27, v13
    move-object/from16 v2, v33
    move-object/from16 v9, v34
    move-object/from16 v10, v35
    move-object/from16 v11, v36
    goto/16 :L117
  :L56
  .line 479
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L57
    iget-object v4, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    iget-object v5, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
  .line 480
    move-object/from16 v1, p0
    move-object v2, v15
    move-object v3, v14
    move-object/from16 v6, v35
    move-object/from16 v7, v34
    move-object/from16 v8, v33
    invoke-direct/range { v1 .. v8 }, Lcom/project7/localmanager/LocalGatewayServer;->handleWeekRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)Z
    move-result v1
    if-eqz v1, :L57
  .line 481
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const-string v1, "weekLifecycleRpc"
    invoke-direct { v12, v15, v14, v0, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
    move-object/from16 v27, v13
    move-object/from16 v2, v33
    move-object/from16 v9, v34
    move-object/from16 v10, v35
    move-object/from16 v11, v36
    goto/16 :L117
  :L57
  .line 482
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L58
    iget-object v4, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    iget-object v5, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
  .line 483
    move-object/from16 v1, p0
    move-object v2, v15
    move-object v3, v14
    move-object/from16 v6, v35
    move-object/from16 v7, v34
    invoke-direct/range { v1 .. v7 }, Lcom/project7/localmanager/LocalGatewayServer;->handleHomeRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)Z
    move-result v1
    if-eqz v1, :L58
    move-object/from16 v27, v13
    move-object/from16 v2, v33
    move-object/from16 v9, v34
    move-object/from16 v10, v35
    move-object/from16 v11, v36
    goto/16 :L117
  :L58
  .line 485
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L59
    iget-object v4, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    iget-object v5, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
  .line 486
    move-object/from16 v1, p0
    move-object v2, v15
    move-object v3, v14
    move-object/from16 v6, v35
    move-object/from16 v7, v34
    move-object/from16 v8, v33
    invoke-direct/range { v1 .. v8 }, Lcom/project7/localmanager/LocalGatewayServer;->handleServiceRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)Z
    move-result v1
    if-eqz v1, :L59
  .line 487
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const-string v1, "cityServiceRpc"
    invoke-direct { v12, v15, v14, v0, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
    move-object/from16 v27, v13
    move-object/from16 v2, v33
    move-object/from16 v9, v34
    move-object/from16 v10, v35
    move-object/from16 v11, v36
    goto/16 :L117
  :L59
  .line 488
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L61
    iget-object v4, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    iget-object v5, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
  .line 489
    move-object/from16 v1, p0
    move-object v2, v15
    move-object v3, v14
    move-object/from16 v6, v35
    invoke-direct/range { v1 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->handleResourceRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;)Z
    move-result v1
    if-eqz v1, :L60
  .line 491
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const-string v2, "resourceRpc"
    invoke-direct { v12, v15, v14, v1, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
  .line 492
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    move-object/from16 v8, v33
    move-object/from16 v9, v34
    move-object/from16 v10, v35
    invoke-direct { v12, v0, v10, v9, v8 }, Lcom/project7/localmanager/LocalGatewayServer;->refreshResourceProfile([BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
    move-object v2, v8
    move-object/from16 v27, v13
    move-object/from16 v11, v36
    goto/16 :L117
  :L60
  .line 489
    move-object/from16 v8, v33
    move-object/from16 v9, v34
    move-object/from16 v10, v35
    goto :L62
  :L61
  .line 488
    move-object/from16 v8, v33
    move-object/from16 v9, v34
    move-object/from16 v10, v35
  :L62
  .line 493
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L63
    iget-object v4, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    iget-object v5, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
  .line 494
    move-object/from16 v1, p0
    move-object v2, v15
    move-object v3, v14
    move-object v6, v10
    invoke-direct/range { v1 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->handleBasicRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;)Z
    move-result v1
    if-eqz v1, :L63
  .line 496
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const-string v1, "basicProfileRpc"
    invoke-direct { v12, v15, v14, v0, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
    move-object v2, v8
    move-object/from16 v27, v13
    move-object/from16 v11, v36
    goto/16 :L117
  :L63
  .line 497
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L64
    iget-object v4, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    iget-object v5, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const/16 v33, 0
  .line 498
    move-object/from16 v1, p0
    move-object v2, v15
    move-object v3, v14
    move-object v6, v10
    move-object v7, v9
    move-object/from16 v34, v8
    move-object/from16 v35, v9
    move-object/from16 v9, v33
    invoke-direct/range { v1 .. v9 }, Lcom/project7/localmanager/LocalGatewayServer;->handleConstructionRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/lang/Integer;)Z
    move-result v1
    if-eqz v1, :L65
  .line 500
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const-string v1, "constructionRpc"
    invoke-direct { v12, v15, v14, v0, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
    move-object/from16 v27, v13
    move-object/from16 v2, v34
    move-object/from16 v9, v35
    move-object/from16 v11, v36
    goto/16 :L117
  :L64
  .line 497
    move-object/from16 v34, v8
    move-object/from16 v35, v9
  :L65
  .line 501
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L66
    iget-object v4, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    iget-object v5, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
  .line 502
    move-object/from16 v1, p0
    move-object v2, v15
    move-object v3, v14
    move-object v6, v10
    move-object/from16 v7, v35
    move-object/from16 v8, v34
    invoke-direct/range { v1 .. v8 }, Lcom/project7/localmanager/LocalGatewayServer;->handleDayRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)Z
    move-result v1
    if-eqz v1, :L66
  .line 504
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const-string v1, "dayRpc"
    invoke-direct { v12, v15, v14, v0, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
    move-object/from16 v27, v13
    move-object/from16 v2, v34
    move-object/from16 v9, v35
    move-object/from16 v11, v36
    goto/16 :L117
  :L66
  .line 505
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L70
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
  .line 506
    const-string v2, "incDayWhenNoActionVal"
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v3
    invoke-static { v1, v3 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    const-string v3, "clearCurDailySettlement"
    if-nez v1, :L67
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
  .line 507
    invoke-static { v3 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v4
    invoke-static { v1, v4 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L70
  :L67
  .line 508
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v4
    invoke-static { v1, v4 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L68
  .line 509
    move-object v8, v2
    goto :L69
  :L68
    move-object v8, v3
  :L69
  .line 510
    move-object/from16 v1, p0
    move-object v2, v15
    move-object v3, v14
    move-object v4, v10
    move-object/from16 v5, v35
    move-object/from16 v6, v34
    move-object v7, v8
    invoke-direct/range { v1 .. v7 }, Lcom/project7/localmanager/LocalGatewayServer;->handleCalendar(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/lang/String;)V
  .line 511
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    invoke-direct { v12, v15, v14, v0, v8 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
  .line 512
    move-object/from16 v27, v13
    move-object/from16 v2, v34
    move-object/from16 v9, v35
    move-object/from16 v11, v36
    goto/16 :L117
  :L70
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L71
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
  .line 513
    const-string v7, "zhaiRequest"
    invoke-static { v7 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v2
    invoke-static { v1, v2 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L71
  .line 514
    move-object/from16 v1, p0
    move-object v2, v15
    move-object v3, v14
    move-object v4, v10
    move-object/from16 v5, v35
    move-object/from16 v6, v34
    invoke-direct/range { v1 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->handleRest(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 515
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    invoke-direct { v12, v15, v14, v0, v7 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
    move-object/from16 v27, v13
    move-object/from16 v2, v34
    move-object/from16 v9, v35
    move-object/from16 v11, v36
    goto/16 :L117
  :L71
  .line 516
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L72
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    sget-object v2, Lcom/project7/localmanager/LocalGatewayServer;->REQUEST_TRIGGER_DA_XUAN_WO:[B
  .line 517
    invoke-static { v1, v2 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L72
  .line 518
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const-string v1, "requestTriggerDaXuanWo"
    invoke-direct { v12, v15, v14, v0, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
    move-object/from16 v27, v13
    move-object/from16 v2, v34
    move-object/from16 v9, v35
    move-object/from16 v11, v36
    goto/16 :L117
  :L72
  .line 524
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L73
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    sget-object v2, Lcom/project7/localmanager/LocalGatewayServer;->SET_PLAYER_NAME:[B
  .line 525
    invoke-static { v1, v2 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L73
  .line 526
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    invoke-direct { v12, v15, v14, v0, v10 }, Lcom/project7/localmanager/LocalGatewayServer;->handleSetPlayerName(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
    move-object/from16 v27, v13
    move-object/from16 v2, v34
    move-object/from16 v9, v35
    move-object/from16 v11, v36
    goto/16 :L117
  :L73
  .line 532
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L75
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    sget-object v2, Lcom/project7/localmanager/LocalGatewayServer;->CHECK_GAMEPLAY_SWITCH:[B
  .line 533
    invoke-static { v1, v2 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L74
  .line 534
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const-string v1, "g"
    invoke-static { v0, v1 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v0
  .line 535
    nop
  .line 540
    const-string v1, "checkGamePlaySwitchReply"
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
  .line 541
    invoke-static { v0, v11, v13 }, Lcom/project7/localmanager/BsonLite;->gamePlaySwitchReplyDocument(Ljava/lang/String;ILjava/lang/String;)[B
    move-result-object v2
  .line 538
    invoke-static { v14, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
  .line 535
    const/4 v2, 5
    invoke-direct { v12, v15, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 544
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "checkGamePlaySwitch allowed gamePlay="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    move-object/from16 v9, v36
    invoke-static { v9, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 545
    move-object v11, v9
    move-object/from16 v27, v13
    move-object/from16 v2, v34
    move-object/from16 v9, v35
    goto/16 :L117
  :L74
  .line 533
    move-object/from16 v9, v36
    const/4 v2, 5
    goto :L76
  :L75
  .line 532
    move-object/from16 v9, v36
    const/4 v2, 5
  :L76
  .line 545
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L82
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    sget-object v3, Lcom/project7/localmanager/LocalGatewayServer;->REQUEST_LUCKY_DRAW_CARD:[B
  .line 546
    invoke-static { v1, v3 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L81
  .line 547
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const-string v3, "idx"
    invoke-static { v1, v3 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v1
  .line 548
    iget-object v3, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    move-object/from16 v4, v27
    invoke-static { v3, v4 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v3
  .line 549
    if-nez v1, :L77
    move/from16 v6, v26
    goto :L78
  :L77
    invoke-virtual { v1 }, Ljava/lang/Integer;->intValue()I
    move-result v6
  :L78
  .line 550
    if-nez v3, :L79
    move v1, v11
    goto :L80
  :L79
    invoke-virtual { v3 }, Ljava/lang/Integer;->intValue()I
    move-result v1
  :L80
  .line 551
    nop
  .line 556
    const-string v3, "replyLuckyDrawCard"
    invoke-static { v3 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v3
  .line 557
    invoke-static { v11, v6, v1 }, Lcom/project7/localmanager/BsonLite;->luckyDrawCardReplyDocument(ZII)[B
    move-result-object v4
  .line 554
    invoke-static { v14, v3, v4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v3
  .line 551
    invoke-direct { v12, v15, v2, v3 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 560
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const-string v2, "requestLuckyDrawCard"
    invoke-direct { v12, v15, v14, v0, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
  .line 562
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "lucky draw card completed index="
    invoke-virtual { v0, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v6 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v2, " type="
    invoke-virtual { v0, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v9, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 563
    move-object v11, v9
    move-object/from16 v27, v13
    move-object/from16 v2, v34
    move-object/from16 v9, v35
    goto/16 :L117
  :L81
  .line 546
    move-object/from16 v4, v27
    goto :L83
  :L82
  .line 545
    move-object/from16 v4, v27
  :L83
  .line 563
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L86
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    sget-object v3, Lcom/project7/localmanager/LocalGatewayServer;->REQUEST_FILE:[B
  .line 564
    invoke-static { v1, v3 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L86
  .line 565
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    invoke-static { v0, v4 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v0
  .line 566
    if-nez v0, :L84
    move v6, v11
    goto :L85
  :L84
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v6
  :L85
  .line 567
    nop
  .line 572
    const-string v0, "replyFile"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
  .line 573
    invoke-static { v11, v6 }, Lcom/project7/localmanager/BsonLite;->luckyDrawFileContentsReplyDocument(ZI)[B
    move-result-object v1
  .line 570
    invoke-static { v14, v0, v1 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
  .line 567
    invoke-direct { v12, v15, v2, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 576
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "lucky draw file contents completed type="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v6 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v9, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 577
    move-object v11, v9
    move-object/from16 v27, v13
    move-object/from16 v2, v34
    move-object/from16 v9, v35
    goto/16 :L117
  :L86
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L89
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    sget-object v3, Lcom/project7/localmanager/LocalGatewayServer;->REQUEST_QUIT_FILE:[B
  .line 578
    invoke-static { v1, v3 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L89
  .line 579
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    invoke-static { v1, v4 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v1
  .line 580
    if-nez v1, :L87
    move v6, v11
    goto :L88
  :L87
    invoke-virtual { v1 }, Ljava/lang/Integer;->intValue()I
    move-result v6
  :L88
  .line 581
    nop
  .line 586
    const-string v1, "replyQuitFile"
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
  .line 587
    invoke-static { v11, v6 }, Lcom/project7/localmanager/BsonLite;->luckyDrawQuitReplyDocument(ZI)[B
    move-result-object v3
  .line 584
    invoke-static { v14, v1, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
  .line 581
    invoke-direct { v12, v15, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 590
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const-string v1, "requestQuitFile"
    invoke-direct { v12, v15, v14, v0, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
  .line 592
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "lucky draw file closed type="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v6 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v9, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 593
    move-object v11, v9
    move-object/from16 v27, v13
    move-object/from16 v2, v34
    move-object/from16 v9, v35
    goto/16 :L117
  :L89
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L91
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    sget-object v3, Lcom/project7/localmanager/LocalGatewayServer;->GET_ALL_AREA_INFO_REQUEST:[B
  .line 594
    invoke-static { v1, v3 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L90
  .line 595
    invoke-static/range { v35 .. v35 }, Lcom/project7/localmanager/LocalGatewayServer;->isHighSchoolUnlocked(Lcom/project7/localmanager/LocalTutorialStore$Progress;)Z
    move-result v1
  .line 596
    nop
  .line 601
    const-string v3, "get_all_area_info_reply"
    invoke-static { v3 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v3
    iget-object v4, v12, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
  .line 602
    move-object/from16 v8, v35
    invoke-interface { v4, v10, v8 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->load(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v4
    invoke-static { v1, v8, v4 }, Lcom/project7/localmanager/BsonLite;->allAreaInfoReplyDocument(ZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
    move-result-object v4
  .line 599
    invoke-static { v14, v3, v4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v3
  .line 596
    invoke-direct { v12, v15, v2, v3 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 605
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const-string v2, "getAllAreaInfoRequest"
    invoke-direct { v12, v15, v14, v0, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
  .line 607
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "all area info completed highSchool="
    invoke-virtual { v0, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v9, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 608
    move-object v11, v9
    move-object/from16 v27, v13
    move-object/from16 v2, v34
    move-object v9, v8
    goto/16 :L117
  :L90
  .line 594
    move-object/from16 v8, v35
    goto :L92
  :L91
  .line 593
    move-object/from16 v8, v35
  :L92
  .line 608
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L96
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    sget-object v3, Lcom/project7/localmanager/LocalGatewayServer;->GET_AREA_INFO_REQUEST:[B
  .line 609
    invoke-static { v1, v3 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L96
  .line 610
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    move-object/from16 v3, v44
    invoke-static { v1, v3 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v1
  .line 611
    invoke-static { v8 }, Lcom/project7/localmanager/LocalGatewayServer;->isHighSchoolUnlocked(Lcom/project7/localmanager/LocalTutorialStore$Progress;)Z
    move-result v3
  .line 612
    iget-object v5, v12, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v5, v10, v8 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->load(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v5
    invoke-static { v1, v5 }, Lcom/project7/localmanager/LocalGatewayServer;->q7QueryAreaAllowed(Ljava/lang/Integer;[B)Z
    move-result v4
  .line 613
    if-eqz v4, :L93
    invoke-static { v1, v3, v5 }, Lcom/project7/localmanager/LocalGatewayServer;->q7QueryAreaId(Ljava/lang/Integer;Z[B)I
    move-result v1
    goto/32 :L94
  :L93
    invoke-virtual { v1 }, Ljava/lang/Integer;->intValue()I
    move-result v1
    const-string v5, "showMessageStr"
    invoke-static { v5 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v4
    const-string v5, "m"
    const-string v0, "\u8be5\u5730\u533a\u6682\u4e0d\u652f\u6301\u67e5\u8be2"
    filled-new-array { v5, v0 }, [Ljava/lang/Object;
    move-result-object v5
    invoke-static { v5 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v3
    invoke-static { v14, v4, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v3
    invoke-direct { v12, v15, v2, v3 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto/32 :L95
  :L94
    nop
  .line 618
    const-string v4, "get_area_info_reply"
    invoke-static { v4 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v4
  .line 620
  .line 619
    invoke-static { v1, v3, v8, v5 }, Lcom/project7/localmanager/BsonLite;->areaInfoReplyDocument(IZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
    move-result-object v3
  .line 616
    invoke-static { v14, v4, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v3
  .line 613
    invoke-direct { v12, v15, v2, v3 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 623
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const-string v2, "getAreaInfoRequest"
    invoke-direct { v12, v15, v14, v0, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
  .line 625
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "area info completed area="
    invoke-virtual { v0, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v9, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  :L95
  .line 626
    move-object v11, v9
    move-object/from16 v27, v13
    move-object/from16 v2, v34
    move-object v9, v8
    goto/16 :L117
  :L96
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L98
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    sget-object v2, Lcom/project7/localmanager/LocalGatewayServer;->COMBAT_OFFLINE_FINISH:[B
  .line 627
    invoke-static { v1, v2 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L97
  .line 628
    iget-object v4, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    move-object/from16 v1, p0
    move-object v2, v15
    move-object v3, v14
    move-object v5, v10
    move-object v6, v8
    move-object/from16 v7, v34
    move-object v11, v8
    move-object/from16 v8, v16
    move-object/from16 v35, v11
    move-object v11, v9
    move-object/from16 v9, v17
    invoke-direct/range { v1 .. v9 }, Lcom/project7/localmanager/LocalGatewayServer;->handleCombatOfflineFinish(Ljava/io/OutputStream;[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;Ljava/util/Set;)V
    move-object/from16 v27, v13
    move-object/from16 v2, v34
    move-object/from16 v9, v35
    goto/16 :L117
  :L97
  .line 627
    move-object/from16 v46, v9
    move-object v9, v8
    move v8, v11
    move-object/from16 v11, v46
    goto :L99
  :L98
  .line 626
    move-object/from16 v46, v9
    move-object v9, v8
    move v8, v11
    move-object/from16 v11, v46
  :L99
  .line 638
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    const-string v7, "combatCancelRpc"
    if-eqz v1, :L102
    iget-object v4, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    iget-object v5, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
  .line 639
    move-object/from16 v1, p0
    move-object v2, v15
    move-object v3, v14
    move-object v6, v10
    move-object/from16 v45, v7
    move-object v7, v9
    invoke-direct/range { v1 .. v7 }, Lcom/project7/localmanager/LocalGatewayServer;->handleCombatCancelRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)Z
    move-result v1
    if-eqz v1, :L101
  .line 640
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    const-string v2, "battleStageGiveup"
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v2
    invoke-static { v1, v2 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L100
  .line 641
    iget-object v4, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const/4 v8, 1
    move-object/from16 v1, p0
    move-object v2, v15
    move-object v3, v14
    move-object v5, v10
    move-object v6, v9
    move-object/from16 v7, v34
    invoke-direct/range { v1 .. v8 }, Lcom/project7/localmanager/LocalGatewayServer;->finishAbandonedStory(Ljava/io/OutputStream;[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Z)V
  :L100
  .line 642
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    move-object/from16 v7, v45
    invoke-direct { v12, v15, v14, v0, v7 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
    move-object/from16 v27, v13
    move-object/from16 v2, v34
    goto/16 :L117
  :L101
  .line 639
    move-object/from16 v7, v45
  :L102
  .line 643
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L104
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
  .line 644
    const-string v2, "battleRealFailWithEventMode"
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v2
    invoke-static { v1, v2 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L103
  .line 645
    iget-object v4, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    const/4 v8, 0
    move-object/from16 v1, p0
    move-object v2, v15
    move-object v3, v14
    move-object v5, v10
    move-object v6, v9
    move-object/from16 v27, v13
    move-object v13, v7
    move-object/from16 v7, v34
    invoke-direct/range { v1 .. v8 }, Lcom/project7/localmanager/LocalGatewayServer;->finishAbandonedStory(Ljava/io/OutputStream;[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Z)V
  .line 646
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    invoke-direct { v12, v15, v14, v0, v13 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
    move-object/from16 v2, v34
    goto/16 :L117
  :L103
  .line 644
    move-object/from16 v27, v13
    goto :L105
  :L104
  .line 643
    move-object/from16 v27, v13
  :L105
  .line 647
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L110
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    sget-object v2, Lcom/project7/localmanager/LocalGatewayServer;->ENTER_PLACE:[B
  .line 648
    invoke-static { v1, v2 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L109
  .line 649
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    move-object/from16 v2, v43
    invoke-static { v1, v2 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v1
  .line 650
    if-nez v1, :L107
  .line 651
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    invoke-static { v0, v2 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v0
  .line 652
    if-nez v0, :L106
    move-object/from16 v1, v20
    goto :L107
  :L106
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    invoke-static { v0 }, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object v0
    move-object v1, v0
  :L107
  .line 654
    move-object/from16 v2, v34
    if-eqz v2, :L108
  .line 655
    invoke-virtual { v2, v1 }, Lcom/project7/localmanager/LocalEventEngine;->enterPlace(Ljava/lang/String;)V
  .line 656
    iget-object v0, v12, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v0, v10, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  :L108
  .line 658
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v3, "enterPlace completed scene="
    invoke-virtual { v0, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v11, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 659
    goto/16 :L117
  :L109
  .line 648
    move-object/from16 v2, v34
    goto :L111
  :L110
  .line 647
    move-object/from16 v2, v34
  :L111
  .line 659
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L114
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    sget-object v3, Lcom/project7/localmanager/LocalGatewayServer;->TUTORIAL_BEGIN:[B
  .line 660
    invoke-static { v1, v3 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L114
  .line 661
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "tutorialBegin accepted pending="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  .line 662
    if-nez v2, :L112
  .line 663
    invoke-static { }, Ljava/util/Collections;->emptySet()Ljava/util/Set;
    move-result-object v1
    goto :L113
  :L112
    invoke-virtual { v2 }, Lcom/project7/localmanager/LocalEventEngine;->processingNewbees()Ljava/util/Set;
    move-result-object v1
  :L113
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
  .line 661
    invoke-static { v11, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
    goto/16 :L117
  :L114
  .line 664
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L115
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    sget-object v3, Lcom/project7/localmanager/LocalGatewayServer;->TUTORIAL_END:[B
  .line 665
    invoke-static { v1, v3 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L115
  .line 666
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v3, "tutorialEnd accepted parameters="
    invoke-virtual { v1, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
  .line 667
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->debugDocument([B)Ljava/lang/String;
    move-result-object v0
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
  .line 666
    invoke-static { v11, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
    goto/16 :L117
  :L115
  .line 668
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->id:[B
    invoke-static { v1, v14 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L116
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
  .line 669
    const-string v3, "exceptUpload"
    invoke-static { v3 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v4
    invoke-static { v1, v4 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-eqz v1, :L116
  .line 670
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    invoke-direct { v12, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->handleClientException([B)V
  .line 671
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    invoke-direct { v12, v15, v14, v0, v3 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
    goto :L117
  :L116
  .line 673
    iget-object v1, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->methodMd5:[B
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->hex([B)Ljava/lang/String;
    move-result-object v1
  .line 674
    new-instance v3, Ljava/lang/StringBuilder;
    invoke-direct { v3 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v4, "unhandled RPC "
    invoke-virtual { v3, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  .line 676
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->knownMethodName(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v4
    invoke-virtual { v3, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v4, " md5="
    invoke-virtual { v3, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v3, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v4, " parameters="
    invoke-virtual { v3, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-object v4, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
  .line 677
    invoke-static { v4 }, Lcom/project7/localmanager/BsonLite;->debugDocument([B)Ljava/lang/String;
    move-result-object v4
    invoke-virtual { v3, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v3 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v3
  .line 674
    invoke-static { v11, v3 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 679
    iget-object v3, v12, Lcom/project7/localmanager/LocalGatewayServer;->listener:Lcom/project7/localmanager/LocalGatewayServer$StatusListener;
    new-instance v4, Ljava/lang/StringBuilder;
    invoke-direct { v4 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v5, "\u6536\u5230\u672a\u5b9e\u73b0\u7684\u4e1a\u52a1 RPC\uff1a"
    invoke-virtual { v4, v5 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  .line 681
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->knownMethodName(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v5
    invoke-virtual { v4, v5 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v5, "\nMD5\uff1a"
    invoke-virtual { v4, v5 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v4, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v4 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v4
  .line 679
    invoke-interface { v3, v8, v4 }, Lcom/project7/localmanager/LocalGatewayServer$StatusListener;->onStatus(ZLjava/lang/String;)V
  .line 684
    iget-object v0, v0, Lcom/project7/localmanager/ProtoLite$EntityMessage;->parameters:[B
    new-instance v3, Ljava/lang/StringBuilder;
    invoke-direct { v3 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v4, "unknown:"
    invoke-virtual { v3, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  .line 688
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->knownMethodName(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v1
    invoke-virtual { v3, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v3 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
  .line 684
    invoke-direct { v12, v15, v14, v0, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->completeEmptyCallback(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
  :L117
  .line 691
    move-object v3, v2
    move-object v4, v9
    move-object v5, v10
    move/from16 v1, v23
    move/from16 v2, v24
    move-object/from16 v24, v25
    move-object/from16 v23, v29
    move-object/from16 v25, v22
    move-object/from16 v22, v28
  :L118
    move-object/from16 v0, v21
    goto/16 :L122
  :L119
  .line 304
    move-exception v0
    move-object/from16 v27, v7
    move-object/from16 v30, v9
    move-object/from16 v31, v11
    move-object/from16 v32, v14
    move-object/from16 v29, v23
    const/16 v26, 0
    move/from16 v23, v1
    move-object v9, v4
    move-object v11, v8
    move-object v14, v10
    const/4 v8, 1
    move-object v10, v5
    move-object/from16 v46, v24
    move/from16 v24, v2
    move-object/from16 v2, v28
    move-object/from16 v28, v22
    move-object/from16 v22, v25
    move-object/from16 v25, v46
  .line 305
    const-string v1, "ignoring malformed entity RPC"
    invoke-static { v11, v1, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
  .line 306
    iget-object v0, v12, Lcom/project7/localmanager/LocalGatewayServer;->listener:Lcom/project7/localmanager/LocalGatewayServer$StatusListener;
    const-string v1, "\u5ffd\u7565\u65e0\u6cd5\u89e3\u6790\u7684\u4e1a\u52a1 RPC\uff0c\u8fde\u63a5\u4fdd\u6301\u4e2d"
    invoke-interface { v0, v8, v1 }, Lcom/project7/localmanager/LocalGatewayServer$StatusListener;->onStatus(ZLjava/lang/String;)V
  .line 307
    move-object/from16 v13, p2
    move-object v3, v2
    move-object v4, v9
    move-object v5, v10
    move-object v8, v11
    move-object v10, v14
    move/from16 v1, v23
    move/from16 v2, v24
    move-object/from16 v24, v25
    move-object/from16 v7, v27
    move-object/from16 v23, v29
    move-object/from16 v9, v30
    move-object/from16 v11, v31
    move-object/from16 v14, v32
    move-object/from16 v25, v22
    move-object/from16 v22, v28
    goto/16 :L0
  :L120
  .line 692
    move-object/from16 v27, v7
    move-object/from16 v30, v9
    move-object/from16 v31, v11
    move-object/from16 v32, v14
    move-object/from16 v29, v23
    const/16 v26, 0
    move/from16 v23, v1
    move-object v9, v4
    move-object v11, v8
    move-object v14, v10
    move-object v10, v5
    move-object/from16 v46, v24
    move/from16 v24, v2
    move-object/from16 v2, v28
    move-object/from16 v28, v22
    move-object/from16 v22, v25
    move-object/from16 v25, v46
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v3, "unhandled service method "
    invoke-virtual { v1, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget v0, v0, Lcom/project7/localmanager/LocalGatewayServer$Frame;->method:I
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v11, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  :L121
  .line 694
    move-object v3, v2
    move-object v4, v9
    move-object v5, v10
    move-object/from16 v0, v21
    move/from16 v1, v23
    move/from16 v2, v24
    move-object/from16 v24, v25
    move-object/from16 v23, v29
    move-object/from16 v25, v22
    move-object/from16 v22, v28
  :L122
    if-eqz v4, :L123
    iget-object v6, v4, Lcom/project7/localmanager/LocalTutorialStore$Progress;->weekCommit:Ljava/lang/String;
    invoke-virtual { v0, v6 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    if-nez v6, :L123
  .line 695
    iget-object v0, v4, Lcom/project7/localmanager/LocalTutorialStore$Progress;->weekCommit:Ljava/lang/String;
  .line 696
    invoke-interface/range { v16 .. v16 }, Ljava/util/Set;->clear()V
    invoke-interface/range { v17 .. v17 }, Ljava/util/Set;->clear()V
    invoke-interface/range { v18 .. v18 }, Ljava/util/Map;->clear()V
    move-object/from16 v21, v0
    goto :L124
  :L123
  .line 698
    move-object/from16 v21, v0
  :L124
    move-object/from16 v13, p2
    move-object v8, v11
    move-object v10, v14
    move-object/from16 v7, v27
    move-object/from16 v9, v30
    move-object/from16 v11, v31
    move-object/from16 v14, v32
    goto/16 :L0
  :L125
  .line 288
    move-exception v0
    const/4 v8, 1
  .line 289
    iget-object v0, v12, Lcom/project7/localmanager/LocalGatewayServer;->activeSession:Lcom/project7/localmanager/LocalGatewayServer$ClientSession;
    move-object/from16 v1, p2
    if-ne v1, v0, :L126
  .line 290
    iget-object v0, v12, Lcom/project7/localmanager/LocalGatewayServer;->listener:Lcom/project7/localmanager/LocalGatewayServer$StatusListener;
    const-string v1, "\u6e38\u620f\u5df2\u65ad\u5f00\n\u7b49\u5f85\u91cd\u65b0\u8fde\u63a5"
    invoke-interface { v0, v8, v1 }, Lcom/project7/localmanager/LocalGatewayServer$StatusListener;->onStatus(ZLjava/lang/String;)V
  :L126
  .line 291
    return-void
  :L127
  .line 699
    return-void
.end method

.method private handleClientException([B)V
  .registers 8
    invoke-static { }, Lcom/project7/localmanager/LocalActionLedger;->clearRequest()V
  .line 833
    const-string v0, "e"
    invoke-static { p1, v0 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object p1
  .line 834
    invoke-static { p1 }, Lcom/project7/localmanager/BsonLite;->keys([B)Ljava/util/List;
    move-result-object v0
    invoke-interface { v0 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v0
  :L0
    invoke-interface { v0 }, Ljava/util/Iterator;->hasNext()Z
    move-result v1
    if-eqz v1, :L3
    invoke-interface { v0 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Ljava/lang/String;
  .line 835
    invoke-static { p1, v1 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v1
  .line 836
    const-string v2, "1"
    invoke-static { v1, v2 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v2
  .line 837
    if-eqz v2, :L0
    invoke-virtual { v2 }, Ljava/lang/String;->trim()Ljava/lang/String;
    move-result-object v3
    invoke-virtual { v3 }, Ljava/lang/String;->isEmpty()Z
    move-result v3
    if-eqz v3, :L1
    goto :L0
  :L1
  .line 838
    new-instance v3, Ljava/lang/StringBuilder;
    invoke-direct { v3 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v4, "client exception report id="
    invoke-virtual { v3, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v4, "0"
    invoke-static { v1, v4 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v1
    invoke-virtual { v3, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v1, "\n"
    invoke-virtual { v3, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v3, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v3 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    const-string v3, "Project7Gateway"
    invoke-static { v3, v1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->e(Ljava/lang/String;Ljava/lang/String;)I
  .line 840
    const-string v1, "BaseException: delay_exception_gc"
    invoke-virtual { v2, v1 }, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v1
    if-eqz v1, :L2
    goto :L0
  :L2
  .line 841
    invoke-virtual { v2 }, Ljava/lang/String;->trim()Ljava/lang/String;
    move-result-object v1
    const-string v2, "\r?\n"
    invoke-virtual { v1, v2 }, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;
    move-result-object v1
  .line 842
    iget-object v2, p0, Lcom/project7/localmanager/LocalGatewayServer;->listener:Lcom/project7/localmanager/LocalGatewayServer$StatusListener;
    new-instance v3, Ljava/lang/StringBuilder;
    invoke-direct { v3 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v4, "\u5ba2\u6237\u7aef\u5f02\u5e38\u62a5\u544a\uff1a"
    invoke-virtual { v3, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    array-length v4, v1
    const/4 v5, 1
    sub-int/2addr v4, v5
    aget-object v1, v1, v4
    invoke-virtual { v3, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v3 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-interface { v2, v5, v1 }, Lcom/project7/localmanager/LocalGatewayServer$StatusListener;->onStatus(ZLjava/lang/String;)V
  .line 843
    goto :L0
  :L3
  .line 844
    return-void
.end method

.method private handleCombatAdmission(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;Ljava/util/Set;I[B)V
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Ljava/io/OutputStream;",
      "[B",
      "Ljava/lang/String;",
      "Lcom/project7/localmanager/LocalTutorialStore$Progress;",
      "Lcom/project7/localmanager/LocalEventEngine;",
      "Ljava/util/Set<",
      "Ljava/lang/Integer;",
      ">;",
      "Ljava/util/Set<",
      "Ljava/lang/Integer;",
      ">;I[B)V"
    }
  .end annotation
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 44
  .line 1950
    move-object/from16 v7, p0
    move-object/from16 v8, p1
    move-object/from16 v9, p2
    move-object/from16 v6, p3
    move-object/from16 v10, p4
    move-object/from16 v11, p5
    move-object/from16 v0, p7
    move/from16 v12, p8
    move-object/from16 v1, p9
    iget-object v2, v7, Lcom/project7/localmanager/LocalGatewayServer;->combatReplies:Ljava/lang/ThreadLocal;
    invoke-virtual { v2 }, Ljava/lang/ThreadLocal;->get()Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Lcom/project7/localmanager/LocalGatewayServer$CombatReplies;
    invoke-virtual { v2, v0, v6, v9 }, Lcom/project7/localmanager/LocalGatewayServer$CombatReplies;->bind(Ljava/util/Set;Ljava/lang/String;[B)V
  .line 1951
    iget-object v3, v2, Lcom/project7/localmanager/LocalGatewayServer$CombatReplies;->values:Ljava/util/Map;
    invoke-static/range { p8 .. p8 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v4
    invoke-interface { v3, v4 }, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v3
    move-object v13, v3
    check-cast v13, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;
  .line 1952
    const-string v14, "combatOfflineReply"
    const-string v5, "Project7Gateway"
    const/4 v4, 2
    const/4 v3, 1
    if-eqz v13, :L6
  .line 1955
    iget-boolean v0, v13, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->delivered:Z
    if-eqz v0, :L0
    return-void
  :L0
  .line 1956
    iget-object v0, v7, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v0, v6, v10 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v16
  .line 1957
    iget-object v0, v13, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->requestHash:[B
    invoke-static/range { p9 .. p9 }, Lcom/project7/localmanager/LocalGatewayServer;->combatHash([B)[B
    move-result-object v1
    invoke-static { v0, v1 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v0
    if-eqz v0, :L4
  .line 1958
    move-object/from16 v0, p0
    move-object v1, v13
    move v15, v3
    move/from16 v3, p8
    move-object/from16 v4, v16
    move-object/from16 v18, v5
    move-object/from16 v5, p5
    invoke-direct/range { v0 .. v5 }, Lcom/project7/localmanager/LocalGatewayServer;->currentCombatReply(Lcom/project7/localmanager/LocalGatewayServer$CombatReply;Lcom/project7/localmanager/LocalGatewayServer$CombatReplies;I[BLcom/project7/localmanager/LocalEventEngine;)Z
    move-result v0
    if-nez v0, :L1
    move-object/from16 v13, v18
    goto :L5
  :L1
  .line 1962
    const/4 v5, 1
    move-object/from16 v0, p0
    move-object/from16 v1, p1
    move-object/from16 v2, p2
    move-object v3, v13
    move-object/from16 v4, v16
    invoke-direct/range { v0 .. v5 }, Lcom/project7/localmanager/LocalGatewayServer;->emitCombatControls(Ljava/io/OutputStream;[BLcom/project7/localmanager/LocalGatewayServer$CombatReply;[BZ)V
  .line 1963
    iget v0, v13, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->type:I
    if-eq v0, v15, :L2
    iget v0, v13, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->type:I
    const/4 v3, 2
    if-ne v0, v3, :L3
  :L2
    invoke-direct/range { p0 .. p5 }, Lcom/project7/localmanager/LocalGatewayServer;->syncEventEffects(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  :L3
  .line 1964
    invoke-direct { v7, v8, v9, v13 }, Lcom/project7/localmanager/LocalGatewayServer;->emitCombatCores(Ljava/io/OutputStream;[BLcom/project7/localmanager/LocalGatewayServer$CombatReply;)V
  .line 1965
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
    iget-object v1, v13, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->parameters:[B
    invoke-static { v9, v0, v1 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
    const/4 v1, 5
    invoke-direct { v7, v8, v1, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1966
    iput-boolean v15, v13, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->delivered:Z
  .line 1967
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "combat admission reply restored seq="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v12 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v1, " type="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget v1, v13, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->type:I
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    move-object/from16 v13, v18
    invoke-static { v13, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 1968
    return-void
  :L4
  .line 1957
    move-object v13, v5
  :L5
  .line 1959
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "stale/mismatched combat admission retry ignored seq="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v12 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v13, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;)I
  .line 1960
    return-void
  :L6
  .line 1970
    move v15, v3
    move v3, v4
    move-object v13, v5
    invoke-static/range { p8 .. p8 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v4
    invoke-interface { v0, v4 }, Ljava/util/Set;->contains(Ljava/lang/Object;)Z
    move-result v4
    if-eqz v4, :L7
  .line 1971
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "combat admission retry has no retained reply seq="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v12 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v13, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;)I
  .line 1972
    return-void
  :L7
  .line 1975
    new-instance v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;
    const/4 v4, 0
    invoke-direct { v5, v4 }, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;-><init>(Lcom/project7/localmanager/LocalGatewayServer$1;)V
    invoke-static/range { p9 .. p9 }, Lcom/project7/localmanager/LocalGatewayServer;->combatHash([B)[B
    move-result-object v4
    iput-object v4, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->requestHash:[B
  .line 1976
    const-string v4, "t"
    invoke-static { v1, v4 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v4
    const-string v15, "s"
    invoke-static { v1, v15 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v15
  .line 1977
    iput v15, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->scene:I
  .line 1978
    const-string v3, "h"
    invoke-static { v1, v3 }, Lcom/project7/localmanager/BsonLite;->intArrayValues([BLjava/lang/String;)Ljava/util/List;
    move-result-object v3
  .line 1979
    move-object/from16 v25, v14
    const-string v14, "d"
    invoke-static { v1, v14 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v26
  .line 1980
    iget-object v8, v7, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v8, v6, v10 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v8
  .line 1981
    invoke-interface { v3 }, Ljava/util/List;->isEmpty()Z
    move-result v17
    const/16 v27, 0
    if-nez v17, :L8
    if-lez v15, :L8
    const/16 v17, 1
    goto :L9
  :L8
    move/from16 v17, v27
  :L9
  .line 1982
    invoke-interface { v3 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v18
  :L10
    invoke-interface/range { v18 .. v18 }, Ljava/util/Iterator;->hasNext()Z
    move-result v19
    if-eqz v19, :L13
    invoke-interface/range { v18 .. v18 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v19
    check-cast v19, Ljava/lang/Integer;
    if-eqz v19, :L11
    iget-object v9, v7, Lcom/project7/localmanager/LocalGatewayServer;->combatCatalog:Lcom/project7/localmanager/LocalCombatCatalog;
    if-eqz v9, :L11
    invoke-virtual/range { v19 .. v19 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    invoke-virtual { v9, v0 }, Lcom/project7/localmanager/LocalCombatCatalog;->supportsHero(I)Z
    move-result v0
    if-eqz v0, :L11
    const/4 v0, 1
    goto :L12
  :L11
    move/from16 v0, v27
  :L12
    and-int v17, v17, v0
    move-object/from16 v9, p2
    move-object/from16 v0, p7
    goto :L10
  :L13
  .line 1983
    nop
  .line 1984
    invoke-static { v1 }, Lcom/project7/localmanager/StoryCityPolicy;->partyAllowed([B)Z
    move-result v0
    and-int v17, v17, v0
    sget-object v0, Ljava/lang/Boolean;->FALSE:Ljava/lang/Boolean;
    const-string v9, "q7WingBattle"
    move-object/from16 v28, v2
    invoke-static { v8, v9 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v2
    move-object/from16 v29, v14
    const-string v14, "done"
    invoke-static { v2, v14 }, Lcom/project7/localmanager/BsonLite;->boolValue([BLjava/lang/String;)Ljava/lang/Boolean;
    move-result-object v2
    invoke-virtual { v0, v2 }, Ljava/lang/Boolean;->equals(Ljava/lang/Object;)Z
    move-result v0
    const-string v2, "q7Battle"
    const-string v14, "f"
    const-string v18, "m"
    move-object/from16 v30, v13
    const-string v13, "showMessageStr"
    if-eqz v0, :L16
    const/4 v0, 2
    if-ne v4, v0, :L15
    const/16 v0, 291
    if-eq v15, v0, :L14
    goto :L15
  :L14
    move-object/from16 v31, v2
    move-object/from16 v32, v14
    const/4 v14, 1
    goto :L17
  :L15
  .line 1986
    nop
  .line 1987
    iget-object v0, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->controls:Ljava/util/List;
    new-instance v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    move-object/from16 v31, v2
    const/4 v2, 2
    new-array v12, v2, [Ljava/lang/Object;
    aput-object v18, v12, v27
    const-string v2, "\u8bf7\u5148\u7ed3\u7b97\u6216\u9000\u51fa\u5f53\u524d\u8349\u836f\u56ed\u6218\u6597"
    move-object/from16 v32, v14
    const/4 v14, 1
    aput-object v2, v12, v14
    invoke-static { v12 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v2
    invoke-direct { v1, v13, v2 }, Lcom/project7/localmanager/LocalResourceEngine$Reply;-><init>(Ljava/lang/String;[B)V
    invoke-interface { v0, v1 }, Ljava/util/List;->add(Ljava/lang/Object;)Z
    move/from16 v13, p8
    move-object v6, v8
    move/from16 v8, v27
    move-object/from16 v14, v31
    move-object/from16 v12, v32
    const/16 v16, 0
    move-object/from16 v31, v3
    move-object/from16 v32, v9
    move-object/from16 v9, v30
    goto/16 :L45
  :L16
  .line 1984
    move-object/from16 v31, v2
    move-object/from16 v32, v14
    const/4 v14, 1
  :L17
  .line 1988
    if-eq v4, v14, :L23
    const/4 v0, 2
    if-eq v4, v0, :L23
  .line 1989
    invoke-static { v4 }, Lcom/project7/localmanager/LocalDailyEngine;->battleType(I)Z
    move-result v0
    and-int v0, v17, v0
  .line 1990
    if-eqz v0, :L20
  .line 1991
    iget-object v2, v7, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    const-string v8, "q7DailyBegin"
    invoke-interface { v2, v6, v8, v1, v10 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v1
  .line 1992
    iget-object v8, v1, Lcom/project7/localmanager/LocalResourceEngine$Result;->profile:[B
    iget-object v2, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->controls:Ljava/util/List;
    iget-object v12, v1, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v2, v12 }, Ljava/util/List;->addAll(Ljava/util/Collection;)Z
  .line 1993
    iget-object v1, v1, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v1 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v1
  :L18
    invoke-interface { v1 }, Ljava/util/Iterator;->hasNext()Z
    move-result v2
    if-eqz v2, :L19
    invoke-interface { v1 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v2, v2, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    invoke-virtual { v13, v2 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v2
    if-eqz v2, :L18
    move/from16 v0, v27
    goto :L18
  :L19
  .line 1994
    goto :L21
  :L20
    iget-object v1, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->controls:Ljava/util/List;
    new-instance v2, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    const/4 v12, 2
    new-array v14, v12, [Ljava/lang/Object;
    aput-object v18, v14, v27
    const-string v12, "\u8be5\u6218\u6597\u6a21\u5f0f\u5c1a\u672a\u63a5\u5165\u672c\u5730\u7f51\u5173\uff0c\u672a\u6263\u9664\u8d44\u6e90"
    const/16 v17, 1
    aput-object v12, v14, v17
  .line 1995
    invoke-static { v14 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v12
    invoke-direct { v2, v13, v12 }, Lcom/project7/localmanager/LocalResourceEngine$Reply;-><init>(Ljava/lang/String;[B)V
  .line 1994
    invoke-interface { v1, v2 }, Ljava/util/List;->add(Ljava/lang/Object;)Z
  :L21
  .line 1996
    if-eqz v0, :L22
  .line 1997
    invoke-static/range { p2 .. p2 }, Lcom/project7/localmanager/LocalGatewayServer;->hex([B)Ljava/lang/String;
    move-result-object v21
    iget-object v1, v7, Lcom/project7/localmanager/LocalGatewayServer;->combatCatalog:Lcom/project7/localmanager/LocalCombatCatalog;
  .line 1996
    move/from16 v17, v4
    move/from16 v18, v15
    move-object/from16 v19, v3
    move-object/from16 v20, v26
    move-object/from16 v22, v8
    move-object/from16 v23, v1
    invoke-static/range { v17 .. v23 }, Lcom/project7/localmanager/LocalDailyEngine;->combatReply(IILjava/util/List;[BLjava/lang/String;[BLcom/project7/localmanager/LocalCombatCatalog;)[B
    move-result-object v1
    iput-object v1, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->parameters:[B
  :L22
  .line 2044
    move/from16 v13, p8
    move-object v6, v8
    move-object/from16 v14, v31
    move-object/from16 v12, v32
    const/16 v16, 0
    move v8, v0
    move-object/from16 v31, v3
    move-object/from16 v32, v9
    move-object/from16 v9, v30
    goto/16 :L45
  :L23
  .line 1998
    invoke-static { v8 }, Lcom/project7/localmanager/LocalDailyEngine;->active([B)Z
    move-result v0
    if-eqz v0, :L24
  .line 1999
    nop
  .line 2000
    iget-object v0, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->controls:Ljava/util/List;
    new-instance v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    const/4 v2, 2
    new-array v12, v2, [Ljava/lang/Object;
    aput-object v18, v12, v27
    const-string v2, "\u8bf7\u5148\u9000\u51fa\u5f53\u524d\u65e5\u5e38\u6218\u6597"
    const/4 v14, 1
    aput-object v2, v12, v14
  .line 2001
    invoke-static { v12 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v2
    invoke-direct { v1, v13, v2 }, Lcom/project7/localmanager/LocalResourceEngine$Reply;-><init>(Ljava/lang/String;[B)V
  .line 2000
    invoke-interface { v0, v1 }, Ljava/util/List;->add(Ljava/lang/Object;)Z
    move/from16 v13, p8
    move-object v6, v8
    move/from16 v8, v27
    move-object/from16 v14, v31
    move-object/from16 v12, v32
    const/16 v16, 0
    move-object/from16 v31, v3
    move-object/from16 v32, v9
    move-object/from16 v9, v30
    goto/16 :L45
  :L24
  .line 2003
    const/4 v14, 1
  .line 2004
    if-ne v4, v14, :L25
    invoke-static { v15 }, Lcom/project7/localmanager/LocalCityProgress;->area(I)I
    move-result v0
    if-nez v0, :L25
  .line 2005
    nop
  .line 2006
    iget-object v0, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->controls:Ljava/util/List;
    new-instance v2, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    const/4 v12, 2
    new-array v14, v12, [Ljava/lang/Object;
    aput-object v18, v14, v27
    const-string v12, "\u8be5\u5730\u533a\u5173\u5361\u5c1a\u672a\u63a5\u5165\u672c\u5730\u7f51\u5173\uff0c\u672a\u4fee\u6539\u8fdb\u5ea6"
    const/16 v17, 1
    aput-object v12, v14, v17
  .line 2007
    invoke-static { v14 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v12
    invoke-direct { v2, v13, v12 }, Lcom/project7/localmanager/LocalResourceEngine$Reply;-><init>(Ljava/lang/String;[B)V
  .line 2006
    invoke-interface { v0, v2 }, Ljava/util/List;->add(Ljava/lang/Object;)Z
    move/from16 v17, v27
  :L25
  .line 2009
    const/4 v0, 2
    if-ne v4, v0, :L27
    if-eqz v17, :L27
  .line 2010
    const/16 v0, 291
    if-ne v15, v0, :L27
  .line 2011
    iget-object v0, v7, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    const-string v2, "q7WingGardenBegin"
    invoke-interface { v0, v6, v2, v1, v10 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v0
  .line 2012
    iget-object v8, v0, Lcom/project7/localmanager/LocalResourceEngine$Result;->profile:[B
    iget-object v2, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->controls:Ljava/util/List;
    iget-object v12, v0, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v2, v12 }, Ljava/util/List;->addAll(Ljava/util/Collection;)Z
  .line 2013
    iget-object v0, v0, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v0 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v0
  :L26
    invoke-interface { v0 }, Ljava/util/Iterator;->hasNext()Z
    move-result v2
    if-eqz v2, :L27
    invoke-interface { v0 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v2, v2, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    invoke-virtual { v13, v2 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v2
    if-eqz v2, :L26
    move/from16 v17, v27
    goto :L26
  :L27
  .line 2016
    const/4 v0, 2
    if-ne v4, v0, :L31
    if-eqz v17, :L31
  .line 2017
    if-eqz v11, :L28
    invoke-static { v7, v6, v10, v11, v15 }, Lcom/project7/localmanager/TrialRetryGateway;->begin(Lcom/project7/localmanager/LocalGatewayServer;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;I)Z
    move-result v0
    if-eqz v0, :L28
    const/4 v0, 1
    goto :L29
  :L28
    move/from16 v0, v27
  :L29
  .line 2018
    if-eqz v0, :L30
    iget-object v2, v7, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v2, v6, v10 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  :L30
  .line 2020
    move/from16 v17, v0
  :L31
    const/4 v0, 1
    if-ne v4, v0, :L32
    if-eqz v17, :L32
  .line 2021
    iget-object v0, v7, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    const-string v2, "begin"
    iget-object v2, v7, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-static { v0, v6, v2, v1, v10 }, Lcom/project7/localmanager/LocalGatewayServer;->q7StoryCityCocBegin(Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalEconomyEngine$Result;
    move-result-object v0
  .line 2022
    iget-object v8, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->profile:[B
    iget-object v1, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->controls:Ljava/util/List;
    iget-object v2, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v1, v2 }, Ljava/util/List;->addAll(Ljava/util/Collection;)Z
  .line 2023
    iget-boolean v1, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->accepted:Z
    move/from16 v33, v1
    move-object v1, v0
    move/from16 v0, v33
    goto :L33
  :L32
  .line 2025
    move/from16 v0, v17
    const/4 v1, 0
  :L33
    if-eqz v0, :L44
  .line 2026
    const/16 v2, 101
    if-ne v15, v2, :L34
    if-eqz v11, :L34
    invoke-virtual/range { p5 .. p5 }, Lcom/project7/localmanager/LocalEventEngine;->availableEvents()Ljava/util/Set;
    move-result-object v2
    const/16 v8, 1043
    invoke-static { v8 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v12
    invoke-interface { v2, v12 }, Ljava/util/Set;->contains(Ljava/lang/Object;)Z
    move-result v2
    if-eqz v2, :L34
  .line 2027
    invoke-virtual { v11, v8 }, Lcom/project7/localmanager/LocalEventEngine;->startEvent(I)Z
    invoke-static { v8 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v2
    move-object/from16 v8, p6
    invoke-interface { v8, v2 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
    iget-object v2, v7, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v2, v6, v10 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  :L34
  .line 2029
    invoke-direct { v7, v6, v10, v11 }, Lcom/project7/localmanager/LocalGatewayServer;->prepareEventEffects(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v2
    iget-object v8, v2, Lcom/project7/localmanager/LocalResourceEngine$Result;->profile:[B
  .line 2030
    nop
  .line 2031
    const/4 v12, 2
    if-ne v4, v12, :L35
    const/16 v12, 291
    if-ne v15, v12, :L35
    invoke-static { v8, v9 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v1
    move-object/from16 v12, v32
    invoke-static { v1, v12 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v1
    move/from16 v13, p8
    move-object/from16 v19, v1
    move-object/from16 v14, v31
    goto :L37
  :L35
    move-object/from16 v12, v32
  .line 2032
    if-nez v1, :L36
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v13, "local-"
    invoke-virtual { v1, v13 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move/from16 v13, p8
    invoke-virtual { v1, v13 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    move-object/from16 v19, v1
    move-object/from16 v14, v31
    goto :L37
  :L36
    move/from16 v13, p8
    iget-object v1, v1, Lcom/project7/localmanager/LocalEconomyEngine$Result;->profile:[B
  .line 2033
    move-object/from16 v14, v31
    invoke-static { v1, v14 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v1
  .line 2032
    invoke-static { v1, v12 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v1
    move-object/from16 v19, v1
  :L37
  .line 2034
    invoke-static/range { p2 .. p2 }, Lcom/project7/localmanager/LocalGatewayServer;->hex([B)Ljava/lang/String;
    move-result-object v22
    const/4 v1, 2
    if-ne v4, v1, :L38
    const/16 v1, 291
    if-ne v15, v1, :L38
    invoke-static { v8 }, Lcom/project7/localmanager/LocalWingBattleEngine;->combatProfile([B)[B
    move-result-object v1
    move-object/from16 v23, v1
    goto :L39
  :L38
    move-object/from16 v23, v8
  :L39
    iget-object v1, v7, Lcom/project7/localmanager/LocalGatewayServer;->combatCatalog:Lcom/project7/localmanager/LocalCombatCatalog;
  .line 2030
    move/from16 v17, v4
    move/from16 v18, v15
    move-object/from16 v20, v3
    move-object/from16 v21, v26
    move-object/from16 v24, v1
    invoke-static/range { v17 .. v24 }, Lcom/project7/localmanager/BsonLite;->combatOfflineReplyDocument(IILjava/lang/String;Ljava/lang/Iterable;[BLjava/lang/String;[BLcom/project7/localmanager/LocalCombatCatalog;)[B
    move-result-object v1
    iput-object v1, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->parameters:[B
  .line 2035
    const/4 v1, 2
    if-ne v4, v1, :L42
  .line 2036
    invoke-virtual { v11, v15 }, Lcom/project7/localmanager/LocalEventEngine;->pendingStoryBattleOwners(I)Ljava/util/Set;
    move-result-object v1
    iput-object v1, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->owners:Ljava/util/Set;
  .line 2037
    invoke-static { v8 }, Lcom/project7/localmanager/LocalServiceEngine;->cores([B)Ljava/util/Map;
    move-result-object v1
  .line 2038
    move/from16 p9, v0
    const/4 v0, 1
  :L40
    move-object/from16 p6, v2
    const/16 v2, 8
    if-gt v0, v2, :L41
    iget-object v2, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->cores:Ljava/util/List;
    move-object/from16 v31, v3
    new-instance v3, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    const/4 v6, 4
    new-array v6, v6, [Ljava/lang/Object;
    const-string v16, "c"
    aput-object v16, v6, v27
  .line 2039
    move-object/from16 v16, v8
    invoke-static { v0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v8
    move-object/from16 v32, v9
    invoke-static/range { v27 .. v27 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v9
    invoke-interface { v1, v8, v9 }, Ljava/util/Map;->getOrDefault(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v8
    const/4 v9, 1
    aput-object v8, v6, v9
    const-string v8, "b"
    const/4 v9, 2
    aput-object v8, v6, v9
    const/4 v8, 3
    invoke-static { v0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v9
    aput-object v9, v6, v8
    invoke-static { v6 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v6
    const-string v8, "updateBlackCore"
    invoke-direct { v3, v8, v6 }, Lcom/project7/localmanager/LocalResourceEngine$Reply;-><init>(Ljava/lang/String;[B)V
  .line 2038
    invoke-interface { v2, v3 }, Ljava/util/List;->add(Ljava/lang/Object;)Z
    add-int/lit8 v0, v0, 1
    move-object/from16 v6, p3
    move-object/from16 v2, p6
    move-object/from16 v8, v16
    move-object/from16 v3, v31
    move-object/from16 v9, v32
    goto :L40
  :L41
  .line 2040
    move-object/from16 v31, v3
    move-object/from16 v16, v8
    move-object/from16 v32, v9
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "story combat black cores="
    invoke-virtual { v0, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    move-object/from16 v9, v30
    invoke-static { v9, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
    goto :L43
  :L42
  .line 2035
    move/from16 p9, v0
    move-object/from16 p6, v2
    move-object/from16 v31, v3
    move-object/from16 v16, v8
    move-object/from16 v32, v9
    move-object/from16 v9, v30
  :L43
  .line 2044
    move/from16 v8, p9
    move-object/from16 v6, v16
    move-object/from16 v16, p6
    goto :L45
  :L44
  .line 2025
    move/from16 v13, p8
    move/from16 p9, v0
    move-object/from16 v14, v31
    move-object/from16 v12, v32
    move-object/from16 v31, v3
    move-object/from16 v32, v9
    move-object/from16 v9, v30
    move-object v6, v8
    const/16 v16, 0
    move/from16 v8, p9
  :L45
  .line 2044
    if-eqz v8, :L46
    move v0, v4
    goto :L47
  :L46
    move/from16 v0, v27
  :L47
    iput v0, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->type:I
  .line 2045
    iget-object v0, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->parameters:[B
    if-nez v0, :L48
    const/16 v17, 0
  .line 2046
    invoke-static { }, Ljava/util/Collections;->emptyList()Ljava/util/List;
    move-result-object v20
    invoke-static/range { p2 .. p2 }, Lcom/project7/localmanager/LocalGatewayServer;->hex([B)Ljava/lang/String;
    move-result-object v22
    sget-object v23, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    iget-object v0, v7, Lcom/project7/localmanager/LocalGatewayServer;->combatCatalog:Lcom/project7/localmanager/LocalCombatCatalog;
  .line 2045
    const-string v19, ""
    move/from16 v18, v15
    move-object/from16 v21, v26
    move-object/from16 v24, v0
    invoke-static/range { v17 .. v24 }, Lcom/project7/localmanager/BsonLite;->combatOfflineReplyDocument(IILjava/lang/String;Ljava/lang/Iterable;[BLjava/lang/String;[BLcom/project7/localmanager/LocalCombatCatalog;)[B
    move-result-object v0
    iput-object v0, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->parameters:[B
  :L48
  .line 2047
    const-string v0, "weeknum"
    invoke-static { v6, v0 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v0
  .line 2048
    const-string v1, "w"
    invoke-static { v0, v1 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v1
    iput v1, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->week:I
    move-object/from16 v1, v29
    invoke-static { v0, v1 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v0
    iput v0, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->day:I
  .line 2049
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->combatHash([B)[B
    move-result-object v0
    iput-object v0, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->profileHash:[B
  .line 2050
    move-object/from16 v2, v28
    iget-object v0, v2, Lcom/project7/localmanager/LocalGatewayServer$CombatReplies;->latestAccepted:Ljava/lang/Integer;
    iput-object v0, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->acceptedAtPreparation:Ljava/lang/Integer;
  .line 2051
    nop
  .line 2052
    const/4 v0, 1
    if-ne v4, v0, :L49
    goto :L51
  :L49
    const/4 v0, 2
    if-ne v4, v0, :L50
    const/16 v0, 291
    if-ne v15, v0, :L50
    move-object/from16 v14, v32
    goto :L51
  :L50
    const-string v0, "q7DailyBattle"
    move-object v14, v0
  :L51
  .line 2051
    invoke-static { v6, v14 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v0
    invoke-static { v0, v12 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v0
    iput-object v0, v5, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->fight:Ljava/lang/String;
  .line 2054
    invoke-virtual { v2, v13, v5 }, Lcom/project7/localmanager/LocalGatewayServer$CombatReplies;->put(ILcom/project7/localmanager/LocalGatewayServer$CombatReply;)V
    invoke-static/range { p8 .. p8 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v0
    move-object/from16 v1, p7
    invoke-interface { v1, v0 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
  .line 2055
    const/4 v12, 0
    move-object/from16 v0, p0
    move-object/from16 v1, p1
    move-object/from16 v2, p2
    move-object/from16 v13, v31
    move-object v3, v5
    move v14, v4
    move-object v4, v6
    move-object v6, v5
    move v5, v12
    invoke-direct/range { v0 .. v5 }, Lcom/project7/localmanager/LocalGatewayServer;->emitCombatControls(Ljava/io/OutputStream;[BLcom/project7/localmanager/LocalGatewayServer$CombatReply;[BZ)V
  .line 2056
    if-eqz v16, :L52
    move-object/from16 v0, p0
    move-object/from16 v1, p1
    move-object/from16 v2, p2
    move-object/from16 v3, p3
    move-object/from16 v4, p4
    move-object/from16 v5, p5
    move-object v10, v6
    move-object/from16 v6, v16
    invoke-direct/range { v0 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->emitEventEffects(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Lcom/project7/localmanager/LocalResourceEngine$Result;)V
    goto :L53
  :L52
    move-object v10, v6
  :L53
  .line 2057
    move-object/from16 v0, p1
    move-object/from16 v1, p2
    invoke-direct { v7, v0, v1, v10 }, Lcom/project7/localmanager/LocalGatewayServer;->emitCombatCores(Ljava/io/OutputStream;[BLcom/project7/localmanager/LocalGatewayServer$CombatReply;)V
  .line 2058
    invoke-static/range { v25 .. v25 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
    iget-object v3, v10, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->parameters:[B
    invoke-static { v1, v2, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
    const/4 v2, 5
    invoke-direct { v7, v0, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2059
    const/4 v0, 1
    iput-boolean v0, v10, Lcom/project7/localmanager/LocalGatewayServer$CombatReply;->delivered:Z
  .line 2060
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "offline combat admission type="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v14 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v1, " scene="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v15 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v1, " heroes="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v13 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v1, " accepted="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v8 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v9, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 2062
    return-void
.end method

.method private handleCombatCancelRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)Z
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 23
  .line 2066
    move-object/from16 v0, p0
    move-object/from16 v1, p1
    move-object/from16 v2, p2
    move-object/from16 v3, p3
    move-object/from16 v4, p5
    move-object/from16 v5, p6
    const-string v6, "battleStageGiveup"
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v7
    invoke-static { v3, v7 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v7
  .line 2067
    const/4 v8, 0
    if-nez v7, :L0
    sget-object v9, Lcom/project7/localmanager/LocalGatewayServer;->COMBAT_OFFLINE_RESET:[B
    invoke-static { v3, v9 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v3
    if-nez v3, :L0
    return v8
  :L0
  .line 2068
    const-string v3, "s"
    move-object/from16 v9, p4
    invoke-static { v9, v3 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v9
  .line 2069
    if-nez v9, :L1
    move v9, v8
    goto :L2
  :L1
    invoke-virtual { v9 }, Ljava/lang/Integer;->intValue()I
    move-result v9
  :L2
  .line 2070
    iget-object v10, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v10, v4, v5 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v10
  .line 2071
    const-string v11, "q7DailyBattle"
    invoke-static { v10, v11 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v11
  .line 2072
    const-string v12, "q7Battle"
    invoke-static { v10, v12 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v12
  .line 2073
    if-eqz v7, :L3
    invoke-static { v3, v9 }, Lcom/project7/localmanager/BsonLite;->intDocument(Ljava/lang/String;I)[B
    move-result-object v13
    goto :L4
  :L3
    sget-object v13, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
  :L4
  .line 2074
    nop
  .line 2075
    invoke-static { v10 }, Lcom/project7/localmanager/LocalDailyEngine;->active([B)Z
    move-result v14
    const/4 v8, 5
    if-eqz v14, :L8
  .line 2076
    if-eqz v7, :L5
    if-lez v9, :L9
    invoke-static { v11, v3 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v11
    if-ne v9, v11, :L9
  :L5
  .line 2077
    iget-object v11, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    const-string v12, "q7DailyReset"
    invoke-interface { v11, v4, v12, v13, v5 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v11
  .line 2078
    iget-object v12, v11, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v12 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v12
  :L6
    invoke-interface { v12 }, Ljava/util/Iterator;->hasNext()Z
    move-result v14
    if-eqz v14, :L7
    invoke-interface { v12 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v14
    check-cast v14, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v15, v14, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 2079
    invoke-static { v15 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v15
    iget-object v14, v14, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v2, v15, v14 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v14
  .line 2078
    invoke-direct { v0, v1, v8, v14 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L6
  :L7
  .line 2080
    iget-object v11, v11, Lcom/project7/localmanager/LocalResourceEngine$Result;->profile:[B
    invoke-static { v11 }, Lcom/project7/localmanager/LocalDailyEngine;->active([B)Z
    move-result v11
    const/4 v12, 1
  .line 2081
    xor-int/2addr v11, v12
    goto :L13
  :L8
  .line 2082
    if-eqz v7, :L10
    if-lez v9, :L9
    invoke-static { v12 }, Lcom/project7/localmanager/BsonLite;->keys([B)Ljava/util/List;
    move-result-object v11
    invoke-interface { v11 }, Ljava/util/List;->isEmpty()Z
    move-result v11
    if-nez v11, :L9
  .line 2083
    invoke-static { v12, v3 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v11
    if-ne v9, v11, :L9
    goto :L10
  :L9
  .line 2089
    const/4 v11, 0
    goto :L13
  :L10
  .line 2084
    iget-object v11, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    const-string v12, "reset"
    invoke-interface { v11, v4, v12, v13, v5 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateEconomy(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalEconomyEngine$Result;
    move-result-object v11
  .line 2085
    iget-object v12, v11, Lcom/project7/localmanager/LocalEconomyEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v12 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v12
  :L11
    invoke-interface { v12 }, Ljava/util/Iterator;->hasNext()Z
    move-result v14
    if-eqz v14, :L12
    invoke-interface { v12 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v14
    check-cast v14, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v15, v14, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 2086
    invoke-static { v15 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v15
    iget-object v14, v14, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v2, v15, v14 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v14
  .line 2085
    invoke-direct { v0, v1, v8, v14 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L11
  :L12
  .line 2087
    iget-boolean v11, v11, Lcom/project7/localmanager/LocalEconomyEngine$Result;->accepted:Z
  :L13
  .line 2089
    if-eqz v7, :L14
    const/16 v12, 291
    if-ne v9, v12, :L16
  :L14
    const-string v12, "q7WingBattle"
    invoke-static { v10, v12 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v10
    invoke-static { v10 }, Lcom/project7/localmanager/BsonLite;->keys([B)Ljava/util/List;
    move-result-object v10
    invoke-interface { v10 }, Ljava/util/List;->isEmpty()Z
    move-result v10
    if-nez v10, :L16
  .line 2090
    iget-object v10, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    const-string v12, "q7WingGardenReset"
    invoke-interface { v10, v4, v12, v13, v5 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v4
  .line 2091
    iget-object v4, v4, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v4 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v4
  :L15
    invoke-interface { v4 }, Ljava/util/Iterator;->hasNext()Z
    move-result v5
    if-eqz v5, :L16
    invoke-interface { v4 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v5
    check-cast v5, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v10, v5, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 2092
    invoke-static { v10 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v10
    iget-object v5, v5, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v2, v10, v5 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v5
  .line 2091
    invoke-direct { v0, v1, v8, v5 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L15
  :L16
  .line 2095
    if-eqz v7, :L17
  .line 2096
    const-string v4, "battleStageGiveupReply"
    invoke-static { v4 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v4
    invoke-static { v3, v9 }, Lcom/project7/localmanager/BsonLite;->intDocument(Ljava/lang/String;I)[B
    move-result-object v3
  .line 2095
    invoke-static { v2, v4, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
    invoke-direct { v0, v1, v8, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L17
  .line 2097
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "combat cancellation method="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    if-eqz v7, :L18
    goto :L19
  :L18
    const-string v6, "combatOfflineReset"
  :L19
    invoke-virtual { v1, v6 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v2, " scene="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v9 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v2, " receiptCleared="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v11 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    const-string v2, "Project7Gateway"
    invoke-static { v2, v1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 2099
    const/4 v1, 1
    return v1
.end method

.method private handleCombatOfflineFinish(Ljava/io/OutputStream;[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;Ljava/util/Set;)V
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Ljava/io/OutputStream;",
      "[B[B",
      "Ljava/lang/String;",
      "Lcom/project7/localmanager/LocalTutorialStore$Progress;",
      "Lcom/project7/localmanager/LocalEventEngine;",
      "Ljava/util/Set<",
      "Ljava/lang/Integer;",
      ">;",
      "Ljava/util/Set<",
      "Ljava/lang/Integer;",
      ">;)V"
    }
  .end annotation
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 32
    invoke-static/range { p0 .. p8 }, Lcom/project7/localmanager/TrialRetryGateway;->handleFinish(Lcom/project7/localmanager/LocalGatewayServer;Ljava/io/OutputStream;[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;Ljava/util/Set;)Z
    move-result v0
    if-eqz v0, :L0
    return-void
  :L0
  .line 2130
    move-object/from16 v12, p0
    move-object/from16 v1, p1
    move-object/from16 v2, p2
    move-object/from16 v0, p3
    move-object/from16 v3, p4
    move-object/from16 v4, p5
    move-object/from16 v5, p6
    const-string v6, "t"
    invoke-static { v0, v6 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v6
  .line 2131
    const-string v7, "s"
    invoke-static { v0, v7 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v7
  .line 2132
    if-nez v6, :L1
    const/4 v9, 0
    goto :L2
  :L1
    invoke-virtual { v6 }, Ljava/lang/Integer;->intValue()I
    move-result v6
    move v9, v6
  :L2
  .line 2133
    if-nez v7, :L3
    const/4 v10, 0
    goto :L4
  :L3
    invoke-virtual { v7 }, Ljava/lang/Integer;->intValue()I
    move-result v6
    move v10, v6
  :L4
  .line 2134
    invoke-static/range { p3 .. p3 }, Lcom/project7/localmanager/BsonLite;->combatWinValue([B)I
    move-result v6
  .line 2135
    const-string v7, "h"
    invoke-static { v0, v7 }, Lcom/project7/localmanager/BsonLite;->intArrayValues([BLjava/lang/String;)Ljava/util/List;
    move-result-object v7
  .line 2136
    const-string v11, "x"
    invoke-static { v0, v11 }, Lcom/project7/localmanager/BsonLite;->intArrayValues([BLjava/lang/String;)Ljava/util/List;
    move-result-object v11
  .line 2137
    const-string v15, " scene="
    const-string v14, "Project7Gateway"
    const/4 v8, 1
    const-string v13, "combatOfflineReward"
    move/from16 v18, v6
    const/4 v6, 5
    if-eq v9, v8, :L8
    const/4 v8, 2
    if-eq v9, v8, :L8
  .line 2138
    invoke-static { v9 }, Lcom/project7/localmanager/LocalDailyEngine;->battleType(I)Z
    move-result v5
    if-eqz v5, :L7
  .line 2139
    iget-object v5, v12, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    const-string v8, "q7DailyFinish"
    invoke-interface { v5, v3, v8, v0, v4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v0
  .line 2140
    nop
  .line 2141
    iget-object v0, v0, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v0 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v0
    const/4 v3, 0
  :L5
    invoke-interface { v0 }, Ljava/util/Iterator;->hasNext()Z
    move-result v4
    if-eqz v4, :L6
    invoke-interface { v0 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v4
    check-cast v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;
  .line 2142
    iget-object v5, v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    invoke-virtual { v13, v5 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v5
    or-int/2addr v3, v5
  .line 2143
    iget-object v5, v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    invoke-static { v5 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v5
    iget-object v4, v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v2, v5, v4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v4
    invoke-direct { v12, v1, v6, v4 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2144
    goto :L5
  :L6
  .line 2145
    if-eqz v3, :L7
    return-void
  :L7
  .line 2147
    invoke-static { v13 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
  .line 2148
    const/4 v3, 0
    invoke-static { v9, v10, v7, v11, v3 }, Lcom/project7/localmanager/BsonLite;->combatOfflineRewardDocument(IILjava/lang/Iterable;Ljava/lang/Iterable;I)[B
    move-result-object v3
  .line 2147
    invoke-static { v2, v0, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
    invoke-direct { v12, v1, v6, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2149
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "non-story settlement rejected type="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v9 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v15 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v10 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v14, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;)I
  .line 2150
    return-void
  :L8
  .line 2152
    const/4 v8, 1
    if-ne v9, v8, :L9
    invoke-static { v10 }, Lcom/project7/localmanager/LocalCityProgress;->area(I)I
    move-result v19
    if-eqz v19, :L9
    move/from16 v19, v8
    goto :L10
  :L9
    const/16 v19, 0
  :L10
  .line 2153
    const/4 v8, 2
    if-ne v9, v8, :L12
    if-eqz v5, :L11
    invoke-virtual { v5, v10 }, Lcom/project7/localmanager/LocalEventEngine;->hasPendingStoryBattle(I)Z
    move-result v8
    if-nez v8, :L12
  :L11
  .line 2154
    invoke-static { v13 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
  .line 2155
    const/4 v3, 0
    invoke-static { v9, v10, v7, v11, v3 }, Lcom/project7/localmanager/BsonLite;->combatOfflineRewardDocument(IILjava/lang/Iterable;Ljava/lang/Iterable;I)[B
    move-result-object v3
  .line 2154
    invoke-static { v2, v0, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
    invoke-direct { v12, v1, v6, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2156
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "story settlement rejected without matching admission scene="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v10 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v14, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;)I
  .line 2157
    return-void
  :L12
  .line 2159
    nop
  .line 2160
    sget-object v21, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
  .line 2161
    const/4 v8, 2
    if-ne v9, v8, :L17
    const/16 v8, 291
    if-ne v10, v8, :L17
    if-eqz v18, :L17
  .line 2162
    iget-object v8, v12, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    const-string v6, "q7WingHarvest"
    invoke-interface { v8, v3, v6, v0, v4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v6
  .line 2163
    iget-object v8, v12, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v8, v3, v4 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 2164
    nop
  .line 2165
    iget-object v6, v6, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v6 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v6
    const/4 v8, 1
  :L13
    invoke-interface { v6 }, Ljava/util/Iterator;->hasNext()Z
    move-result v17
    if-eqz v17, :L15
    invoke-interface { v6 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v17
    move-object/from16 v5, v17
    check-cast v5, Lcom/project7/localmanager/LocalResourceEngine$Reply;
  .line 2166
    move-object/from16 v17, v6
    iget-object v6, v5, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    move-object/from16 v20, v14
    const-string v14, "showMessageStr"
    invoke-virtual { v14, v6 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v6
    if-eqz v6, :L14
    const/4 v8, 0
  :L14
  .line 2167
    iget-object v6, v5, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v6
    iget-object v5, v5, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v2, v6, v5 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v5
    const/4 v6, 5
    invoke-direct { v12, v1, v6, v5 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2168
    move-object/from16 v5, p6
    move-object/from16 v6, v17
    move-object/from16 v14, v20
    goto :L13
  :L15
  .line 2169
    move-object/from16 v20, v14
    const/4 v6, 5
    if-nez v8, :L16
  .line 2170
    invoke-static { v13 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
  .line 2171
    const/4 v5, 0
    invoke-static { v9, v10, v7, v11, v5 }, Lcom/project7/localmanager/BsonLite;->combatOfflineRewardDocument(IILjava/lang/Iterable;Ljava/lang/Iterable;I)[B
    move-result-object v3
  .line 2170
    invoke-static { v2, v0, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
    invoke-direct { v12, v1, v6, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2172
    return-void
  :L16
  .line 2169
    const/4 v5, 0
    goto :L18
  :L17
  .line 2161
    move-object/from16 v20, v14
    const/4 v5, 0
  :L18
  .line 2175
    if-eqz v19, :L23
  .line 2176
    iget-object v6, v12, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    const-string v8, "finish"
    invoke-static { v6, v3, v8, v0, v4 }, Lcom/project7/localmanager/LocalGatewayServer;->q7StoryCityCocFinish(Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalEconomyEngine$Result;
    move-result-object v0
  .line 2177
    iget-object v6, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v6 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v6
  :L19
    invoke-interface { v6 }, Ljava/util/Iterator;->hasNext()Z
    move-result v8
    if-eqz v8, :L20
    invoke-interface { v6 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v8
    check-cast v8, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v14, v8, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 2178
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v14
    iget-object v8, v8, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v2, v14, v8 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v8
  .line 2177
    const/4 v14, 5
    invoke-direct { v12, v1, v14, v8 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L19
  :L20
  .line 2179
    iget-boolean v6, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->accepted:Z
    if-eqz v6, :L21
    iget v8, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->win:I
    goto :L22
  :L21
    move v8, v5
  :L22
  .line 2180
    iget-object v5, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->reward:[B
  .line 2181
    new-instance v6, Ljava/lang/StringBuilder;
    invoke-direct { v6 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v14, "battle settlement accepted="
    invoke-virtual { v6, v14 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-boolean v14, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->accepted:Z
    invoke-virtual { v6, v14 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    const-string v14, " replay="
    invoke-virtual { v6, v14 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-boolean v14, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->replay:Z
    invoke-virtual { v6, v14 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    invoke-virtual { v6, v15 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v6, v10 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v14, " reason="
    invoke-virtual { v6, v14 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-object v14, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->reason:Ljava/lang/String;
    invoke-virtual { v6, v14 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v14, " reward="
    invoke-virtual { v6, v14 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  .line 2182
    invoke-static { v5 }, Lcom/project7/localmanager/BsonLite;->debugDocument([B)Ljava/lang/String;
    move-result-object v14
    invoke-virtual { v6, v14 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v6 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v6
  .line 2181
    move-object/from16 v14, v20
    invoke-static { v14, v6 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
    move-object/from16 v22, v0
    move-object/from16 v18, v5
    goto :L24
  :L23
  .line 2175
    move-object/from16 v14, v20
    move/from16 v8, v18
    move-object/from16 v18, v21
    const/16 v22, 0
  :L24
  .line 2185
    nop
  .line 2190
    invoke-static { v13 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
  .line 2191
    move v13, v9
    move-object v5, v14
    move v14, v10
    move-object v6, v15
    move-object v15, v7
    move-object/from16 v16, v11
    move/from16 v17, v8
    invoke-static/range { v13 .. v18 }, Lcom/project7/localmanager/BsonLite;->combatOfflineRewardDocument(IILjava/lang/Iterable;Ljava/lang/Iterable;I[B)[B
    move-result-object v11
  .line 2188
    invoke-static { v2, v0, v11 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
  .line 2185
    const/4 v11, 5
    invoke-direct { v12, v1, v11, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2195
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v11, "offline combat finished type="
    invoke-virtual { v0, v11 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v9 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v6 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v10 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v6, " win="
    invoke-virtual { v0, v6 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v8 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v6, " heroes="
    invoke-virtual { v0, v6 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v7 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v5, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 2201
    move-object/from16 v0, p0
    move-object/from16 v1, p1
    move-object/from16 v2, p2
    move-object/from16 v3, p4
    move-object/from16 v4, p5
    move-object/from16 v5, p6
    move-object/from16 v6, p7
    move-object/from16 v7, p8
    move/from16 v18, v8
    move v8, v9
    move v9, v10
    move/from16 v10, v18
    move-object/from16 v11, v22
    invoke-direct/range { v0 .. v11 }, Lcom/project7/localmanager/LocalGatewayServer;->finishStoryCombat(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;Ljava/util/Set;IIILcom/project7/localmanager/LocalEconomyEngine$Result;)V
  .line 2203
    return-void
.end method

.method private handleConstructionRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/lang/Integer;)Z
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 15
  .line 2290
    const-string v0, "areaBuildRequest"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v1
    invoke-static { p3, v1 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    const/4 v2, 0
    const-string v3, "playerDestroyBuilding"
    const-string v4, "areaLevelUpRequest"
    if-eqz v1, :L0
    goto :L3
  :L0
  .line 2291
    invoke-static { v4 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    invoke-static { p3, v0 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v0
    if-eqz v0, :L1
    move-object v0, v4
    goto :L3
  :L1
  .line 2292
    invoke-static { v3 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    invoke-static { p3, v0 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result p3
    if-eqz p3, :L2
    move-object v0, v3
    goto :L3
  :L2
    move-object v0, v2
  :L3
  .line 2293
    if-nez v0, :L4
    const/4 p1, 0
    return p1
  :L4
  .line 2294
    iget-object p3, p0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { p3, p5, v0, p4, p6 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateEconomy(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalEconomyEngine$Result;
    move-result-object p3
  .line 2295
    iget-object p4, p0, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { p4, p5, p6 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 2296
    iget-object p4, p3, Lcom/project7/localmanager/LocalEconomyEngine$Result;->replies:Ljava/util/List;
    invoke-interface { p4 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object p4
  :L5
    invoke-interface { p4 }, Ljava/util/Iterator;->hasNext()Z
    move-result v1
    const/4 v3, 5
    if-eqz v1, :L8
    invoke-interface { p4 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;
  .line 2297
    iget-object v4, v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    const-string v5, "area_build_reply"
    invoke-virtual { v5, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v4
    if-nez v4, :L6
    iget-object v4, v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    const-string v5, "area_level_up_reply"
    invoke-virtual { v5, v4 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v4
    if-eqz v4, :L7
  :L6
    if-eqz p8, :L7
  .line 2298
    invoke-virtual { p8 }, Ljava/lang/Integer;->intValue()I
    move-result p8
    invoke-direct { p0, p1, p2, p8, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->completeCallback(Ljava/io/OutputStream;[BILjava/lang/String;)V
  .line 2299
    move-object p8, v2
  :L7
  .line 2301
    iget-object v4, v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    invoke-static { v4 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v4
    iget-object v1, v1, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { p2, v4, v1 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
    invoke-direct { p0, p1, v3, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2302
    goto :L5
  :L8
  .line 2303
    if-eqz p8, :L9
    invoke-virtual { p8 }, Ljava/lang/Integer;->intValue()I
    move-result p4
    invoke-direct { p0, p1, p2, p4, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->completeCallback(Ljava/io/OutputStream;[BILjava/lang/String;)V
  :L9
  .line 2304
    if-eqz p7, :L10
    iget-boolean p4, p3, Lcom/project7/localmanager/LocalEconomyEngine$Result;->accepted:Z
    if-eqz p4, :L10
  .line 2305
    iget-object p4, p0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { p4, p5, p6 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object p4
    invoke-virtual { p7, p4 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  .line 2306
    const-string p4, "pushEvents"
    invoke-static { p4 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object p4
  .line 2307
    invoke-virtual { p7 }, Lcom/project7/localmanager/LocalEventEngine;->availableEvents()Ljava/util/Set;
    move-result-object p5
    invoke-virtual { p7 }, Lcom/project7/localmanager/LocalEventEngine;->processingEvents()Ljava/util/Set;
    move-result-object p6
    invoke-static { p5, p6 }, Lcom/project7/localmanager/BsonLite;->eventListsDocument(Ljava/lang/Iterable;Ljava/lang/Iterable;)[B
    move-result-object p5
  .line 2306
    invoke-static { p2, p4, p5 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object p2
    invoke-direct { p0, p1, v3, p2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L10
  .line 2309
    new-instance p1, Ljava/lang/StringBuilder;
    invoke-direct { p1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string p2, "city operation="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string p2, " accepted="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-boolean p2, p3, Lcom/project7/localmanager/LocalEconomyEngine$Result;->accepted:Z
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    const-string p2, " reason="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-object p2, p3, Lcom/project7/localmanager/LocalEconomyEngine$Result;->reason:Ljava/lang/String;
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string p2, " actions="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget p2, p3, Lcom/project7/localmanager/LocalEconomyEngine$Result;->remainingActions:I
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { p1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p1
    const-string p2, "Project7Gateway"
    invoke-static { p2, p1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 2311
    const/4 p1, 1
    return p1
.end method

.method private handleDailyRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)Z
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 11
  .line 703
    const/4 v0, 0
    if-eqz p5, :L6
    if-nez p6, :L0
    goto :L6
  :L0
  .line 704
    sget-object v1, Lcom/project7/localmanager/LocalDailyEngine;->METHODS:Ljava/util/List;
    invoke-interface { v1 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v1
  :L1
    invoke-interface { v1 }, Ljava/util/Iterator;->hasNext()Z
    move-result v2
    if-eqz v2, :L5
    invoke-interface { v1 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Ljava/lang/String;
  .line 705
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v3
    invoke-static { p3, v3 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v3
    if-nez v3, :L2
    goto :L1
  :L2
  .line 706
    iget-object p3, p0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { p3, p5, v2, p4, p6 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object p3
  .line 707
    iget-object p3, p3, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { p3 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object p3
  :L3
    invoke-interface { p3 }, Ljava/util/Iterator;->hasNext()Z
    move-result p6
    if-eqz p6, :L4
    invoke-interface { p3 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object p6
    check-cast p6, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    const/4 v0, 5
    iget-object v1, p6, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 708
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    iget-object p6, p6, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { p2, v1, p6 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object p6
  .line 707
    invoke-direct { p0, p1, v0, p6 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L3
  :L4
  .line 709
    new-instance p1, Ljava/lang/StringBuilder;
    invoke-direct { p1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string p2, "daily feature="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string p2, " account="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, p5 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string p2, " params="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-static { p4 }, Lcom/project7/localmanager/BsonLite;->debugDocument([B)Ljava/lang/String;
    move-result-object p2
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p1
    const-string p2, "Project7Gateway"
    invoke-static { p2, p1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 710
    const/4 p1, 1
    return p1
  :L5
  .line 712
    return v0
  :L6
  .line 703
    return v0
.end method

.method private handleDayRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)Z
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 28
  .line 2317
    move-object/from16 v6, p0
    move-object/from16 v7, p1
    move-object/from16 v8, p2
    move-object/from16 v0, p3
    move-object/from16 v1, p4
    move-object/from16 v2, p5
    move-object/from16 v3, p6
    move-object/from16 v5, p7
    const-string v4, "statusCheck"
    invoke-static { v4 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v4
    invoke-static { v0, v4 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v4
    const-string v9, "Project7Gateway"
    const/4 v10, 5
    const/4 v11, 0
    const/4 v12, 1
    if-eqz v4, :L12
  .line 2318
    const-string v0, "s"
    invoke-static { v1, v0 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v13
  .line 2319
    iget-object v1, v6, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v1, v2, v3 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v14
  .line 2320
    const-string v15, "nextday"
    invoke-virtual { v15, v13 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L0
    invoke-static { v14, v3 }, Lcom/project7/localmanager/LocalEconomyEngine;->nextDayBlocker([BLcom/project7/localmanager/LocalTutorialStore$Progress;)Ljava/lang/String;
    move-result-object v1
    goto :L1
  :L0
    const/4 v1, 0
  :L1
    move-object/from16 v16, v1
  .line 2321
    const-string v1, "statusCheckReply"
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    const/4 v4, 4
    new-array v2, v4, [Ljava/lang/Object;
    const-string v17, "r"
    aput-object v17, v2, v11
  .line 2322
    const-string v17, "ok"
    if-nez v16, :L2
    move-object/from16 v18, v17
    goto :L3
  :L2
    const-string v18, "blocked"
  :L3
    aput-object v18, v2, v12
    const/4 v12, 2
    aput-object v0, v2, v12
    if-nez v13, :L4
    const-string v0, ""
    goto :L5
  :L4
    move-object v0, v13
  :L5
    const/16 v19, 3
    aput-object v0, v2, v19
    invoke-static { v2 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v0
  .line 2321
    invoke-static { v8, v1, v0 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
    invoke-direct { v6, v7, v10, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2323
    if-eqz v16, :L6
  .line 2324
    const-string v0, "showMessageStr"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
    new-array v1, v12, [Ljava/lang/Object;
    const-string v2, "m"
    aput-object v2, v1, v11
    const/4 v2, 1
    aput-object v16, v1, v2
    invoke-static { v1 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v1
  .line 2323
    invoke-static { v8, v0, v1 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
    invoke-direct { v6, v7, v10, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L6
  .line 2325
    if-eqz v16, :L7
    move-object/from16 v0, p0
    move-object/from16 v1, p1
    move-object/from16 v2, p2
    move-object/from16 v3, p6
    move v10, v4
    move-object v4, v14
    move-object/from16 v5, p7
    invoke-direct/range { v0 .. v5 }, Lcom/project7/localmanager/LocalGatewayServer;->restorePendingPatrol(Ljava/io/OutputStream;[BLcom/project7/localmanager/LocalTutorialStore$Progress;[BLcom/project7/localmanager/LocalEventEngine;)V
    goto :L8
  :L7
    move v10, v4
  :L8
  .line 2326
    invoke-virtual { v15, v13 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L9
    invoke-static { v14 }, Lcom/project7/localmanager/LocalEconomyEngine;->hasDailySettlement([B)Z
    move-result v0
    if-eqz v0, :L9
  .line 2327
    const-string v0, "weeknum"
    invoke-static { v14, v0 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v0
  .line 2328
    nop
  .line 2329
    const-string v1, "showDailySettlement"
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    new-array v2, v10, [Ljava/lang/Object;
    const-string v3, "c"
    aput-object v3, v2, v11
    invoke-static { v0, v3 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v3
    const/4 v4, 1
    aput-object v3, v2, v4
    const-string v3, "l"
    aput-object v3, v2, v12
  .line 2330
    invoke-static { v0, v3 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v0
    aput-object v0, v2, v19
  .line 2329
    invoke-static { v2 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v0
  .line 2328
    invoke-static { v8, v1, v0 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
    const/4 v1, 5
    invoke-direct { v6, v7, v1, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L9
  .line 2332
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "status check="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v13 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v1, " result="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    if-nez v16, :L10
    move-object/from16 v1, v17
    goto :L11
  :L10
    move-object/from16 v1, v16
  :L11
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v9, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 2333
    const/4 v0, 1
    return v0
  :L12
  .line 2335
    const-string v4, "canteenRequest"
    invoke-static { v4 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v10
    invoke-static { v0, v10 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v0
    if-nez v0, :L13
    return v11
  :L13
  .line 2336
    iget-object v0, v6, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v0, v2, v4, v1, v3 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateEconomy(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalEconomyEngine$Result;
    move-result-object v0
  .line 2337
    iget-object v1, v6, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v1, v2, v3 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 2338
    iget-object v1, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v1 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v1
  :L14
    invoke-interface { v1 }, Ljava/util/Iterator;->hasNext()Z
    move-result v4
    if-eqz v4, :L15
    invoke-interface { v1 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v4
    check-cast v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v10, v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 2339
    invoke-static { v10 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v10
    iget-object v4, v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v8, v10, v4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v4
  .line 2338
    const/4 v10, 5
    invoke-direct { v6, v7, v10, v4 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L14
  :L15
  .line 2340
    if-eqz v5, :L16
    iget-object v1, v6, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v1, v2, v3 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v1
    invoke-virtual { v5, v1 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  :L16
  .line 2341
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "canteen accepted="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-boolean v2, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->accepted:Z
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    const-string v2, " replay="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-boolean v2, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->replay:Z
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    const-string v2, " reason="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-object v0, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->reason:Ljava/lang/String;
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v9, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 2342
    const/4 v0, 1
    return v0
.end method

.method private handleHomeRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)Z
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 13
  .line 717
    const/4 v0, 0
    if-eqz p5, :L5
    if-nez p6, :L0
    goto :L5
  :L0
  .line 718
    sget-object v1, Lcom/project7/localmanager/LocalHomeEngine;->METHODS:[Ljava/lang/String;
    array-length v2, v1
    move v3, v0
  :L1
    if-ge v3, v2, :L4
    aget-object v4, v1, v3
    invoke-static { v4 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v5
    invoke-static { p3, v5 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v5
    if-eqz v5, :L3
  .line 719
    invoke-static { }, Ljava/lang/System;->nanoTime()J
    move-result-wide v0
  .line 720
    iget-object p3, p0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { p3, p5, v4, p4, p6 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object p3
  .line 721
    const-string p5, "_cbid_"
    invoke-static { p4, p5 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object p4
  .line 720
    invoke-direct { p0, p1, p2, p3, p4 }, Lcom/project7/localmanager/LocalGatewayServer;->emitHomeResult(Ljava/io/OutputStream;[BLcom/project7/localmanager/LocalResourceEngine$Result;Ljava/lang/Integer;)[B
  .line 722
    invoke-static { }, Ljava/lang/System;->nanoTime()J
    move-result-wide p1
    sub-long/2addr p1, v0
    const-wide/32 p3, 1000000
    div-long/2addr p1, p3
  .line 723
    const-wide/16 p3, 250
    cmp-long p3, p1, p3
    if-ltz p3, :L2
    new-instance p3, Ljava/lang/StringBuilder;
    invoke-direct { p3 }, Ljava/lang/StringBuilder;-><init>()V
    const-string p4, "slow home RPC method="
    invoke-virtual { p3, p4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p3, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string p4, " elapsedMs="
    invoke-virtual { p3, p4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p3, p1, p2 }, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;
    invoke-virtual { p3 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p1
    const-string p2, "Project7Gateway"
    invoke-static { p2, p1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;)I
  :L2
  .line 725
    const/4 p1, 1
    return p1
  :L3
  .line 718
    add-int/lit8 v3, v3, 1
    goto :L1
  :L4
  .line 727
    return v0
  :L5
  .line 717
    return v0
.end method

.method private handleReliableRpc(Ljava/io/OutputStream;[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;Ljava/util/Set;Ljava/util/Map;Ljava/util/Set;)V
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Ljava/io/OutputStream;",
      "[B[B",
      "Ljava/lang/String;",
      "Lcom/project7/localmanager/LocalTutorialStore$Progress;",
      "Lcom/project7/localmanager/LocalEventEngine;",
      "Ljava/util/Set<",
      "Ljava/lang/Integer;",
      ">;",
      "Ljava/util/Set<",
      "Ljava/lang/Integer;",
      ">;",
      "Ljava/util/Map<",
      "Ljava/lang/Integer;",
      "Lcom/project7/localmanager/LocalPatrolEngine$Result;",
      ">;",
      "Ljava/util/Set<",
      "Ljava/lang/Integer;",
      ">;)V"
    }
  .end annotation
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .catch Lorg/json/JSONException; { :L138 .. :L139 } :L141
  .catch Lorg/json/JSONException; { :L148 .. :L150 } :L151
  .registers 58
    invoke-static { }, Lcom/project7/localmanager/LocalActionLedger;->clearRequest()V
    move-object/from16 v37, p0
    move-object/from16 v38, p1
    move-object/from16 v39, p2
    move-object/from16 v40, p3
    move-object/from16 v41, p4
    move-object/from16 v42, p5
    move-object/from16 v43, p6
    move-object/from16 v44, p7
    move-object/from16 v45, p8
    move-object/from16 v46, p9
    move-object/from16 p0, p10
  .line 1286
    move-object/from16 v11, v37
    move-object/from16 v12, v38
    move-object/from16 v13, v39
    move-object/from16 v0, v40
    move-object/from16 v8, v41
    move-object/from16 v9, v42
    move-object/from16 v10, v43
    move-object/from16 v14, v44
    move-object/from16 v15, v45
    move-object/from16 v7, v46
    move-object/from16 v6, p0
    invoke-static { }, Ljava/lang/System;->nanoTime()J
    move-result-wide v16
  .line 1287
    const-string v1, "w"
    invoke-static { v0, v1 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v1
  .line 1288
    const-string v5, "Project7Gateway"
    if-nez v1, :L0
  .line 1289
    const-string v0, "reliableRpcCall missing wrapper"
    invoke-static { v5, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;)I
  .line 1290
    invoke-static { }, Lcom/project7/localmanager/LocalActionLedger;->endRequest()V
    return-void
  :L0
  .line 1292
    const-string v2, "r"
    invoke-static { v1, v2 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v4
  .line 1293
    const-string v3, "m"
    invoke-static { v1, v3 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v2
  .line 1294
    const-string v14, "p"
    invoke-static { v1, v14 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v1
  .line 1295
    move-object/from16 v18, v3
    const-string v3, "_cbid_"
    invoke-static { v0, v3 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v3
  .line 1296
    invoke-static { v13, v4, v2, v1, v8 }, Lcom/project7/localmanager/LocalActionLedger;->beginRequest([BLjava/lang/Integer;Ljava/lang/String;[BLjava/lang/String;)V
    if-nez v4, :L1
  .line 1297
    const-string v0, "reliableRpcCall missing sequence"
    invoke-static { v5, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;)I
  .line 1298
    invoke-static { }, Lcom/project7/localmanager/LocalActionLedger;->endRequest()V
    return-void
  :L1
  .line 1301
    nop
  .line 1306
    const-string v0, "reliableRpcAck"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
  .line 1307
    invoke-virtual { v4 }, Ljava/lang/Integer;->intValue()I
    move-result v6
    move-object/from16 v19, v14
    const-string v14, "s"
    invoke-static { v14, v6 }, Lcom/project7/localmanager/BsonLite;->intDocument(Ljava/lang/String;I)[B
    move-result-object v6
  .line 1304
    invoke-static { v13, v0, v6 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
  .line 1301
    const/4 v6, 5
    invoke-direct { v11, v12, v6, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    move-object/from16 v21, v11
    move-object/from16 v22, v12
    move-object/from16 v23, v13
    move-object/from16 v24, v2
    move-object/from16 v25, v1
    move-object/from16 v26, v3
    move-object/from16 v27, v8
    move-object/from16 v28, v9
    move-object/from16 v29, v10
    move-object/from16 v30, v4
    move-object/from16 v31, p0
    invoke-static/range { v21 .. v31 }, Lcom/project7/localmanager/OfflineMechanismGateway;->handleSequencedRequest(Lcom/project7/localmanager/LocalGatewayServer;Ljava/io/OutputStream;[BLjava/lang/String;[BLjava/lang/Integer;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/lang/Integer;Ljava/util/Set;)Z
    move-result v0
    if-eqz v0, :L2
    invoke-static { }, Lcom/project7/localmanager/LocalActionLedger;->endRequest()V
    return-void
  :L2
  .line 1310
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v6, "reliable RPC acknowledged seq="
    invoke-virtual { v0, v6 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v6, " method="
    invoke-virtual { v0, v6 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-object/from16 v20, v14
    const-string v14, " callback="
    invoke-virtual { v0, v14 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v14, " parameters="
    invoke-virtual { v0, v14 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  .line 1314
    const-string v14, "setHeadImage"
    invoke-virtual { v14, v2 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v14
    if-eqz v14, :L3
    const-string v14, "<avatar metadata/image redacted>"
    goto :L4
  :L3
    invoke-static { v1 }, Lcom/project7/localmanager/BsonLite;->debugDocument([B)Ljava/lang/String;
    move-result-object v14
  :L4
    invoke-virtual { v0, v14 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
  .line 1310
    invoke-static { v5, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 1317
    const-string v0, "enterPatrolRequest"
    invoke-virtual { v0, v2 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-nez v0, :L5
    const-string v0, "patrolReward"
    invoke-virtual { v0, v2 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L7
  :L5
  .line 1318
    invoke-interface { v7, v4 }, Ljava/util/Map;->containsKey(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L7
  .line 1319
    if-eqz v3, :L6
    invoke-virtual { v3 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    move-object/from16 p1, v11
    move-object/from16 p2, v12
    move-object/from16 p3, v13
    move/from16 p4, v0
    move-object/from16 p5, v2
    move-object/from16 p6, v41
    move-object/from16 p7, v42
    move-object/from16 p8, v43
    invoke-static/range { p1 .. p8 }, Lcom/project7/localmanager/DreamPatrolReply;->complete(Lcom/project7/localmanager/LocalGatewayServer;Ljava/io/OutputStream;[BILjava/lang/String;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  :L6
  .line 1320
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "duplicate patrol RPC ignored seq="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v6 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v5, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 1321
    invoke-static { }, Lcom/project7/localmanager/LocalActionLedger;->endRequest()V
    return-void
  :L7
  .line 1324
    const-string v0, "combatOfflineRequest"
    invoke-virtual { v0, v2 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    const-string v14, " seq="
    if-eqz v0, :L10
  .line 1325
    nop
  .line 1326
    invoke-virtual { v4 }, Ljava/lang/Integer;->intValue()I
    move-result v0
  .line 1325
    move-object v7, v1
    move-object/from16 v1, v37
    move-object v6, v2
    move-object/from16 v2, v38
    move-object v15, v3
    move-object/from16 v3, v39
    move-object/from16 v22, v14
    move-object v14, v4
    move-object/from16 v4, v41
    move-object v8, v5
    move-object/from16 v5, v42
    move-object/from16 v9, p0
    move-object/from16 v23, v14
    move-object v14, v6
    move-object/from16 v6, v43
    move-object v10, v7
    move-object/from16 v7, v44
    move-object/from16 v24, v8
    move-object/from16 v8, p0
    move v9, v0
    invoke-direct/range { v1 .. v10 }, Lcom/project7/localmanager/LocalGatewayServer;->handleCombatAdmission(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;Ljava/util/Set;I[B)V
  .line 1327
    if-eqz v15, :L8
    invoke-virtual { v15 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    move-object/from16 p1, v11
    move-object/from16 p2, v12
    move-object/from16 p3, v13
    move/from16 p4, v0
    move-object/from16 p5, v14
    move-object/from16 p6, v41
    move-object/from16 p7, v42
    move-object/from16 p8, v43
    invoke-static/range { p1 .. p8 }, Lcom/project7/localmanager/DreamPatrolReply;->complete(Lcom/project7/localmanager/LocalGatewayServer;Ljava/io/OutputStream;[BILjava/lang/String;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  :L8
  .line 1328
    iget-object v0, v11, Lcom/project7/localmanager/LocalGatewayServer;->listener:Lcom/project7/localmanager/LocalGatewayServer$StatusListener;
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "\u5df2\u5904\u7406\u4e1a\u52a1 RPC\uff1a"
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v14 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v2, "\n\u5e8f\u53f7\uff1a"
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-object/from16 v5, v23
    invoke-virtual { v1, v5 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    const/4 v2, 1
    invoke-interface { v0, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer$StatusListener;->onStatus(ZLjava/lang/String;)V
  .line 1329
    invoke-static { }, Ljava/lang/System;->nanoTime()J
    move-result-wide v0
    sub-long v0, v0, v16
    const-wide/32 v2, 1000000
    div-long/2addr v0, v2
  .line 1330
    const-wide/16 v2, 250
    cmp-long v2, v0, v2
    if-ltz v2, :L9
    new-instance v2, Ljava/lang/StringBuilder;
    invoke-direct { v2 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v3, "slow reliable RPC method="
    invoke-virtual { v2, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v2, v14 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-object/from16 v4, v22
    invoke-virtual { v2, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v2, v5 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v3, " elapsedMs="
    invoke-virtual { v2, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v2, v0, v1 }, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;
    invoke-virtual { v2 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    move-object/from16 v3, v24
    invoke-static { v3, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;)I
  :L9
  .line 1332
    invoke-static { }, Lcom/project7/localmanager/LocalActionLedger;->endRequest()V
    return-void
  :L10
  .line 1335
    move-object/from16 v0, p0
    move-object v15, v3
    move-object v3, v5
    move-object v5, v4
    move-object v4, v14
    move-object v14, v2
    move-object v2, v1
    const-string v1, "setChooseHeroes"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    const-string v10, "puzzleRoomGetClue"
    if-nez v1, :L13
  .line 1336
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGuildShopEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L11
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGuildEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L11
    invoke-static { v14 }, Lcom/project7/localmanager/LocalWhiteNightEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L11
    invoke-static { v14 }, Lcom/project7/localmanager/LocalCommerceEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L11
    invoke-static { v14 }, Lcom/project7/localmanager/LocalMailEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L11
    invoke-static { v14 }, Lcom/project7/localmanager/LocalDrawEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L11
  .line 1337
    invoke-static { v14 }, Lcom/project7/localmanager/LocalTreasurePlanEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L11
    invoke-static { v14 }, Lcom/project7/localmanager/LocalEquipmentEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L11
  .line 1338
    invoke-static { v14 }, Lcom/project7/localmanager/LocalTreasureUpgradeEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L11
  .line 1339
    invoke-static { v14 }, Lcom/project7/localmanager/LocalTreasureOperationEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L11
  .line 1340
    invoke-static { v14 }, Lcom/project7/localmanager/LocalMemoryExchangeEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L11
  .line 1341
    invoke-virtual { v10, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L11
  .line 1342
    const-string v1, "setHeadImage"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L11
    const-string v1, "setImgState"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L11
  .line 1343
    invoke-static { v14 }, Lcom/project7/localmanager/LocalArtifactEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L11
    invoke-static { v14 }, Lcom/project7/localmanager/LocalSkinDyeEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L11
  .line 1344
    invoke-static { v14 }, Lcom/project7/localmanager/LocalHeroGrowthEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L11
    invoke-static { v14 }, Lcom/project7/localmanager/LocalHeroLiberateEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L11
  .line 1345
    invoke-static { v14 }, Lcom/project7/localmanager/LocalHeroAwakeEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L11
    const-string v1, "set_hero_shoucang"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L11
  .line 1346
    const-string v1, "getGiftCardReward"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L11
    const-string v1, "monthCardGetFudaiReward"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L11
  .line 1347
    const-string v1, "requestGetCurMonHead"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L11
    const-string v1, "rewardAchievement"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L11
  .line 1348
    const-string v1, "requestNewAchievementReward"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L11
    const-string v1, "requestNewAchievementAutoShow"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L13
  :L11
  .line 1349
    invoke-interface { v0, v5 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L13
  .line 1350
    if-eqz v15, :L12
    invoke-virtual { v15 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    move-object/from16 p1, v11
    move-object/from16 p2, v12
    move-object/from16 p3, v13
    move/from16 p4, v0
    move-object/from16 p5, v14
    move-object/from16 p6, v41
    move-object/from16 p7, v42
    move-object/from16 p8, v43
    invoke-static/range { p1 .. p8 }, Lcom/project7/localmanager/DreamPatrolReply;->complete(Lcom/project7/localmanager/LocalGatewayServer;Ljava/io/OutputStream;[BILjava/lang/String;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  :L12
  .line 1351
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "duplicate commerce RPC ignored seq="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v5 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v6 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v14 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v3, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 1352
    invoke-static { }, Lcom/project7/localmanager/LocalActionLedger;->endRequest()V
    return-void
  :L13
  .line 1354
    nop
  .line 1355
    const/16 v22, 0
    const/4 v1, 0
    if-eqz v14, :L21
    invoke-static { v14 }, Lcom/project7/localmanager/LocalHomeEngine;->handles(Ljava/lang/String;)Z
    move-result v24
    if-eqz v24, :L21
  .line 1356
    iget-object v6, v11, Lcom/project7/localmanager/LocalGatewayServer;->homeCallbacks:Ljava/lang/ThreadLocal;
    invoke-virtual { v6 }, Ljava/lang/ThreadLocal;->get()Ljava/lang/Object;
    move-result-object v6
    check-cast v6, Lcom/project7/localmanager/LocalGatewayServer$HomeCallbacks;
  .line 1357
    iget-object v7, v6, Lcom/project7/localmanager/LocalGatewayServer$HomeCallbacks;->owner:Ljava/util/Set;
    if-ne v7, v0, :L14
    iget-object v7, v6, Lcom/project7/localmanager/LocalGatewayServer$HomeCallbacks;->account:Ljava/lang/String;
    invoke-static { v7, v8 }, Ljava/util/Objects;->equals(Ljava/lang/Object;Ljava/lang/Object;)Z
    move-result v7
    if-nez v7, :L15
  :L14
  .line 1358
    iput-object v0, v6, Lcom/project7/localmanager/LocalGatewayServer$HomeCallbacks;->owner:Ljava/util/Set;
    iput-object v8, v6, Lcom/project7/localmanager/LocalGatewayServer$HomeCallbacks;->account:Ljava/lang/String;
    iget-object v7, v6, Lcom/project7/localmanager/LocalGatewayServer$HomeCallbacks;->values:Ljava/util/Map;
    invoke-interface { v7 }, Ljava/util/Map;->clear()V
  :L15
  .line 1360
    invoke-interface { v0, v5 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L17
  .line 1361
    iget-object v0, v11, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v0, v8, v14, v2, v9 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v0
  .line 1362
    invoke-direct { v11, v12, v13, v0, v15 }, Lcom/project7/localmanager/LocalGatewayServer;->emitHomeResult(Ljava/io/OutputStream;[BLcom/project7/localmanager/LocalResourceEngine$Result;Ljava/lang/Integer;)[B
    move-result-object v0
  .line 1363
    iget-object v1, v6, Lcom/project7/localmanager/LocalGatewayServer$HomeCallbacks;->values:Ljava/util/Map;
    invoke-interface { v1, v5, v0 }, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
  .line 1364
    iget-object v0, v6, Lcom/project7/localmanager/LocalGatewayServer$HomeCallbacks;->values:Ljava/util/Map;
    invoke-interface { v0 }, Ljava/util/Map;->size()I
    move-result v0
    const/16 v1, 128
    if-le v0, v1, :L16
    iget-object v0, v6, Lcom/project7/localmanager/LocalGatewayServer$HomeCallbacks;->values:Ljava/util/Map;
    iget-object v1, v6, Lcom/project7/localmanager/LocalGatewayServer$HomeCallbacks;->values:Ljava/util/Map;
    invoke-interface { v1 }, Ljava/util/Map;->keySet()Ljava/util/Set;
    move-result-object v1
    invoke-interface { v1 }, Ljava/util/Set;->iterator()Ljava/util/Iterator;
    move-result-object v1
    invoke-interface { v1 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v1
    invoke-interface { v0, v1 }, Ljava/util/Map;->remove(Ljava/lang/Object;)Ljava/lang/Object;
  :L16
  .line 1365
    const/16 v21, 1
    goto :L20
  :L17
    if-eqz v15, :L19
  .line 1366
    iget-object v0, v6, Lcom/project7/localmanager/LocalGatewayServer$HomeCallbacks;->values:Ljava/util/Map;
    invoke-interface { v0, v5 }, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v0
    check-cast v0, [B
  .line 1367
    if-nez v0, :L18
    const/4 v0, 2
    new-array v2, v0, [Ljava/lang/Object;
    const-string v0, "_result_"
    aput-object v0, v2, v1
    invoke-static { v1 }, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
    move-result-object v0
    const/4 v6, 1
    aput-object v0, v2, v6
    invoke-static { v2 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v0
  :L18
  .line 1368
    const-string v2, "serverCallbackCarrier"
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
    const/4 v6, 4
    new-array v6, v6, [Ljava/lang/Object;
    const-string v7, "_r_"
    aput-object v7, v6, v1
    const/16 v21, 1
    aput-object v0, v6, v21
    const-string v0, "_cbid_"
    const/16 v23, 2
    aput-object v0, v6, v23
    const/4 v0, 3
    aput-object v15, v6, v0
  .line 1369
    invoke-static { v6 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v0
  .line 1368
    invoke-static { v13, v2, v0 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
    const/4 v1, 5
    invoke-direct { v11, v12, v1, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L20
  :L19
  .line 1365
    const/16 v21, 1
  :L20
  .line 1371
    nop
  .line 1372
    move-object v8, v4
    move-object v10, v5
    move-object v15, v14
    move/from16 v5, v21
    move-object v14, v3
    move-object/from16 v3, v22
    goto/16 :L200
  :L21
  .line 1355
    const/16 v21, 1
    const/16 v23, 2
    const/16 v24, 5
  .line 1372
    if-eqz v14, :L23
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v25
    move-object/from16 v1, v37
    move-object/from16 v40, v2
    move-object/from16 v2, v38
    move-object/from16 v28, v3
    move-object/from16 v27, v18
    move-object/from16 v3, v39
    move-object/from16 v29, v4
    move-object/from16 v4, v25
    move-object/from16 v30, v5
    move-object/from16 v5, v40
    move-object/from16 v31, v6
    move-object/from16 v6, v41
    move-object/from16 v7, v42
    invoke-direct/range { v1 .. v7 }, Lcom/project7/localmanager/LocalGatewayServer;->handleCombatCancelRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)Z
    move-result v1
    if-eqz v1, :L24
  .line 1374
    const-string v0, "battleStageGiveup"
    invoke-virtual { v0, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L22
    const/4 v0, 1
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object/from16 v4, v40
    move-object/from16 v5, v41
    move-object/from16 v6, v42
    move-object/from16 v7, v43
    move v8, v0
    invoke-direct/range { v1 .. v8 }, Lcom/project7/localmanager/LocalGatewayServer;->finishAbandonedStory(Ljava/io/OutputStream;[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Z)V
  :L22
    move-object/from16 v40, v15
    move-object/from16 v8, v29
    move-object/from16 v10, v30
    move-object v15, v14
    move-object/from16 v14, v28
    goto/16 :L199
  :L23
  .line 1372
    move-object/from16 v40, v2
    move-object/from16 v28, v3
    move-object/from16 v29, v4
    move-object/from16 v30, v5
    move-object/from16 v31, v6
    move-object/from16 v27, v18
  :L24
  .line 1375
    const-string v1, "battleYazhiAsk"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L27
  .line 1376
    move-object/from16 v10, v30
    invoke-interface { v0, v10 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L25
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v4
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object/from16 v5, v40
    move-object/from16 v6, v41
    move-object/from16 v7, v42
    move-object/from16 v8, v43
    move-object/from16 v9, v44
    move-object/from16 v32, v10
    move-object/from16 v10, v45
    invoke-direct/range { v1 .. v10 }, Lcom/project7/localmanager/LocalGatewayServer;->handleSuppressionRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;Ljava/util/Set;)Z
    move-object/from16 v40, v15
    move-object/from16 v8, v29
    move-object/from16 v10, v32
    goto :L26
  :L25
    move-object/from16 v32, v10
    move-object/from16 v40, v15
    move-object/from16 v8, v29
  :L26
    move-object v15, v14
    move-object/from16 v14, v28
    goto/16 :L199
  :L27
  .line 1378
    move-object/from16 v32, v30
    const-string v1, "battleRealFailWithEventMode"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L28
  .line 1379
    const/4 v0, 0
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object/from16 v4, v40
    move-object/from16 v5, v41
    move-object/from16 v6, v42
    move-object/from16 v7, v43
    move v8, v0
    invoke-direct/range { v1 .. v8 }, Lcom/project7/localmanager/LocalGatewayServer;->finishAbandonedStory(Ljava/io/OutputStream;[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Z)V
    move-object/from16 v40, v15
    move-object/from16 v8, v29
    move-object/from16 v10, v32
    move-object v15, v14
    move-object/from16 v14, v28
    goto/16 :L199
  :L28
  .line 1380
    if-eqz v14, :L34
    sget-object v1, Lcom/project7/localmanager/LocalDailyEngine;->METHODS:Ljava/util/List;
    invoke-interface { v1, v14 }, Ljava/util/List;->contains(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L34
  .line 1381
    if-eqz v15, :L29
    invoke-virtual { v15 }, Ljava/lang/Integer;->intValue()I
    move-result v1
    move-object/from16 p1, v11
    move-object/from16 p2, v12
    move-object/from16 p3, v13
    move/from16 p4, v1
    move-object/from16 p5, v14
    move-object/from16 p6, v41
    move-object/from16 p7, v42
    move-object/from16 p8, v43
    invoke-static/range { p1 .. p8 }, Lcom/project7/localmanager/DreamPatrolReply;->complete(Lcom/project7/localmanager/LocalGatewayServer;Ljava/io/OutputStream;[BILjava/lang/String;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
    goto :L30
  :L29
    move-object/from16 v22, v15
  :L30
  .line 1382
    invoke-static { v14 }, Lcom/project7/localmanager/LocalDailyEngine;->repeatableReply(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L31
    move-object/from16 v10, v32
    invoke-interface { v0, v10 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L33
    goto :L32
  :L31
    move-object/from16 v10, v32
  :L32
  .line 1383
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v4
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object/from16 v5, v40
    move-object/from16 v6, v41
    move-object/from16 v7, v42
    invoke-direct/range { v1 .. v7 }, Lcom/project7/localmanager/LocalGatewayServer;->handleDailyRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)Z
  :L33
  .line 1878
    move-object v15, v14
    move/from16 v5, v21
    move-object/from16 v3, v22
    move-object/from16 v14, v28
    move-object/from16 v8, v29
    goto/16 :L200
  :L34
  .line 1380
    move-object/from16 v7, v32
  .line 1384
    if-eqz v14, :L35
    move-object/from16 v6, v40
    invoke-static { v14, v6 }, Lcom/project7/localmanager/LocalSpecialItemEngine;->handles(Ljava/lang/String;[B)Z
    move-result v1
    if-eqz v1, :L36
  .line 1385
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v4
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object v5, v6
    move-object/from16 v6, v41
    move-object v10, v7
    move-object/from16 v7, v42
    move-object/from16 v8, v43
    invoke-direct/range { v1 .. v8 }, Lcom/project7/localmanager/LocalGatewayServer;->handleSpecialItemRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)Z
    move-object/from16 v40, v15
    move-object/from16 v8, v29
    move-object v15, v14
    move-object/from16 v14, v28
    goto/16 :L199
  :L35
  .line 1384
    move-object/from16 v6, v40
  :L36
  .line 1386
    if-eqz v14, :L39
    invoke-static { v14 }, Lcom/project7/localmanager/LocalWeekEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L37
    const-string v1, "updateClientAvatarAsk"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L39
  :L37
  .line 1387
    invoke-interface { v0, v7 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L38
  .line 1388
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v4
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object v5, v6
    move-object/from16 v6, v41
    move-object v10, v7
    move-object/from16 v7, v42
    move-object/from16 v8, v43
    invoke-direct/range { v1 .. v8 }, Lcom/project7/localmanager/LocalGatewayServer;->handleWeekRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)Z
    move-object/from16 v40, v15
    move-object/from16 v8, v29
    move-object v15, v14
    move-object/from16 v14, v28
    goto/16 :L199
  :L38
  .line 1387
    move-object v10, v7
    move-object/from16 v40, v15
    move-object/from16 v8, v29
    move-object v15, v14
    move-object/from16 v14, v28
    goto/16 :L199
  :L39
  .line 1389
    invoke-static { v14 }, Lcom/project7/localmanager/LocalConstructionEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-eqz v1, :L41
  .line 1390
    invoke-interface { v0, v7 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L40
  .line 1391
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v4
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object v5, v6
    move-object/from16 v6, v41
    move-object v10, v7
    move-object/from16 v7, v42
    move-object/from16 v8, v43
    move-object v9, v15
    invoke-direct/range { v1 .. v9 }, Lcom/project7/localmanager/LocalGatewayServer;->handleConstructionRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/lang/Integer;)Z
  .line 1393
    move-object v15, v14
    move/from16 v5, v21
    move-object/from16 v3, v22
    move-object/from16 v14, v28
    move-object/from16 v8, v29
    goto/16 :L200
  :L40
  .line 1390
    move-object v10, v7
    move-object/from16 v40, v15
    move-object/from16 v8, v29
    move-object v15, v14
    move-object/from16 v14, v28
    goto/16 :L199
  :L41
  .line 1395
    if-eqz v14, :L48
    invoke-static { v14 }, Lcom/project7/localmanager/LocalStoryEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-eqz v1, :L48
  .line 1396
    const-string v1, "q7StoryList"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L43
    const-string v1, "findStoryData"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L43
  .line 1397
    const-string v1, "requestStoryHttpInfo"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L43
    const-string v1, "requestSelfStoryHttpInfo"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L42
    goto :L43
  :L42
    const/4 v2, 0
    goto :L44
  :L43
    move/from16 v2, v21
  :L44
  .line 1398
    if-nez v2, :L46
    invoke-interface { v0, v7 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L45
    goto :L46
  :L45
    move-object v10, v7
    goto :L47
  :L46
  .line 1399
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v4
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object v5, v6
    move-object/from16 v6, v41
    move-object v10, v7
    move-object/from16 v7, v42
    move-object/from16 v8, v43
    invoke-direct/range { v1 .. v8 }, Lcom/project7/localmanager/LocalGatewayServer;->handleServiceRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)Z
  :L47
  .line 1400
    move-object/from16 v40, v15
    move-object/from16 v8, v29
    move-object v15, v14
    move-object/from16 v14, v28
    goto/16 :L199
  :L48
    if-eqz v14, :L53
    invoke-static { v14 }, Lcom/project7/localmanager/LocalServiceEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L50
    invoke-static { v14 }, Lcom/project7/localmanager/LocalIntelligenceEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L50
  .line 1401
    invoke-static { v14 }, Lcom/project7/localmanager/LocalCommunityEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L50
    invoke-static { v14 }, Lcom/project7/localmanager/LocalHeroGiftEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L50
    invoke-static { v14 }, Lcom/project7/localmanager/LocalWingDrugEngine;->handles(Ljava/lang/String;)Z
    move-result v1
    if-nez v1, :L50
  .line 1402
    invoke-virtual { v10, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L50
  .line 1403
    const-string v1, "actionRewardRequest"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L50
    const-string v1, "updateSouvenirLevel"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L49
    goto :L50
  :L49
    move-object v10, v7
    goto :L54
  :L50
  .line 1404
    invoke-virtual { v10, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L52
    invoke-interface { v0, v7 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L51
    goto :L52
  :L51
    move-object v10, v7
    move-object/from16 v40, v15
    move-object/from16 v8, v29
    move-object v15, v14
    move-object/from16 v14, v28
    goto/16 :L199
  :L52
  .line 1405
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v4
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object v5, v6
    move-object/from16 v6, v41
    move-object v10, v7
    move-object/from16 v7, v42
    move-object/from16 v8, v43
    invoke-direct/range { v1 .. v8 }, Lcom/project7/localmanager/LocalGatewayServer;->handleServiceRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)Z
    move-object/from16 v40, v15
    move-object/from16 v8, v29
    move-object v15, v14
    move-object/from16 v14, v28
    goto/16 :L199
  :L53
  .line 1400
    move-object v10, v7
  :L54
  .line 1406
    if-eqz v14, :L60
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v4
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object v5, v6
    move-object v7, v6
    move-object/from16 v6, v41
    invoke-direct/range { v1 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->handleResourceRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;)Z
    move-result v1
    if-eqz v1, :L59
  .line 1407
    move-object/from16 v6, v43
    if-eqz v6, :L58
  .line 1408
    if-eqz v15, :L55
  .line 1409
    invoke-virtual { v15 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    move-object/from16 p1, v11
    move-object/from16 p2, v12
    move-object/from16 p3, v13
    move/from16 p4, v0
    move-object/from16 p5, v14
    move-object/from16 p6, v41
    move-object/from16 p7, v42
    move-object/from16 p8, v43
    invoke-static/range { p1 .. p8 }, Lcom/project7/localmanager/DreamPatrolReply;->complete(Lcom/project7/localmanager/LocalGatewayServer;Ljava/io/OutputStream;[BILjava/lang/String;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 1410
    move-object/from16 v3, v22
    goto :L56
  :L55
  .line 1408
    move-object v3, v15
  :L56
  .line 1412
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    invoke-direct { v11, v0, v8, v9, v6 }, Lcom/project7/localmanager/LocalGatewayServer;->refreshResourceProfile([BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 1413
    const-string v0, "requestLuckyDrawFile"
    invoke-virtual { v0, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L57
    const/16 v0, 93
    const-string v1, "card_box"
    invoke-virtual { v6, v0, v1 }, Lcom/project7/localmanager/LocalEventEngine;->beginNewbeeForPanel(ILjava/lang/String;)Z
    move-result v0
    if-eqz v0, :L57
  .line 1414
    iget-object v0, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v0, v8, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  :L57
  .line 1415
    move-object/from16 v4, v45
    move/from16 v5, v21
    invoke-direct { v11, v12, v13, v6, v4 }, Lcom/project7/localmanager/LocalGatewayServer;->triggerPendingNewbees(Ljava/io/OutputStream;[BLcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;)V
    move-object v15, v14
    move-object/from16 v14, v28
    move-object/from16 v8, v29
    goto/16 :L200
  :L58
  .line 1407
    move/from16 v5, v21
    move-object/from16 v40, v15
    move-object/from16 v8, v29
    move-object v15, v14
    move-object/from16 v14, v28
    goto/16 :L199
  :L59
  .line 1406
    move-object/from16 v6, v43
    move-object/from16 v4, v45
    move/from16 v5, v21
    goto :L61
  :L60
    move-object/from16 v4, v45
    move-object v7, v6
    move/from16 v5, v21
    move-object/from16 v6, v43
  :L61
  .line 1417
    if-eqz v14, :L62
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v18
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object v0, v4
    move-object/from16 v4, v18
    move-object/from16 v23, v10
    move v10, v5
    move-object v5, v7
    move-object v10, v6
    move-object/from16 v6, v41
    invoke-direct/range { v1 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->handleBasicRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;)Z
    move-result v1
    if-eqz v1, :L63
    move-object/from16 v40, v15
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    move-object v15, v14
    move-object/from16 v14, v28
    goto/16 :L199
  :L62
    move-object v0, v4
    move-object/from16 v23, v10
    move-object v10, v6
  :L63
  .line 1420
    const-string v1, "incDayWhenNoActionVal"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L197
    const-string v1, "clearCurDailySettlement"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L64
    move-object v7, v8
    move-object/from16 v40, v15
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    move-object v15, v14
    move-object/from16 v14, v28
    goto/16 :L198
  :L64
  .line 1423
    const-string v1, "canteenRequest"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L195
    const-string v1, "statusCheck"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L65
    move-object/from16 v40, v15
    move-object/from16 v10, v23
    move-object/from16 v6, v29
    move-object v15, v14
    move-object/from16 v14, v28
    move-object/from16 v36, v8
    move-object v8, v7
    move-object/from16 v7, v36
    goto/16 :L196
  :L65
  .line 1425
    const-string v1, "zhaiRequest"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L66
  .line 1426
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object/from16 v4, v41
    move-object/from16 v5, v42
    move-object/from16 v6, v43
    invoke-direct/range { v1 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->handleRest(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
    move-object/from16 v40, v15
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    move-object v15, v14
    move-object/from16 v14, v28
    goto/16 :L199
  :L66
  .line 1427
    const-string v1, "statusSwitch"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L71
  .line 1428
    move-object/from16 v6, v20
    invoke-static { v7, v6 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v0
  .line 1429
    if-nez v0, :L67
  .line 1430
    const-string v0, "statusSwitch missing requested status"
    move-object/from16 v5, v28
    invoke-static { v5, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;)I
    goto :L70
  :L67
  .line 1432
    move-object/from16 v5, v28
    const-string v1, "summon"
    invoke-virtual { v1, v0 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L68
    invoke-direct/range { v37 .. v39 }, Lcom/project7/localmanager/LocalGatewayServer;->syncDrawCalendar(Ljava/io/OutputStream;[B)V
  :L68
  .line 1433
    if-eqz v10, :L69
  .line 1434
    invoke-virtual { v10, v0 }, Lcom/project7/localmanager/LocalEventEngine;->updateStatus(Ljava/lang/String;)V
  .line 1435
    iget-object v1, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v1, v8, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  :L69
  .line 1437
    nop
  .line 1442
    const-string v1, "statusSwitchReply"
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
  .line 1443
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->statusSwitchReplyDocument(Ljava/lang/String;)[B
    move-result-object v2
  .line 1440
    invoke-static { v13, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
  .line 1437
    const/4 v4, 5
    invoke-direct { v11, v12, v4, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1446
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "statusSwitch completed status="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v5, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  :L70
  .line 1448
    move-object/from16 v40, v15
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    move-object v15, v14
    move-object v14, v5
    goto/16 :L199
  :L71
    move-object/from16 v6, v20
    move-object/from16 v5, v28
    const/4 v4, 5
    const-string v1, "requestLuckyDrawFile"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L75
  .line 1449
    const-string v1, "t"
    invoke-static { v7, v1 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v1
  .line 1450
    if-nez v1, :L72
    const/4 v1, 1
    goto :L73
  :L72
    invoke-virtual { v1 }, Ljava/lang/Integer;->intValue()I
    move-result v1
  :L73
  .line 1451
    nop
  .line 1456
    const-string v2, "replyLuckyDrawFile"
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
  .line 1457
    const/4 v3, 1
    invoke-static { v3, v1 }, Lcom/project7/localmanager/BsonLite;->luckyDrawFileReplyDocument(ZI)[B
    move-result-object v6
  .line 1454
    invoke-static { v13, v2, v6 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
  .line 1451
    invoke-direct { v11, v12, v4, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1460
    if-eqz v10, :L74
    const/16 v2, 93
    const-string v3, "card_box"
    invoke-virtual { v10, v2, v3 }, Lcom/project7/localmanager/LocalEventEngine;->beginNewbeeForPanel(ILjava/lang/String;)Z
    move-result v2
    if-eqz v2, :L74
  .line 1461
    iget-object v2, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v2, v8, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 1462
    const-string v2, "card-box tutorial activated by lucky draw request event=93"
    invoke-static { v5, v2 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  :L74
  .line 1464
    invoke-direct { v11, v12, v13, v10, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->triggerPendingNewbees(Ljava/io/OutputStream;[BLcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;)V
  .line 1466
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "lucky draw file opened type="
    invoke-virtual { v0, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v5, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 1467
    move-object/from16 v40, v15
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    move-object v15, v14
    move-object v14, v5
    goto/16 :L199
  :L75
    const-string v1, "pullEvents"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    const-string v2, " processing="
    if-eqz v1, :L81
  .line 1468
    if-eqz v10, :L76
    iget-object v1, v11, Lcom/project7/localmanager/LocalGatewayServer;->preparedQuery:Ljava/lang/ThreadLocal;
    invoke-virtual { v1 }, Ljava/lang/ThreadLocal;->get()Ljava/lang/Object;
    move-result-object v1
    if-eq v1, v10, :L76
  .line 1469
    iget-object v1, v11, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v1, v8, v9 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v1
    invoke-virtual { v10, v1 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  :L76
  .line 1470
    if-nez v10, :L77
  .line 1471
    invoke-static { }, Ljava/util/Collections;->emptySet()Ljava/util/Set;
    move-result-object v1
    goto :L78
  :L77
    invoke-virtual/range { v43 .. v43 }, Lcom/project7/localmanager/LocalEventEngine;->availableEvents()Ljava/util/Set;
    move-result-object v1
  :L78
  .line 1472
    if-nez v10, :L79
  .line 1473
    invoke-static { }, Ljava/util/Collections;->emptySet()Ljava/util/Set;
    move-result-object v3
    goto :L80
  :L79
    invoke-virtual/range { v43 .. v43 }, Lcom/project7/localmanager/LocalEventEngine;->processingEvents()Ljava/util/Set;
    move-result-object v3
  :L80
  .line 1474
    nop
  .line 1479
    const-string v6, "pullEventsReply"
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v6
  .line 1480
    invoke-static { v1, v3 }, Lcom/project7/localmanager/BsonLite;->eventListsDocument(Ljava/lang/Iterable;Ljava/lang/Iterable;)[B
    move-result-object v7
  .line 1477
    invoke-static { v13, v6, v7 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v6
  .line 1474
    invoke-direct { v11, v12, v4, v6 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1483
    new-instance v4, Ljava/lang/StringBuilder;
    invoke-direct { v4 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v6, "pullEvents completed available="
    invoke-virtual { v4, v6 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v4, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v4, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v4, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v4 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-static { v5, v1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 1488
    invoke-direct { v11, v12, v13, v10, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->triggerPendingNewbees(Ljava/io/OutputStream;[BLcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;)V
  .line 1490
    move-object/from16 v40, v15
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    move-object v15, v14
    move-object v14, v5
    goto/16 :L199
  :L81
    const-string v1, "triggerExternalEvent"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    const-string v18, "pushEvents"
    const-string v3, "e"
    if-eqz v1, :L86
  .line 1491
    invoke-static { v7, v3 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v0
  .line 1492
    if-eqz v10, :L82
    if-eqz v0, :L82
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v1
    invoke-virtual { v10, v1 }, Lcom/project7/localmanager/LocalEventEngine;->triggerExternalEvent(I)Z
    move-result v1
    if-eqz v1, :L82
    const/4 v1, 1
    goto :L83
  :L82
    const/4 v1, 0
  :L83
  .line 1493
    if-eqz v1, :L84
    iget-object v2, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v2, v8, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  :L84
  .line 1495
    nop
  .line 1496
    const-string v2, "triggerExternalEventReply"
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
    sget-object v3, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
  .line 1495
    invoke-static { v13, v2, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
    invoke-direct { v11, v12, v4, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1497
    if-eqz v1, :L85
  .line 1498
    invoke-static/range { v18 .. v18 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
  .line 1499
    invoke-virtual/range { v43 .. v43 }, Lcom/project7/localmanager/LocalEventEngine;->availableEvents()Ljava/util/Set;
    move-result-object v3
    invoke-virtual/range { v43 .. v43 }, Lcom/project7/localmanager/LocalEventEngine;->processingEvents()Ljava/util/Set;
    move-result-object v6
  .line 1498
    invoke-static { v3, v6 }, Lcom/project7/localmanager/BsonLite;->eventListsDocument(Ljava/lang/Iterable;Ljava/lang/Iterable;)[B
    move-result-object v3
  .line 1497
    invoke-static { v13, v2, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
    invoke-direct { v11, v12, v4, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L85
  .line 1500
    new-instance v2, Ljava/lang/StringBuilder;
    invoke-direct { v2 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v3, "external UI event="
    invoke-virtual { v2, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v2, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v0, " accepted="
    invoke-virtual { v2, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v2, v1 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    invoke-virtual { v2 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v5, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 1501
    move-object/from16 v40, v15
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    move-object v15, v14
    move-object v14, v5
    goto/16 :L199
  :L86
    const-string v1, "startEvent"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    const-string v20, "startEventReply"
    if-eqz v1, :L94
    if-eqz v10, :L94
  .line 1502
    invoke-static { v7, v3 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v0
  .line 1503
    if-eqz v0, :L91
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v1
    invoke-virtual { v10, v1 }, Lcom/project7/localmanager/LocalEventEngine;->startEvent(I)Z
    move-result v1
    if-eqz v1, :L91
  .line 1504
    move-object/from16 v1, v44
    invoke-interface { v1, v0 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
    move-result v18
  .line 1505
    iget-object v1, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v1, v8, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 1506
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v7
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object/from16 v40, v15
    move v15, v4
    move-object/from16 v4, v41
    move-object/from16 v33, v5
    move-object/from16 v5, v42
    move-object v15, v6
    move-object/from16 v6, v43
    invoke-direct/range { v1 .. v7 }, Lcom/project7/localmanager/LocalGatewayServer;->syncPuzzleStart(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;I)V
  .line 1507
    invoke-direct/range { v1 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->syncEventEffects(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 1508
    iget-object v1, v11, Lcom/project7/localmanager/LocalGatewayServer;->eventCatalog:Lcom/project7/localmanager/LocalEventCatalog;
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v2
    invoke-virtual { v1, v2 }, Lcom/project7/localmanager/LocalEventCatalog;->get(I)Lcom/project7/localmanager/LocalEventCatalog$Event;
    move-result-object v1
  .line 1509
    if-eqz v18, :L87
    if-eqz v1, :L87
    iget-boolean v2, v1, Lcom/project7/localmanager/LocalEventCatalog$Event;->autoStart:Z
    if-eqz v2, :L87
    iget-object v1, v1, Lcom/project7/localmanager/LocalEventCatalog$Event;->completeConditions:Ljava/util/Map;
    invoke-interface { v1 }, Ljava/util/Map;->isEmpty()Z
    move-result v1
    if-eqz v1, :L87
  .line 1512
    const-string v1, "evalCode"
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    const/4 v6, 2
    new-array v2, v6, [Ljava/lang/Object;
    const/4 v5, 0
    aput-object v15, v2, v5
  .line 1513
    const-string v3, "if '_q7_install_ui_event_bridge' in globals():\n    _q7_install_ui_event_bridge(type(gg.avatar))\n"
    invoke-static { v3 }, Lcom/project7/localmanager/LocalClientCompatibility;->encode(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v3
    const/4 v4, 1
    aput-object v3, v2, v4
    invoke-static { v2 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v2
  .line 1512
    invoke-static { v13, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
    const/4 v2, 5
    invoke-direct { v11, v12, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L87
  .line 1518
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v1
    const/16 v2, 1043
    if-ne v1, v2, :L88
    if-eqz v18, :L88
  .line 1519
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v6
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object/from16 v4, v41
    move-object/from16 v5, v42
    invoke-direct/range { v1 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->syncTutorialCityState(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;I)V
  :L88
  .line 1520
    nop
  .line 1525
    invoke-static/range { v20 .. v20 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
  .line 1526
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v2
    const/4 v3, 1
    invoke-static { v2, v3 }, Lcom/project7/localmanager/BsonLite;->eventReplyDocument(II)[B
    move-result-object v2
  .line 1523
    invoke-static { v13, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
  .line 1520
    const/4 v2, 5
    invoke-direct { v11, v12, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1529
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    if-eqz v18, :L89
    const-string v2, "tutorial event started event="
    goto :L90
  :L89
  .line 1530
    const-string v2, "tutorial event start replayed event="
  :L90
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
  .line 1529
    move-object/from16 v4, v33
    invoke-static { v4, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
    goto :L92
  :L91
  .line 1503
    move-object v4, v5
    move-object/from16 v40, v15
    const/4 v5, 0
  .line 1531
    if-eqz v0, :L92
  .line 1532
    nop
  .line 1533
    invoke-static/range { v20 .. v20 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v2
    invoke-static { v2, v5 }, Lcom/project7/localmanager/BsonLite;->eventReplyDocument(II)[B
    move-result-object v2
  .line 1532
    invoke-static { v13, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
    const/4 v2, 5
    invoke-direct { v11, v12, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1534
    nop
  .line 1535
    invoke-static/range { v18 .. v18 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    invoke-virtual/range { v43 .. v43 }, Lcom/project7/localmanager/LocalEventEngine;->availableEvents()Ljava/util/Set;
    move-result-object v3
    invoke-virtual/range { v43 .. v43 }, Lcom/project7/localmanager/LocalEventEngine;->processingEvents()Ljava/util/Set;
    move-result-object v5
    invoke-static { v3, v5 }, Lcom/project7/localmanager/BsonLite;->eventListsDocument(Ljava/lang/Iterable;Ljava/lang/Iterable;)[B
    move-result-object v3
  .line 1534
    invoke-static { v13, v1, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
    invoke-direct { v11, v12, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1536
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "story event rejected event="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v0, " blockers="
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual/range { v43 .. v43 }, Lcom/project7/localmanager/LocalEventEngine;->blockedStoryEvents()Ljava/util/List;
    move-result-object v0
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v4, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
    goto :L93
  :L92
  .line 1531
    nop
  :L93
  .line 1538
    move-object v15, v14
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    move-object v14, v4
    goto/16 :L199
  :L94
  .line 1501
    move-object/from16 v1, v44
    move-object v4, v5
    move-object/from16 v40, v15
    const/4 v5, 0
    move-object v15, v6
    move-object/from16 v6, v19
  .line 1538
    const-string v5, "reliableEcho"
    invoke-virtual { v5, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v5
    if-eqz v5, :L95
  .line 1540
    const-string v0, "native reliable echo barrier"
    invoke-static { v4, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
    move-object v15, v14
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    move-object v14, v4
    goto/16 :L199
  :L95
  .line 1541
    const-string v5, "q7CompleteUiEvent"
    invoke-virtual { v5, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v5
    const-string v19, "completeEventReplyEnd"
    const-string v24, "completeEventReplyStart"
    if-eqz v5, :L98
    if-eqz v10, :L98
  .line 1542
    invoke-static { v7, v3 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v0
  .line 1543
    if-eqz v0, :L96
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v3
    invoke-virtual { v10, v3 }, Lcom/project7/localmanager/LocalEventEngine;->completeImmediateEvent(I)Z
    move-result v3
    if-eqz v3, :L96
  .line 1544
    iget-object v2, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v2, v8, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 1545
    nop
  .line 1546
    invoke-static/range { v24 .. v24 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v3
    invoke-static { v3 }, Lcom/project7/localmanager/BsonLite;->eventRewardDocument(I)[B
    move-result-object v3
  .line 1545
    invoke-static { v13, v2, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
    const/4 v3, 5
    invoke-direct { v11, v12, v3, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1547
    nop
  .line 1548
    invoke-static/range { v19 .. v19 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v5
    invoke-static { v5 }, Lcom/project7/localmanager/BsonLite;->eventDocument(I)[B
    move-result-object v5
  .line 1547
    invoke-static { v13, v2, v5 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
    invoke-direct { v11, v12, v3, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1549
    invoke-interface { v1, v0 }, Ljava/util/Set;->remove(Ljava/lang/Object;)Z
  .line 1550
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object v7, v4
    move-object/from16 v4, v41
    move-object/from16 v5, v42
    move-object/from16 v6, v43
    invoke-direct/range { v1 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->syncEventEffects(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 1551
    invoke-static/range { v18 .. v18 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
  .line 1552
    invoke-virtual/range { v43 .. v43 }, Lcom/project7/localmanager/LocalEventEngine;->availableEvents()Ljava/util/Set;
    move-result-object v2
    invoke-virtual/range { v43 .. v43 }, Lcom/project7/localmanager/LocalEventEngine;->processingEvents()Ljava/util/Set;
    move-result-object v3
    invoke-static { v2, v3 }, Lcom/project7/localmanager/BsonLite;->eventListsDocument(Ljava/lang/Iterable;Ljava/lang/Iterable;)[B
    move-result-object v2
  .line 1551
    invoke-static { v13, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
    const/4 v2, 5
    invoke-direct { v11, v12, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1553
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "UI-only event completed after native UI event="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v7, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
    goto :L97
  :L96
  .line 1543
    move-object v7, v4
  .line 1555
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v3, "UI-only event acknowledgement ignored event="
    invoke-virtual { v1, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  .line 1556
    invoke-virtual/range { v43 .. v43 }, Lcom/project7/localmanager/LocalEventEngine;->processingEvents()Ljava/util/Set;
    move-result-object v0
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
  .line 1555
    invoke-static { v7, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  :L97
  .line 1558
    move-object v15, v14
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    move-object v14, v7
    goto/16 :L199
  :L98
  .line 1541
    move-object v5, v4
  .line 1558
    const-string v4, "startEventOption"
    invoke-virtual { v4, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v4
    if-eqz v4, :L109
    if-eqz v10, :L109
  .line 1559
    invoke-static { v7, v3 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v0
  .line 1560
    const-string v3, "se"
    invoke-static { v7, v3 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v15
  .line 1561
    const-string v3, "op"
    invoke-static { v7, v3 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v7
  .line 1562
    const-string v6, " selectedEvent="
    if-eqz v0, :L104
    if-eqz v15, :L104
  .line 1563
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v3
    invoke-virtual { v15 }, Ljava/lang/Integer;->intValue()I
    move-result v4
    invoke-virtual { v10, v3, v4 }, Lcom/project7/localmanager/LocalEventEngine;->selectEventOption(II)Z
    move-result v3
    if-eqz v3, :L103
  .line 1564
    move-object v4, v1
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object/from16 v45, v7
    move-object v7, v4
    move-object/from16 v4, v41
    move-object/from16 v34, v5
    move-object/from16 v5, v42
    move-object/from16 v35, v6
    move-object/from16 v6, v43
    invoke-direct/range { v1 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->syncEventEffects(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 1565
    invoke-interface { v7, v0 }, Ljava/util/Set;->remove(Ljava/lang/Object;)Z
  .line 1566
    iget-object v1, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v1, v8, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 1567
    nop
  .line 1572
    invoke-static/range { v24 .. v24 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
  .line 1573
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v2
    invoke-static { v2 }, Lcom/project7/localmanager/BsonLite;->eventRewardDocument(I)[B
    move-result-object v2
  .line 1570
    invoke-static { v13, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
  .line 1567
    const/4 v2, 5
    invoke-direct { v11, v12, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1576
    nop
  .line 1581
    invoke-static/range { v19 .. v19 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
  .line 1582
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v3
    invoke-static { v3 }, Lcom/project7/localmanager/BsonLite;->eventDocument(I)[B
    move-result-object v3
  .line 1579
    invoke-static { v13, v1, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
  .line 1576
    invoke-direct { v11, v12, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1586
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v6
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    invoke-direct/range { v1 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->syncTutorialCityCompletion(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;I)V
  .line 1587
    if-eqz v40, :L99
  .line 1588
    invoke-virtual/range { v40 .. v40 }, Ljava/lang/Integer;->intValue()I
    move-result v1
    move-object/from16 p1, v11
    move-object/from16 p2, v12
    move-object/from16 p3, v13
    move/from16 p4, v1
    move-object/from16 p5, v14
    move-object/from16 p6, v41
    move-object/from16 p7, v42
    move-object/from16 p8, v43
    invoke-static/range { p1 .. p8 }, Lcom/project7/localmanager/DreamPatrolReply;->complete(Lcom/project7/localmanager/LocalGatewayServer;Ljava/io/OutputStream;[BILjava/lang/String;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 1589
    goto :L100
  :L99
  .line 1587
    move-object/from16 v22, v40
  :L100
  .line 1593
    invoke-virtual { v15 }, Ljava/lang/Integer;->intValue()I
    move-result v1
    invoke-virtual { v10, v1 }, Lcom/project7/localmanager/LocalEventEngine;->startEvent(I)Z
    move-result v1
    if-eqz v1, :L101
  .line 1594
    invoke-interface { v7, v15 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
  .line 1595
    iget-object v1, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v1, v8, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 1596
    invoke-virtual { v15 }, Ljava/lang/Integer;->intValue()I
    move-result v7
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object/from16 v4, v41
    move-object/from16 v5, v42
    move-object/from16 v6, v43
    move-object/from16 v8, v45
    invoke-direct/range { v1 .. v7 }, Lcom/project7/localmanager/LocalGatewayServer;->syncPuzzleStart(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;I)V
  .line 1597
    invoke-direct/range { v1 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->syncEventEffects(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 1598
    nop
  .line 1599
    invoke-static/range { v20 .. v20 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
  .line 1600
    invoke-virtual { v15 }, Ljava/lang/Integer;->intValue()I
    move-result v2
    const/4 v3, 1
    invoke-static { v2, v3 }, Lcom/project7/localmanager/BsonLite;->eventReplyDocument(II)[B
    move-result-object v2
  .line 1598
    invoke-static { v13, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
    const/4 v2, 5
    invoke-direct { v11, v12, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L102
  :L101
  .line 1593
    move-object/from16 v8, v45
  :L102
  .line 1602
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "tutorial event option selected event="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-object/from16 v3, v35
    invoke-virtual { v1, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v15 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v0, " option="
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v8 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    move-object/from16 v5, v34
    invoke-static { v5, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
    move-object/from16 v3, v22
    goto :L108
  :L103
  .line 1563
    move-object v3, v6
    move-object v8, v7
    goto :L105
  :L104
  .line 1562
    move-object v3, v6
    move-object v8, v7
  :L105
  .line 1608
    if-eqz v0, :L106
    if-eqz v15, :L106
  .line 1609
    invoke-virtual/range { v43 .. v43 }, Lcom/project7/localmanager/LocalEventEngine;->processingEvents()Ljava/util/Set;
    move-result-object v1
    invoke-interface { v1, v15 }, Ljava/util/Set;->contains(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L106
  .line 1610
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "duplicate tutorial event option ignored event="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v15 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v0, " option="
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v8 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v5, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
    goto :L107
  :L106
  .line 1617
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v4, "tutorial event option rejected event="
    invoke-virtual { v1, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v15 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  .line 1621
    invoke-virtual/range { v43 .. v43 }, Lcom/project7/localmanager/LocalEventEngine;->processingEvents()Ljava/util/Set;
    move-result-object v0
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
  .line 1617
    invoke-static { v5, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;)I
  :L107
  .line 1624
    move-object/from16 v3, v40
  :L108
    move-object v15, v14
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    move-object v14, v5
    const/4 v5, 1
    goto/16 :L200
  :L109
  .line 1558
    move-object v8, v7
    move-object v7, v1
  .line 1624
    const-string v1, "clientTraceProcessingEvent"
    invoke-virtual { v1, v14 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    const-string v2, "c"
    if-eqz v1, :L121
    if-eqz v10, :L121
  .line 1625
    const-string v1, "k"
    invoke-static { v8, v1 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v15
  .line 1626
    const-string v1, "d"
    invoke-static { v8, v1 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v1
  .line 1627
    new-instance v8, Ljava/util/ArrayList;
    invoke-direct { v8 }, Ljava/util/ArrayList;-><init>()V
  .line 1628
    if-nez v1, :L110
    move-object/from16 v3, v22
    goto :L111
  :L110
    invoke-static { v1, v2 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v3
  :L111
  .line 1629
    if-eqz v3, :L112
  .line 1630
    invoke-interface { v8, v3 }, Ljava/util/List;->add(Ljava/lang/Object;)Z
    goto :L113
  :L112
  .line 1631
    if-eqz v1, :L113
  .line 1632
    invoke-static { v1, v2 }, Lcom/project7/localmanager/BsonLite;->intArrayValues([BLjava/lang/String;)Ljava/util/List;
    move-result-object v1
    invoke-interface { v8, v1 }, Ljava/util/List;->addAll(Ljava/util/Collection;)Z
  :L113
  .line 1634
    move-object/from16 v1, v37
    move-object v2, v15
    move-object v3, v8
    move-object/from16 v4, v41
    move-object v6, v5
    move-object/from16 v5, v42
    move-object/from16 v20, v14
    move-object v14, v6
    move-object/from16 v6, v43
    invoke-direct/range { v1 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->closePuzzleBeforeTrace(Ljava/lang/String;Ljava/util/List;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 1635
    invoke-virtual { v10, v15, v8 }, Lcom/project7/localmanager/LocalEventEngine;->trace(Ljava/lang/String;Ljava/util/Collection;)Ljava/util/List;
    move-result-object v18
  .line 1637
    iget-object v1, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    move-object/from16 v6, v41
    invoke-virtual { v1, v6, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 1638
    invoke-interface/range { v18 .. v18 }, Ljava/util/List;->isEmpty()Z
    move-result v1
    if-nez v1, :L116
  .line 1639
    invoke-interface/range { v18 .. v18 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v25
  :L114
    invoke-interface/range { v25 .. v25 }, Ljava/util/Iterator;->hasNext()Z
    move-result v1
    if-eqz v1, :L115
    invoke-interface/range { v25 .. v25 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Ljava/lang/Integer;
  .line 1640
    invoke-virtual { v1 }, Ljava/lang/Integer;->intValue()I
    move-result v2
    invoke-direct { v11, v12, v13, v6, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->sendTutorialHeroReward(Ljava/io/OutputStream;[BLjava/lang/String;I)V
  .line 1641
    nop
  .line 1646
    invoke-static/range { v24 .. v24 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
  .line 1647
    invoke-virtual { v1 }, Ljava/lang/Integer;->intValue()I
    move-result v3
    invoke-static { v3 }, Lcom/project7/localmanager/BsonLite;->eventRewardDocument(I)[B
    move-result-object v3
  .line 1644
    invoke-static { v13, v2, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
  .line 1641
    const/4 v3, 5
    invoke-direct { v11, v12, v3, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1650
    nop
  .line 1655
    invoke-static/range { v19 .. v19 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
  .line 1656
    invoke-virtual { v1 }, Ljava/lang/Integer;->intValue()I
    move-result v4
    invoke-static { v4 }, Lcom/project7/localmanager/BsonLite;->eventDocument(I)[B
    move-result-object v4
  .line 1653
    invoke-static { v13, v2, v4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
  .line 1650
    invoke-direct { v11, v12, v3, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1659
    invoke-interface { v7, v1 }, Ljava/util/Set;->remove(Ljava/lang/Object;)Z
  .line 1660
    new-instance v2, Ljava/lang/StringBuilder;
    invoke-direct { v2 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v3, "event completed event="
    invoke-virtual { v2, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v2, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v3, " condition="
    invoke-virtual { v2, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v2, v15 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v2, v8 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v2 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v2
    invoke-static { v14, v2 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 1661
    invoke-virtual { v1 }, Ljava/lang/Integer;->intValue()I
    move-result v26
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object/from16 v4, v41
    move-object/from16 v5, v42
    move-object v7, v6
    move/from16 v6, v26
    invoke-direct/range { v1 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->syncTutorialCityCompletion(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;I)V
  .line 1662
    move-object v6, v7
    move-object/from16 v7, v44
    goto :L114
  :L115
  .line 1663
    move-object v7, v6
    iget-object v1, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v1, v7, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
    goto :L117
  :L116
  .line 1638
    move-object v7, v6
  :L117
  .line 1666
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object/from16 v4, v41
    move-object/from16 v5, v42
    move-object/from16 v6, v43
    invoke-direct/range { v1 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->syncEventEffects(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 1669
    if-eqz v40, :L118
  .line 1670
    invoke-virtual/range { v40 .. v40 }, Ljava/lang/Integer;->intValue()I
    move-result v1
    move-object/from16 v5, v20
    move-object/from16 p1, v11
    move-object/from16 p2, v12
    move-object/from16 p3, v13
    move/from16 p4, v1
    move-object/from16 p5, v5
    move-object/from16 p6, v41
    move-object/from16 p7, v42
    move-object/from16 p8, v43
    invoke-static/range { p1 .. p8 }, Lcom/project7/localmanager/DreamPatrolReply;->complete(Lcom/project7/localmanager/LocalGatewayServer;Ljava/io/OutputStream;[BILjava/lang/String;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 1671
    move-object/from16 v3, v22
    goto :L119
  :L118
  .line 1669
    move-object/from16 v5, v20
    move-object/from16 v3, v40
  :L119
  .line 1673
    invoke-interface/range { v18 .. v18 }, Ljava/util/List;->isEmpty()Z
    move-result v1
    if-nez v1, :L120
    invoke-direct { v11, v12, v13, v10, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->triggerPendingNewbees(Ljava/io/OutputStream;[BLcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;)V
  :L120
  .line 1675
    move-object v15, v5
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    const/4 v5, 1
    goto/16 :L200
  :L121
  .line 1624
    move-object/from16 v7, v41
    move-object/from16 v36, v14
    move-object v14, v5
    move-object/from16 v5, v36
  .line 1675
    const-string v1, "clientAskTriggerNewbee"
    invoke-virtual { v1, v5 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L128
    if-eqz v9, :L128
  .line 1676
    invoke-static { v8, v3 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v1
  .line 1677
    if-eqz v1, :L122
    if-eqz v10, :L122
    invoke-virtual { v1 }, Ljava/lang/Integer;->intValue()I
    move-result v2
    invoke-virtual { v10, v2 }, Lcom/project7/localmanager/LocalEventEngine;->requestNewbee(I)Z
    move-result v2
    if-eqz v2, :L122
    const/4 v15, 1
    goto :L123
  :L122
    const/4 v15, 0
  :L123
  .line 1678
    if-eqz v15, :L126
  .line 1679
    iget-object v2, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v2, v7, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 1680
    if-eqz v40, :L124
  .line 1681
    invoke-virtual/range { v40 .. v40 }, Ljava/lang/Integer;->intValue()I
    move-result v2
    move-object/from16 p1, v11
    move-object/from16 p2, v12
    move-object/from16 p3, v13
    move/from16 p4, v2
    move-object/from16 p5, v5
    move-object/from16 p6, v41
    move-object/from16 p7, v42
    move-object/from16 p8, v43
    invoke-static/range { p1 .. p8 }, Lcom/project7/localmanager/DreamPatrolReply;->complete(Lcom/project7/localmanager/LocalGatewayServer;Ljava/io/OutputStream;[BILjava/lang/String;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 1682
    move-object/from16 v3, v22
    goto :L125
  :L124
  .line 1680
    move-object/from16 v3, v40
  :L125
  .line 1684
    nop
  .line 1689
    const-string v2, "triggerClientNewbee"
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
  .line 1690
    invoke-virtual { v1 }, Ljava/lang/Integer;->intValue()I
    move-result v4
    invoke-static { v4 }, Lcom/project7/localmanager/BsonLite;->eventDocument(I)[B
    move-result-object v4
  .line 1687
    invoke-static { v13, v2, v4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
  .line 1684
    const/4 v4, 5
    invoke-direct { v11, v12, v4, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1693
    invoke-interface { v0, v1 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
  .line 1694
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "tutorial guidance requested/replayed event="
    invoke-virtual { v0, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v14, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
    goto :L127
  :L126
  .line 1678
    move-object/from16 v3, v40
  :L127
  .line 1696
    move-object v15, v5
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    const/4 v5, 1
    goto/16 :L200
  :L128
    const-string v1, "clientFinishNewbee"
    invoke-virtual { v1, v5 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L135
    if-eqz v9, :L135
  .line 1697
    invoke-static { v8, v3 }, Lcom/project7/localmanager/BsonLite;->intArrayValues([BLjava/lang/String;)Ljava/util/List;
    move-result-object v8
  .line 1698
    if-nez v10, :L129
  .line 1699
    invoke-static { }, Ljava/util/Collections;->emptySet()Ljava/util/Set;
    move-result-object v1
    goto :L130
  :L129
    invoke-virtual { v10, v8 }, Lcom/project7/localmanager/LocalEventEngine;->finishNewbees(Ljava/util/Collection;)Ljava/util/Set;
    move-result-object v1
  :L130
    move-object v15, v1
  .line 1700
    const/16 v1, 190
    invoke-static { v1 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v1
    invoke-interface { v8, v1 }, Ljava/util/List;->contains(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L131
  .line 1701
    iget-object v1, v11, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v1, v7, v9 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->load(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v1
    invoke-static { v1, v9 }, Lcom/project7/localmanager/LocalSouvenirEngine;->recoverShopUnlock([BLcom/project7/localmanager/LocalTutorialStore$Progress;)V
  :L131
  .line 1703
    invoke-interface { v0, v8 }, Ljava/util/Set;->removeAll(Ljava/util/Collection;)Z
  .line 1704
    iget-object v0, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v0, v7, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 1705
    const/16 v0, 20
    invoke-static { v0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v0
    invoke-interface { v8, v0 }, Ljava/util/List;->contains(Ljava/lang/Object;)Z
    move-result v0
    if-nez v0, :L133
    const/16 v0, 27
    invoke-static { v0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v0
    invoke-interface { v8, v0 }, Ljava/util/List;->contains(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L132
    goto :L133
  :L132
    move-object v7, v5
    goto :L134
  :L133
  .line 1706
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object/from16 v4, v41
    move-object v7, v5
    move-object/from16 v5, v42
    move-object/from16 v6, v43
    invoke-direct/range { v1 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->syncEventEffects(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  :L134
  .line 1707
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "tutorial guidance completed events="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v8 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v1, " released="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v15 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v14, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 1709
    move-object v15, v7
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    goto/16 :L199
  :L135
    const-string v0, "checkProcessingEvent"
    invoke-virtual { v0, v5 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L136
    if-eqz v9, :L136
  .line 1710
    nop
  .line 1715
    const-string v0, "triggerProcessingEvent"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
    iget-object v1, v9, Lcom/project7/localmanager/LocalTutorialStore$Progress;->processingNewbees:Ljava/util/Set;
  .line 1716
    const-string v2, "pe"
    invoke-static { v2, v1 }, Lcom/project7/localmanager/BsonLite;->intListDocument(Ljava/lang/String;Ljava/lang/Iterable;)[B
    move-result-object v1
  .line 1713
    invoke-static { v13, v0, v1 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
  .line 1710
    const/4 v1, 5
    invoke-direct { v11, v12, v1, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    move-object v15, v5
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    goto/16 :L199
  :L136
  .line 1719
    const-string v0, "passInitPrologue"
    invoke-virtual { v0, v5 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L137
    if-eqz v9, :L137
  .line 1720
    const/4 v1, 0
    iput-boolean v1, v9, Lcom/project7/localmanager/LocalTutorialStore$Progress;->initPrologue:Z
  .line 1721
    iget-object v0, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v0, v7, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
    move-object v15, v5
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    goto/16 :L199
  :L137
  .line 1722
    const-string v0, "updateEventCondClient"
    invoke-virtual { v0, v5 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    const-string v4, "v"
    if-eqz v0, :L155
    if-eqz v9, :L155
  .line 1723
    invoke-static { v8, v2 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v0
  .line 1724
    if-eqz v0, :L146
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v1
    const/16 v2, 100
    if-ne v1, v2, :L146
    if-eqz v10, :L146
  .line 1725
    invoke-static { v8, v4 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v0
  .line 1726
    nop
  .line 1728
    if-nez v0, :L138
    goto :L140
  :L138
    new-instance v1, Lorg/json/JSONTokener;
    invoke-direct { v1, v0 }, Lorg/json/JSONTokener;-><init>(Ljava/lang/String;)V
    invoke-virtual { v1 }, Lorg/json/JSONTokener;->nextValue()Ljava/lang/Object;
    move-result-object v0
  :L139
    move-object/from16 v22, v0
  :L140
  .line 1731
    move-object/from16 v0, v22
    goto :L142
  :L141
  .line 1729
    move-exception v0
  .line 1730
    const-string v1, "invalid area entrance JSON"
    invoke-static { v14, v1, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    move-object/from16 v0, v22
  :L142
  .line 1732
    instance-of v1, v0, Ljava/lang/String;
    if-eqz v1, :L143
    move-object v1, v0
    check-cast v1, Ljava/lang/String;
  .line 1733
    invoke-virtual { v10, v1 }, Lcom/project7/localmanager/LocalEventEngine;->updateAreaClick(Ljava/lang/String;)Z
    move-result v1
    if-eqz v1, :L143
    const/4 v15, 1
    goto :L144
  :L143
    const/4 v15, 0
  :L144
  .line 1734
    if-eqz v15, :L145
  .line 1735
    iget-object v1, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v1, v7, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  :L145
  .line 1737
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "area entrance condition="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v0, " accepted="
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v15 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    const-string v0, " available="
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  .line 1738
    invoke-virtual/range { v43 .. v43 }, Lcom/project7/localmanager/LocalEventEngine;->availableEvents()Ljava/util/Set;
    move-result-object v0
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v0, " blockers="
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  .line 1739
    invoke-virtual/range { v43 .. v43 }, Lcom/project7/localmanager/LocalEventEngine;->blockedStoryEvents()Ljava/util/List;
    move-result-object v0
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
  .line 1737
    invoke-static { v14, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 1740
    goto :L154
  :L146
    if-eqz v0, :L152
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v1
    const/16 v2, 102
    if-ne v1, v2, :L152
    if-eqz v10, :L152
  .line 1741
    invoke-static { v8, v4 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v0
  .line 1743
    if-nez v0, :L148
  :L147
    move-object/from16 v0, v22
    goto :L149
  :L148
    new-instance v1, Lorg/json/JSONTokener;
    invoke-direct { v1, v0 }, Lorg/json/JSONTokener;-><init>(Ljava/lang/String;)V
    invoke-virtual { v1 }, Lorg/json/JSONTokener;->nextValue()Ljava/lang/Object;
    move-result-object v22
    goto :L147
  :L149
  .line 1744
    instance-of v1, v0, Ljava/lang/Number;
    if-eqz v1, :L150
  .line 1745
    check-cast v0, Ljava/lang/Number;
    invoke-virtual { v0 }, Ljava/lang/Number;->intValue()I
    move-result v0
    invoke-virtual { v10, v0 }, Lcom/project7/localmanager/LocalEventEngine;->updateClientOperation(I)V
  .line 1746
    iget-object v0, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v0, v7, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  :L150
  .line 1750
    goto :L153
  :L151
  .line 1748
    move-exception v0
  .line 1749
    const-string v1, "invalid client operation JSON"
    invoke-static { v14, v1, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    goto :L153
  :L152
  .line 1751
    if-eqz v0, :L153
  .line 1752
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "client:"
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-static { v0 }, Ljava/util/Collections;->singleton(Ljava/lang/Object;)Ljava/util/Set;
    move-result-object v0
    invoke-virtual { v9, v1, v0 }, Lcom/project7/localmanager/LocalTutorialStore$Progress;->recordCondition(Ljava/lang/String;Ljava/util/Collection;)V
  .line 1753
    iget-object v0, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v0, v7, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
    goto :L154
  :L153
  .line 1751
    nop
  :L154
  .line 1755
    move-object v15, v5
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    goto/16 :L199
  :L155
    const-string v0, "enterPlace"
    invoke-virtual { v0, v5 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L157
    if-eqz v10, :L157
  .line 1756
    invoke-static { v8, v6 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v0
  .line 1757
    if-nez v0, :L156
  .line 1758
    invoke-static { v8, v15 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v0
  :L156
  .line 1760
    invoke-virtual { v10, v0 }, Lcom/project7/localmanager/LocalEventEngine;->enterPlace(Ljava/lang/String;)V
  .line 1761
    iget-object v0, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v0, v7, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 1762
    move-object v15, v5
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    goto/16 :L199
  :L157
    const-string v0, "enterPatrolRequest"
    invoke-virtual { v0, v5 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    const-string v6, "aid"
    if-eqz v0, :L181
    if-eqz v10, :L181
  .line 1763
    invoke-static { v8, v6 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v0
  .line 1764
    if-nez v0, :L158
    const/4 v1, 0
    goto :L159
  :L158
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v1
  :L159
  .line 1765
    const-string v0, "hs"
    invoke-static { v8, v0 }, Lcom/project7/localmanager/BsonLite;->intArrayValues([BLjava/lang/String;)Ljava/util/List;
    move-result-object v0
  .line 1766
    iget-object v2, v11, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v2, v7, v9 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v2
  .line 1767
    invoke-static { v9, v2 }, Lcom/project7/localmanager/DreamCoordinator;->hasPendingChoice(Lcom/project7/localmanager/LocalTutorialStore$Progress;[B)Z
    move-result v2
    if-eqz v2, :L160
  .line 1770
    iget v1, v9, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolArea:I
  .line 1771
    new-instance v0, Ljava/util/ArrayList;
    iget-object v2, v9, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolHeroes:Ljava/util/Set;
    invoke-direct { v0, v2 }, Ljava/util/ArrayList;-><init>(Ljava/util/Collection;)V
  .line 1772
    const-string v2, "evalCode"
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
    const/4 v3, 2
    new-array v8, v3, [Ljava/lang/Object;
    const/4 v3, 0
    aput-object v15, v8, v3
  .line 1773
    invoke-static/range { v42 .. v42 }, Lcom/project7/localmanager/LocalPatrolEngine;->pendingContext(Lcom/project7/localmanager/LocalTutorialStore$Progress;)Ljava/lang/String;
    move-result-object v3
    invoke-static { v3 }, Lcom/project7/localmanager/LocalClientCompatibility;->encode(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v3
    const/4 v15, 1
    aput-object v3, v8, v15
    invoke-static { v8 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v3
  .line 1772
    invoke-static { v13, v2, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
    const/4 v3, 5
    invoke-direct { v11, v12, v3, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    move-object v8, v0
    move v15, v1
    goto :L161
  :L160
  .line 1767
    move-object v8, v0
    move v15, v1
  :L161
  .line 1775
    move-object/from16 v3, v46
    move-object/from16 v2, v23
    invoke-interface { v3, v2 }, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Lcom/project7/localmanager/LocalPatrolEngine$Result;
  .line 1776
    if-nez v0, :L169
  .line 1777
    iget-object v0, v11, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v0, v7, v9 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v0
  .line 1778
    invoke-static { v9, v0, v15, v8 }, Lcom/project7/localmanager/DreamCoordinator;->canResume(Lcom/project7/localmanager/LocalTutorialStore$Progress;[BILjava/util/List;)Z
    move-result v1
  .line 1780
    move-object/from16 v23, v2
    iget v2, v9, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolArea:I
    if-nez v2, :L162
    iget-object v2, v9, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolHeroes:Ljava/util/Set;
    iget-object v3, v11, Lcom/project7/localmanager/LocalGatewayServer;->patrolCatalog:Lcom/project7/localmanager/LocalPatrolCatalog;
    invoke-virtual { v10, v15, v2, v3 }, Lcom/project7/localmanager/LocalEventEngine;->patrolEvents(ILjava/util/Collection;Lcom/project7/localmanager/LocalPatrolCatalog;)Ljava/util/List;
    move-result-object v2
    goto :L163
  :L162
    invoke-static { }, Ljava/util/Collections;->emptyList()Ljava/util/List;
    move-result-object v2
  :L163
  .line 1781
    iget v3, v9, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolArea:I
    if-nez v3, :L164
    invoke-interface/range { v46 .. v46 }, Ljava/util/Map;->isEmpty()Z
    move-result v3
    if-eqz v3, :L164
    iget-boolean v3, v9, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolRewardPending:Z
    if-eqz v3, :L164
  .line 1782
    invoke-static { v0 }, Lcom/project7/localmanager/LocalPatrolEngine;->dayKey([B)Ljava/lang/String;
    move-result-object v0
    iget-object v3, v9, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolDay:Ljava/lang/String;
    invoke-virtual { v0, v3 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L164
    iget-object v0, v9, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolEvents:Ljava/util/Set;
  .line 1783
    invoke-interface { v0 }, Ljava/util/Set;->isEmpty()Z
    move-result v0
    if-nez v0, :L164
  .line 1784
    invoke-interface { v2 }, Ljava/util/List;->isEmpty()Z
    move-result v0
    if-nez v0, :L164
    iget-object v0, v9, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolEvents:Ljava/util/Set;
    invoke-interface { v0, v2 }, Ljava/util/Set;->containsAll(Ljava/util/Collection;)Z
    move-result v0
    if-eqz v0, :L164
    iget-object v0, v9, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolHeroes:Ljava/util/Set;
    new-instance v2, Ljava/util/HashSet;
    invoke-direct { v2, v8 }, Ljava/util/HashSet;-><init>(Ljava/util/Collection;)V
  .line 1785
    invoke-interface { v0, v2 }, Ljava/util/Set;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L164
  .line 1786
    invoke-interface { v8 }, Ljava/util/List;->size()I
    move-result v0
    iget-object v2, v9, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolHeroes:Ljava/util/Set;
    invoke-interface { v2 }, Ljava/util/Set;->size()I
    move-result v2
    if-ne v0, v2, :L164
    const/4 v0, 1
    goto :L165
  :L164
    const/4 v0, 0
  :L165
    or-int/2addr v0, v1
  .line 1787
    if-eqz v0, :L166
    new-instance v0, Lcom/project7/localmanager/LocalPatrolEngine$Result;
    new-instance v1, Ljava/util/ArrayList;
    iget-object v2, v9, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolEvents:Ljava/util/Set;
    invoke-direct { v1, v2 }, Ljava/util/ArrayList;-><init>(Ljava/util/Collection;)V
    const-string v2, "resume paid patrol"
    const/4 v3, 1
    invoke-direct { v0, v3, v1, v2 }, Lcom/project7/localmanager/LocalPatrolEngine$Result;-><init>(ZLjava/util/List;Ljava/lang/String;)V
    move-object/from16 v19, v4
    move-object/from16 v24, v14
    move-object/from16 v10, v23
    const/16 v20, 0
    move-object/from16 v14, v46
    move/from16 v23, v15
    move-object v15, v5
    goto :L168
  :L166
  .line 1789
    iget-boolean v0, v9, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolRewardPending:Z
    if-eqz v0, :L167
    new-instance v0, Lcom/project7/localmanager/LocalPatrolEngine$Result;
  .line 1790
    invoke-static { }, Ljava/util/Collections;->emptyList()Ljava/util/List;
    move-result-object v1
    const-string v2, "\u8bf7\u5148\u5b8c\u6210\u5f53\u524d\u5de1\u67e5"
    const/4 v3, 0
    invoke-direct { v0, v3, v1, v2 }, Lcom/project7/localmanager/LocalPatrolEngine$Result;-><init>(ZLjava/util/List;Ljava/lang/String;)V
    move/from16 v20, v3
    move-object/from16 v19, v4
    move-object/from16 v24, v14
    move-object/from16 v10, v23
    move-object/from16 v14, v46
    move/from16 v23, v15
    move-object v15, v5
    goto :L168
  :L167
    const/4 v3, 0
    iget-object v0, v11, Lcom/project7/localmanager/LocalGatewayServer;->patrolCatalog:Lcom/project7/localmanager/LocalPatrolCatalog;
    iget-object v1, v11, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
  .line 1791
    invoke-interface { v1, v7, v9 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->load(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v19
  .line 1790
    move-object/from16 v1, v42
    move-object/from16 v10, v23
    move-object/from16 v2, v43
    move/from16 v20, v3
    move-object/from16 v24, v14
    move-object/from16 v14, v46
    move-object/from16 v3, v19
    move-object/from16 v19, v4
    move v4, v15
    move/from16 v23, v15
    move-object v15, v5
    move-object v5, v8
    move-object/from16 p1, v0
    move-object/from16 p2, v1
    move-object/from16 p3, v2
    move-object/from16 p4, v3
    move/from16 p5, v4
    move-object/from16 p6, v5
    move-object/from16 p7, v11
    move-object/from16 p8, v7
    invoke-static/range { p1 .. p8 }, Lcom/project7/localmanager/DreamPatrolGatewayHooks;->begin(Lcom/project7/localmanager/LocalPatrolCatalog;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;[BILjava/util/List;Lcom/project7/localmanager/LocalGatewayServer;Ljava/lang/String;)Lcom/project7/localmanager/LocalPatrolEngine$Result;
    move-result-object v0
  :L168
  .line 1792
    iget-object v1, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
  .line 1793
    invoke-interface { v14, v10, v0 }, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    goto :L170
  :L169
  .line 1776
    move-object v10, v2
    move-object/from16 v19, v4
    move-object/from16 v24, v14
    move/from16 v23, v15
    const/16 v20, 0
    move-object v15, v5
  :L170
  .line 1796
    if-eqz v40, :L171
  .line 1797
    invoke-virtual/range { v40 .. v40 }, Ljava/lang/Integer;->intValue()I
    move-result v1
    move-object/from16 p1, v11
    move-object/from16 p2, v12
    move-object/from16 p3, v13
    move/from16 p4, v1
    move-object/from16 p5, v15
    move-object/from16 p6, v41
    move-object/from16 p7, v42
    move-object/from16 p8, v43
    invoke-static/range { p1 .. p8 }, Lcom/project7/localmanager/DreamPatrolReply;->complete(Lcom/project7/localmanager/LocalGatewayServer;Ljava/io/OutputStream;[BILjava/lang/String;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 1798
    move-object/from16 v3, v22
    goto :L172
  :L171
  .line 1796
    move-object/from16 v3, v40
  :L172
  .line 1800
    iget-boolean v1, v0, Lcom/project7/localmanager/LocalPatrolEngine$Result;->success:Z
    if-eqz v1, :L178
  .line 1801
    iget-object v1, v11, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    const/4 v2, 2
    new-array v4, v2, [Ljava/lang/Object;
    aput-object v6, v4, v20
  .line 1802
    invoke-static/range { v23 .. v23 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v2
    const/4 v5, 1
    aput-object v2, v4, v5
    invoke-static { v4 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v2
  .line 1801
    const-string v4, "q7RecordPatrolAchievement"
    invoke-interface { v1, v7, v4, v2, v9 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v1
  .line 1803
    iget-object v2, v1, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v2 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v2
  :L173
    invoke-interface { v2 }, Ljava/util/Iterator;->hasNext()Z
    move-result v4
    if-eqz v4, :L174
    invoke-interface { v2 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v4
    check-cast v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v5, v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 1804
    invoke-static { v5 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v5
    iget-object v4, v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v13, v5, v4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v4
  .line 1803
    const/4 v5, 5
    invoke-direct { v11, v12, v5, v4 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L173
  :L174
  .line 1805
    invoke-static { v1 }, Lcom/project7/localmanager/LocalStoryProgressDelivery;->sent(Lcom/project7/localmanager/LocalResourceEngine$Result;)[B
    move-result-object v1
  .line 1806
    invoke-static { v1 }, Lcom/project7/localmanager/BsonLite;->keys([B)Ljava/util/List;
    move-result-object v2
    invoke-interface { v2 }, Ljava/util/List;->isEmpty()Z
    move-result v2
    if-nez v2, :L175
    iget-object v2, v11, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    const-string v4, "q7AckStoryProgress"
    invoke-interface { v2, v7, v4, v1, v9 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
  :L175
  .line 1807
    const-string v1, "syncSandglass"
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    const/4 v2, 2
    new-array v2, v2, [Ljava/lang/Object;
    aput-object v19, v2, v20
    iget-object v4, v11, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
  .line 1808
    invoke-interface { v4, v7, v9 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->load(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v4
    invoke-static { v4, v9 }, Lcom/project7/localmanager/LocalEconomyEngine;->sandglass([BLcom/project7/localmanager/LocalTutorialStore$Progress;)I
    move-result v4
    invoke-static { v4 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v4
    const/4 v5, 1
    aput-object v4, v2, v5
    invoke-static { v2 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v2
  .line 1807
    invoke-static { v13, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
    const/4 v2, 5
    invoke-direct { v11, v12, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1809
    nop
  .line 1810
    const-string v1, "get_city_data_reply"
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    iget-object v4, v11, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v4, v7, v9 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->load(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v4
    invoke-static { v9, v4 }, Lcom/project7/localmanager/BsonLite;->cityDataReplyDocument(Lcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
    move-result-object v4
  .line 1809
    invoke-static { v13, v1, v4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
    invoke-direct { v11, v12, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1811
    invoke-interface { v8 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v1
  :L176
    invoke-interface { v1 }, Ljava/util/Iterator;->hasNext()Z
    move-result v2
    if-eqz v2, :L178
    invoke-interface { v1 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Ljava/lang/Integer;
  .line 1812
    iget-object v4, v9, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolFatigue:Ljava/util/Map;
    invoke-interface { v4, v2 }, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v4
    check-cast v4, Ljava/lang/Integer;
  .line 1813
    if-eqz v4, :L177
  .line 1814
    const-string v5, "updateCurFatigueValue"
    invoke-static { v5 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v5
    invoke-virtual { v2 }, Ljava/lang/Integer;->intValue()I
    move-result v2
    invoke-virtual { v4 }, Ljava/lang/Integer;->intValue()I
    move-result v4
    invoke-static { v2, v4 }, Lcom/project7/localmanager/BsonLite;->heroValueDocument(II)[B
    move-result-object v2
  .line 1813
    invoke-static { v13, v5, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
    const/4 v4, 5
    invoke-direct { v11, v12, v4, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L177
  .line 1815
    goto :L176
  :L178
  .line 1817
    nop
  .line 1818
    const-string v1, "enter_patrol_reply"
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    iget-boolean v2, v0, Lcom/project7/localmanager/LocalPatrolEngine$Result;->success:Z
    iget-object v4, v0, Lcom/project7/localmanager/LocalPatrolEngine$Result;->events:Ljava/util/List;
    invoke-static { v2, v4 }, Lcom/project7/localmanager/BsonLite;->patrolReplyDocument(ZLjava/lang/Iterable;)[B
    move-result-object v2
  .line 1817
    invoke-static { v13, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
    const/4 v2, 5
    invoke-direct { v11, v12, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1819
    iget-boolean v1, v0, Lcom/project7/localmanager/LocalPatrolEngine$Result;->success:Z
    if-eqz v1, :L179
  .line 1822
    nop
  .line 1823
    invoke-static/range { v18 .. v18 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
  .line 1824
    invoke-virtual/range { v43 .. v43 }, Lcom/project7/localmanager/LocalEventEngine;->availableEvents()Ljava/util/Set;
    move-result-object v2
    invoke-virtual/range { v43 .. v43 }, Lcom/project7/localmanager/LocalEventEngine;->processingEvents()Ljava/util/Set;
    move-result-object v4
  .line 1823
    invoke-static { v2, v4 }, Lcom/project7/localmanager/BsonLite;->eventListsDocument(Ljava/lang/Iterable;Ljava/lang/Iterable;)[B
    move-result-object v2
  .line 1822
    invoke-static { v13, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
    const/4 v2, 5
    invoke-direct { v11, v12, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L179
  .line 1826
    iget-boolean v1, v0, Lcom/project7/localmanager/LocalPatrolEngine$Result;->success:Z
    if-nez v1, :L180
  .line 1827
    nop
  .line 1828
    const-string v1, "showMessageStr"
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    iget-object v2, v0, Lcom/project7/localmanager/LocalPatrolEngine$Result;->reason:Ljava/lang/String;
  .line 1829
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->patrolFailureMessage(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v2
  .line 1828
    move-object/from16 v4, v27
    invoke-static { v4, v2 }, Lcom/project7/localmanager/BsonLite;->stringDocument(Ljava/lang/String;Ljava/lang/String;)[B
    move-result-object v2
  .line 1827
    invoke-static { v13, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
    const/4 v2, 5
    invoke-direct { v11, v12, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L180
  .line 1831
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "patrol completed area="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move/from16 v2, v23
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v2, " heroes="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v8 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v2, " success="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-boolean v2, v0, Lcom/project7/localmanager/LocalPatrolEngine$Result;->success:Z
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    const-string v2, " reason="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-object v2, v0, Lcom/project7/localmanager/LocalPatrolEngine$Result;->reason:Ljava/lang/String;
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v2, " events="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-object v0, v0, Lcom/project7/localmanager/LocalPatrolEngine$Result;->events:Ljava/util/List;
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v0, " actions="
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget v0, v9, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolActions:I
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    move-object/from16 v5, v24
    invoke-static { v5, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 1834
    move-object v14, v5
    move-object/from16 v8, v29
    const/4 v5, 1
    goto/16 :L200
  :L181
  .line 1762
    move-object v15, v5
    move-object v5, v14
    move-object/from16 v10, v23
    const/16 v20, 0
    move-object/from16 v14, v46
  .line 1834
    const-string v0, "patrolReward"
    invoke-virtual { v0, v15 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L190
    if-eqz v9, :L190
  .line 1835
    iget-object v0, v11, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
  .line 1836
    invoke-interface { v0, v7, v9 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->load(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v0
  .line 1835
    move-object/from16 p1, v9
    move-object/from16 p2, v0
    move-object/from16 p3, v11
    move-object/from16 p4, v7
    move-object/from16 p5, v43
    invoke-static/range { p1 .. p5 }, Lcom/project7/localmanager/DreamPatrolGatewayHooks;->claim(Lcom/project7/localmanager/LocalTutorialStore$Progress;[BLcom/project7/localmanager/LocalGatewayServer;Ljava/lang/String;Lcom/project7/localmanager/LocalEventEngine;)Ljava/util/Map;
    move-result-object v0
    if-nez v0, :L182
    move-object/from16 p1, v11
    move-object/from16 p2, v12
    move-object/from16 p3, v13
    move-object/from16 p4, v40
    invoke-static/range { p1 .. p4 }, Lcom/project7/localmanager/DreamPatrolReply;->rejectClaim(Lcom/project7/localmanager/LocalGatewayServer;Ljava/io/OutputStream;[BLjava/lang/Integer;)V
    invoke-static { }, Lcom/project7/localmanager/LocalActionLedger;->endRequest()V
    return-void
  :L182
  .line 1837
    iget-object v1, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
  .line 1838
    new-instance v1, Lcom/project7/localmanager/LocalPatrolEngine$Result;
  .line 1839
    invoke-static { }, Ljava/util/Collections;->emptyList()Ljava/util/List;
    move-result-object v2
    const-string v3, "friendship claimed"
    const/4 v4, 1
    invoke-direct { v1, v4, v2, v3 }, Lcom/project7/localmanager/LocalPatrolEngine$Result;-><init>(ZLjava/util/List;Ljava/lang/String;)V
  .line 1838
    invoke-interface { v14, v10, v1 }, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
  .line 1840
    if-eqz v40, :L183
  .line 1841
    invoke-virtual/range { v40 .. v40 }, Ljava/lang/Integer;->intValue()I
    move-result v1
    move-object/from16 p1, v11
    move-object/from16 p2, v12
    move-object/from16 p3, v13
    move/from16 p4, v1
    move-object/from16 p5, v15
    move-object/from16 p6, v41
    move-object/from16 p7, v42
    move-object/from16 p8, v43
    invoke-static/range { p1 .. p8 }, Lcom/project7/localmanager/DreamPatrolReply;->complete(Lcom/project7/localmanager/LocalGatewayServer;Ljava/io/OutputStream;[BILjava/lang/String;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 1842
    goto :L184
  :L183
  .line 1840
    move-object/from16 v22, v40
  :L184
  .line 1844
    invoke-interface { v0 }, Ljava/util/Map;->keySet()Ljava/util/Set;
    move-result-object v1
    invoke-interface { v1 }, Ljava/util/Set;->iterator()Ljava/util/Iterator;
    move-result-object v1
  :L185
    invoke-interface { v1 }, Ljava/util/Iterator;->hasNext()Z
    move-result v2
    if-eqz v2, :L186
    invoke-interface { v1 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Ljava/lang/Integer;
  .line 1845
    nop
  .line 1846
    const-string v3, "updateFriendlyValue"
    invoke-static { v3 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v3
  .line 1847
    invoke-virtual { v2 }, Ljava/lang/Integer;->intValue()I
    move-result v4
    iget-object v6, v9, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolFriendly:Ljava/util/Map;
    invoke-interface { v6, v2 }, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Ljava/lang/Integer;
    invoke-virtual { v2 }, Ljava/lang/Integer;->intValue()I
    move-result v2
    invoke-static { v4, v2 }, Lcom/project7/localmanager/BsonLite;->heroValueDocument(II)[B
    move-result-object v2
  .line 1845
    invoke-static { v13, v3, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
    const/4 v3, 5
    invoke-direct { v11, v12, v3, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1848
    goto :L185
  :L186
  .line 1849
    invoke-interface { v0 }, Ljava/util/Map;->isEmpty()Z
    move-result v1
    if-nez v1, :L187
  .line 1850
    const-string v1, "notify_add_friendly"
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->friendlyRewardDocument(Ljava/util/Map;)[B
    move-result-object v2
  .line 1849
    invoke-static { v13, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
    const/4 v2, 5
    invoke-direct { v11, v12, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L187
  .line 1851
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "patrol friendship claimed gains="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-static { v5, v1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 1852
    invoke-interface { v0 }, Ljava/util/Map;->isEmpty()Z
    move-result v0
    if-nez v0, :L188
  .line 1853
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object/from16 v4, v41
    move-object v14, v5
    move-object/from16 v5, v42
    move-object/from16 v6, v43
    invoke-direct/range { v1 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->syncEventEffects(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 1854
    iget-object v0, v11, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v0, v7, v9 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 1855
    if-eqz v43, :L189
  .line 1856
    invoke-static/range { v18 .. v18 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
  .line 1857
    invoke-virtual/range { v43 .. v43 }, Lcom/project7/localmanager/LocalEventEngine;->availableEvents()Ljava/util/Set;
    move-result-object v1
    invoke-virtual/range { v43 .. v43 }, Lcom/project7/localmanager/LocalEventEngine;->processingEvents()Ljava/util/Set;
    move-result-object v2
  .line 1856
    invoke-static { v1, v2 }, Lcom/project7/localmanager/BsonLite;->eventListsDocument(Ljava/lang/Iterable;Ljava/lang/Iterable;)[B
    move-result-object v1
  .line 1855
    invoke-static { v13, v0, v1 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
    const/4 v1, 5
    invoke-direct { v11, v12, v1, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L189
  :L188
  .line 1852
    move-object v14, v5
  :L189
  .line 1859
    move-object/from16 v3, v22
    move-object/from16 v8, v29
    const/4 v5, 1
    goto/16 :L200
  :L190
  .line 1834
    move-object v14, v5
  .line 1859
    const-string v0, "getAreaStagesRequest"
    invoke-virtual { v0, v15 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L194
  .line 1860
    invoke-static { v8, v6 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v0
  .line 1861
    invoke-static/range { v42 .. v42 }, Lcom/project7/localmanager/LocalGatewayServer;->isHighSchoolUnlocked(Lcom/project7/localmanager/LocalTutorialStore$Progress;)Z
    move-result v1
    iget-object v2, v11, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v2, v7, v9 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v2
    invoke-static { v0, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->q7QueryAreaAllowed(Ljava/lang/Integer;[B)Z
    move-result v3
  .line 1862
    if-eqz v3, :L191
    invoke-static { v0, v1, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->q7QueryAreaId(Ljava/lang/Integer;Z[B)I
    move-result v0
    goto/32 :L192
  :L191
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    const-string v1, "showMessageStr"
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    const-string v3, "m"
    const-string v4, "\u8be5\u5730\u533a\u6682\u4e0d\u652f\u6301\u67e5\u8be2"
    filled-new-array { v3, v4 }, [Ljava/lang/Object;
    move-result-object v3
    invoke-static { v3 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v2
    invoke-static { v13, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
    const/4 v3, 5
    invoke-direct { v11, v12, v3, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto/32 :L193
  :L192
    nop
  .line 1867
    const-string v1, "get_area_stages_reply"
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
  .line 1868
    invoke-static { v0, v9, v2 }, Lcom/project7/localmanager/BsonLite;->areaStagesReplyDocument(ILcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
    move-result-object v2
  .line 1865
    invoke-static { v13, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
  .line 1862
    const/4 v2, 5
    invoke-direct { v11, v12, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1871
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "area stages completed area="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v14, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  :L193
  .line 1872
    move-object/from16 v8, v29
    goto/16 :L199
  :L194
  .line 1873
    nop
    iget-object v0, v11, Lcom/project7/localmanager/LocalGatewayServer;->unimplementedReliableRpc:Ljava/lang/ThreadLocal;
    const/4 v1, 1
    invoke-static { v1 }, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
    move-result-object v1
    invoke-virtual { v0, v1 }, Ljava/lang/ThreadLocal;->set(Ljava/lang/Object;)V
  .line 1874
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "unimplemented reliable RPC account="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v7 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-object/from16 v1, v31
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v15 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-object/from16 v6, v29
    invoke-virtual { v0, v6 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v10 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v1, " parameters="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  .line 1875
    invoke-static { v8 }, Lcom/project7/localmanager/BsonLite;->debugDocument([B)Ljava/lang/String;
    move-result-object v1
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
  .line 1874
    invoke-static { v14, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;)I
    move-object/from16 v3, v40
    move-object v8, v6
    move/from16 v5, v20
    goto :L200
  :L195
  .line 1423
    move-object/from16 v40, v15
    move-object/from16 v10, v23
    move-object/from16 v6, v29
    move-object v15, v14
    move-object/from16 v14, v28
    move-object/from16 v36, v8
    move-object v8, v7
    move-object/from16 v7, v36
  :L196
  .line 1424
    invoke-static { v15 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v4
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object v5, v8
    move-object v8, v6
    move-object/from16 v6, v41
    move-object/from16 v7, v42
    move-object v9, v8
    move-object/from16 v8, v43
    invoke-direct/range { v1 .. v8 }, Lcom/project7/localmanager/LocalGatewayServer;->handleDayRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)Z
    move-object v8, v9
    goto :L199
  :L197
  .line 1420
    move-object v7, v8
    move-object/from16 v40, v15
    move-object/from16 v10, v23
    move-object/from16 v8, v29
    move-object v15, v14
    move-object/from16 v14, v28
  :L198
  .line 1421
    move-object/from16 v0, p0
    invoke-interface { v0, v10 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L199
  .line 1422
    move-object/from16 v1, v37
    move-object/from16 v2, v38
    move-object/from16 v3, v39
    move-object/from16 v4, v41
    move-object/from16 v5, v42
    move-object/from16 v6, v43
    move-object v7, v15
    invoke-direct/range { v1 .. v7 }, Lcom/project7/localmanager/LocalGatewayServer;->handleCalendar(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/lang/String;)V
  :L199
  .line 1878
    move-object/from16 v3, v40
    const/4 v5, 1
  :L200
    if-eqz v3, :L201
  .line 1879
    invoke-virtual { v3 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    move-object/from16 p1, v11
    move-object/from16 p2, v12
    move-object/from16 p3, v13
    move/from16 p4, v0
    move-object/from16 p5, v15
    move-object/from16 p6, v41
    move-object/from16 p7, v42
    move-object/from16 p8, v43
    invoke-static/range { p1 .. p8 }, Lcom/project7/localmanager/DreamPatrolReply;->complete(Lcom/project7/localmanager/LocalGatewayServer;Ljava/io/OutputStream;[BILjava/lang/String;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  :L201
  .line 1881
    iget-object v0, v11, Lcom/project7/localmanager/LocalGatewayServer;->listener:Lcom/project7/localmanager/LocalGatewayServer$StatusListener;
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    if-eqz v5, :L202
    const-string v2, "\u5df2\u5904\u7406\u4e1a\u52a1 RPC\uff1a"
    goto :L203
  :L202
    const-string v2, "\u4e1a\u52a1 RPC \u5c1a\u672a\u5b9e\u73b0\uff1a"
  :L203
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v15 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v2, "\n\u5e8f\u53f7\uff1a"
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v10 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    const/4 v2, 1
    invoke-interface { v0, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer$StatusListener;->onStatus(ZLjava/lang/String;)V
  .line 1883
    invoke-static { }, Ljava/lang/System;->nanoTime()J
    move-result-wide v0
    sub-long v0, v0, v16
    const-wide/32 v2, 1000000
    div-long/2addr v0, v2
  .line 1884
    const-wide/16 v2, 250
    cmp-long v2, v0, v2
    if-ltz v2, :L204
    new-instance v2, Ljava/lang/StringBuilder;
    invoke-direct { v2 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v3, "slow reliable RPC method="
    invoke-virtual { v2, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v2, v15 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v2, v8 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v2, v10 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v3, " elapsedMs="
    invoke-virtual { v2, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v2, v0, v1 }, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;
    invoke-virtual { v2 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v14, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;)I
  :L204
  .line 1886
    invoke-static { }, Lcom/project7/localmanager/LocalActionLedger;->endRequest()V
    return-void
.end method

.method private handleResourceRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;)Z
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 93
    invoke-static/range { p0 .. p5 }, Lcom/project7/localmanager/CoreGapBridge;->handleResourceRpc(Lcom/project7/localmanager/LocalGatewayServer;Ljava/io/OutputStream;[B[B[BLjava/lang/String;)Z
    move-result v0
    if-eqz v0, :L0
    const/4 v0, 1
    return v0
  :L0
  .line 1096
    move-object/from16 v0, p0
    move-object/from16 v1, p1
    move-object/from16 v2, p2
    move-object/from16 v3, p3
    move-object/from16 v4, p4
    move-object/from16 v5, p5
    const/4 v6, 2
    new-array v7, v6, [[Ljava/lang/String;
    sget-object v8, Lcom/project7/localmanager/LocalGuildEngine;->METHODS:[Ljava/lang/String;
    const/4 v9, 0
    aput-object v8, v7, v9
    sget-object v8, Lcom/project7/localmanager/LocalGuildShopEngine;->METHODS:[Ljava/lang/String;
    const/4 v10, 1
    aput-object v8, v7, v10
    move v8, v9
  :L1
    const/4 v11, 5
    if-ge v8, v6, :L7
    aget-object v12, v7, v8
  .line 1097
    array-length v13, v12
    move v14, v9
  :L2
    if-ge v14, v13, :L6
    aget-object v15, v12, v14
    invoke-static { v15 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v9
    invoke-static { v3, v9 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v9
    if-eqz v9, :L5
  .line 1098
    iget-object v3, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v3, v5, v15, v4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateResources(Ljava/lang/String;Ljava/lang/String;[B)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v3
  .line 1099
    iget-object v3, v3, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v3 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v3
  :L3
    invoke-interface { v3 }, Ljava/util/Iterator;->hasNext()Z
    move-result v4
    if-eqz v4, :L4
    invoke-interface { v3 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v4
    check-cast v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v5, v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 1100
    invoke-static { v5 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v5
    iget-object v4, v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v2, v5, v4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v4
  .line 1099
    invoke-direct { v0, v1, v11, v4 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L3
  :L4
  .line 1101
    return v10
  :L5
  .line 1097
    add-int/lit8 v14, v14, 1
    const/4 v9, 0
    goto :L2
  :L6
  .line 1096
    add-int/lit8 v8, v8, 1
    const/4 v9, 0
    goto :L1
  :L7
  .line 1103
    sget-object v7, Lcom/project7/localmanager/LocalWhiteNightEngine;->METHODS:[Ljava/lang/String;
    array-length v8, v7
    const/4 v9, 0
  :L8
    if-ge v9, v8, :L12
    aget-object v12, v7, v9
    invoke-static { v12 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v13
    invoke-static { v3, v13 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v13
    if-eqz v13, :L11
  .line 1104
    iget-object v3, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v3, v5, v12, v4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateResources(Ljava/lang/String;Ljava/lang/String;[B)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v3
  .line 1105
    iget-object v3, v3, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v3 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v3
  :L9
    invoke-interface { v3 }, Ljava/util/Iterator;->hasNext()Z
    move-result v4
    if-eqz v4, :L10
    invoke-interface { v3 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v4
    check-cast v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v5, v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 1106
    invoke-static { v5 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v5
    iget-object v4, v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v2, v5, v4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v4
  .line 1105
    invoke-direct { v0, v1, v11, v4 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L9
  :L10
  .line 1107
    return v10
  :L11
  .line 1103
    add-int/lit8 v9, v9, 1
    goto :L8
  :L12
  .line 1109
    new-array v7, v6, [[Ljava/lang/String;
    sget-object v8, Lcom/project7/localmanager/LocalArtifactEngine;->METHODS:[Ljava/lang/String;
    const/4 v9, 0
    aput-object v8, v7, v9
    sget-object v8, Lcom/project7/localmanager/LocalSkinDyeEngine;->METHODS:[Ljava/lang/String;
    aput-object v8, v7, v10
    const/4 v9, 0
  :L13
    if-ge v9, v6, :L19
    aget-object v8, v7, v9
  .line 1110
    array-length v12, v8
    const/4 v13, 0
  :L14
    if-ge v13, v12, :L18
    aget-object v14, v8, v13
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v15
    invoke-static { v3, v15 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v15
    if-eqz v15, :L17
  .line 1111
    iget-object v3, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v3, v5, v14, v4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateResources(Ljava/lang/String;Ljava/lang/String;[B)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v3
  .line 1112
    iget-object v3, v3, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v3 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v3
  :L15
    invoke-interface { v3 }, Ljava/util/Iterator;->hasNext()Z
    move-result v4
    if-eqz v4, :L16
    invoke-interface { v3 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v4
    check-cast v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v5, v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 1113
    invoke-static { v5 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v5
    iget-object v4, v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v2, v5, v4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v4
  .line 1112
    invoke-direct { v0, v1, v11, v4 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L15
  :L16
  .line 1114
    return v10
  :L17
  .line 1110
    add-int/lit8 v13, v13, 1
    goto :L14
  :L18
  .line 1109
    add-int/lit8 v9, v9, 1
    goto :L13
  :L19
  .line 1116
    const/16 v6, 71
    const-string v16, "queryMailDetail"
    const-string v17, "readMail"
    const-string v18, "delMail"
    const-string v19, "fetchAttachmentAndDel"
    const-string v20, "fetchAttachmentAndDelBatch"
    const-string v21, "fetchAttachmentAndDelBatch2"
    const-string v22, "requestLuckyDrawFile"
    const-string v23, "requestLuckyDrawCard"
    const-string v24, "requestFile"
    const-string v25, "requestQuitFile"
    const-string v26, "requestLuckyDrawFileAndOpenAll"
    const-string v27, "requestLuckyDrawAllLeftCard"
    const-string v28, "setChooseHeroes"
    const-string v29, "requestLuckyDrawFriendCard"
    const-string v30, "requestLuckyDrawNewFriendCard"
    const-string v31, "requestLuckyDrawFriendLianChouCard"
    const-string v32, "requestLuckyDrawNewFriendLianChouCard"
    const-string v33, "rookieGainRewards"
    const-string v34, "summoncoinExchange"
    const-string v35, "buyCardMallItem"
    const-string v36, "buyMoney"
    const-string v37, "getGiftCardReward"
    const-string v38, "monthCardGetFudaiReward"
    const-string v39, "GiftCardClickEvent"
    const-string v40, "requestGetCurMonHead"
    const-string v41, "rewardAchievement"
    const-string v42, "equipTreasureBatch"
    const-string v43, "unequipTreasure"
    const-string v44, "unequipAllTreasure"
    const-string v45, "unequipTreasureAllHero"
    const-string v46, "incHeroStarOrder"
    const-string v47, "tupoLiberateStage"
    const-string v48, "upgradeLiberate"
    const-string v49, "updateWanwufadian"
    const-string v50, "dressPendant"
    const-string v51, "liberateChange"
    const-string v52, "upgradeAwakeStage"
    const-string v53, "changeAwakeSkinStyle"
    const-string v54, "seeAwakeSkillChanged"
    const-string v55, "changeTreasureForbid"
    const-string v56, "upgradeTreasure"
    const-string v57, "upgradeTreasureTargetLv"
    const-string v58, "upgradeAllTreasure"
    const-string v59, "memoryCrystalExchangeSuipian"
    const-string v60, "decomposeTreasure"
    const-string v61, "smeltTreasure"
    const-string v62, "transferTreasure"
    const-string v63, "composeTreasure"
    const-string v64, "composeTreasureBatch"
    const-string v65, "tupoTreasure"
    const-string v66, "refreshTreasureGoldAsk"
    const-string v67, "refreshTreasureOrangeAsk"
    const-string v68, "refreshTreasureApply"
    const-string v69, "refreshTreasureApplyOrange"
    const-string v70, "upgradeTreasureExp"
    const-string v71, "upgradeTreasureClassByItem"
    const-string v72, "requestItemHotRankList"
    const-string v73, "requestSaveTreasurePlan"
    const-string v74, "removeTreasurePlan"
    const-string v75, "requestUseTreasurePlan"
    const-string v76, "requestUnuseTreasurePlan"
    const-string v77, "dailyCheck"
    const-string v78, "requestMonDailyCheck"
    const-string v79, "requestMonDailyReCheck"
    const-string v80, "reqesutMonDailyTotalReward"
    const-string v81, "requestTaskList"
    const-string v82, "requesGetNewbieTaskReward"
    const-string v83, "requestNewbieTaskNodeReward"
    const-string v84, "updateNewAchievementTaskFromClient"
    const-string v85, "requestNewAchievementReward"
    const-string v86, "requestNewAchievementAutoShow"
    filled-new-array/range { v16 .. v86 }, [Ljava/lang/String;
    move-result-object v7
    const/4 v9, 0
  :L20
    if-ge v9, v6, :L24
    aget-object v8, v7, v9
  .line 1136
    invoke-static { v8 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v12
    invoke-static { v3, v12 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v12
    if-nez v12, :L21
  .line 1116
    add-int/lit8 v9, v9, 1
    goto :L20
  :L21
  .line 1137
    invoke-static { }, Ljava/lang/System;->nanoTime()J
    move-result-wide v6
  .line 1138
    iget-object v3, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v3, v5, v8, v4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateResources(Ljava/lang/String;Ljava/lang/String;[B)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v3
  .line 1139
    iget-object v9, v3, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v9 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v9
  :L22
    invoke-interface { v9 }, Ljava/util/Iterator;->hasNext()Z
    move-result v12
    if-eqz v12, :L23
    invoke-interface { v9 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v12
    check-cast v12, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v13, v12, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 1140
    invoke-static { v13 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v13
    iget-object v12, v12, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v2, v13, v12 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v12
  .line 1139
    invoke-direct { v0, v1, v11, v12 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L22
  :L23
  .line 1141
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "resource RPC account="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v5 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v2, " method="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v8 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v2, " parameters="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  .line 1142
    invoke-static/range { p4 .. p4 }, Lcom/project7/localmanager/BsonLite;->debugDocument([B)Ljava/lang/String;
    move-result-object v2
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v2, " replies="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-object v2, v3, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v2 }, Ljava/util/List;->size()I
    move-result v2
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v2, " elapsedMs="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  .line 1143
    invoke-static { }, Ljava/lang/System;->nanoTime()J
    move-result-wide v2
    sub-long/2addr v2, v6
    const-wide/32 v4, 1000000
    div-long/2addr v2, v4
    invoke-virtual { v1, v2, v3 }, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
  .line 1141
    const-string v2, "Project7Gateway"
    invoke-static { v2, v1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 1144
    return v10
  :L24
  .line 1146
    const/4 v1, 0
    return v1
.end method

.method private handleRest(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 11
  .line 2347
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    sget-object v1, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    const-string v2, "zhaiRequest"
    invoke-interface { v0, p3, v2, v1, p4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateEconomy(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalEconomyEngine$Result;
    move-result-object v0
  .line 2348
    iget-object v1, p0, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v1, p3, p4 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 2349
    iget v1, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->remainingActions:I
    const/4 v2, 5
    if-ltz v1, :L0
  .line 2350
    const-string v1, "get_city_data_reply"
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    iget-object v3, p0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v3, p3, p4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->load(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v3
    invoke-static { p4, v3 }, Lcom/project7/localmanager/BsonLite;->cityDataReplyDocument(Lcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
    move-result-object v3
  .line 2349
    invoke-static { p2, v1, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v1
    invoke-direct { p0, p1, v2, v1 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L0
  .line 2351
    iget-object v1, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v1 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v1
  :L1
    invoke-interface { v1 }, Ljava/util/Iterator;->hasNext()Z
    move-result v3
    if-eqz v3, :L2
    invoke-interface { v1 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v3
    check-cast v3, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v4, v3, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 2352
    invoke-static { v4 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v4
    iget-object v3, v3, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { p2, v4, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v3
  .line 2351
    invoke-direct { p0, p1, v2, v3 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L1
  :L2
  .line 2353
    if-eqz p5, :L3
    iget-object p1, p0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { p1, p3, p4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->load(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object p1
    invoke-virtual { p5, p1 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  :L3
  .line 2354
    new-instance p1, Ljava/lang/StringBuilder;
    invoke-direct { p1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string p2, "rest accepted="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-boolean p2, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->accepted:Z
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    const-string p2, " replay="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-boolean p2, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->replay:Z
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    const-string p2, " reason="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-object p2, v0, Lcom/project7/localmanager/LocalEconomyEngine$Result;->reason:Ljava/lang/String;
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p1
    const-string p2, "Project7Gateway"
    invoke-static { p2, p1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 2355
    return-void
.end method

.method private handleServiceRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)Z
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 42
    invoke-static/range { p0 .. p7 }, Lcom/project7/localmanager/OfflineMechanismGateway;->handleDirect(Lcom/project7/localmanager/LocalGatewayServer;Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)Z
    move-result v0
    if-eqz v0, :L0
    return v0
  :L0
  .line 848
    move-object/from16 v7, p0
    move-object/from16 v8, p1
    move-object/from16 v9, p2
    move-object/from16 v10, p5
    move-object/from16 v11, p6
    move-object/from16 v12, p7
    new-instance v0, Ljava/util/ArrayList;
    const-string v13, "requestRecoverJingshenli"
    const-string v14, "readPendingNote"
    const-string v15, "readPlayerNote"
    const-string v16, "readPrivateMsg"
    const-string v17, "readSocialMsg"
    const-string v18, "replyPrivateMsg"
    const-string v19, "triggerSocialMsgEvent"
    const-string v20, "syncAllIntelligenceRequest"
    const-string v21, "readTodayIntelligence"
    const-string v22, "openIntelligenceRequest"
    const-string v23, "handleIntelligenceRequest"
    const-string v24, "delDestroyBuilding"
    const-string v25, "actionRewardRequest"
    const-string v26, "updateSouvenirLevel"
    const-string v27, "tryGiftToHero"
    const-string v28, "puzzleRoomGetClue"
    const-string v29, "dailyPureChooseHero"
    const-string v30, "requestFlashbackIncDay"
    filled-new-array/range { v13 .. v30 }, [Ljava/lang/String;
    move-result-object v1
    invoke-static { v1 }, Ljava/util/Arrays;->asList([Ljava/lang/Object;)Ljava/util/List;
    move-result-object v1
    invoke-direct { v0, v1 }, Ljava/util/ArrayList;-><init>(Ljava/util/Collection;)V
  .line 852
    sget-object v1, Lcom/project7/localmanager/LocalCommunityEngine;->METHODS:[Ljava/lang/String;
    invoke-static { v1 }, Ljava/util/Arrays;->asList([Ljava/lang/Object;)Ljava/util/List;
    move-result-object v1
    invoke-interface { v0, v1 }, Ljava/util/List;->addAll(Ljava/util/Collection;)Z
  .line 853
    sget-object v1, Lcom/project7/localmanager/LocalStoryEngine;->METHODS:[Ljava/lang/String;
    invoke-static { v1 }, Ljava/util/Arrays;->asList([Ljava/lang/Object;)Ljava/util/List;
    move-result-object v1
    invoke-interface { v0, v1 }, Ljava/util/List;->addAll(Ljava/util/Collection;)Z
  .line 854
    sget-object v1, Lcom/project7/localmanager/LocalStoryClueEngine;->METHODS:[Ljava/lang/String;
    invoke-static { v1 }, Ljava/util/Arrays;->asList([Ljava/lang/Object;)Ljava/util/List;
    move-result-object v1
    invoke-interface { v0, v1 }, Ljava/util/List;->addAll(Ljava/util/Collection;)Z
  .line 855
    const-string v1, "daerweilaFirstChooseAsazile"
    invoke-interface { v0, v1 }, Ljava/util/List;->add(Ljava/lang/Object;)Z
  .line 856
    sget-object v1, Lcom/project7/localmanager/LocalWingDrugEngine;->METHODS:[Ljava/lang/String;
    invoke-static { v1 }, Ljava/util/Arrays;->asList([Ljava/lang/Object;)Ljava/util/List;
    move-result-object v1
    invoke-interface { v0, v1 }, Ljava/util/List;->addAll(Ljava/util/Collection;)Z
  .line 857
    sget-object v1, Lcom/project7/localmanager/LocalStoryDiscussion;->METHODS:Ljava/util/List;
    invoke-interface { v0, v1 }, Ljava/util/List;->addAll(Ljava/util/Collection;)Z
  .line 858
    invoke-interface { v0 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v0
  :L1
    invoke-interface { v0 }, Ljava/util/Iterator;->hasNext()Z
    move-result v1
    const/4 v2, 0
    if-eqz v1, :L20
    invoke-interface { v0 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v1
    move-object v13, v1
    check-cast v13, Ljava/lang/String;
  .line 859
    invoke-static { v13 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v1
    move-object/from16 v3, p3
    invoke-static { v3, v1 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    if-nez v1, :L2
    goto :L1
  :L2
  .line 860
    iget-object v0, v7, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    move-object/from16 v1, p4
    invoke-interface { v0, v10, v13, v1, v11 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v14
  .line 861
    const-string v15, "requestFlashbackIncDay"
    invoke-virtual { v15, v13 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L3
    if-eqz v12, :L3
  .line 862
    invoke-virtual { v12, v2 }, Lcom/project7/localmanager/LocalEventEngine;->updateClientOperation(I)V
  .line 863
    iget-object v0, v14, Lcom/project7/localmanager/LocalResourceEngine$Result;->profile:[B
    invoke-virtual { v12, v0 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  .line 864
    iget-object v0, v7, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v0, v10, v11 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  :L3
  .line 866
    const-string v0, "dailyPureChooseHero"
    invoke-virtual { v0, v13 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    const-string v6, "replyPrivateMsg"
    if-nez v0, :L4
    invoke-static { v13 }, Lcom/project7/localmanager/LocalHeroGiftEngine;->handles(Ljava/lang/String;)Z
    move-result v0
    if-nez v0, :L4
    invoke-static { v13 }, Lcom/project7/localmanager/LocalWingDrugEngine;->handles(Ljava/lang/String;)Z
    move-result v0
    if-nez v0, :L4
    invoke-virtual { v6, v13 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L5
  :L4
    if-eqz v12, :L5
  .line 867
    iget-object v0, v14, Lcom/project7/localmanager/LocalResourceEngine$Result;->profile:[B
    invoke-virtual { v12, v0 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  :L5
  .line 868
    const-string v0, "readPlayerNote"
    invoke-virtual { v0, v13 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    const-string v5, " method="
    const-string v4, "Project7Gateway"
    if-nez v0, :L6
    const-string v0, "readPendingNote"
    invoke-virtual { v0, v13 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L7
  :L6
  .line 869
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "diary read account="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v10 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v5 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v13 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v1, " "
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-object v1, v14, Lcom/project7/localmanager/LocalResourceEngine$Result;->profile:[B
  .line 870
    invoke-static { v1, v11 }, Lcom/project7/localmanager/LocalDiaryEngine;->diagnostic([BLcom/project7/localmanager/LocalTutorialStore$Progress;)Ljava/lang/String;
    move-result-object v1
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
  .line 869
    invoke-static { v4, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  :L7
  .line 871
    invoke-static { v13 }, Lcom/project7/localmanager/LocalIntelligenceEngine;->handles(Ljava/lang/String;)Z
    move-result v0
    if-nez v0, :L8
    invoke-static { v13 }, Lcom/project7/localmanager/LocalHeroGiftEngine;->handles(Ljava/lang/String;)Z
    move-result v0
    if-nez v0, :L8
  .line 872
    const-string v0, "triggerSocialMsgEvent"
    invoke-virtual { v0, v13 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-nez v0, :L8
    invoke-virtual { v6, v13 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L9
  :L8
  .line 873
    iget-object v0, v7, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v0, v10, v11 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  :L9
  .line 874
    iget-object v0, v14, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v0 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v16
  :L10
    invoke-interface/range { v16 .. v16 }, Ljava/util/Iterator;->hasNext()Z
    move-result v0
    const/4 v3, 1
    if-eqz v0, :L15
    invoke-interface/range { v16 .. v16 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;
  .line 875
    iget-object v1, v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    const-string v2, "q7StartSocialEvent"
    invoke-virtual { v2, v1 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    const-string v2, "e"
    if-eqz v1, :L12
  .line 876
    iget-object v0, v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v0, v2 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v17
  .line 877
    if-eqz v12, :L11
    if-eqz v17, :L11
    invoke-virtual/range { v17 .. v17 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    invoke-virtual { v12, v0 }, Lcom/project7/localmanager/LocalEventEngine;->startEvent(I)Z
    move-result v0
    if-eqz v0, :L11
  .line 878
    iget-object v0, v7, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v0, v10, v11 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 879
    invoke-virtual/range { v17 .. v17 }, Ljava/lang/Integer;->intValue()I
    move-result v18
    move-object/from16 v0, p0
    move-object/from16 v1, p1
    const/4 v12, 5
    move-object/from16 v2, p2
    move v12, v3
    move-object/from16 v3, p5
    move-object/from16 v31, v4
    move-object/from16 v4, p6
    move-object/from16 v32, v5
    move-object/from16 v5, p7
    move-object/from16 v33, v6
    move/from16 v6, v18
    invoke-direct/range { v0 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->syncPuzzleStart(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;I)V
  .line 880
    invoke-direct/range { v0 .. v5 }, Lcom/project7/localmanager/LocalGatewayServer;->syncEventEffects(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 881
    nop
  .line 882
    const-string v0, "startEventReply"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
    invoke-virtual/range { v17 .. v17 }, Ljava/lang/Integer;->intValue()I
    move-result v1
    invoke-static { v1, v12 }, Lcom/project7/localmanager/BsonLite;->eventReplyDocument(II)[B
    move-result-object v1
  .line 881
    invoke-static { v9, v0, v1 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
    const/4 v1, 5
    invoke-direct { v7, v8, v1, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    move-object/from16 v12, p7
    move-object/from16 v4, v31
    move-object/from16 v5, v32
    move-object/from16 v6, v33
    goto :L10
  :L11
  .line 877
    move-object/from16 v31, v4
    move-object/from16 v32, v5
    move-object/from16 v33, v6
    move-object/from16 v12, p7
    goto :L10
  :L12
  .line 886
    move-object/from16 v31, v4
    move-object/from16 v32, v5
    move-object/from16 v33, v6
    iget-object v1, v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    const-string v3, "triggerIntelligenceEvents"
    invoke-virtual { v3, v1 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L14
  .line 887
    iget-object v1, v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v1, v2 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v1
  .line 888
    if-eqz v1, :L13
    iget-object v2, v11, Lcom/project7/localmanager/LocalTutorialStore$Progress;->availableEvents:Ljava/util/Set;
    invoke-interface { v2, v1 }, Ljava/util/Set;->contains(Ljava/lang/Object;)Z
    move-result v2
    if-nez v2, :L14
    iget-object v2, v11, Lcom/project7/localmanager/LocalTutorialStore$Progress;->processingEvents:Ljava/util/Set;
    invoke-interface { v2, v1 }, Ljava/util/Set;->contains(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L14
  :L13
    move-object/from16 v12, p7
    move-object/from16 v4, v31
    move-object/from16 v5, v32
    move-object/from16 v6, v33
    goto/16 :L10
  :L14
  .line 890
    iget-object v1, v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 891
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    iget-object v0, v0, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v9, v1, v0 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
  .line 890
    const/4 v1, 5
    invoke-direct { v7, v8, v1, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 892
    move-object/from16 v12, p7
    move-object/from16 v4, v31
    move-object/from16 v5, v32
    move-object/from16 v6, v33
    goto/16 :L10
  :L15
  .line 893
    move v12, v3
    move-object/from16 v31, v4
    move-object/from16 v32, v5
    move-object/from16 v33, v6
    const/4 v1, 5
    invoke-static { v13 }, Lcom/project7/localmanager/LocalWingDrugEngine;->handles(Ljava/lang/String;)Z
    move-result v0
    if-nez v0, :L16
    invoke-virtual { v15, v13 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L17
  :L16
  .line 894
    invoke-static { v14 }, Lcom/project7/localmanager/LocalStoryProgressDelivery;->sent(Lcom/project7/localmanager/LocalResourceEngine$Result;)[B
    move-result-object v0
  .line 895
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->keys([B)Ljava/util/List;
    move-result-object v2
    invoke-interface { v2 }, Ljava/util/List;->isEmpty()Z
    move-result v2
    if-nez v2, :L17
    iget-object v2, v7, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    const-string v3, "q7AckStoryProgress"
    invoke-interface { v2, v10, v3, v0, v11 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
  :L17
  .line 897
    invoke-virtual { v15, v13 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-nez v0, :L18
    move-object/from16 v0, v33
    invoke-virtual { v0, v13 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-nez v0, :L18
    invoke-static { v13 }, Lcom/project7/localmanager/LocalHeroGiftEngine;->handles(Ljava/lang/String;)Z
    move-result v0
    if-nez v0, :L18
    invoke-static { v13 }, Lcom/project7/localmanager/LocalWingDrugEngine;->handles(Ljava/lang/String;)Z
    move-result v0
    if-eqz v0, :L19
  :L18
    move v6, v1
    if-eqz p7, :L19
  .line 898
    move-object/from16 v0, p0
    move-object/from16 v1, p1
    move-object/from16 v2, p2
    move-object/from16 v3, p5
    move-object/from16 v4, p6
    move-object/from16 v5, p7
    invoke-direct/range { v0 .. v5 }, Lcom/project7/localmanager/LocalGatewayServer;->syncEventEffects(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 899
    const-string v0, "pushEvents"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
  .line 900
    invoke-virtual/range { p7 .. p7 }, Lcom/project7/localmanager/LocalEventEngine;->availableEvents()Ljava/util/Set;
    move-result-object v1
    invoke-virtual/range { p7 .. p7 }, Lcom/project7/localmanager/LocalEventEngine;->processingEvents()Ljava/util/Set;
    move-result-object v2
    invoke-static { v1, v2 }, Lcom/project7/localmanager/BsonLite;->eventListsDocument(Ljava/lang/Iterable;Ljava/lang/Iterable;)[B
    move-result-object v1
  .line 899
    invoke-static { v9, v0, v1 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
    invoke-direct { v7, v8, v6, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L19
  .line 902
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "city service account="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v10 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-object/from16 v1, v32
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v13 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    move-object/from16 v1, v31
    invoke-static { v1, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 903
    return v12
  :L20
  .line 905
    return v2
.end method

.method private handleSetPlayerName(Ljava/io/OutputStream;[B[BLjava/lang/String;)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 10
  .line 802
    const-string v0, "n"
    invoke-static { p3, v0 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v0
  .line 803
    const-string v1, "in"
    invoke-static { p3, v1 }, Lcom/project7/localmanager/BsonLite;->boolValue([BLjava/lang/String;)Ljava/lang/Boolean;
    move-result-object p3
  .line 804
    if-eqz p4, :L0
    if-eqz v0, :L0
  .line 806
    invoke-virtual { v0 }, Ljava/lang/String;->trim()Ljava/lang/String;
    move-result-object v1
    invoke-virtual { v1 }, Ljava/lang/String;->isEmpty()Z
    move-result v1
    if-nez v1, :L0
  .line 807
    invoke-virtual { v0 }, Ljava/lang/String;->length()I
    move-result v1
    const/16 v2, 24
    if-gt v1, v2, :L0
    const/4 v1, 1
    goto :L1
  :L0
    const/4 v1, 0
  :L1
  .line 808
    if-eqz v1, :L2
  .line 809
    iget-object v2, p0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v2, p4, v0 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->savePlayerName(Ljava/lang/String;Ljava/lang/String;)V
  :L2
  .line 811
    const/4 v2, 5
  .line 816
    const-string v3, "setPlayerNameReply"
    invoke-static { v3 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v3
    sget-object v4, Ljava/lang/Boolean;->TRUE:Ljava/lang/Boolean;
  .line 819
    invoke-virtual { v4, p3 }, Ljava/lang/Boolean;->equals(Ljava/lang/Object;)Z
    move-result v4
  .line 817
    invoke-static { v1, v4 }, Lcom/project7/localmanager/BsonLite;->playerNameReplyDocument(ZZ)[B
    move-result-object v4
  .line 814
    invoke-static { p2, v3, v4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object p2
  .line 811
    invoke-direct { p0, p1, v2, p2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 823
    new-instance p1, Ljava/lang/StringBuilder;
    invoke-direct { p1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string p2, "setPlayerName completed account="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, p4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string p2, " playerName="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string p2, " accepted="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, v1 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    const-string p2, " isNewName="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, p3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { p1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p1
    const-string p2, "Project7Gateway"
    invoke-static { p2, p1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 830
    return-void
.end method

.method private handleSpecialItemRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)Z
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 11
  .line 744
    const-string v0, "buyCardMallItem"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v1
    invoke-static { p3, v1 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v1
    const-string v2, "requestSandglassToday"
    if-eqz v1, :L0
    goto :L2
  :L0
  .line 745
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v0
    invoke-static { p3, v0 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result p3
    if-eqz p3, :L1
    move-object v0, v2
    goto :L2
  :L1
    const/4 v0, 0
  :L2
  .line 746
    if-eqz v0, :L7
    invoke-static { v0, p4 }, Lcom/project7/localmanager/LocalSpecialItemEngine;->handles(Ljava/lang/String;[B)Z
    move-result p3
    if-eqz p3, :L7
    if-eqz p5, :L7
    if-nez p6, :L3
    goto :L7
  :L3
  .line 747
    iget-object p3, p0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { p3, p5, v0, p4, p6 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object p3
  .line 748
    iget-object v1, p0, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v1, p5, p6 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 749
    if-eqz p7, :L4
    iget-object v1, p3, Lcom/project7/localmanager/LocalResourceEngine$Result;->profile:[B
    invoke-static { v1, p6 }, Lcom/project7/localmanager/BsonLite;->withPatrolProgress([BLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object p6
    invoke-virtual { p7, p6 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  :L4
  .line 750
    iget-object p3, p3, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { p3 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object p3
  :L5
    invoke-interface { p3 }, Ljava/util/Iterator;->hasNext()Z
    move-result p6
    if-eqz p6, :L6
    invoke-interface { p3 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object p6
    check-cast p6, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    const/4 p7, 5
    iget-object v1, p6, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 751
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    iget-object p6, p6, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { p2, v1, p6 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object p6
  .line 750
    invoke-direct { p0, p1, p7, p6 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L5
  :L6
  .line 752
    new-instance p1, Ljava/lang/StringBuilder;
    invoke-direct { p1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string p2, "special item account="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, p5 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string p2, " method="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string p2, " params="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-static { p4 }, Lcom/project7/localmanager/BsonLite;->debugDocument([B)Ljava/lang/String;
    move-result-object p2
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p1
    const-string p2, "Project7Gateway"
    invoke-static { p2, p1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 753
    const/4 p1, 1
    return p1
  :L7
  .line 746
    const/4 p1, 0
    return p1
.end method

.method private handleSuppressionRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;Ljava/util/Set;)Z
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Ljava/io/OutputStream;",
      "[B[B[B",
      "Ljava/lang/String;",
      "Lcom/project7/localmanager/LocalTutorialStore$Progress;",
      "Lcom/project7/localmanager/LocalEventEngine;",
      "Ljava/util/Set<",
      "Ljava/lang/Integer;",
      ">;",
      "Ljava/util/Set<",
      "Ljava/lang/Integer;",
      ">;)Z"
    }
  .end annotation
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 26
  .line 2208
    move-object/from16 v12, p0
    move-object/from16 v1, p1
    move-object/from16 v2, p2
    move-object/from16 v0, p4
    const-string v3, "battleYazhiAsk"
    invoke-static { v3 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v4
    move-object/from16 v5, p3
    invoke-static { v5, v4 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v4
    const/4 v5, 0
    if-nez v4, :L0
    return v5
  :L0
  .line 2209
    iget-object v4, v12, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    move-object/from16 v6, p5
    move-object/from16 v7, p6
    invoke-interface { v4, v6, v3, v0, v7 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateEconomy(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalEconomyEngine$Result;
    move-result-object v13
  .line 2210
    iget-object v3, v13, Lcom/project7/localmanager/LocalEconomyEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v3 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v3
  :L1
    invoke-interface { v3 }, Ljava/util/Iterator;->hasNext()Z
    move-result v4
    const/4 v8, 5
    if-eqz v4, :L2
    invoke-interface { v3 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v4
    check-cast v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v9, v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 2211
    invoke-static { v9 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v9
    iget-object v4, v4, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v2, v9, v4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v4
  .line 2210
    invoke-direct { v12, v1, v8, v4 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L1
  :L2
  .line 2212
    const-string v3, "s"
    invoke-static { v0, v3 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v14
  .line 2213
    iget-boolean v4, v13, Lcom/project7/localmanager/LocalEconomyEngine$Result;->accepted:Z
    const/4 v15, 1
    if-eqz v4, :L4
  .line 2214
    iget-boolean v4, v13, Lcom/project7/localmanager/LocalEconomyEngine$Result;->replay:Z
    if-nez v4, :L3
  .line 2215
    const-string v4, "battleYazhiReply"
    invoke-static { v4 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v4
    const/16 v9, 8
    new-array v9, v9, [Ljava/lang/Object;
    const-string v10, "a"
    aput-object v10, v9, v5
    invoke-static { v0, v10 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v5
    invoke-static { v5 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v5
    aput-object v5, v9, v15
    const/4 v5, 2
    aput-object v3, v9, v5
    const/4 v3, 3
    invoke-static { v14 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v5
    aput-object v5, v9, v3
    const/4 v3, 4
    const-string v5, "h"
    aput-object v5, v9, v3
  .line 2216
    invoke-static { v0, v5 }, Lcom/project7/localmanager/BsonLite;->intArrayValues([BLjava/lang/String;)Ljava/util/List;
    move-result-object v0
    aput-object v0, v9, v8
    const/4 v0, 6
    const-string v3, "r"
    aput-object v3, v9, v0
    const/4 v0, 7
    iget-object v3, v13, Lcom/project7/localmanager/LocalEconomyEngine$Result;->reward:[B
    aput-object v3, v9, v0
  .line 2215
    invoke-static { v9 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v0
  .line 2214
    invoke-static { v2, v4, v0 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v0
    invoke-direct { v12, v1, v8, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L3
  .line 2217
    const/4 v8, 1
    const/4 v10, 1
    move-object/from16 v0, p0
    move-object/from16 v1, p1
    move-object/from16 v2, p2
    move-object/from16 v3, p5
    move-object/from16 v4, p6
    move-object/from16 v5, p7
    move-object/from16 v6, p8
    move-object/from16 v7, p9
    move v9, v14
    move-object v11, v13
    invoke-direct/range { v0 .. v11 }, Lcom/project7/localmanager/LocalGatewayServer;->finishStoryCombat(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;Ljava/util/Set;IIILcom/project7/localmanager/LocalEconomyEngine$Result;)V
  :L4
  .line 2219
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct { v0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "suppression scene="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0, v14 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v1, " accepted="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-boolean v1, v13, Lcom/project7/localmanager/LocalEconomyEngine$Result;->accepted:Z
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    const-string v1, " replay="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-boolean v1, v13, Lcom/project7/localmanager/LocalEconomyEngine$Result;->replay:Z
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    const-string v1, " reason="
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-object v1, v13, Lcom/project7/localmanager/LocalEconomyEngine$Result;->reason:Ljava/lang/String;
    invoke-virtual { v0, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    const-string v1, "Project7Gateway"
    invoke-static { v1, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 2221
    return v15
.end method

.method private handleWeekRpc(Ljava/io/OutputStream;[B[B[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)Z
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 32
    move-object/from16 v16, p0
    move-object/from16 v17, p1
    move-object/from16 v18, p2
    move-object/from16 v19, p3
    move-object/from16 v20, p4
    move-object/from16 v21, p5
    move-object/from16 v22, p6
    move-object/from16 v23, p7
  .line 758
    move-object/from16 v0, v16
    move-object/from16 v1, v17
    move-object/from16 v2, v18
    move-object/from16 v3, v19
    move-object/from16 v4, v21
    move-object/from16 v5, v22
    move-object/from16 v6, v23
    const/4 v7, 0
    if-eqz v4, :L11
    if-nez v5, :L0
    goto/16 :L11
  :L0
  .line 759
    const-string v8, "updateClientAvatarAsk"
    invoke-static { v8 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v8
    invoke-static { v3, v8 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v8
    const-string v9, "Project7Gateway"
    const/4 v10, 5
    const/4 v11, 1
    if-eqz v8, :L3
  .line 760
    iget-object v3, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v3, v4, v5 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->load(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v3
  .line 761
    iget-object v8, v0, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v8, v4, v5 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 762
    invoke-static { v3, v5 }, Lcom/project7/localmanager/BsonLite;->withTutorialProgress([BLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v3
    invoke-static { v3, v5 }, Lcom/project7/localmanager/BsonLite;->withLocalCityState([BLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v3
  .line 763
    invoke-static { v3, v5 }, Lcom/project7/localmanager/LocalWeekEngine;->awaitingEntrance([BLcom/project7/localmanager/LocalTutorialStore$Progress;)Z
    move-result v5
    const-string v8, "s"
    const/4 v12, 2
    if-eqz v5, :L1
  .line 764
    const-string v5, "evalCode"
    invoke-static { v5 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v5
    new-array v13, v12, [Ljava/lang/Object;
    aput-object v8, v13, v7
    const-string v14, "exec('gg.event_trigger_cache = None\\ngg.avatar_status = None\\ngetattr(gg.avatar, \"_q7_reset_story_continuations\", lambda: None)()')"
    aput-object v14, v13, v11
  .line 765
    invoke-static { v13 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v13
  .line 764
    invoke-static { v2, v5, v13 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v5
    invoke-direct { v0, v1, v10, v5 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 766
    new-instance v5, Ljava/lang/StringBuilder;
    invoke-direct { v5 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v13, "week entrance transient cache reset account="
    invoke-virtual { v5, v13 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v5, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v5 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-static { v9, v4 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  :L1
  .line 768
    const-string v4, "updateClientAvatarReply"
    invoke-static { v4 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v4
    new-array v5, v12, [Ljava/lang/Object;
    aput-object v8, v5, v7
    new-instance v7, Lcom/project7/localmanager/BsonLite$BinaryValue;
  .line 769
    invoke-static { v3 }, Lcom/project7/localmanager/LocalAvatarPayload;->encode([B)[B
    move-result-object v8
    invoke-direct { v7, v8 }, Lcom/project7/localmanager/BsonLite$BinaryValue;-><init>([B)V
    aput-object v7, v5, v11
    invoke-static { v5 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v5
  .line 768
    invoke-static { v2, v4, v5 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v4
    invoke-direct { v0, v1, v10, v4 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 770
    invoke-virtual { v0, v1, v2, v3 }, Lcom/project7/localmanager/LocalGatewayServer;->syncFurnitureLogin(Ljava/io/OutputStream;[B[B)V
  .line 771
    if-eqz v6, :L2
    invoke-virtual { v6, v3 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  :L2
  .line 772
    return v11
  :L3
  .line 774
    sget-object v8, Lcom/project7/localmanager/LocalWeekEngine;->METHODS:[Ljava/lang/String;
    array-length v12, v8
    move v13, v7
  :L4
    if-ge v13, v12, :L10
    aget-object v14, v8, v13
  .line 775
    invoke-static { v14 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v15
    invoke-static { v3, v15 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v15
    if-nez v15, :L5
  .line 774
    add-int/lit8 v13, v13, 1
    goto :L4
  :L5
  .line 776
    move-object/from16 p0, v0
    move-object/from16 p1, v1
    move-object/from16 p2, v2
    move-object/from16 p3, v4
    move-object/from16 p4, v5
    move-object/from16 p5, v6
    move-object/from16 p6, v14
    invoke-static/range { p0 .. p6 }, Lcom/project7/localmanager/EventResetWeekGateway;->beforeWeek(Lcom/project7/localmanager/LocalGatewayServer;Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Ljava/lang/String;)Z
    move-result v7
    if-nez v7, :L6
    const/4 v7, 1
    return v7
  :L6
    iget-object v3, v5, Lcom/project7/localmanager/LocalTutorialStore$Progress;->weekCommit:Ljava/lang/String;
  .line 777
    iget-object v7, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    move-object/from16 v8, v20
    invoke-interface { v7, v4, v14, v8, v5 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v7
  .line 778
    iget-object v8, v0, Lcom/project7/localmanager/LocalGatewayServer;->tutorialStore:Lcom/project7/localmanager/LocalTutorialStore;
    invoke-virtual { v8, v4, v5 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  .line 779
    if-eqz v6, :L7
    iget-object v5, v5, Lcom/project7/localmanager/LocalTutorialStore$Progress;->weekCommit:Ljava/lang/String;
    invoke-virtual { v3, v5 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v3
    if-nez v3, :L7
    iget-object v3, v7, Lcom/project7/localmanager/LocalResourceEngine$Result;->profile:[B
    invoke-virtual { v6, v3 }, Lcom/project7/localmanager/LocalEventEngine;->resetWeekContext([B)V
  :L7
  .line 780
    iget-object v3, v7, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v3 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v3
  :L8
    invoke-interface { v3 }, Ljava/util/Iterator;->hasNext()Z
    move-result v5
    if-eqz v5, :L9
    invoke-interface { v3 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v5
    check-cast v5, Lcom/project7/localmanager/LocalResourceEngine$Reply;
    iget-object v6, v5, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
  .line 781
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v6
    iget-object v5, v5, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v2, v6, v5 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v5
  .line 780
    invoke-direct { v0, v1, v10, v5 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L8
  :L9
  .line 782
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "week lifecycle account="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v2, " method="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v14 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v2, " week="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget-object v2, v7, Lcom/project7/localmanager/LocalResourceEngine$Result;->profile:[B
  .line 783
    const-string v3, "weeknum"
    invoke-static { v2, v3 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v2
    const-string v3, "w"
    invoke-static { v2, v3 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v2
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
  .line 782
    invoke-static { v9, v1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 784
    return v11
  :L10
  .line 786
    return v7
  :L11
  .line 758
    return v7
.end method

.method private static hex([B)Ljava/lang/String;
  .registers 8
  .line 2665
    new-instance v0, Ljava/lang/StringBuilder;
    array-length v1, p0
    mul-int/lit8 v1, v1, 2
    invoke-direct { v0, v1 }, Ljava/lang/StringBuilder;-><init>(I)V
  .line 2666
    array-length v1, p0
    const/4 v2, 0
    move v3, v2
  :L0
    if-ge v3, v1, :L1
    aget-byte v4, p0, v3
  .line 2667
    sget-object v5, Ljava/util/Locale;->US:Ljava/util/Locale;
    const/4 v6, 1
    new-array v6, v6, [Ljava/lang/Object;
    and-int/lit16 v4, v4, 255
    invoke-static { v4 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v4
    aput-object v4, v6, v2
    const-string v4, "%02x"
    invoke-static { v5, v4, v6 }, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;
    move-result-object v4
    invoke-virtual { v0, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  .line 2666
    add-int/lit8 v3, v3, 1
    goto :L0
  :L1
  .line 2669
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p0
    return-object p0
.end method

.method private static isHighSchoolUnlocked(Lcom/project7/localmanager/LocalTutorialStore$Progress;)Z
  .registers 2
  .line 2400
    if-eqz p0, :L0
    iget-object p0, p0, Lcom/project7/localmanager/LocalTutorialStore$Progress;->completedEvents:Ljava/util/Set;
    const/16 v0, 1004
    invoke-static { v0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v0
    invoke-interface { p0, v0 }, Ljava/util/Set;->contains(Ljava/lang/Object;)Z
    move-result p0
    if-eqz p0, :L0
    const/4 p0, 1
    goto :L1
  :L0
    const/4 p0, 0
  :L1
    return p0
.end method

.method private static knownMethodName(Ljava/lang/String;)Ljava/lang/String;
  .registers 2
  .line 2520
    invoke-virtual { p0 }, Ljava/lang/String;->hashCode()I
    move-result v0
    sparse-switch v0, :L19
  :L0
    goto :L9
  :L1
    const-string v0, "e14f329db4d0e69178add0cb0fb2721b"
    invoke-virtual { p0, v0 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result p0
    if-eqz p0, :L0
    const/4 p0, 3
    goto :L10
  :L2
    const-string v0, "43891612ade9652116a491adc872870a"
    invoke-virtual { p0, v0 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result p0
    if-eqz p0, :L0
    const/4 p0, 1
    goto :L10
  :L3
    const-string v0, "c98b48ce939a85367850f73c46262135"
    invoke-virtual { p0, v0 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result p0
    if-eqz p0, :L0
    const/4 p0, 2
    goto :L10
  :L4
    const-string v0, "2685968efbe18f8ce157ba5cd205fdb2"
    invoke-virtual { p0, v0 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result p0
    if-eqz p0, :L0
    const/4 p0, 5
    goto :L10
  :L5
    const-string v0, "0bd2b958144ca852b93120c95f57eaa6"
    invoke-virtual { p0, v0 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result p0
    if-eqz p0, :L0
    const/4 p0, 7
    goto :L10
  :L6
    const-string v0, "86b7f6b757903e376b56a0d6d6adfd07"
    invoke-virtual { p0, v0 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result p0
    if-eqz p0, :L0
    const/4 p0, 0
    goto :L10
  :L7
    const-string v0, "1855aef234af3e9d1edf66c0ff95ae2d"
    invoke-virtual { p0, v0 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result p0
    if-eqz p0, :L0
    const/4 p0, 4
    goto :L10
  :L8
    const-string v0, "6f714ca281f3444f391d2c0b6b533d2b"
    invoke-virtual { p0, v0 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result p0
    if-eqz p0, :L0
    const/4 p0, 6
    goto :L10
  :L9
    const/4 p0, -1
  :L10
    packed-switch p0, :L20
  .line 2538
    const-string p0, "unknown"
    return-object p0
  :L11
  .line 2536
    const-string p0, "uploadTouchHistory"
    return-object p0
  :L12
  .line 2534
    const-string p0, "logCheckCheat"
    return-object p0
  :L13
  .line 2532
    const-string p0, "exceptUpload"
    return-object p0
  :L14
  .line 2530
    const-string p0, "tutorialBegin"
    return-object p0
  :L15
  .line 2528
    const-string p0, "enterPlace"
    return-object p0
  :L16
  .line 2526
    const-string p0, "requestTriggerDaXuanWo"
    return-object p0
  :L17
  .line 2524
    const-string p0, "uploadDeviceInfo"
    return-object p0
  :L18
  .line 2522
    const-string p0, "syncAllIntelligenceRequest"
    return-object p0
  :L19
  .sparse-switch
    -1897169271 -> :L8
    -1609959665 -> :L7
    -1380682449 -> :L6
    -1330808243 -> :L5
    -880899896 -> :L4
    -382736884 -> :L3
    519580846 -> :L2
    923864272 -> :L1
  .end sparse-switch
  :L20
  .packed-switch 0
    :L18
    :L17
    :L16
    :L15
    :L14
    :L13
    :L12
    :L11
  .end packed-switch
.end method

.method static synthetic lambda$emitEventEffects$7(Lcom/project7/localmanager/LocalResourceEngine$Reply;)Z
  .registers 2
  .line 983
    iget-object p0, p0, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    const-string v0, "get_all_area_info_reply"
    invoke-virtual { v0, p0 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result p0
    return p0
.end method

.method static synthetic lambda$new$0()Lcom/project7/localmanager/LocalGatewayServer$HomeCallbacks;
  .registers 2
  .line 101
    new-instance v0, Lcom/project7/localmanager/LocalGatewayServer$HomeCallbacks;
    const/4 v1, 0
    invoke-direct { v0, v1 }, Lcom/project7/localmanager/LocalGatewayServer$HomeCallbacks;-><init>(Lcom/project7/localmanager/LocalGatewayServer$1;)V
    return-object v0
.end method

.method static synthetic lambda$new$1()Ljava/lang/Boolean;
  .registers 1
  .line 102
    const/4 v0, 0
    invoke-static { v0 }, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
    move-result-object v0
    return-object v0
.end method

.method static synthetic lambda$new$2()Lcom/project7/localmanager/LocalGatewayServer$EventQueryCache;
  .registers 2
  .line 123
    new-instance v0, Lcom/project7/localmanager/LocalGatewayServer$EventQueryCache;
    const/4 v1, 0
    invoke-direct { v0, v1 }, Lcom/project7/localmanager/LocalGatewayServer$EventQueryCache;-><init>(Lcom/project7/localmanager/LocalGatewayServer$1;)V
    return-object v0
.end method

.method static synthetic lambda$new$3()Lcom/project7/localmanager/LocalGatewayServer$CombatReplies;
  .registers 2
  .line 167
    new-instance v0, Lcom/project7/localmanager/LocalGatewayServer$CombatReplies;
    const/4 v1, 0
    invoke-direct { v0, v1 }, Lcom/project7/localmanager/LocalGatewayServer$CombatReplies;-><init>(Lcom/project7/localmanager/LocalGatewayServer$1;)V
    return-object v0
.end method

.method static synthetic lambda$new$4(Ljava/lang/Runnable;)Ljava/lang/Thread;
  .registers 3
  .line 175
    new-instance v0, Ljava/lang/Thread;
    const-string v1, "Project7Connection"
    invoke-direct { v0, p0, v1 }, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V
  .line 176
    const/4 p0, 1
    invoke-virtual { v0, p0 }, Ljava/lang/Thread;->setDaemon(Z)V
  .line 177
    return-object v0
.end method

.method static synthetic lambda$syncPuzzleStart$6(Lcom/project7/localmanager/LocalResourceEngine$Reply;)Z
  .registers 2
  .line 913
    iget-object p0, p0, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    const-string v0, "syncPuzzleRoomClue"
    invoke-virtual { v0, p0 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result p0
    return p0
.end method

.method private static md5(Ljava/lang/String;)[B
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .catch Ljava/security/NoSuchAlgorithmException; { :L0 .. :L1 } :L2
  .registers 3
  :L0
  .line 2612
    const-string v0, "MD5"
    invoke-static { v0 }, Ljava/security/MessageDigest;->getInstance(Ljava/lang/String;)Ljava/security/MessageDigest;
    move-result-object v0
    sget-object v1, Ljava/nio/charset/StandardCharsets;->US_ASCII:Ljava/nio/charset/Charset;
    invoke-virtual { p0, v1 }, Ljava/lang/String;->getBytes(Ljava/nio/charset/Charset;)[B
    move-result-object p0
    invoke-virtual { v0, p0 }, Ljava/security/MessageDigest;->digest([B)[B
    move-result-object p0
  :L1
    return-object p0
  :L2
  .line 2613
    move-exception p0
  .line 2614
    new-instance v0, Ljava/io/IOException;
    const-string v1, "MD5 unavailable"
    invoke-direct { v0, v1, p0 }, Ljava/io/IOException;-><init>(Ljava/lang/String;Ljava/lang/Throwable;)V
    throw v0
.end method

.method private objectId()[B
  .registers 3
  .line 2605
    const/16 v0, 12
    new-array v0, v0, [B
  .line 2606
    iget-object v1, p0, Lcom/project7/localmanager/LocalGatewayServer;->random:Ljava/security/SecureRandom;
    invoke-virtual { v1, v0 }, Ljava/security/SecureRandom;->nextBytes([B)V
  .line 2607
    return-object v0
.end method

.method static patrolFailureMessage(Ljava/lang/String;)Ljava/lang/String;
  .registers 2
  .line 2383
    const-string v0, "insufficient insight"
    invoke-virtual { v0, p0 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L0
    const-string p0, "\u6240\u9009\u795e\u5668\u4f7f\u7684\u5de1\u67e5\u529b\u4e0d\u8db3\uff0c\u8bf7\u68c0\u67e5\u672c\u65e5\u5de1\u67e5\u6b21\u6570\u548c\u5efa\u7b51\u52a0\u6210\u3002"
    return-object p0
  :L0
  .line 2384
    const-string v0, "insufficient fatigue"
    invoke-virtual { v0, p0 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L1
    const-string p0, "\u6240\u9009\u795e\u5668\u4f7f\u7684\u75b2\u52b3\u503c\u4e0d\u8db3\u3002"
    return-object p0
  :L1
  .line 2385
    const-string v0, "insufficient actions"
    invoke-virtual { v0, p0 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L2
    const-string p0, "\u5269\u4f59\u884c\u52a8\u529b\u4e0d\u8db3\uff0c\u65e0\u6cd5\u5f00\u59cb\u65b0\u7684\u5de1\u67e5\u3002"
    return-object p0
  :L2
  .line 2386
    const-string v0, "hero not owned"
    invoke-virtual { v0, p0 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L3
    const-string p0, "\u5de1\u67e5\u961f\u4f0d\u5305\u542b\u672a\u62e5\u6709\u7684\u795e\u5668\u4f7f\uff0c\u8bf7\u91cd\u65b0\u9009\u62e9\u3002"
    return-object p0
  :L3
  .line 2387
    const-string v0, "area unavailable"
    invoke-virtual { v0, p0 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L4
    const-string p0, "\u8be5\u5730\u533a\u5f53\u524d\u5c1a\u4e0d\u80fd\u5de1\u67e5\uff0c\u8bf7\u5148\u5b8c\u6210\u5730\u533a\u89e3\u653e\u6216\u7d27\u6025\u5267\u60c5\u3002"
    return-object p0
  :L4
  .line 2388
    const-string v0, "invalid team"
    invoke-virtual { v0, p0 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L5
    const-string p0, "\u8bf7\u9009\u62e9\u4e00\u81f3\u4e09\u540d\u4e0d\u540c\u7684\u795e\u5668\u4f7f\u8fdb\u884c\u5de1\u67e5\u3002"
    return-object p0
  :L5
  .line 2389
    if-nez p0, :L6
    const-string p0, "\u65e0\u6cd5\u5f00\u59cb\u5de1\u67e5\uff0c\u8bf7\u91cd\u65b0\u9009\u62e9\u961f\u4f0d\u3002"
  :L6
    return-object p0
.end method

.method private prepareEventEffects(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)Lcom/project7/localmanager/LocalResourceEngine$Result;
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 20
    invoke-static/range { p0 .. p3 }, Lcom/project7/localmanager/TrialRetryGateway;->recover(Lcom/project7/localmanager/LocalGatewayServer;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .line 939
    move-object/from16 v0, p0
    move-object/from16 v1, p1
    move-object/from16 v2, p2
    move-object/from16 v3, p3
    iget-object v4, v0, Lcom/project7/localmanager/LocalGatewayServer;->storyClosureIncomplete:Ljava/lang/ThreadLocal;
    const/4 v5, 0
    invoke-static { v5 }, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
    move-result-object v6
    invoke-virtual { v4, v6 }, Ljava/lang/ThreadLocal;->set(Ljava/lang/Object;)V
  .line 940
    if-eqz v3, :L0
    iget-object v4, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v4, v1, v2 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v4
    invoke-virtual { v3, v4 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  :L0
  .line 941
    if-nez v3, :L1
    invoke-static { }, Ljava/util/Collections;->emptySet()Ljava/util/Set;
    move-result-object v4
    goto :L2
  :L1
    invoke-virtual/range { p3 .. p3 }, Lcom/project7/localmanager/LocalEventEngine;->messagePublishers()Ljava/util/Set;
    move-result-object v4
  :L2
  .line 942
    iget-object v6, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    sget-object v7, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    const-string v8, "effects"
    invoke-interface { v6, v1, v8, v7, v2 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v6
  .line 943
    if-nez v3, :L3
    return-object v6
  :L3
  .line 944
    move v7, v5
  :L4
    const/16 v9, 8
    if-ge v7, v9, :L16
  .line 945
    iget-object v9, v6, Lcom/project7/localmanager/LocalResourceEngine$Result;->profile:[B
    invoke-virtual { v3, v9 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  .line 946
    invoke-virtual/range { p3 .. p3 }, Lcom/project7/localmanager/LocalEventEngine;->messagePublishers()Ljava/util/Set;
    move-result-object v9
  .line 947
    invoke-interface { v4, v9 }, Ljava/util/Set;->containsAll(Ljava/util/Collection;)Z
    move-result v10
    if-eqz v10, :L5
    return-object v6
  :L5
  .line 948
    invoke-interface { v4, v9 }, Ljava/util/Set;->addAll(Ljava/util/Collection;)Z
  .line 949
    iget-object v9, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    sget-object v10, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    invoke-interface { v9, v1, v8, v10, v2 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v9
  .line 951
    iget-object v10, v9, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v10 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v10
  :L6
    invoke-interface { v10 }, Ljava/util/Iterator;->hasNext()Z
    move-result v11
    if-eqz v11, :L15
    invoke-interface { v10 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v11
    check-cast v11, Lcom/project7/localmanager/LocalResourceEngine$Reply;
  .line 952
    invoke-static { v11 }, Lcom/project7/localmanager/LocalStoryProgressDelivery;->key(Lcom/project7/localmanager/LocalResourceEngine$Reply;)Ljava/lang/String;
    move-result-object v12
  .line 953
    nop
  .line 954
    move v14, v5
  :L7
    iget-object v15, v6, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v15 }, Ljava/util/List;->size()I
    move-result v15
    if-ge v14, v15, :L11
  .line 955
    iget-object v15, v6, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v15, v14 }, Ljava/util/List;->get(I)Ljava/lang/Object;
    move-result-object v15
    check-cast v15, Lcom/project7/localmanager/LocalResourceEngine$Reply;
  .line 956
    if-eqz v12, :L8
    invoke-static { v15 }, Lcom/project7/localmanager/LocalStoryProgressDelivery;->key(Lcom/project7/localmanager/LocalResourceEngine$Reply;)Ljava/lang/String;
    move-result-object v5
    invoke-virtual { v12, v5 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v5
    if-eqz v5, :L8
    goto :L9
  :L8
  .line 957
    iget-object v5, v15, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    iget-object v13, v11, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    invoke-virtual { v5, v13 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v5
    if-eqz v5, :L10
    iget-object v5, v15, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    iget-object v13, v11, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { v5, v13 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v5
    if-eqz v5, :L10
  :L9
  .line 959
    move v13, v14
    goto :L12
  :L10
  .line 954
    add-int/lit8 v14, v14, 1
    const/4 v5, 0
    goto :L7
  :L11
    const/4 v13, -1
  :L12
  .line 959
    if-ltz v13, :L13
    iget-object v5, v6, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v5, v13, v11 }, Ljava/util/List;->set(ILjava/lang/Object;)Ljava/lang/Object;
    goto :L14
  :L13
  .line 960
    iget-object v5, v6, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { v5, v11 }, Ljava/util/List;->add(Ljava/lang/Object;)Z
  :L14
  .line 961
    const/4 v5, 0
    goto :L6
  :L15
  .line 962
    iget-object v5, v9, Lcom/project7/localmanager/LocalResourceEngine$Result;->profile:[B
    iput-object v5, v6, Lcom/project7/localmanager/LocalResourceEngine$Result;->profile:[B
  .line 944
    add-int/lit8 v7, v7, 1
    const/4 v5, 0
    goto/16 :L4
  :L16
  .line 965
    iget-object v2, v6, Lcom/project7/localmanager/LocalResourceEngine$Result;->profile:[B
    invoke-virtual { v3, v2 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  .line 966
    iget-object v2, v0, Lcom/project7/localmanager/LocalGatewayServer;->storyClosureIncomplete:Ljava/lang/ThreadLocal;
    const/4 v3, 1
    invoke-static { v3 }, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
    move-result-object v3
    invoke-virtual { v2, v3 }, Ljava/lang/ThreadLocal;->set(Ljava/lang/Object;)V
  .line 967
    new-instance v2, Ljava/lang/StringBuilder;
    invoke-direct { v2 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v3, "story message closure budget exhausted; no player event forced account="
    invoke-virtual { v2, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v2, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v2 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    const-string v2, "Project7Gateway"
    invoke-static { v2, v1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;)I
  .line 968
    return-object v6
.end method

.method private static q7QueryAreaAllowed(Ljava/lang/Integer;[B)Z
  .registers 4
    invoke-static { p1 }, Lcom/project7/localmanager/StoryCityPolicy;->owns([B)Z
    move-result v0
    if-eqz v0, :L1
    if-eqz p0, :L1
    invoke-virtual { p0 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    const/4 v1, 1
    if-lt v0, v1, :L2
    const/16 v1, 8
    if-gt v0, v1, :L0
    goto/32 :L1
  :L0
    invoke-static { v0 }, Lcom/project7/localmanager/StoryCityPolicy;->knownArea(I)Z
    move-result v1
    if-eqz v1, :L2
  :L1
    const/4 v0, 1
    return v0
  :L2
    const/4 v0, 0
    return v0
.end method

.method private static q7QueryAreaId(Ljava/lang/Integer;Z[B)I
  .registers 5
    invoke-static { p2 }, Lcom/project7/localmanager/StoryCityPolicy;->owns([B)Z
    move-result v0
    if-nez v0, :L0
    goto/32 :L5
  :L0
    if-eqz p1, :L2
    if-eqz p0, :L4
    invoke-virtual { p0 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    const/4 v1, 1
    if-lt v0, v1, :L4
    const/16 v1, 8
    if-gt v0, v1, :L1
    return v0
  :L1
    invoke-static { v0 }, Lcom/project7/localmanager/StoryCityPolicy;->knownArea(I)Z
    move-result v1
    return v0
  :L2
    if-eqz p0, :L3
    invoke-virtual { p0 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    return v0
  :L3
    const/4 v0, 0
    return v0
  :L4
    const/4 v0, 1
    return v0
  :L5
    invoke-static { p0, p1 }, Lcom/project7/localmanager/LocalGatewayServer;->resolveAreaId(Ljava/lang/Integer;Z)I
    move-result v0
    return v0
.end method

.method private static q7StoryCityCocBegin(Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalEconomyEngine$Result;
  .registers 16
    move-object v0, p0
    move-object v1, p1
    move-object v2, p3
    move-object v3, p4
    invoke-static { v0 }, Lcom/project7/localmanager/FailureSafeProfileProvider;->unwrapStore(Ljava/lang/Object;)Lcom/project7/localmanager/LocalProfileStore;
    move-result-object v5
    if-eqz v5, :L3
    move-object v8, v0
    move-object v9, v1
    move-object v10, v3
    invoke-interface { v8, v9, v10 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v6
    move-object v9, v2
    const-string v10, "s"
    invoke-static { v9, v10 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v7
    if-eqz v7, :L3
    move-object v9, v7
    invoke-virtual { v9 }, Ljava/lang/Integer;->intValue()I
    move-result v4
    move-object v7, v3
    move-object v8, v6
    move v9, v4
    move-object v10, v2
    invoke-static { v7, v8, v9, v10 }, Lcom/project7/localmanager/StoryCityCocPolicy;->admit(Lcom/project7/localmanager/LocalTutorialStore$Progress;[BI[B)Lcom/project7/localmanager/StoryCityCocPolicy$Admission;
    move-result-object v7
    iget-object v9, v7, Lcom/project7/localmanager/StoryCityCocPolicy$Admission;->reason:Ljava/lang/String;
    sget-object v10, Lcom/project7/localmanager/StoryCityCocPolicy;->UNKNOWN_SCENE:Ljava/lang/String;
    invoke-virtual { v9, v10 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v8
    if-nez v8, :L3
    iget-object v9, v7, Lcom/project7/localmanager/StoryCityCocPolicy$Admission;->reason:Ljava/lang/String;
    sget-object v10, Lcom/project7/localmanager/StoryCityCocPolicy;->NOT_PREPARED:Ljava/lang/String;
    invoke-virtual { v9, v10 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v8
    if-nez v8, :L3
    iget-boolean v8, v7, Lcom/project7/localmanager/StoryCityCocPolicy$Admission;->allowed:Z
    if-eqz v8, :L1
    move-object v10, v6
    move-object v6, v1
    move-object v7, v3
    move-object v8, v10
    move v9, v4
    move-object v10, v2
    invoke-static/range { v5 .. v10 }, Lcom/project7/localmanager/StoryCityCocPolicy;->begin(Lcom/project7/localmanager/LocalProfileStore;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;[BI[B)Lcom/project7/localmanager/StoryCityCocPolicy$Settlement;
    move-result-object v5
    iget-object v6, v5, Lcom/project7/localmanager/StoryCityCocPolicy$Settlement;->storeResult:Lcom/project7/localmanager/LocalEconomyEngine$Result;
    if-eqz v6, :L2
    iget-boolean v8, v5, Lcom/project7/localmanager/StoryCityCocPolicy$Settlement;->accepted:Z
    if-eqz v8, :L0
    invoke-virtual { p2, v1, v3 }, Lcom/project7/localmanager/LocalTutorialStore;->save(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)V
  :L0
    move-object v9, v6
    return-object v9
  :L1
    move-object v10, v7
    new-instance v9, Lcom/project7/localmanager/LocalEconomyEngine$Result;
    move-object v5, v9
    invoke-direct { v5, v6 }, Lcom/project7/localmanager/LocalEconomyEngine$Result;-><init>([B)V
    const/4 v8, 0
    iput-boolean v8, v9, Lcom/project7/localmanager/LocalEconomyEngine$Result;->accepted:Z
    iget-object v8, v10, Lcom/project7/localmanager/StoryCityCocPolicy$Admission;->reason:Ljava/lang/String;
    iput-object v8, v9, Lcom/project7/localmanager/LocalEconomyEngine$Result;->reason:Ljava/lang/String;
    return-object v9
  :L2
    move-object v8, v0
    move-object v9, v1
    move-object v10, v3
    invoke-interface { v8, v9, v10 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v6
    move-object v10, v5
    new-instance v9, Lcom/project7/localmanager/LocalEconomyEngine$Result;
    move-object v5, v9
    invoke-direct { v5, v6 }, Lcom/project7/localmanager/LocalEconomyEngine$Result;-><init>([B)V
    const/4 v8, 0
    iput-boolean v8, v9, Lcom/project7/localmanager/LocalEconomyEngine$Result;->accepted:Z
    iget-object v8, v10, Lcom/project7/localmanager/StoryCityCocPolicy$Settlement;->reason:Ljava/lang/String;
    iput-object v8, v9, Lcom/project7/localmanager/LocalEconomyEngine$Result;->reason:Ljava/lang/String;
    return-object v9
  :L3
    const-string p2, "begin"
    invoke-interface { p0, p1, p2, p3, p4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateEconomy(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalEconomyEngine$Result;
    move-result-object v9
    return-object v9
.end method

.method private static q7StoryCityCocFinish(Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalEconomyEngine$Result;
  .registers 16
    move-object v0, p0
    move-object v1, p1
    move-object v2, p3
    move-object v3, p4
    invoke-static { v0 }, Lcom/project7/localmanager/FailureSafeProfileProvider;->unwrapStore(Ljava/lang/Object;)Lcom/project7/localmanager/LocalProfileStore;
    move-result-object v5
    if-eqz v5, :L3
    move-object v8, v0
    move-object v9, v1
    move-object v10, v3
    invoke-interface { v8, v9, v10 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v6
    move-object v9, v2
    const-string v10, "s"
    invoke-static { v9, v10 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v9
    if-eqz v9, :L3
    move-object v10, v9
    invoke-virtual { v10 }, Ljava/lang/Integer;->intValue()I
    move-result v4
    move-object v7, v3
    move-object v8, v6
    move v9, v4
    move-object v10, v2
    invoke-static { v7, v8, v9, v10 }, Lcom/project7/localmanager/StoryCityCocPolicy;->admit(Lcom/project7/localmanager/LocalTutorialStore$Progress;[BI[B)Lcom/project7/localmanager/StoryCityCocPolicy$Admission;
    move-result-object v7
    iget-object v9, v7, Lcom/project7/localmanager/StoryCityCocPolicy$Admission;->reason:Ljava/lang/String;
    sget-object v10, Lcom/project7/localmanager/StoryCityCocPolicy;->UNKNOWN_SCENE:Ljava/lang/String;
    invoke-virtual { v9, v10 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v8
    if-nez v8, :L3
    iget-object v9, v7, Lcom/project7/localmanager/StoryCityCocPolicy$Admission;->reason:Ljava/lang/String;
    sget-object v10, Lcom/project7/localmanager/StoryCityCocPolicy;->NOT_PREPARED:Ljava/lang/String;
    invoke-virtual { v9, v10 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v8
    if-nez v8, :L3
    iget-boolean v8, v7, Lcom/project7/localmanager/StoryCityCocPolicy$Admission;->allowed:Z
    if-eqz v8, :L0
    move-object v9, v2
    invoke-static { v9 }, Lcom/project7/localmanager/BsonLite;->combatWinValue([B)I
    move-result v8
    move p3, v8
    move-object v8, v5
    move-object v9, v1
    move-object v10, v3
    move-object p0, v6
    move p1, v4
    move-object p2, v2
    const/4 p4, 0
    invoke-static/range { v8 .. p4 }, Lcom/project7/localmanager/StoryCityCocPolicy;->settle(Lcom/project7/localmanager/LocalProfileStore;Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;[BI[BILcom/project7/localmanager/LocalEventEngine;)Lcom/project7/localmanager/StoryCityCocPolicy$Settlement;
    move-result-object v10
    iget-object v9, v10, Lcom/project7/localmanager/StoryCityCocPolicy$Settlement;->storeResult:Lcom/project7/localmanager/LocalEconomyEngine$Result;
    if-eqz v9, :L2
    return-object v9
  :L0
    move-object v9, v2
    invoke-static { v9 }, Lcom/project7/localmanager/BsonLite;->combatWinValue([B)I
    move-result v8
    const/4 v10, 1
    if-ne v8, v10, :L1
    iget-object v9, v7, Lcom/project7/localmanager/StoryCityCocPolicy$Admission;->reason:Ljava/lang/String;
    sget-object v10, Lcom/project7/localmanager/StoryCityCocPolicy;->ALREADY_SETTLED:Ljava/lang/String;
    invoke-virtual { v9, v10 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v8
    if-eqz v8, :L1
    invoke-static { v3, v6, v4, v2 }, Lcom/project7/localmanager/StoryCityCocPolicy;->recoverableProgress(Lcom/project7/localmanager/LocalTutorialStore$Progress;[BI[B)Z
    move-result v8
    if-eqz v8, :L1
    new-instance v9, Lcom/project7/localmanager/LocalEconomyEngine$Result;
    move-object v8, v9
    move-object v9, v6
    invoke-direct { v8, v9 }, Lcom/project7/localmanager/LocalEconomyEngine$Result;-><init>([B)V
    const/4 v9, 1
    iput-boolean v9, v8, Lcom/project7/localmanager/LocalEconomyEngine$Result;->accepted:Z
    iput-boolean v9, v8, Lcom/project7/localmanager/LocalEconomyEngine$Result;->replay:Z
    iput v9, v8, Lcom/project7/localmanager/LocalEconomyEngine$Result;->win:I
    iget v9, v3, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolActions:I
    iput v9, v8, Lcom/project7/localmanager/LocalEconomyEngine$Result;->remainingActions:I
    sget-object v10, Lcom/project7/localmanager/StoryCityCocPolicy;->ALREADY_SETTLED:Ljava/lang/String;
    iput-object v10, v8, Lcom/project7/localmanager/LocalEconomyEngine$Result;->reason:Ljava/lang/String;
    return-object v8
  :L1
    move-object v10, v7
    new-instance v9, Lcom/project7/localmanager/LocalEconomyEngine$Result;
    move-object v8, v9
    move-object v9, v6
    invoke-direct { v8, v9 }, Lcom/project7/localmanager/LocalEconomyEngine$Result;-><init>([B)V
    const/4 v5, 0
    iput-boolean v5, v8, Lcom/project7/localmanager/LocalEconomyEngine$Result;->accepted:Z
    iput v5, v8, Lcom/project7/localmanager/LocalEconomyEngine$Result;->win:I
    iget-object v10, v7, Lcom/project7/localmanager/StoryCityCocPolicy$Admission;->reason:Ljava/lang/String;
    iput-object v10, v8, Lcom/project7/localmanager/LocalEconomyEngine$Result;->reason:Ljava/lang/String;
    return-object v8
  :L2
    move-object p1, v10
    move-object v8, v0
    move-object v9, v1
    move-object v10, v3
    invoke-interface { v8, v9, v10 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v6
    new-instance v9, Lcom/project7/localmanager/LocalEconomyEngine$Result;
    move-object v8, v9
    move-object v9, v6
    invoke-direct { v8, v9 }, Lcom/project7/localmanager/LocalEconomyEngine$Result;-><init>([B)V
    const/4 v5, 0
    iput-boolean v5, v8, Lcom/project7/localmanager/LocalEconomyEngine$Result;->accepted:Z
    iput v5, v8, Lcom/project7/localmanager/LocalEconomyEngine$Result;->win:I
    iget-object v10, p1, Lcom/project7/localmanager/StoryCityCocPolicy$Settlement;->reason:Ljava/lang/String;
    iput-object v10, v8, Lcom/project7/localmanager/LocalEconomyEngine$Result;->reason:Ljava/lang/String;
    return-object v8
  :L3
    invoke-interface { p0, p1, p2, p3, p4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateEconomy(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalEconomyEngine$Result;
    move-result-object v9
    return-object v9
.end method

.method private static readByte(Ljava/io/InputStream;)I
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 1
  .line 2644
    invoke-virtual { p0 }, Ljava/io/InputStream;->read()I
    move-result p0
  .line 2645
    if-ltz p0, :L0
  .line 2648
    return p0
  :L0
  .line 2646
    new-instance p0, Ljava/io/EOFException;
    invoke-direct { p0 }, Ljava/io/EOFException;-><init>()V
    throw p0
.end method

.method private static readExactly(Ljava/io/InputStream;I)[B
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 5
  .line 2652
    new-array v0, p1, [B
  .line 2653
    const/4 v1, 0
  :L0
  .line 2654
    if-ge v1, p1, :L2
  .line 2655
    sub-int v2, p1, v1
    invoke-virtual { p0, v0, v1, v2 }, Ljava/io/InputStream;->read([BII)I
    move-result v2
  .line 2656
    if-ltz v2, :L1
  .line 2659
    add-int/2addr v1, v2
  .line 2660
    goto :L0
  :L1
  .line 2657
    new-instance p0, Ljava/io/EOFException;
    invoke-direct { p0 }, Ljava/io/EOFException;-><init>()V
    throw p0
  :L2
  .line 2661
    return-object v0
.end method

.method private readFrame(Ljava/io/InputStream;)Lcom/project7/localmanager/LocalGatewayServer$Frame;
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 6
  .line 2585
    invoke-static { p1 }, Lcom/project7/localmanager/LocalGatewayServer;->readLeInt(Ljava/io/InputStream;)I
    move-result v0
  .line 2586
    const/4 v1, 2
    if-lt v0, v1, :L0
    const/high16 v2, 1024
    if-gt v0, v2, :L0
  .line 2589
    invoke-static { p1 }, Lcom/project7/localmanager/LocalGatewayServer;->readByte(Ljava/io/InputStream;)I
    move-result v2
  .line 2590
    invoke-static { p1 }, Lcom/project7/localmanager/LocalGatewayServer;->readByte(Ljava/io/InputStream;)I
    move-result v3
  .line 2591
    sub-int/2addr v0, v1
    invoke-static { p1, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->readExactly(Ljava/io/InputStream;I)[B
    move-result-object p1
  .line 2592
    new-instance v0, Lcom/project7/localmanager/LocalGatewayServer$Frame;
    shl-int/lit8 v1, v3, 8
    or-int/2addr v1, v2
    invoke-direct { v0, v1, p1 }, Lcom/project7/localmanager/LocalGatewayServer$Frame;-><init>(I[B)V
    return-object v0
  :L0
  .line 2587
    new-instance p1, Ljava/io/IOException;
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "invalid frame size "
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-direct { p1, v0 }, Ljava/io/IOException;-><init>(Ljava/lang/String;)V
    throw p1
.end method

.method private static readLeInt(Ljava/io/InputStream;)I
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 4
  .line 2629
    invoke-static { p0 }, Lcom/project7/localmanager/LocalGatewayServer;->readByte(Ljava/io/InputStream;)I
    move-result v0
  .line 2630
    invoke-static { p0 }, Lcom/project7/localmanager/LocalGatewayServer;->readByte(Ljava/io/InputStream;)I
    move-result v1
  .line 2631
    invoke-static { p0 }, Lcom/project7/localmanager/LocalGatewayServer;->readByte(Ljava/io/InputStream;)I
    move-result v2
  .line 2632
    invoke-static { p0 }, Lcom/project7/localmanager/LocalGatewayServer;->readByte(Ljava/io/InputStream;)I
    move-result p0
  .line 2633
    shl-int/lit8 v1, v1, 8
    or-int/2addr v0, v1
    shl-int/lit8 v1, v2, 16
    or-int/2addr v0, v1
    shl-int/lit8 p0, p0, 24
    or-int/2addr p0, v0
    return p0
.end method

.method private refreshResourceProfile([BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 27
  .line 1173
    move-object/from16 v0, p0
    move-object/from16 v1, p1
    move-object/from16 v2, p2
    move-object/from16 v3, p3
    move-object/from16 v4, p4
    if-eqz v4, :L21
    const-string v5, "requestItemHotRankList"
    invoke-static { v5 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v5
    invoke-static { v1, v5 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v5
    if-eqz v5, :L0
    goto/16 :L21
  :L0
  .line 1174
    const/4 v5, 4
    new-array v6, v5, [[Ljava/lang/String;
    sget-object v7, Lcom/project7/localmanager/LocalArtifactEngine;->METHODS:[Ljava/lang/String;
    const/4 v8, 0
    aput-object v7, v6, v8
    sget-object v7, Lcom/project7/localmanager/LocalSkinDyeEngine;->METHODS:[Ljava/lang/String;
    const/4 v9, 1
    aput-object v7, v6, v9
    const/4 v7, 2
    sget-object v9, Lcom/project7/localmanager/LocalGuildEngine;->METHODS:[Ljava/lang/String;
    aput-object v9, v6, v7
    const/4 v7, 3
    sget-object v9, Lcom/project7/localmanager/LocalGuildShopEngine;->METHODS:[Ljava/lang/String;
    aput-object v9, v6, v7
    move v7, v8
  :L1
    if-ge v7, v5, :L5
    aget-object v9, v6, v7
  .line 1175
    array-length v10, v9
    move v11, v8
  :L2
    if-ge v11, v10, :L4
    aget-object v12, v9, v11
    invoke-static { v12 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v12
    invoke-static { v1, v12 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v12
    if-eqz v12, :L3
  .line 1176
    iget-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v1, v2, v3 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v1
    invoke-virtual { v4, v1 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
    return-void
  :L3
  .line 1175
    add-int/lit8 v11, v11, 1
    goto :L2
  :L4
  .line 1174
    add-int/lit8 v7, v7, 1
    goto :L1
  :L5
  .line 1178
    sget-object v5, Lcom/project7/localmanager/LocalWhiteNightEngine;->METHODS:[Ljava/lang/String;
    array-length v6, v5
    move v7, v8
  :L6
    if-ge v7, v6, :L8
    aget-object v9, v5, v7
    invoke-static { v9 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v9
    invoke-static { v1, v9 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v9
    if-eqz v9, :L7
  .line 1179
    iget-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v1, v2, v3 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v1
    invoke-virtual { v4, v1 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
    return-void
  :L7
  .line 1178
    add-int/lit8 v7, v7, 1
    goto :L6
  :L8
  .line 1181
    const/16 v5, 13
    const-string v9, "incHeroStarOrder"
    const-string v10, "tupoLiberateStage"
    const-string v11, "upgradeLiberate"
    const-string v12, "updateWanwufadian"
    const-string v13, "dressPendant"
    const-string v14, "liberateChange"
    const-string v15, "upgradeAwakeStage"
    const-string v16, "changeAwakeSkinStyle"
    const-string v17, "seeAwakeSkillChanged"
    const-string v18, "rewardAchievement"
    const-string v19, "requestNewAchievementReward"
    const-string v20, "requestNewAchievementAutoShow"
    const-string v21, "updateNewAchievementTaskFromClient"
    filled-new-array/range { v9 .. v21 }, [Ljava/lang/String;
    move-result-object v6
    move v7, v8
  :L9
    if-ge v7, v5, :L11
    aget-object v9, v6, v7
  .line 1185
    invoke-static { v9 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v9
    invoke-static { v1, v9 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v9
    if-eqz v9, :L10
  .line 1186
    iget-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v1, v2, v3 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v1
    invoke-virtual { v4, v1 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  .line 1187
    return-void
  :L10
  .line 1181
    add-int/lit8 v7, v7, 1
    goto :L9
  :L11
  .line 1190
    const/16 v5, 11
    const-string v9, "requestLuckyDrawFile"
    const-string v10, "requestLuckyDrawCard"
    const-string v11, "requestFile"
    const-string v12, "requestQuitFile"
    const-string v13, "requestLuckyDrawFileAndOpenAll"
    const-string v14, "requestLuckyDrawAllLeftCard"
    const-string v15, "setChooseHeroes"
    const-string v16, "requestLuckyDrawFriendCard"
    const-string v17, "requestLuckyDrawNewFriendCard"
    const-string v18, "requestLuckyDrawFriendLianChouCard"
    const-string v19, "requestLuckyDrawNewFriendLianChouCard"
    filled-new-array/range { v9 .. v19 }, [Ljava/lang/String;
    move-result-object v6
    move v7, v8
  :L12
    if-ge v7, v5, :L14
    aget-object v9, v6, v7
  .line 1193
    invoke-static { v9 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v9
    invoke-static { v1, v9 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v9
    if-eqz v9, :L13
  .line 1196
    iget-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v1, v2, v3 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v1
    invoke-virtual { v4, v1 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  .line 1197
    return-void
  :L13
  .line 1190
    add-int/lit8 v7, v7, 1
    goto :L12
  :L14
  .line 1200
    sget-object v5, Lcom/project7/localmanager/LocalTreasureOperationEngine;->METHODS:Ljava/util/List;
    invoke-interface { v5 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v5
  :L15
    invoke-interface { v5 }, Ljava/util/Iterator;->hasNext()Z
    move-result v6
    if-eqz v6, :L17
    invoke-interface { v5 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v6
    check-cast v6, Ljava/lang/String;
  .line 1201
    invoke-static { v6 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v6
    invoke-static { v1, v6 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v6
    if-eqz v6, :L16
  .line 1202
    iget-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v1, v2, v3 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v1
    invoke-virtual { v4, v1 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  .line 1203
    return-void
  :L16
  .line 1205
    goto :L15
  :L17
  .line 1206
    const/16 v5, 12
    const-string v9, "equipTreasureBatch"
    const-string v10, "unequipTreasure"
    const-string v11, "unequipAllTreasure"
    const-string v12, "unequipTreasureAllHero"
    const-string v13, "requestSaveTreasurePlan"
    const-string v14, "removeTreasurePlan"
    const-string v15, "requestUseTreasurePlan"
    const-string v16, "requestUnuseTreasurePlan"
    const-string v17, "changeTreasureForbid"
    const-string v18, "upgradeTreasure"
    const-string v19, "upgradeTreasureTargetLv"
    const-string v20, "upgradeAllTreasure"
    filled-new-array/range { v9 .. v20 }, [Ljava/lang/String;
    move-result-object v6
  :L18
    if-ge v8, v5, :L20
    aget-object v7, v6, v8
  .line 1210
    invoke-static { v7 }, Lcom/project7/localmanager/LocalGatewayServer;->digest(Ljava/lang/String;)[B
    move-result-object v7
    invoke-static { v1, v7 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v7
    if-eqz v7, :L19
  .line 1212
    iget-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v1, v2, v3 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v1
    invoke-virtual { v4, v1 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  .line 1213
    return-void
  :L19
  .line 1206
    add-int/lit8 v8, v8, 1
    goto :L18
  :L20
  .line 1218
    iget-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v1, v2, v3 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->snapshot(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v1
    invoke-virtual { v4, v1 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  .line 1219
    return-void
  :L21
  .line 1173
    return-void
.end method

.method private static resolveAreaId(Ljava/lang/Integer;Z)I
  .registers 4
  .line 2393
    if-nez p1, :L2
  .line 2394
    if-nez p0, :L0
    const/4 p0, 0
    goto :L1
  :L0
    invoke-virtual { p0 }, Ljava/lang/Integer;->intValue()I
    move-result p0
  :L1
    return p0
  :L2
  .line 2396
    const/4 p1, 1
    if-eqz p0, :L4
    invoke-virtual { p0 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    if-lt v0, p1, :L4
    invoke-virtual { p0 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    const/16 v1, 8
    if-le v0, v1, :L3
    goto :L4
  :L3
    invoke-virtual { p0 }, Ljava/lang/Integer;->intValue()I
    move-result p1
  :L4
    return p1
.end method

.method private restorePendingPatrol(Ljava/io/OutputStream;[BLcom/project7/localmanager/LocalTutorialStore$Progress;[BLcom/project7/localmanager/LocalEventEngine;)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 9
  .line 2374
    if-eqz p5, :L1
    invoke-static { p3, p4 }, Lcom/project7/localmanager/LocalPatrolEngine;->hasPendingChoice(Lcom/project7/localmanager/LocalTutorialStore$Progress;[B)Z
    move-result p4
    if-nez p4, :L0
    goto :L1
  :L0
  .line 2375
    const-string p4, "pushEvents"
    invoke-static { p4 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object p4
  .line 2376
    invoke-virtual { p5 }, Lcom/project7/localmanager/LocalEventEngine;->availableEvents()Ljava/util/Set;
    move-result-object v0
    invoke-virtual { p5 }, Lcom/project7/localmanager/LocalEventEngine;->processingEvents()Ljava/util/Set;
    move-result-object p5
    invoke-static { v0, p5 }, Lcom/project7/localmanager/BsonLite;->eventListsDocument(Ljava/lang/Iterable;Ljava/lang/Iterable;)[B
    move-result-object p5
  .line 2375
    invoke-static { p2, p4, p5 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object p4
    const/4 p5, 5
    invoke-direct { p0, p1, p5, p4 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2377
    const-string p4, "evalCode"
    invoke-static { p4 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object p4
    const/4 v0, 2
    new-array v0, v0, [Ljava/lang/Object;
    const/4 v1, 0
    const-string v2, "s"
    aput-object v2, v0, v1
    const/4 v1, 1
  .line 2378
    invoke-static { p3 }, Lcom/project7/localmanager/LocalPatrolEngine;->pendingChoiceSource(Lcom/project7/localmanager/LocalTutorialStore$Progress;)Ljava/lang/String;
    move-result-object v2
    invoke-static { v2 }, Lcom/project7/localmanager/LocalClientCompatibility;->encode(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v2
    aput-object v2, v0, v1
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v0
  .line 2377
    invoke-static { p2, p4, v0 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object p2
    invoke-direct { p0, p1, p5, p2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2379
    new-instance p1, Ljava/lang/StringBuilder;
    invoke-direct { p1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string p2, "restored paid patrol choice area="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget p2, p3, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolArea:I
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { p1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p1
    const-string p2, "Project7Gateway"
    invoke-static { p2, p1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 2380
    return-void
  :L1
  .line 2374
    return-void
.end method

.method private sendLoginFailure(Ljava/io/OutputStream;[BLjava/lang/String;)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 5
  .line 2484
    nop
  .line 2489
    const-string v0, "onLoginFail"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
  .line 2490
    invoke-static { p3 }, Lcom/project7/localmanager/BsonLite;->loginFailureDocument(Ljava/lang/String;)[B
    move-result-object p3
  .line 2487
    invoke-static { p2, v0, p3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object p2
  .line 2484
    const/4 p3, 5
    invoke-direct { p0, p1, p3, p2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2493
    return-void
.end method

.method private sendTutorialHeroReward(Ljava/io/OutputStream;[BLjava/lang/String;I)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 8
  .line 2410
    const/16 v0, 1001
    if-ne p4, v0, :L1
  .line 2411
    const/16 v0, 24
  .line 2415
    iget-object v1, p0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v1, p3, v0 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->ensureHero(Ljava/lang/String;I)Z
    move-result p3
    if-nez p3, :L0
  .line 2416
    return-void
  :L0
  .line 2418
    const/4 p3, 5
  .line 2423
    const-string v1, "addHero"
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
  .line 2424
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->addHeroDocument(I)[B
    move-result-object v2
  .line 2421
    invoke-static { p2, v1, v2 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object p2
  .line 2418
    invoke-direct { p0, p1, p3, p2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2427
    new-instance p1, Ljava/lang/StringBuilder;
    invoke-direct { p1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string p2, "tutorial hero granted event="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, p4 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string p2, " hero="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, v0 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { p1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p1
    const-string p2, "Project7Gateway"
    invoke-static { p2, p1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 2428
    return-void
  :L1
  .line 2413
    return-void
.end method

.method private static starterEventForHero(I)I
  .registers 2
  .line 2435
    const/16 v0, 8
    if-ne p0, v0, :L0
    const/16 p0, 1038
    goto :L2
  :L0
    const/4 v0, 7
    if-ne p0, v0, :L1
    const/16 p0, 1039
    goto :L2
  :L1
    const/16 p0, 1040
  :L2
    return p0
.end method

.method private static starterHeroForUsername(Ljava/lang/String;)I
  .registers 1
  .line 2431
    const/4 p0, 7
    return p0
.end method

.method private syncClientCompatibility(Ljava/io/OutputStream;[B)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 9
  .line 1150
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    invoke-interface { v0 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->clientCompatibility()Ljava/lang/String;
    move-result-object v0
  .line 1151
    invoke-virtual { v0 }, Ljava/lang/String;->isEmpty()Z
    move-result v1
    if-nez v1, :L0
    const/4 v1, 5
  .line 1153
    const-string v2, "evalCode"
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
    const/4 v3, 2
    new-array v3, v3, [Ljava/lang/Object;
    const/4 v4, 0
    const-string v5, "s"
    aput-object v5, v3, v4
    const/4 v4, 1
    invoke-static { v0 }, Lcom/project7/localmanager/LocalClientCompatibility;->encode(Ljava/lang/String;)Ljava/lang/String;
    move-result-object v0
    aput-object v0, v3, v4
    invoke-static { v3 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v0
  .line 1151
    invoke-static { p2, v2, v0 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object p2
    invoke-direct { p0, p1, v1, p2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  :L0
  .line 1154
    return-void
.end method

.method private syncDrawCalendar(Ljava/io/OutputStream;[B)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 7
  .line 2283
    nop
  .line 2284
    const-string v0, "evalCode"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
    const/4 v1, 2
    new-array v1, v1, [Ljava/lang/Object;
    const/4 v2, 0
    const-string v3, "s"
    aput-object v3, v1, v2
    const/4 v2, 1
    const-string v3, "import com.data.cdata.activity_config as ac; import com.data.cdata.chouka_info as ci; import com.utils.runtime_mapping_table as mt; ac.data=dict(ac.data); ac.data[175]=dict(ac.data[175]); ci.data=dict(ci.data); ci.data[484]=dict(ci.data[484]); ci.data[354]=dict(ci.data[354]); ci.data[354].update({'begin_time':(2016,1,1,7,0,0,0,0,0),'end_time':(2035,9,22,7,0,0,0,0,0)}); ac.data[175]['open_range']=(2021,9,22,7,0,0,2035,9,22,7,0,0); ci.data[484]['begin_time']=(2016,1,1,7,0,0,0,0,0); ci.data[484]['end_time']=(2035,9,22,7,0,0,0,0,0); mt.reload(); mt._CELL_MAPPING_CONFIG.setdefault('chouka_info',{}).setdefault(354,{}).update({'begin_time':ci.data[354]['begin_time'],'end_time':ci.data[354]['end_time']}); mt._CELL_MAPPING_CONFIG.setdefault('chouka_info',{}).setdefault(484,{}).update({'begin_time':ci.data[484]['begin_time'],'end_time':ci.data[484]['end_time']}); print('local_draw_calendar_v3', ci.data[484]['end_time'], mt.get_table('chouka_info').data.get(484,{}).get('end_time'))"
    aput-object v3, v1, v2
    invoke-static { v1 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v1
  .line 2283
    invoke-static { p2, v0, v1 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object p2
    const/4 v0, 5
    invoke-direct { p0, p1, v0, p2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2285
    return-void
.end method

.method private syncEventEffects(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 13
  .line 933
    nop
  .line 934
    invoke-direct { p0, p3, p4, p5 }, Lcom/project7/localmanager/LocalGatewayServer;->prepareEventEffects(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object v6
  .line 933
    move-object v0, p0
    move-object v1, p1
    move-object v2, p2
    move-object v3, p3
    move-object v4, p4
    move-object v5, p5
    invoke-direct/range { v0 .. v6 }, Lcom/project7/localmanager/LocalGatewayServer;->emitEventEffects(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;Lcom/project7/localmanager/LocalResourceEngine$Result;)V
  .line 935
    return-void
.end method

.method private syncPuzzleStart(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;Lcom/project7/localmanager/LocalEventEngine;I)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 11
  .line 910
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->eventCatalog:Lcom/project7/localmanager/LocalEventCatalog;
    if-eqz v0, :L4
    iget-object v0, v0, Lcom/project7/localmanager/LocalEventCatalog;->puzzleRooms:Ljava/util/Map;
    invoke-static { p6 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v1
    invoke-interface { v0, v1 }, Ljava/util/Map;->containsKey(Ljava/lang/Object;)Z
    move-result v0
    if-nez v0, :L0
    goto :L4
  :L0
  .line 911
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
    const/4 v1, 2
    new-array v1, v1, [Ljava/lang/Object;
    const/4 v2, 0
    const-string v3, "e"
    aput-object v3, v1, v2
    const/4 v2, 1
  .line 912
    invoke-static { p6 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v3
    aput-object v3, v1, v2
    invoke-static { v1 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v1
  .line 911
    const-string v2, "q7PuzzleBegin"
    invoke-interface { v0, p3, v2, v1, p4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->updateServices(Ljava/lang/String;Ljava/lang/String;[BLcom/project7/localmanager/LocalTutorialStore$Progress;)Lcom/project7/localmanager/LocalResourceEngine$Result;
    move-result-object p3
  .line 913
    iget-object p4, p3, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { p4 }, Ljava/util/List;->stream()Ljava/util/stream/Stream;
    move-result-object p4
    sget-object v0, Lcom/project7/localmanager/LocalGatewayServer$$ExternalSyntheticLambda3;->INSTANCE:Lcom/project7/localmanager/LocalGatewayServer$$ExternalSyntheticLambda3;
    invoke-interface { p4, v0 }, Ljava/util/stream/Stream;->noneMatch(Ljava/util/function/Predicate;)Z
    move-result p4
    if-nez p4, :L3
  .line 915
    iget-object p4, p3, Lcom/project7/localmanager/LocalResourceEngine$Result;->profile:[B
    invoke-virtual { p5, p4 }, Lcom/project7/localmanager/LocalEventEngine;->refreshProfile([B)V
  .line 916
    iget-object p3, p3, Lcom/project7/localmanager/LocalResourceEngine$Result;->replies:Ljava/util/List;
    invoke-interface { p3 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object p3
  :L1
    invoke-interface { p3 }, Ljava/util/Iterator;->hasNext()Z
    move-result p4
    if-eqz p4, :L2
    invoke-interface { p3 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object p4
    check-cast p4, Lcom/project7/localmanager/LocalResourceEngine$Reply;
  .line 917
    const/4 p5, 5
    iget-object p6, p4, Lcom/project7/localmanager/LocalResourceEngine$Reply;->method:Ljava/lang/String;
    invoke-static { p6 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object p6
    iget-object p4, p4, Lcom/project7/localmanager/LocalResourceEngine$Reply;->parameters:[B
    invoke-static { p2, p6, p4 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object p4
    invoke-direct { p0, p1, p5, p4 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
    goto :L1
  :L2
  .line 918
    return-void
  :L3
  .line 914
    new-instance p1, Ljava/io/IOException;
    new-instance p2, Ljava/lang/StringBuilder;
    invoke-direct { p2 }, Ljava/lang/StringBuilder;-><init>()V
    const-string p3, "authorized puzzle room could not resume event="
    invoke-virtual { p2, p3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p2, p6 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { p2 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p2
    invoke-direct { p1, p2 }, Ljava/io/IOException;-><init>(Ljava/lang/String;)V
    throw p1
  :L4
  .line 910
    return-void
.end method

.method private syncTutorialCityCompletion(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;I)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 7
  .line 1167
    const/16 v0, 1004
    if-eq p5, v0, :L0
    const/16 v0, 1047
    if-eq p5, v0, :L0
    const/16 v0, 1013
    if-ne p5, v0, :L1
  :L0
  .line 1168
    invoke-direct/range { p0 .. p5 }, Lcom/project7/localmanager/LocalGatewayServer;->syncTutorialCityState(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;I)V
  :L1
  .line 1169
    return-void
.end method

.method private syncTutorialCityState(Ljava/io/OutputStream;[BLjava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;I)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 10
  .line 1158
    invoke-static { p4 }, Lcom/project7/localmanager/LocalGatewayServer;->isHighSchoolUnlocked(Lcom/project7/localmanager/LocalTutorialStore$Progress;)Z
    move-result v0
    if-nez v0, :L0
    return-void
  :L0
  .line 1159
    const/4 v0, 5
  .line 1160
    const-string v1, "get_all_area_info_reply"
    invoke-static { v1 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v1
    const/4 v2, 1
    iget-object v3, p0, Lcom/project7/localmanager/LocalGatewayServer;->profileProvider:Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;
  .line 1161
    invoke-interface { v3, p3, p4 }, Lcom/project7/localmanager/LocalGatewayServer$ProfileProvider;->load(Ljava/lang/String;Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object p3
  .line 1160
    invoke-static { v2, p4, p3 }, Lcom/project7/localmanager/BsonLite;->allAreaInfoReplyDocument(ZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
    move-result-object p3
  .line 1159
    invoke-static { p2, v1, p3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object p2
    invoke-direct { p0, p1, v0, p2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 1162
    new-instance p1, Ljava/lang/StringBuilder;
    invoke-direct { p1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string p2, "city battle state refreshed after event="
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, p5 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { p1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p1
    const-string p2, "Project7Gateway"
    invoke-static { p2, p1 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 1163
    return-void
.end method

.method private triggerPendingNewbees(Ljava/io/OutputStream;[BLcom/project7/localmanager/LocalEventEngine;Ljava/util/Set;)V
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Ljava/io/OutputStream;",
      "[B",
      "Lcom/project7/localmanager/LocalEventEngine;",
      "Ljava/util/Set<",
      "Ljava/lang/Integer;",
      ">;)V"
    }
  .end annotation
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 9
  .line 2444
    if-nez p3, :L0
  .line 2445
    return-void
  :L0
  .line 2447
    invoke-virtual { p3 }, Lcom/project7/localmanager/LocalEventEngine;->processingNewbees()Ljava/util/Set;
    move-result-object p3
    invoke-interface { p3 }, Ljava/util/Set;->iterator()Ljava/util/Iterator;
    move-result-object p3
  :L1
    invoke-interface { p3 }, Ljava/util/Iterator;->hasNext()Z
    move-result v0
    if-eqz v0, :L3
    invoke-interface { p3 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Ljava/lang/Integer;
  .line 2448
    invoke-interface { p4, v0 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
    move-result v1
    if-nez v1, :L2
  .line 2449
    goto :L1
  :L2
  .line 2451
    const/4 v1, 5
  .line 2456
    const-string v2, "triggerClientNewbee"
    invoke-static { v2 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v2
  .line 2457
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v3
    invoke-static { v3 }, Lcom/project7/localmanager/BsonLite;->eventDocument(I)[B
    move-result-object v3
  .line 2454
    invoke-static { p2, v2, v3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object v2
  .line 2451
    invoke-direct { p0, p1, v1, v2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 2460
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct { v1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "pending tutorial guidance pushed event="
    invoke-virtual { v1, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual { v1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    const-string v1, "Project7Gateway"
    invoke-static { v1, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->i(Ljava/lang/String;Ljava/lang/String;)I
  .line 2461
    goto :L1
  :L3
  .line 2462
    return-void
.end method

.method private writeFrame(Ljava/io/OutputStream;I[B)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 5
  .line 2596
    array-length v0, p3
    add-int/lit8 v0, v0, 2
  .line 2597
    invoke-static { p1, v0 }, Lcom/project7/localmanager/LocalGatewayServer;->writeLeInt(Ljava/io/OutputStream;I)V
  .line 2598
    and-int/lit16 v0, p2, 255
    invoke-virtual { p1, v0 }, Ljava/io/OutputStream;->write(I)V
  .line 2599
    ushr-int/lit8 p2, p2, 8
    and-int/lit16 p2, p2, 255
    invoke-virtual { p1, p2 }, Ljava/io/OutputStream;->write(I)V
  .line 2600
    invoke-virtual { p1, p3 }, Ljava/io/OutputStream;->write([B)V
  .line 2601
    invoke-virtual { p1 }, Ljava/io/OutputStream;->flush()V
  .line 2602
    return-void
.end method

.method private static writeLeInt(Ljava/io/OutputStream;I)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 3
  .line 2637
    and-int/lit16 v0, p1, 255
    invoke-virtual { p0, v0 }, Ljava/io/OutputStream;->write(I)V
  .line 2638
    ushr-int/lit8 v0, p1, 8
    and-int/lit16 v0, v0, 255
    invoke-virtual { p0, v0 }, Ljava/io/OutputStream;->write(I)V
  .line 2639
    ushr-int/lit8 v0, p1, 16
    and-int/lit16 v0, v0, 255
    invoke-virtual { p0, v0 }, Ljava/io/OutputStream;->write(I)V
  .line 2640
    ushr-int/lit8 p1, p1, 24
    and-int/lit16 p1, p1, 255
    invoke-virtual { p0, p1 }, Ljava/io/OutputStream;->write(I)V
  .line 2641
    return-void
.end method

.method public close()V
  .catch Ljava/io/IOException; { :L2 .. :L3 } :L4
  .registers 3
  .line 2544
    const/4 v0, 1
    iput-boolean v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->closed:Z
  .line 2545
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->clients:Ljava/util/Set;
    invoke-interface { v0 }, Ljava/util/Set;->iterator()Ljava/util/Iterator;
    move-result-object v0
  :L0
    invoke-interface { v0 }, Ljava/util/Iterator;->hasNext()Z
    move-result v1
    if-eqz v1, :L1
    invoke-interface { v0 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;
    invoke-virtual { v1 }, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;->close()V
    goto :L0
  :L1
  .line 2546
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->connections:Ljava/util/concurrent/ThreadPoolExecutor;
    invoke-virtual { v0 }, Ljava/util/concurrent/ThreadPoolExecutor;->shutdownNow()Ljava/util/List;
  .line 2547
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->socket:Ljava/net/ServerSocket;
  .line 2548
    if-eqz v0, :L5
  :L2
  .line 2550
    invoke-virtual { v0 }, Ljava/net/ServerSocket;->close()V
  :L3
  .line 2552
    goto :L5
  :L4
  .line 2551
    move-exception v0
  :L5
  .line 2554
    return-void
.end method

.method currentUsername()Ljava/lang/String;
  .registers 3
  .line 2559
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->activeSession:Lcom/project7/localmanager/LocalGatewayServer$ClientSession;
  .line 2561
    iget-boolean v1, p0, Lcom/project7/localmanager/LocalGatewayServer;->closed:Z
    if-nez v1, :L0
    if-eqz v0, :L0
    iget-boolean v1, v0, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;->cancelled:Z
    if-nez v1, :L0
    iget-object v1, p0, Lcom/project7/localmanager/LocalGatewayServer;->clients:Ljava/util/Set;
  .line 2560
    invoke-interface { v1, v0 }, Ljava/util/Set;->contains(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :L0
    iget-object v1, v0, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;->client:Ljava/net/Socket;
  .line 2561
    invoke-virtual { v1 }, Ljava/net/Socket;->isClosed()Z
    move-result v1
    if-nez v1, :L0
    iget-object v0, v0, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;->username:Ljava/lang/String;
    goto :L1
  :L0
    const/4 v0, 0
  :L1
  .line 2560
    return-object v0
.end method

.method public synthetic lambda$run$5$LocalGatewayServer(Lcom/project7/localmanager/LocalGatewayServer$ClientSession;)V
  .catch Ljava/io/IOException; { :L0 .. :L1 } :L13
  .catch Ljava/lang/RuntimeException; { :L0 .. :L1 } :L12
  .catchall { :L0 .. :L1 } :L11
  .catchall { :L1 .. :L2 } :L5
  .catch Ljava/io/IOException; { :L3 .. :L4 } :L13
  .catch Ljava/lang/RuntimeException; { :L3 .. :L4 } :L12
  .catchall { :L3 .. :L4 } :L11
  .catchall { :L6 .. :L7 } :L8
  .catch Ljava/io/IOException; { :L9 .. :L11 } :L13
  .catch Ljava/lang/RuntimeException; { :L9 .. :L11 } :L12
  .catchall { :L9 .. :L11 } :L11
  .catchall { :L14 .. :L15 } :L11
  .registers 6
  :L0
  .line 228
    iget-object v0, p1, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;->client:Ljava/net/Socket;
  :L1
  .line 229
    invoke-direct { p0, v0, p1 }, Lcom/project7/localmanager/LocalGatewayServer;->handleClient(Ljava/net/Socket;Lcom/project7/localmanager/LocalGatewayServer$ClientSession;)V
  :L2
  .line 230
    if-eqz v0, :L15
  :L3
    invoke-virtual { v0 }, Ljava/net/Socket;->close()V
  :L4
    goto :L15
  :L5
  .line 228
    move-exception v1
    if-eqz v0, :L10
  :L6
    invoke-virtual { v0 }, Ljava/net/Socket;->close()V
  :L7
    goto :L10
  :L8
    move-exception v0
  :L9
    invoke-virtual { v1, v0 }, Ljava/lang/Throwable;->addSuppressed(Ljava/lang/Throwable;)V
  :L10
    throw v1
  :L11
  .line 234
    move-exception v0
    goto :L16
  :L12
  .line 230
    move-exception v0
    goto :L14
  :L13
    move-exception v0
  :L14
  .line 231
    iget-boolean v1, p0, Lcom/project7/localmanager/LocalGatewayServer;->closed:Z
    if-nez v1, :L15
    iget-boolean v1, p1, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;->cancelled:Z
    if-nez v1, :L15
  .line 232
    const-string v1, "Project7Gateway"
    new-instance v2, Ljava/lang/StringBuilder;
    invoke-direct { v2 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v3, "connection ended: "
    invoke-virtual { v2, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/lang/Object;->getClass()Ljava/lang/Class;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/lang/Class;->getSimpleName()Ljava/lang/String;
    move-result-object v0
    invoke-virtual { v2, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v2 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static { v1, v0 }, Lcom/project7/localmanager/LocalDiagnosticLog;->w(Ljava/lang/String;Ljava/lang/String;)I
  :L15
  .line 234
    iget-object v0, p1, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;->done:Ljava/util/concurrent/CountDownLatch;
    invoke-virtual { v0 }, Ljava/util/concurrent/CountDownLatch;->countDown()V
  .line 235
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->clients:Ljava/util/Set;
    invoke-interface { v0, p1 }, Ljava/util/Set;->remove(Ljava/lang/Object;)Z
  .line 236
    nop
  .line 237
    return-void
  :L16
  .line 234
    iget-object v1, p1, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;->done:Ljava/util/concurrent/CountDownLatch;
    invoke-virtual { v1 }, Ljava/util/concurrent/CountDownLatch;->countDown()V
  .line 235
    iget-object v1, p0, Lcom/project7/localmanager/LocalGatewayServer;->clients:Ljava/util/Set;
    invoke-interface { v1, p1 }, Ljava/util/Set;->remove(Ljava/lang/Object;)Z
  .line 236
    throw v0
.end method

.method public run()V
  .catch Ljava/io/IOException; { :L0 .. :L1 } :L24
  .catchall { :L0 .. :L1 } :L23
  .catchall { :L1 .. :L3 } :L17
  .catch Ljava/io/IOException; { :L4 .. :L5 } :L10
  .catchall { :L4 .. :L5 } :L17
  .catch Ljava/util/concurrent/RejectedExecutionException; { :L5 .. :L6 } :L7
  .catch Ljava/io/IOException; { :L5 .. :L6 } :L10
  .catchall { :L5 .. :L6 } :L17
  .catch Ljava/io/IOException; { :L8 .. :L9 } :L10
  .catchall { :L8 .. :L9 } :L17
  .catchall { :L11 .. :L12 } :L17
  .catch Ljava/io/IOException; { :L13 .. :L14 } :L24
  .catchall { :L13 .. :L14 } :L23
  .catchall { :L18 .. :L19 } :L20
  .catch Ljava/io/IOException; { :L21 .. :L23 } :L24
  .catchall { :L21 .. :L23 } :L23
  .catchall { :L25 .. :L26 } :L23
  .registers 12
  .line 216
    const-string v0, "Project7Gateway"
    const-string v1, "\n\u8d26\u53f7\u6a21\u677f\uff1atencolors"
    const-string v2, "\u76d1\u542c\u5730\u5740\uff1a127.0.0.1:"
    const/4 v3, 0
    const/4 v4, 0
  :L0
    new-instance v5, Ljava/net/ServerSocket;
    iget v6, p0, Lcom/project7/localmanager/LocalGatewayServer;->port:I
    const/4 v7, 4
    const-string v8, "127.0.0.1"
    invoke-static { v8 }, Ljava/net/InetAddress;->getByName(Ljava/lang/String;)Ljava/net/InetAddress;
    move-result-object v8
    invoke-direct { v5, v6, v7, v8 }, Ljava/net/ServerSocket;-><init>(IILjava/net/InetAddress;)V
  :L1
  .line 217
    iput-object v5, p0, Lcom/project7/localmanager/LocalGatewayServer;->socket:Ljava/net/ServerSocket;
  .line 218
    iget-object v6, p0, Lcom/project7/localmanager/LocalGatewayServer;->listener:Lcom/project7/localmanager/LocalGatewayServer$StatusListener;
    new-instance v7, Ljava/lang/StringBuilder;
    invoke-direct { v7 }, Ljava/lang/StringBuilder;-><init>()V
    invoke-virtual { v7, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget v8, p0, Lcom/project7/localmanager/LocalGatewayServer;->port:I
    invoke-virtual { v7, v8 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v8, "\n\u8d26\u53f7\u6a21\u677f\uff1atencolors\n\u7b49\u5f85\u6e38\u620f\u8fde\u63a5"
    invoke-virtual { v7, v8 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v7 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v7
    const/4 v8, 1
    invoke-interface { v6, v8, v7 }, Lcom/project7/localmanager/LocalGatewayServer$StatusListener;->onStatus(ZLjava/lang/String;)V
  :L2
  .line 219
    iget-boolean v6, p0, Lcom/project7/localmanager/LocalGatewayServer;->closed:Z
  :L3
    if-nez v6, :L13
  :L4
  .line 221
    invoke-virtual { v5 }, Ljava/net/ServerSocket;->accept()Ljava/net/Socket;
    move-result-object v6
  .line 222
    invoke-virtual { v6, v8 }, Ljava/net/Socket;->setTcpNoDelay(Z)V
  .line 223
    const/16 v7, 15000
    invoke-virtual { v6, v7 }, Ljava/net/Socket;->setSoTimeout(I)V
  .line 224
    new-instance v7, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;
    invoke-direct { v7, v6 }, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;-><init>(Ljava/net/Socket;)V
  .line 225
    iget-object v6, p0, Lcom/project7/localmanager/LocalGatewayServer;->clients:Ljava/util/Set;
    invoke-interface { v6, v7 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
  :L5
  .line 227
    iget-object v6, p0, Lcom/project7/localmanager/LocalGatewayServer;->connections:Ljava/util/concurrent/ThreadPoolExecutor;
    new-instance v9, Lcom/project7/localmanager/LocalGatewayServer$$ExternalSyntheticLambda0;
    invoke-direct { v9, p0, v7 }, Lcom/project7/localmanager/LocalGatewayServer$$ExternalSyntheticLambda0;-><init>(Lcom/project7/localmanager/LocalGatewayServer;Lcom/project7/localmanager/LocalGatewayServer$ClientSession;)V
    invoke-virtual { v6, v9 }, Ljava/util/concurrent/ThreadPoolExecutor;->execute(Ljava/lang/Runnable;)V
  :L6
  .line 241
    goto :L12
  :L7
  .line 238
    move-exception v6
  :L8
  .line 239
    iget-object v6, p0, Lcom/project7/localmanager/LocalGatewayServer;->clients:Ljava/util/Set;
    invoke-interface { v6, v7 }, Ljava/util/Set;->remove(Ljava/lang/Object;)Z
  .line 240
    invoke-virtual { v7 }, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;->close()V
  :L9
    goto :L12
  :L10
  .line 242
    move-exception v6
  :L11
  .line 243
    iget-boolean v7, p0, Lcom/project7/localmanager/LocalGatewayServer;->closed:Z
    if-nez v7, :L12
  .line 244
    const-string v7, "client connection failed"
    invoke-static { v0, v7, v6 }, Lcom/project7/localmanager/LocalDiagnosticLog;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
  .line 245
    iget-object v7, p0, Lcom/project7/localmanager/LocalGatewayServer;->listener:Lcom/project7/localmanager/LocalGatewayServer$StatusListener;
    new-instance v9, Ljava/lang/StringBuilder;
    invoke-direct { v9 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v10, "\u7f51\u5173\u8fde\u63a5\u9519\u8bef\uff1a"
    invoke-virtual { v9, v10 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v6 }, Ljava/io/IOException;->getMessage()Ljava/lang/String;
    move-result-object v6
    invoke-virtual { v9, v6 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v9 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v6
    invoke-interface { v7, v8, v6 }, Lcom/project7/localmanager/LocalGatewayServer$StatusListener;->onStatus(ZLjava/lang/String;)V
  :L12
  .line 247
    goto :L2
  :L13
  .line 249
    invoke-virtual { v5 }, Ljava/net/ServerSocket;->close()V
  :L14
  .line 255
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->clients:Ljava/util/Set;
    invoke-interface { v0 }, Ljava/util/Set;->iterator()Ljava/util/Iterator;
    move-result-object v0
  :L15
    invoke-interface { v0 }, Ljava/util/Iterator;->hasNext()Z
    move-result v5
    if-eqz v5, :L16
    invoke-interface { v0 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v5
    check-cast v5, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;
    invoke-virtual { v5 }, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;->close()V
    goto :L15
  :L16
  .line 256
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->connections:Ljava/util/concurrent/ThreadPoolExecutor;
    invoke-virtual { v0 }, Ljava/util/concurrent/ThreadPoolExecutor;->shutdownNow()Ljava/util/List;
  .line 257
    iput-object v3, p0, Lcom/project7/localmanager/LocalGatewayServer;->socket:Ljava/net/ServerSocket;
  .line 258
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->listener:Lcom/project7/localmanager/LocalGatewayServer$StatusListener;
    new-instance v3, Ljava/lang/StringBuilder;
    invoke-direct { v3 }, Ljava/lang/StringBuilder;-><init>()V
    goto :L29
  :L17
  .line 216
    move-exception v6
  :L18
    invoke-virtual { v5 }, Ljava/net/ServerSocket;->close()V
  :L19
    goto :L22
  :L20
    move-exception v5
  :L21
    invoke-virtual { v6, v5 }, Ljava/lang/Throwable;->addSuppressed(Ljava/lang/Throwable;)V
  :L22
    throw v6
  :L23
  .line 255
    move-exception v0
    goto :L30
  :L24
  .line 249
    move-exception v5
  :L25
  .line 250
    iget-boolean v6, p0, Lcom/project7/localmanager/LocalGatewayServer;->closed:Z
    if-nez v6, :L26
  .line 251
    const-string v6, "gateway listener failed"
    invoke-static { v0, v6, v5 }, Lcom/project7/localmanager/LocalDiagnosticLog;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
  .line 252
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->listener:Lcom/project7/localmanager/LocalGatewayServer$StatusListener;
    new-instance v6, Ljava/lang/StringBuilder;
    invoke-direct { v6 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v7, "\u65e0\u6cd5\u76d1\u542c 127.0.0.1:"
    invoke-virtual { v6, v7 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget v7, p0, Lcom/project7/localmanager/LocalGatewayServer;->port:I
    invoke-virtual { v6, v7 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string v7, "\uff1a"
    invoke-virtual { v6, v7 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v5 }, Ljava/io/IOException;->getMessage()Ljava/lang/String;
    move-result-object v5
    invoke-virtual { v6, v5 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v6 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v5
    invoke-interface { v0, v4, v5 }, Lcom/project7/localmanager/LocalGatewayServer$StatusListener;->onStatus(ZLjava/lang/String;)V
  :L26
  .line 255
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->clients:Ljava/util/Set;
    invoke-interface { v0 }, Ljava/util/Set;->iterator()Ljava/util/Iterator;
    move-result-object v0
  :L27
    invoke-interface { v0 }, Ljava/util/Iterator;->hasNext()Z
    move-result v5
    if-eqz v5, :L28
    invoke-interface { v0 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v5
    check-cast v5, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;
    invoke-virtual { v5 }, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;->close()V
    goto :L27
  :L28
  .line 256
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->connections:Ljava/util/concurrent/ThreadPoolExecutor;
    invoke-virtual { v0 }, Ljava/util/concurrent/ThreadPoolExecutor;->shutdownNow()Ljava/util/List;
  .line 257
    iput-object v3, p0, Lcom/project7/localmanager/LocalGatewayServer;->socket:Ljava/net/ServerSocket;
  .line 258
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->listener:Lcom/project7/localmanager/LocalGatewayServer$StatusListener;
    new-instance v3, Ljava/lang/StringBuilder;
    invoke-direct { v3 }, Ljava/lang/StringBuilder;-><init>()V
  :L29
    invoke-virtual { v3, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget v2, p0, Lcom/project7/localmanager/LocalGatewayServer;->port:I
    invoke-virtual { v3, v2 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v3, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v3 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-interface { v0, v4, v1 }, Lcom/project7/localmanager/LocalGatewayServer$StatusListener;->onStatus(ZLjava/lang/String;)V
  .line 259
    nop
  .line 260
    return-void
  :L30
  .line 255
    iget-object v5, p0, Lcom/project7/localmanager/LocalGatewayServer;->clients:Ljava/util/Set;
    invoke-interface { v5 }, Ljava/util/Set;->iterator()Ljava/util/Iterator;
    move-result-object v5
  :L31
    invoke-interface { v5 }, Ljava/util/Iterator;->hasNext()Z
    move-result v6
    if-eqz v6, :L32
    invoke-interface { v5 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v6
    check-cast v6, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;
    invoke-virtual { v6 }, Lcom/project7/localmanager/LocalGatewayServer$ClientSession;->close()V
    goto :L31
  :L32
  .line 256
    iget-object v5, p0, Lcom/project7/localmanager/LocalGatewayServer;->connections:Ljava/util/concurrent/ThreadPoolExecutor;
    invoke-virtual { v5 }, Ljava/util/concurrent/ThreadPoolExecutor;->shutdownNow()Ljava/util/List;
  .line 257
    iput-object v3, p0, Lcom/project7/localmanager/LocalGatewayServer;->socket:Ljava/net/ServerSocket;
  .line 258
    iget-object v3, p0, Lcom/project7/localmanager/LocalGatewayServer;->listener:Lcom/project7/localmanager/LocalGatewayServer$StatusListener;
    new-instance v5, Ljava/lang/StringBuilder;
    invoke-direct { v5 }, Ljava/lang/StringBuilder;-><init>()V
    invoke-virtual { v5, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget v2, p0, Lcom/project7/localmanager/LocalGatewayServer;->port:I
    invoke-virtual { v5, v2 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v5, v1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v5 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-interface { v3, v4, v1 }, Lcom/project7/localmanager/LocalGatewayServer$StatusListener;->onStatus(ZLjava/lang/String;)V
  .line 259
    throw v0
.end method

.method saveWritersStopped()Z
  .registers 2
  .line 2556
    iget-object v0, p0, Lcom/project7/localmanager/LocalGatewayServer;->connections:Ljava/util/concurrent/ThreadPoolExecutor;
    invoke-virtual { v0 }, Ljava/util/concurrent/ThreadPoolExecutor;->isTerminated()Z
    move-result v0
    return v0
.end method

.method syncFurnitureLogin(Ljava/io/OutputStream;[B[B)V
  .annotation system Ldalvik/annotation/Throws;
    value = {
      Ljava/io/IOException;
    }
  .end annotation
  .registers 8
  .line 792
    const-string v0, "reInitFromDict"
    invoke-static { v0 }, Lcom/project7/localmanager/LocalGatewayServer;->md5(Ljava/lang/String;)[B
    move-result-object v0
    const/4 v1, 2
    new-array v1, v1, [Ljava/lang/Object;
    const/4 v2, 0
    const-string v3, "d"
    aput-object v3, v1, v2
  .line 793
    const-string v2, "fnd"
    invoke-static { p3, v2 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object p3
    const/4 v2, 1
    aput-object p3, v1, v2
    invoke-static { v1 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object p3
  .line 792
    invoke-static { p2, v0, p3 }, Lcom/project7/localmanager/ProtoLite;->entityMessage([B[B[B)[B
    move-result-object p2
    const/4 p3, 5
    invoke-direct { p0, p1, p3, p2 }, Lcom/project7/localmanager/LocalGatewayServer;->writeFrame(Ljava/io/OutputStream;I[B)V
  .line 794
    return-void
.end method
