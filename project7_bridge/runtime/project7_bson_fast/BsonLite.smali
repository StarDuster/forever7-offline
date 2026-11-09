.class final Lcom/project7/localmanager/BsonLite;
.super Ljava/lang/Object;
.source "BsonLite.java"

.annotation system Ldalvik/annotation/MemberClasses;
  value = {
    Lcom/project7/localmanager/BsonLite$Element;,
    Lcom/project7/localmanager/BsonLite$UuidValue;,
    Lcom/project7/localmanager/BsonLite$BinaryValue;,
    Lcom/project7/localmanager/BsonLite$ArrayValue;
  }
.end annotation

.field final static EMPTY_DOCUMENT:[B

.field private final static HERO_INDEX:Ljava/lang/ThreadLocal;
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "Ljava/lang/ThreadLocal<",
      "Ljava/util/LinkedHashMap<",
      "[B",
      "Ljava/util/Map<",
      "Ljava/lang/Integer;",
      "[B>;>;>;"
    }
  .end annotation
.end field

.method static constructor <clinit>()V
  .registers 1
  .line 14
    const/4 v0, 5
    new-array v0, v0, [B
    fill-array-data v0, :L0
    sput-object v0, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
  .line 267
    sget-object v0, Lcom/project7/localmanager/BsonLite$$ExternalSyntheticLambda0;->INSTANCE:Lcom/project7/localmanager/BsonLite$$ExternalSyntheticLambda0;
  .line 268
    invoke-static { v0 }, Ljava/lang/ThreadLocal;->withInitial(Ljava/util/function/Supplier;)Ljava/lang/ThreadLocal;
    move-result-object v0
    sput-object v0, Lcom/project7/localmanager/BsonLite;->HERO_INDEX:Ljava/lang/ThreadLocal;
  .line 267
    return-void
  :L0
  .array-data 1
    5t
    0t
    0t
    0t
    0t
  .end array-data
.end method

.method private constructor <init>()V
  .registers 1
  .line 16
    invoke-direct { p0 }, Ljava/lang/Object;-><init>()V
  .line 17
    return-void
.end method

.method static addHeroDocument(I)[B
  .registers 3
  .line 742
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 743
    const-string v1, "h"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 744
    invoke-static { p0 }, Lcom/project7/localmanager/BsonLite;->heroDataDocument(I)[B
    move-result-object p0
    const-string v1, "d"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 745
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static allAreaInfoReplyDocument(Z)[B
  .registers 2
  .line 374
    const/4 v0, 0
    invoke-static { p0, v0 }, Lcom/project7/localmanager/BsonLite;->allAreaInfoReplyDocument(ZLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object p0
    return-object p0
.end method

.method static allAreaInfoReplyDocument(ZLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
  .registers 4
  .line 379
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 380
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->areasDocument(ZLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object p0
    const-string v1, "ais"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 381
    invoke-static { p1 }, Lcom/project7/localmanager/BsonLite;->cityValuesDocument(Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object p0
    const-string p1, "cd"
    invoke-static { v0, p1, p0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 382
    const-string p0, "sm"
    const/4 p1, 0
    invoke-static { v0, p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
  .line 383
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static allAreaInfoReplyDocument(ZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
  .registers 4
    invoke-static { p0, p1, p2 }, Lcom/project7/localmanager/StoryCityPolicy;->allAreaInfoReplyDocument(ZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
    move-result-object v0
    return-object v0
.end method

.method private static areaDocument(IZLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
  .registers 4
  .line 481
    const/4 v0, 0
    invoke-static { p0, p1, p2, v0 }, Lcom/project7/localmanager/BsonLite;->areaDocument(IZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
    move-result-object p0
    return-object p0
.end method

.method private static areaDocument(IZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
  .registers 7
  .line 486
    const/4 v0, 2
    const/4 v1, 1
    if-lt p0, v1, :L0
    const/16 v2, 8
    if-gt p0, v2, :L0
    goto :L1
  :L0
    move p0, v0
  :L1
  .line 488
    if-eqz p1, :L4
  .line 489
    if-nez p2, :L2
    if-ne p0, v1, :L3
    move v0, v1
    goto :L3
  :L2
  .line 490
    invoke-static { p2, p0, p3 }, Lcom/project7/localmanager/LocalCityProgress;->status(Lcom/project7/localmanager/LocalTutorialStore$Progress;I[B)I
    move-result p1
    move v0, p1
  :L3
    goto :L5
  :L4
  .line 492
    nop
  :L5
  .line 495
    new-instance p1, Ljava/io/ByteArrayOutputStream;
    invoke-direct { p1 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 496
    const-string v2, "0"
    invoke-static { p1, v2, v0 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 497
    const-string v0, "1"
    const/4 v2, 0
    invoke-static { p1, v0, v2 }, Lcom/project7/localmanager/BsonLite;->writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
  .line 498
    const-string v0, "2"
    invoke-static { p1, v0, v2 }, Lcom/project7/localmanager/BsonLite;->writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
  .line 500
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 501
    const-string v2, "id"
    invoke-static { v0, v2, p0 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 502
    invoke-static { p1 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p1
    const-string v2, "st"
    invoke-static { v0, v2, p1 }, Lcom/project7/localmanager/BsonLite;->writeArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 503
    const-string p1, "lv"
    invoke-static { v0, p1, v1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 504
    sget-object p1, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    const-string v1, "bd"
    invoke-static { v0, v1, p1 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 505
    const-string v1, "dbd"
    invoke-static { v0, v1, p1 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 506
    const/4 p1, 4
    const-string v1, "mbn"
    invoke-static { v0, v1, p1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 507
    invoke-static { p2, p0, p3 }, Lcom/project7/localmanager/LocalCityProgress;->mapStages(Lcom/project7/localmanager/LocalTutorialStore$Progress;I[B)[B
    move-result-object p0
    const-string p1, "stage"
    invoke-static { v0, p1, p0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 508
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static areaInfoReplyDocument(IZ)[B
  .registers 3
  .line 387
    const/4 v0, 0
    invoke-static { p0, p1, v0 }, Lcom/project7/localmanager/BsonLite;->areaInfoReplyDocument(IZLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object p0
    return-object p0
.end method

.method static areaInfoReplyDocument(IZLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
  .registers 4
  .line 402
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 403
    nop
  .line 406
    if-eqz p1, :L0
    const/4 p1, 1
    invoke-static { p0, p1, p2 }, Lcom/project7/localmanager/BsonLite;->areaDocument(IZLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object p0
    goto :L1
  :L0
    sget-object p0, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
  :L1
  .line 403
    const-string p1, "ai"
    invoke-static { v0, p1, p0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 408
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static areaInfoReplyDocument(IZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
  .registers 7
  .line 396
    const/4 v0, 2
    new-array v0, v0, [Ljava/lang/Object;
    const/4 v1, 0
    const-string v2, "ai"
    aput-object v2, v0, v1
    const/4 v1, 1
    if-eqz p1, :L0
    invoke-static { v1, p2, p3 }, Lcom/project7/localmanager/BsonLite;->persistedAreas(ZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
    move-result-object p1
    new-instance p2, Ljava/lang/StringBuilder;
    invoke-direct { p2 }, Ljava/lang/StringBuilder;-><init>()V
    const-string p3, "area_"
    invoke-virtual { p2, p3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p2, p0 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { p2 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p0
    invoke-static { p1, p0 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object p0
    goto :L1
  :L0
  .line 397
    sget-object p0, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
  :L1
    aput-object p0, v0, v1
  .line 396
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object p0
    return-object p0
.end method

.method private static areaStagesDocument(ILcom/project7/localmanager/LocalTutorialStore$Progress;)[B
  .registers 2
  .line 619
    invoke-static { p1, p0 }, Lcom/project7/localmanager/LocalCityProgress;->stages(Lcom/project7/localmanager/LocalTutorialStore$Progress;I)[B
    move-result-object p0
    return-object p0
.end method

.method static areaStagesReplyDocument(I)[B
  .registers 2
  .line 359
    const/4 v0, 0
    invoke-static { p0, v0 }, Lcom/project7/localmanager/BsonLite;->areaStagesReplyDocument(ILcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object p0
    return-object p0
.end method

.method static areaStagesReplyDocument(ILcom/project7/localmanager/LocalTutorialStore$Progress;)[B
  .registers 3
  .line 363
    const/4 v0, 0
    invoke-static { p0, p1, v0 }, Lcom/project7/localmanager/BsonLite;->areaStagesReplyDocument(ILcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
    move-result-object p0
    return-object p0
.end method

.method static areaStagesReplyDocument(ILcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
  .registers 5
  .line 367
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 368
    const-string v1, "ai"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 369
    invoke-static { p1, p0, p2 }, Lcom/project7/localmanager/LocalCityProgress;->stages(Lcom/project7/localmanager/LocalTutorialStore$Progress;I[B)[B
    move-result-object p0
    const-string p1, "st"
    invoke-static { v0, p1, p0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 370
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method private static areasDocument(ZLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
  .registers 3
  .line 456
    const/4 v0, 0
    invoke-static { p0, p1, v0 }, Lcom/project7/localmanager/BsonLite;->areasDocument(ZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
    move-result-object p0
    return-object p0
.end method

.method private static areasDocument(ZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
  .registers 7
  .line 461
    if-nez p0, :L0
  .line 462
    sget-object p0, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    return-object p0
  :L0
  .line 464
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 465
    const/4 v1, 1
  :L1
    const/16 v2, 8
    if-gt v1, v2, :L2
  .line 466
    new-instance v2, Ljava/lang/StringBuilder;
    invoke-direct { v2 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v3, "area_"
    invoke-virtual { v2, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v2, v1 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { v2 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v2
  .line 469
    invoke-static { v1, p0, p1, p2 }, Lcom/project7/localmanager/BsonLite;->areaDocument(IZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
    move-result-object v3
  .line 466
    invoke-static { v0, v2, v3 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 465
    add-int/lit8 v1, v1, 1
    goto :L1
  :L2
  .line 472
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static arrayValue([BLjava/lang/String;)[B
  .registers 3
  .line 97
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->findElement([BLjava/lang/String;)Lcom/project7/localmanager/BsonLite$Element;
    move-result-object p0
  .line 98
    if-eqz p0, :L0
    iget p1, p0, Lcom/project7/localmanager/BsonLite$Element;->type:I
    const/4 v0, 4
    if-ne p1, v0, :L0
    iget-object p0, p0, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    goto :L1
  :L0
    const/4 p0, 0
  :L1
    return-object p0
.end method

.method static bbsSkinReplyDocument(Ljava/lang/Iterable;I)[B
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Ljava/lang/Iterable<",
      "Ljava/lang/Integer;",
      ">;I)[B"
    }
  .end annotation
  .registers 4
  .line 990
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 991
    invoke-static { p0 }, Lcom/project7/localmanager/BsonLite;->profileIntArrayBytes(Ljava/lang/Iterable;)[B
    move-result-object p0
    const-string v1, "tbk"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 992
    const-string p0, "bk"
    invoke-static { v0, p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 993
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static binaryValue([BLjava/lang/String;)[B
  .registers 4
  .line 79
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->findElement([BLjava/lang/String;)Lcom/project7/localmanager/BsonLite$Element;
    move-result-object p0
  .line 80
    const/4 p1, 0
    if-eqz p0, :L3
    iget v0, p0, Lcom/project7/localmanager/BsonLite$Element;->type:I
    const/4 v1, 5
    if-ne v0, v1, :L3
    iget-object v0, p0, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    array-length v0, v0
    if-ge v0, v1, :L0
    goto :L3
  :L0
  .line 81
    iget-object p0, p0, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    invoke-static { p0 }, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;
    move-result-object p0
    sget-object v0, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { p0, v0 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object p0
  .line 82
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result v0
  .line 83
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->get()B
    move-result v1
    and-int/lit16 v1, v1, 255
  .line 84
    if-nez v1, :L2
    if-ltz v0, :L2
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->remaining()I
    move-result v1
    if-eq v0, v1, :L1
    goto :L2
  :L1
  .line 85
    new-array p1, v0, [B
    invoke-virtual { p0, p1 }, Ljava/nio/ByteBuffer;->get([B)Ljava/nio/ByteBuffer;
    return-object p1
  :L2
  .line 84
    return-object p1
  :L3
  .line 80
    return-object p1
.end method

.method private static boolBytes(Z)[B
  .registers 3
  .line 1514
    const/4 v0, 1
    new-array v0, v0, [B
    int-to-byte p0, p0
    const/4 v1, 0
    aput-byte p0, v0, v1
    return-object v0
.end method

.method static boolValue([BLjava/lang/String;)Ljava/lang/Boolean;
  .registers 3
  .line 51
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->findElement([BLjava/lang/String;)Lcom/project7/localmanager/BsonLite$Element;
    move-result-object p0
  .line 52
    if-eqz p0, :L3
    iget p1, p0, Lcom/project7/localmanager/BsonLite$Element;->type:I
    const/16 v0, 8
    if-ne p1, v0, :L3
    iget-object p1, p0, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    array-length p1, p1
    const/4 v0, 1
    if-eq p1, v0, :L0
    goto :L3
  :L0
  .line 55
    iget-object p0, p0, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    const/4 p1, 0
    aget-byte p0, p0, p1
    if-eqz p0, :L1
    goto :L2
  :L1
    move v0, p1
  :L2
    invoke-static { v0 }, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
    move-result-object p0
    return-object p0
  :L3
  .line 53
    const/4 p0, 0
    return-object p0
.end method

.method static callbackDocument(I)[B
  .registers 5
  .line 1239
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 1240
    const/4 v1, 3
    invoke-virtual { v0, v1 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1241
    const-string v1, "_r_"
    invoke-static { v0, v1 }, Lcom/project7/localmanager/BsonLite;->writeCString(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 1242
    sget-object v1, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    array-length v2, v1
    const/4 v3, 0
    invoke-virtual { v0, v1, v3, v2 }, Ljava/io/ByteArrayOutputStream;->write([BII)V
  .line 1243
    const/16 v1, 16
    invoke-virtual { v0, v1 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1244
    const-string v1, "_cbid_"
    invoke-static { v0, v1 }, Lcom/project7/localmanager/BsonLite;->writeCString(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 1245
    invoke-static { v0, p0 }, Lcom/project7/localmanager/BsonLite;->writeLeInt(Ljava/io/ByteArrayOutputStream;I)V
  .line 1246
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static cityAreaStatus(Lcom/project7/localmanager/LocalTutorialStore$Progress;I)I
  .registers 2
  .line 476
    invoke-static { p0, p1 }, Lcom/project7/localmanager/LocalCityProgress;->status(Lcom/project7/localmanager/LocalTutorialStore$Progress;I)I
    move-result p0
    return p0
.end method

.method static cityDataReplyDocument(Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
  .registers 3
  .line 525
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 526
    invoke-static { p0 }, Lcom/project7/localmanager/BsonLite;->cityValuesDocument(Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object p0
    const-string v1, "cd"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 527
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static cityDataReplyDocument(Lcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
  .registers 5
  .line 550
    const/4 v0, 2
    new-array v0, v0, [Ljava/lang/Object;
    const/4 v1, 0
    const-string v2, "cd"
    aput-object v2, v0, v1
    invoke-static { p1, p0 }, Lcom/project7/localmanager/BsonLite;->persistedCityValues([BLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object p0
    const/4 p1, 1
    aput-object p0, v0, p1
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object p0
    return-object p0
.end method

.method private static cityValuesDocument(Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
  .registers 4
  .line 512
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 513
    if-eqz p0, :L0
    iget v1, p0, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolActions:I
    if-ltz v1, :L0
  .line 514
    iget v1, p0, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolActions:I
    goto :L1
  :L0
    const/16 v1, 24
  :L1
  .line 513
    const-string v2, "av"
    invoke-static { v0, v2, v1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 515
    const/4 v1, 1
    if-nez p0, :L2
    goto :L3
  :L2
    iget p0, p0, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolCount:I
    add-int/2addr v1, p0
  :L3
    const-string p0, "pn"
    invoke-static { v0, p0, v1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 516
    const-string p0, "bf"
    const/4 v1, 0
    invoke-static { v0, p0, v1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 517
    const-string p0, "dv"
    invoke-static { v0, p0, v1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 518
    const-string p0, "ev"
    invoke-static { v0, p0, v1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 519
    const-string p0, "fv"
    invoke-static { v0, p0, v1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 520
    const-string p0, "rv"
    invoke-static { v0, p0, v1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 521
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method private static combatDataDocument(Ljava/lang/Iterable;Ljava/lang/String;[BLcom/project7/localmanager/LocalCombatCatalog;III)[B
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Ljava/lang/Iterable<",
      "Ljava/lang/Integer;",
      ">;",
      "Ljava/lang/String;",
      "[B",
      "Lcom/project7/localmanager/LocalCombatCatalog;",
      "III)[B"
    }
  .end annotation
  .registers 30
  .line 198
    move-object/from16 v8, p2
    move-object/from16 v9, p3
    move/from16 v10, p4
    move/from16 v11, p5
    move/from16 v12, p6
    new-instance v13, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v13 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 199
    new-instance v14, Ljava/util/ArrayList;
    invoke-direct { v14 }, Ljava/util/ArrayList;-><init>()V
  .line 200
    new-instance v0, Ljava/util/LinkedHashSet;
    invoke-direct { v0 }, Ljava/util/LinkedHashSet;-><init>()V
  .line 201
    invoke-interface/range { p0 .. p0 }, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;
    move-result-object v1
  :L0
    invoke-interface { v1 }, Ljava/util/Iterator;->hasNext()Z
    move-result v2
    if-eqz v2, :L1
    invoke-interface { v1 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Ljava/lang/Integer;
    invoke-interface { v0, v2 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
    goto :L0
  :L1
  .line 204
    const/4 v15, 2
    if-ne v12, v15, :L4
    const/16 v1, 164
    if-ne v11, v1, :L4
  .line 205
    const-string v1, "heromgr"
    invoke-static { v8, v1 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v1
    const-string v2, "hrs"
    invoke-static { v1, v2 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v1
  .line 204
    invoke-static { v1 }, Lcom/project7/localmanager/LocalResourceEngine;->array([B)Ljava/util/List;
    move-result-object v1
    invoke-interface { v1 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v1
  :L2
    invoke-interface { v1 }, Ljava/util/Iterator;->hasNext()Z
    move-result v2
    if-eqz v2, :L4
    invoke-interface { v1 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v2
    check-cast v2, [B
  .line 206
    const-string v3, "0"
    invoke-static { v2, v3 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v3
    const-string v4, "1"
    invoke-static { v2, v4 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v2
    const-string v4, "cf"
    invoke-static { v2, v4 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v2
  .line 207
    if-eqz v3, :L3
    invoke-virtual { v3 }, Ljava/lang/Integer;->intValue()I
    move-result v4
    if-lez v4, :L3
    if-eqz v2, :L3
    invoke-virtual { v2 }, Ljava/lang/Integer;->intValue()I
    move-result v2
    if-lez v2, :L3
    invoke-virtual { v3 }, Ljava/lang/Integer;->intValue()I
    move-result v2
    invoke-virtual { v9, v2 }, Lcom/project7/localmanager/LocalCombatCatalog;->supportsHero(I)Z
    move-result v2
    if-eqz v2, :L3
  .line 208
    invoke-interface { v0, v3 }, Ljava/util/Set;->add(Ljava/lang/Object;)Z
  :L3
  .line 209
    goto :L2
  :L4
  .line 210
    invoke-interface { v0 }, Ljava/util/Set;->iterator()Ljava/util/Iterator;
    move-result-object v16
  :L5
    invoke-interface/range { v16 .. v16 }, Ljava/util/Iterator;->hasNext()Z
    move-result v0
    const/16 v17, 0
    if-eqz v0, :L20
    invoke-interface/range { v16 .. v16 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v0
    move-object v5, v0
    check-cast v5, Ljava/lang/Integer;
  .line 211
    if-eqz v5, :L19
    invoke-virtual { v5 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    if-nez v0, :L6
  .line 212
    goto :L5
  :L6
  .line 214
    invoke-virtual { v5 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    invoke-static { v8, v0 }, Lcom/project7/localmanager/BsonLite;->profileHeroDocument([BI)[B
    move-result-object v4
  .line 215
    invoke-virtual { v5 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    invoke-static { v0, v4 }, Lcom/project7/localmanager/BsonLite;->combatSkinDocument(I[B)[B
    move-result-object v0
    invoke-interface { v14, v0 }, Ljava/util/List;->add(Ljava/lang/Object;)Z
  .line 216
    const-string v0, "sl"
    invoke-static { v4, v0 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v0
  .line 217
    const-string v1, "so"
    invoke-static { v4, v1 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v1
  .line 218
    if-nez v0, :L7
    const/4 v2, 1
    goto :L8
  :L7
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    move v2, v0
  :L8
  .line 219
    if-nez v1, :L9
    const/4 v3, 1
    goto :L10
  :L9
    invoke-virtual { v1 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    move v3, v0
  :L10
  .line 220
    invoke-virtual { v5 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    invoke-virtual { v9, v0, v4, v10 }, Lcom/project7/localmanager/LocalCombatCatalog;->equipmentFor(I[BI)Lcom/project7/localmanager/LocalEquipmentCombat;
    move-result-object v1
  .line 221
    nop
  .line 222
    invoke-virtual { v5 }, Ljava/lang/Integer;->intValue()I
    move-result v0
  .line 223
    invoke-virtual { v5 }, Ljava/lang/Integer;->intValue()I
    move-result v6
    invoke-virtual { v9, v6, v2, v3, v4 }, Lcom/project7/localmanager/LocalCombatCatalog;->skillsFor(III[B)[[I
    move-result-object v6
  .line 224
    invoke-virtual { v5 }, Ljava/lang/Integer;->intValue()I
    move-result v7
    invoke-virtual { v9, v7, v4 }, Lcom/project7/localmanager/LocalCombatCatalog;->artifactSkillsFor(I[B)[[I
    move-result-object v7
  .line 225
    invoke-virtual { v5 }, Ljava/lang/Integer;->intValue()I
    move-result v19
    move v15, v0
    move-object/from16 v0, p3
    move-object/from16 v20, v1
    move/from16 v1, v19
    move-object/from16 v19, v4
    move-object/from16 v21, v5
    move/from16 v5, p4
    move-object v8, v6
    move-object/from16 v6, p2
    move-object/from16 v18, v13
    move-object/from16 v22, v14
    const/4 v13, 3
    move-object v14, v7
    move-object/from16 v7, v20
    invoke-virtual/range { v0 .. v7 }, Lcom/project7/localmanager/LocalCombatCatalog;->attributesFor(III[BI[BLcom/project7/localmanager/LocalEquipmentCombat;)Ljava/util/Map;
    move-result-object v0
  .line 221
    invoke-static { v15, v8, v14, v0 }, Lcom/project7/localmanager/BsonLite;->heroCombatDataDocument(I[[I[[ILjava/util/Map;)[B
    move-result-object v0
  .line 226
    move-object/from16 v1, v20
    iget-object v2, v1, Lcom/project7/localmanager/LocalEquipmentCombat;->tricks:Ljava/util/Set;
    const-string v3, "t"
    invoke-static { v0, v3, v2 }, Lcom/project7/localmanager/BsonLite;->withProfileIntArray([BLjava/lang/String;Ljava/lang/Iterable;)[B
    move-result-object v0
  .line 227
    const/4 v2, 2
    new-array v3, v2, [Ljava/io/Serializable;
    iget v2, v1, Lcom/project7/localmanager/LocalEquipmentCombat;->exclusiveStage:I
    if-lez v2, :L11
    const/4 v6, 1
    goto :L12
  :L11
    move/from16 v6, v17
  :L12
    invoke-static { v6 }, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
    move-result-object v2
    aput-object v2, v3, v17
    iget v1, v1, Lcom/project7/localmanager/LocalEquipmentCombat;->exclusiveStage:I
    invoke-static { v1 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v1
    const/4 v2, 1
    aput-object v1, v3, v2
    invoke-static { v3 }, Ljava/util/Arrays;->asList([Ljava/lang/Object;)Ljava/util/List;
    move-result-object v1
    const-string v3, "ai"
    invoke-static { v0, v3, v1 }, Lcom/project7/localmanager/BsonLite;->withProfileArray([BLjava/lang/String;Ljava/util/List;)[B
    move-result-object v0
  .line 228
    invoke-virtual/range { v21 .. v21 }, Ljava/lang/Integer;->intValue()I
    move-result v1
    move-object/from16 v3, v19
    invoke-virtual { v9, v1, v3 }, Lcom/project7/localmanager/LocalCombatCatalog;->awakeStage(I[B)I
    move-result v1
    const-string v3, "as"
    invoke-static { v0, v3, v1 }, Lcom/project7/localmanager/BsonLite;->withProfileInt([BLjava/lang/String;I)[B
    move-result-object v0
  .line 231
    invoke-static { v2, v10 }, Ljava/lang/Math;->max(II)I
    move-result v1
    const-string v3, "lv"
    invoke-static { v0, v3, v1 }, Lcom/project7/localmanager/BsonLite;->withProfileInt([BLjava/lang/String;I)[B
    move-result-object v0
  .line 232
    if-eq v12, v2, :L14
    const/4 v1, 2
    if-ne v12, v1, :L13
    goto :L14
  :L13
    const/4 v1, 0
    goto :L15
  :L14
    invoke-virtual/range { v21 .. v21 }, Ljava/lang/Integer;->intValue()I
    move-result v1
    invoke-virtual { v9, v11, v1 }, Lcom/project7/localmanager/LocalCombatCatalog;->missionHero(II)[B
    move-result-object v1
  :L15
  .line 233
    if-eqz v1, :L16
    move-object v0, v1
  :L16
  .line 235
    new-array v1, v13, [Ljava/lang/String;
    aput-object p1, v1, v17
    const-string v2, ""
    const/4 v3, 1
    aput-object v2, v1, v3
    const-string v2, "robot_id"
    const/4 v3, 2
    aput-object v2, v1, v3
    move/from16 v2, v17
  :L17
    if-ge v2, v13, :L18
    aget-object v3, v1, v2
  .line 236
    new-instance v4, Ljava/lang/StringBuilder;
    invoke-direct { v4 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v5, "('"
    invoke-virtual { v4, v5 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v4, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v3, "', "
    invoke-virtual { v4, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-object/from16 v3, v21
    invoke-virtual { v4, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    const-string v5, ")"
    invoke-virtual { v4, v5 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v4 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v4
    move-object/from16 v5, v18
    invoke-static { v5, v4, v0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 235
    add-int/lit8 v2, v2, 1
    goto :L17
  :L18
  .line 238
    move-object/from16 v5, v18
    move-object/from16 v8, p2
    move-object v13, v5
    move-object/from16 v14, v22
    const/4 v15, 2
    goto/16 :L5
  :L19
  .line 211
    move-object v5, v13
    move-object/from16 v22, v14
    move-object/from16 v8, p2
    const/4 v15, 2
    goto/16 :L5
  :L20
  .line 240
    move-object v5, v13
    move-object/from16 v22, v14
    const/4 v13, 3
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 241
    invoke-static { v5 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object v1
    const-string v2, "heroes"
    invoke-static { v0, v2, v1 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 242
    const/4 v1, 2
    new-array v2, v1, [Ljava/lang/Object;
    const-string v1, "skins"
    aput-object v1, v2, v17
    const/4 v3, 1
    aput-object v22, v2, v3
    invoke-static { v2 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v2
    invoke-static { v2, v1 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v2
    invoke-static { v0, v1, v2 }, Lcom/project7/localmanager/BsonLite;->writeArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 243
    invoke-static { v3, v10 }, Ljava/lang/Math;->max(II)I
    move-result v1
    const-string v2, "hero_lv"
    invoke-static { v0, v2, v1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 244
    const-string v1, "monster_lv"
    invoke-static { v0, v1, v3 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 245
    invoke-static/range { p2 .. p2 }, Lcom/project7/localmanager/LocalIntelligenceEffects;->monsterRate([B)D
    move-result-wide v1
  .line 246
    const-wide/16 v3, 0
    cmpl-double v3, v1, v3
    if-lez v3, :L21
    const/4 v3, 4
    new-array v3, v3, [Ljava/lang/Object;
    const-string v4, "hurt_addition_rate"
    aput-object v4, v3, v17
  .line 247
    invoke-static { v1, v2 }, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;
    move-result-object v4
    const/4 v5, 1
    aput-object v4, v3, v5
    const-string v4, "max_hp_addition_rate"
    const/4 v5, 2
    aput-object v4, v3, v5
    invoke-static { v1, v2 }, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;
    move-result-object v1
    aput-object v1, v3, v13
  .line 246
    invoke-static { v3 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object v1
    const-string v2, "monster"
    invoke-static { v0, v2, v1 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  :L21
  .line 248
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object v0
    return-object v0
.end method

.method static combatOfflineReplyDocument(IILjava/lang/String;Ljava/lang/Iterable;[BLjava/lang/String;[BLcom/project7/localmanager/LocalCombatCatalog;)[B
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(II",
      "Ljava/lang/String;",
      "Ljava/lang/Iterable<",
      "Ljava/lang/Integer;",
      ">;[B",
      "Ljava/lang/String;",
      "[B",
      "Lcom/project7/localmanager/LocalCombatCatalog;",
      ")[B"
    }
  .end annotation
  .registers 18
  .line 156
    nop
  .line 157
    const-string v0, "level"
    move-object/from16 v7, p6
    invoke-static { v7, v0 }, Lcom/project7/localmanager/LocalResourceEngine;->value([BLjava/lang/String;)I
    move-result v0
    const/4 v1, 1
    invoke-static { v1, v0 }, Ljava/lang/Math;->max(II)I
    move-result v9
  .line 156
    move v1, p0
    move v2, p1
    move-object v3, p2
    move-object v4, p3
    move-object v5, p4
    move-object v6, p5
    move-object/from16 v8, p7
    invoke-static/range { v1 .. v9 }, Lcom/project7/localmanager/BsonLite;->combatOfflineReplyDocument(IILjava/lang/String;Ljava/lang/Iterable;[BLjava/lang/String;[BLcom/project7/localmanager/LocalCombatCatalog;I)[B
    move-result-object v0
    return-object v0
.end method

.method static combatOfflineReplyDocument(IILjava/lang/String;Ljava/lang/Iterable;[BLjava/lang/String;[BLcom/project7/localmanager/LocalCombatCatalog;I)[B
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(II",
      "Ljava/lang/String;",
      "Ljava/lang/Iterable<",
      "Ljava/lang/Integer;",
      ">;[B",
      "Ljava/lang/String;",
      "[B",
      "Lcom/project7/localmanager/LocalCombatCatalog;",
      "I)[B"
    }
  .end annotation
  .registers 24
  .line 162
    move v7, p0
    move/from16 v8, p1
    move-object/from16 v9, p6
    move-object/from16 v10, p7
    new-instance v11, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v11 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 163
    const-string v0, "t"
    invoke-static { v11, v0, p0 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 164
    const-string v0, "s"
    invoke-static { v11, v0, v8 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 165
    if-nez p2, :L0
    const-string v0, "local"
    goto :L1
  :L0
    move-object/from16 v0, p2
  :L1
    const-string v1, "f"
    invoke-static { v11, v1, v0 }, Lcom/project7/localmanager/BsonLite;->writeStringElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/String;)V
  .line 166
    const-string v0, "h"
    move-object/from16 v1, p3
    invoke-static { v11, v0, v1 }, Lcom/project7/localmanager/BsonLite;->writeIntArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/Iterable;)V
  .line 167
    if-nez p4, :L2
    sget-object v0, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    goto :L3
  :L2
    move-object/from16 v0, p4
  :L3
    const-string v2, "d"
    invoke-static { v11, v2, v0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 168
    const/4 v12, 2
    const/4 v13, 1
    if-eq v7, v13, :L5
    if-ne v7, v12, :L4
    goto :L5
  :L4
    move/from16 v14, p8
    goto :L9
  :L5
  .line 169
    const-string v0, "level"
    invoke-static { v9, v0 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v0
  .line 170
    if-nez v0, :L6
    move v0, v13
    goto :L7
  :L6
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    invoke-static { v13, v0 }, Ljava/lang/Math;->max(II)I
    move-result v0
  :L7
  .line 171
    if-eqz v10, :L8
    const-string v2, "adjust_hero_lv"
    invoke-virtual { v10, v8, v2, v0 }, Lcom/project7/localmanager/LocalCombatCatalog;->missionLevel(ILjava/lang/String;I)I
    move-result v0
  :L8
    move v14, v0
  :L9
  .line 173
    move-object/from16 v0, p3
    move-object/from16 v1, p5
    move-object/from16 v2, p6
    move-object/from16 v3, p7
    move v4, v14
    move/from16 v5, p1
    move v6, p0
    invoke-static/range { v0 .. v6 }, Lcom/project7/localmanager/BsonLite;->combatDataDocument(Ljava/lang/Iterable;Ljava/lang/String;[BLcom/project7/localmanager/LocalCombatCatalog;III)[B
    move-result-object v0
  .line 174
    if-eq v7, v13, :L10
    if-ne v7, v12, :L18
  :L10
  .line 175
    const-string v1, "weeknum"
    invoke-static { v9, v1 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v2
    const-string v3, "wl"
    invoke-static { v2, v3 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v2
  .line 176
    invoke-static { v9, v1 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v1
    const-string v3, "w"
    invoke-static { v1, v3 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v1
  .line 177
    if-ne v7, v12, :L13
    if-eqz v10, :L13
  .line 178
    if-nez v1, :L11
    const/4 v1, 0
    goto :L12
  :L11
    invoke-virtual { v1 }, Ljava/lang/Integer;->intValue()I
    move-result v1
  :L12
    invoke-virtual { v10, v8, v1 }, Lcom/project7/localmanager/LocalCombatCatalog;->storyMonsterLevel(II)I
    move-result v13
    goto :L15
  :L13
  .line 179
    if-nez v2, :L14
    goto :L15
  :L14
    invoke-virtual { v2 }, Ljava/lang/Integer;->intValue()I
    move-result v1
    invoke-static { v13, v1 }, Ljava/lang/Math;->max(II)I
    move-result v13
  :L15
  .line 180
    if-eqz v10, :L16
    const-string v1, "adjust_monster_lv"
    invoke-virtual { v10, v8, v1, v13 }, Lcom/project7/localmanager/LocalCombatCatalog;->missionLevel(ILjava/lang/String;I)I
    move-result v13
  :L16
  .line 181
    const-string v1, "monster_lv"
    invoke-static { v0, v1, v13 }, Lcom/project7/localmanager/BsonLite;->withProfileInt([BLjava/lang/String;I)[B
    move-result-object v0
  .line 182
    const-string v1, "hero_lv"
    invoke-static { v0, v1, v14 }, Lcom/project7/localmanager/BsonLite;->withProfileInt([BLjava/lang/String;I)[B
    move-result-object v0
  .line 183
    if-ne v7, v12, :L18
    if-eqz v10, :L18
  .line 184
    invoke-virtual { v10, v8, v9 }, Lcom/project7/localmanager/LocalCombatCatalog;->wingEnhancement(I[B)[B
    move-result-object v1
  .line 185
    const-string v2, "battle_enhance"
    invoke-static { v1, v2 }, Lcom/project7/localmanager/BsonLite;->numericValue([BLjava/lang/String;)Ljava/lang/Number;
    move-result-object v3
  .line 186
    const-string v4, "reduce_fatigue"
    invoke-static { v1, v4 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v1
  .line 187
    if-eqz v3, :L17
    invoke-virtual { v3 }, Ljava/lang/Number;->doubleValue()D
    move-result-wide v5
    invoke-static { v0, v2, v5, v6 }, Lcom/project7/localmanager/BsonLite;->withProfileDouble([BLjava/lang/String;D)[B
    move-result-object v0
  :L17
  .line 188
    if-eqz v1, :L18
    invoke-virtual { v1 }, Ljava/lang/Integer;->intValue()I
    move-result v1
    invoke-static { v0, v4, v1 }, Lcom/project7/localmanager/BsonLite;->withProfileInt([BLjava/lang/String;I)[B
    move-result-object v0
  :L18
  .line 191
    const-string v1, "c"
    invoke-static { v11, v1, v0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 192
    invoke-static { v11 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object v0
    return-object v0
.end method

.method static combatOfflineRewardDocument(IILjava/lang/Iterable;Ljava/lang/Iterable;I)[B
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(II",
      "Ljava/lang/Iterable<",
      "Ljava/lang/Integer;",
      ">;",
      "Ljava/lang/Iterable<",
      "Ljava/lang/Integer;",
      ">;I)[B"
    }
  .end annotation
  .registers 11
  .line 343
    sget-object v5, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    move v0, p0
    move v1, p1
    move-object v2, p2
    move-object v3, p3
    move v4, p4
    invoke-static/range { v0 .. v5 }, Lcom/project7/localmanager/BsonLite;->combatOfflineRewardDocument(IILjava/lang/Iterable;Ljava/lang/Iterable;I[B)[B
    move-result-object p0
    return-object p0
.end method

.method static combatOfflineRewardDocument(IILjava/lang/Iterable;Ljava/lang/Iterable;I[B)[B
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(II",
      "Ljava/lang/Iterable<",
      "Ljava/lang/Integer;",
      ">;",
      "Ljava/lang/Iterable<",
      "Ljava/lang/Integer;",
      ">;I[B)[B"
    }
  .end annotation
  .registers 8
  .line 348
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 349
    const-string v1, "t"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 350
    const-string p0, "s"
    invoke-static { v0, p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 351
    const-string p0, "h"
    invoke-static { v0, p0, p2 }, Lcom/project7/localmanager/BsonLite;->writeIntArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/Iterable;)V
  .line 352
    const-string p0, "x"
    invoke-static { v0, p0, p3 }, Lcom/project7/localmanager/BsonLite;->writeIntArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/Iterable;)V
  .line 353
    const-string p0, "r"
    invoke-static { v0, p0, p5 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 354
    const-string p0, "w"
    invoke-static { v0, p0, p4 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 355
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method private static combatSkinDocument(I[B)[B
  .registers 8
  .line 252
    const-string v0, "cs"
    invoke-static { p1, v0 }, Lcom/project7/localmanager/BsonLite;->uuidValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v0
  .line 253
    if-nez v0, :L0
    const/4 p1, 0
    goto :L1
  :L0
    const-string v1, "sk"
    invoke-static { p1, v1 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object p1
    invoke-static { p1, v0 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object p1
  :L1
  .line 254
    const-string v1, "i"
    invoke-static { p1, v1 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v2
  .line 255
    const-string v3, "u"
    if-eqz v2, :L2
    invoke-virtual { v2 }, Ljava/lang/Integer;->intValue()I
    move-result v2
    if-lez v2, :L2
    sget-object v2, Ljava/lang/Boolean;->TRUE:Ljava/lang/Boolean;
    const-string v4, "fb"
    invoke-static { p1, v4 }, Lcom/project7/localmanager/BsonLite;->boolValue([BLjava/lang/String;)Ljava/lang/Boolean;
    move-result-object v4
    invoke-virtual { v2, v4 }, Ljava/lang/Boolean;->equals(Ljava/lang/Object;)Z
    move-result v2
    if-nez v2, :L2
  .line 258
    invoke-static { p1, v3, v0 }, Lcom/project7/localmanager/BsonLite;->withProfileString([BLjava/lang/String;Ljava/lang/String;)[B
    move-result-object p0
    return-object p0
  :L2
  .line 260
    const/16 p1, 10
    new-array p1, p1, [Ljava/lang/Object;
    const/4 v0, 0
    aput-object v1, p1, v0
    invoke-static { p0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v1
    const/4 v2, 1
    aput-object v1, p1, v2
    const/4 v1, 2
    aput-object v3, p1, v1
    const/4 v3, 3
    sget-object v4, Ljava/util/Locale;->ROOT:Ljava/util/Locale;
    new-array v1, v1, [Ljava/lang/Object;
    invoke-static { p0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v5
    aput-object v5, v1, v0
    invoke-static { p0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object p0
    aput-object p0, v1, v2
    const-string p0, "%08x%016x"
    invoke-static { v4, p0, v1 }, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;
    move-result-object p0
    aput-object p0, p1, v3
    const/4 p0, 4
    const-string v1, "cd"
    aput-object v1, p1, p0
    const/4 p0, 5
    sget-object v1, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    aput-object v1, p1, p0
    const/4 p0, 6
    const-string v2, "pd"
    aput-object v2, p1, p0
    const/4 p0, 7
    aput-object v1, p1, p0
    const/16 p0, 8
    const-string v1, "dn"
    aput-object v1, p1, p0
    const/16 p0, 9
  .line 261
    invoke-static { v0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v0
    aput-object v0, p1, p0
  .line 260
    invoke-static { p1 }, Lcom/project7/localmanager/BsonLite;->document([Ljava/lang/Object;)[B
    move-result-object p0
    return-object p0
.end method

.method static combatWinValue([B)I
  .registers 3
  .line 70
    const-string v0, "w"
    invoke-static { p0, v0 }, Lcom/project7/localmanager/BsonLite;->boolValue([BLjava/lang/String;)Ljava/lang/Boolean;
    move-result-object v1
  .line 71
    if-eqz v1, :L0
  .line 72
    invoke-virtual { v1 }, Ljava/lang/Boolean;->booleanValue()Z
    move-result p0
    return p0
  :L0
  .line 74
    invoke-static { p0, v0 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object p0
  .line 75
    if-eqz p0, :L1
    invoke-virtual { p0 }, Ljava/lang/Integer;->intValue()I
    move-result p0
    if-eqz p0, :L1
    const/4 p0, 1
    goto :L2
  :L1
    const/4 p0, 0
  :L2
    return p0
.end method

.method static debugDocument([B)Ljava/lang/String;
  .registers 2
  .line 1250
    const/4 v0, 0
    invoke-static { p0, v0 }, Lcom/project7/localmanager/BsonLite;->debugDocument([BI)Ljava/lang/String;
    move-result-object p0
    return-object p0
.end method

.method private static debugDocument([BI)Ljava/lang/String;
  .registers 10
  .line 1254
    const-string v0, "<invalid>"
    if-eqz p0, :L8
    array-length v1, p0
    const/4 v2, 5
    if-lt v1, v2, :L8
    const/4 v1, 3
    if-le p1, v1, :L0
    goto/16 :L8
  :L0
  .line 1257
    invoke-static { p0 }, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;
    move-result-object v1
    sget-object v3, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { v1, v3 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object v1
  .line 1258
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result v3
  .line 1259
    if-lt v3, v2, :L7
    array-length p0, p0
    if-le v3, p0, :L1
    goto/16 :L7
  :L1
  .line 1262
    new-instance p0, Ljava/lang/StringBuilder;
    const-string v0, "{"
    invoke-direct { p0, v0 }, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
  .line 1263
    const/4 v0, 1
  :L2
  .line 1264
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result v2
    add-int/lit8 v4, v3, -1
    if-ge v2, v4, :L6
  .line 1265
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->get()B
    move-result v2
    and-int/lit16 v2, v2, 255
  .line 1266
    invoke-static { v1, v3 }, Lcom/project7/localmanager/BsonLite;->readCString(Ljava/nio/ByteBuffer;I)Ljava/lang/String;
    move-result-object v4
  .line 1267
    if-nez v4, :L3
  .line 1268
    const-string p1, "<truncated>}"
    invoke-virtual { p0, p1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p0
    return-object p0
  :L3
  .line 1270
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result v5
  .line 1271
    invoke-static { v1, v2, v3 }, Lcom/project7/localmanager/BsonLite;->skipValue(Ljava/nio/ByteBuffer;II)Z
    move-result v6
    if-nez v6, :L4
  .line 1272
    const-string p1, "<unsupported:"
    invoke-virtual { p0, p1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p0, v2 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string p1, ">}"
    invoke-virtual { p0, p1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p0
    return-object p0
  :L4
  .line 1274
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result v6
    sub-int/2addr v6, v5
    new-array v6, v6, [B
  .line 1275
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result v7
  .line 1276
    invoke-virtual { v1, v5 }, Ljava/nio/ByteBuffer;->position(I)Ljava/nio/Buffer;
    move-result-object v5
    check-cast v5, Ljava/nio/ByteBuffer;
  .line 1277
    invoke-virtual { v1, v6 }, Ljava/nio/ByteBuffer;->get([B)Ljava/nio/ByteBuffer;
  .line 1278
    invoke-virtual { v1, v7 }, Ljava/nio/ByteBuffer;->position(I)Ljava/nio/Buffer;
    move-result-object v5
    check-cast v5, Ljava/nio/ByteBuffer;
  .line 1279
    if-nez v0, :L5
  .line 1280
    const/16 v0, 44
    invoke-virtual { p0, v0 }, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;
  :L5
  .line 1282
    const/4 v0, 0
  .line 1283
    invoke-virtual { p0, v4 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const/16 v4, 61
    invoke-virtual { p0, v4 }, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;
    invoke-static { v2, v6, p1 }, Lcom/project7/localmanager/BsonLite;->debugValue(I[BI)Ljava/lang/String;
    move-result-object v2
    invoke-virtual { p0, v2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  .line 1284
    goto :L2
  :L6
  .line 1285
    const/16 p1, 125
    invoke-virtual { p0, p1 }, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;
    invoke-virtual { p0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p0
    return-object p0
  :L7
  .line 1260
    return-object v0
  :L8
  .line 1255
    return-object v0
.end method

.method private static debugValue(I[BI)Ljava/lang/String;
  .registers 6
  .line 1289
    invoke-static { p1 }, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;
    move-result-object v0
    sget-object v1, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { v0, v1 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object v0
  .line 1290
    const/4 v1, 0
    const/4 v2, 1
    packed-switch p0, :L13
  :L0
  .line 1315
    sget-object p2, Ljava/util/Locale;->US:Ljava/util/Locale;
    const/4 v0, 2
    new-array v0, v0, [Ljava/lang/Object;
    invoke-static { p0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object p0
    aput-object p0, v0, v1
    array-length p0, p1
    invoke-static { p0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object p0
    aput-object p0, v0, v2
    const-string p0, "<type:%02x bytes:%d>"
    invoke-static { p2, p0, v0 }, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;
    move-result-object p0
    return-object p0
  :L1
  .line 1309
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->getLong()J
    move-result-wide p0
    invoke-static { p0, p1 }, Ljava/lang/Long;->toString(J)Ljava/lang/String;
    move-result-object p0
    return-object p0
  :L2
  .line 1307
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result p0
    invoke-static { p0 }, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object p0
    return-object p0
  :L3
  .line 1305
    const-string p0, "null"
    return-object p0
  :L4
  .line 1303
    aget-byte p0, p1, v1
    if-nez p0, :L5
    const-string p0, "false"
    goto :L6
  :L5
    const-string p0, "true"
  :L6
    return-object p0
  :L7
  .line 1311
    new-instance p0, Ljava/lang/StringBuilder;
    invoke-direct { p0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string p2, "ObjectId("
    invoke-virtual { p0, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const/16 p2, 12
    invoke-static { p1, p2 }, Lcom/project7/localmanager/BsonLite;->hex([BI)Ljava/lang/String;
    move-result-object p1
    invoke-virtual { p0, p1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string p1, ")"
    invoke-virtual { p0, p1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p0
    return-object p0
  :L8
  .line 1313
    new-instance p0, Ljava/lang/StringBuilder;
    invoke-direct { p0 }, Ljava/lang/StringBuilder;-><init>()V
    const-string p1, "<binary:"
    invoke-virtual { p0, p1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result p1
    invoke-virtual { p0, p1 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    const-string p1, ">"
    invoke-virtual { p0, p1 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p0
    return-object p0
  :L9
  .line 1301
    add-int/2addr p2, v2
    invoke-static { p1, p2 }, Lcom/project7/localmanager/BsonLite;->debugDocument([BI)Ljava/lang/String;
    move-result-object p0
    return-object p0
  :L10
  .line 1292
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result p0
  .line 1293
    if-lt p0, v2, :L12
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->remaining()I
    move-result p1
    if-le p0, p1, :L11
    goto :L12
  :L11
  .line 1296
    sub-int/2addr p0, v2
    new-array p0, p0, [B
  .line 1297
    invoke-virtual { v0, p0 }, Ljava/nio/ByteBuffer;->get([B)Ljava/nio/ByteBuffer;
  .line 1298
    new-instance p1, Ljava/lang/StringBuilder;
    invoke-direct { p1 }, Ljava/lang/StringBuilder;-><init>()V
    const/16 p2, 34
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;
    new-instance v0, Ljava/lang/String;
    sget-object v1, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;
    invoke-direct { v0, p0, v1 }, Ljava/lang/String;-><init>([BLjava/nio/charset/Charset;)V
    invoke-virtual { p1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;
    invoke-virtual { p1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p0
    return-object p0
  :L12
  .line 1294
    const-string p0, "<invalid-string>"
    return-object p0
  :L13
  .packed-switch 2
    :L10
    :L9
    :L9
    :L8
    :L0
    :L7
    :L4
    :L0
    :L3
    :L0
    :L0
    :L0
    :L0
    :L0
    :L2
    :L0
    :L1
  .end packed-switch
.end method

.method static varargs document([Ljava/lang/Object;)[B
  .registers 5
  .line 925
    array-length v0, p0
    rem-int/lit8 v0, v0, 2
    if-nez v0, :L2
  .line 926
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 927
    const/4 v1, 0
  :L0
    array-length v2, p0
    if-ge v1, v2, :L1
  .line 928
    aget-object v2, p0, v1
    check-cast v2, Ljava/lang/String;
    add-int/lit8 v3, v1, 1
    aget-object v3, p0, v3
    invoke-static { v0, v2, v3 }, Lcom/project7/localmanager/BsonLite;->writeValue(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/Object;)V
  .line 927
    add-int/lit8 v1, v1, 2
    goto :L0
  :L1
  .line 930
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
  :L2
  .line 925
    new-instance p0, Ljava/lang/IllegalArgumentException;
    const-string v0, "BSON key/value pairs required"
    invoke-direct { p0, v0 }, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V
    throw p0
.end method

.method static documentEntries([B)Ljava/util/Map;
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "([B)",
      "Ljava/util/Map<",
      "Ljava/lang/String;",
      "[B>;"
    }
  .end annotation
  .registers 8
  .line 891
    new-instance v0, Ljava/util/LinkedHashMap;
    invoke-direct { v0 }, Ljava/util/LinkedHashMap;-><init>()V
  .line 892
    if-eqz p0, :L7
    array-length v1, p0
    const/4 v2, 5
    if-ge v1, v2, :L0
    goto :L7
  :L0
  .line 893
    invoke-static { p0 }, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;
    move-result-object v1
    sget-object v3, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { v1, v3 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object v1
  .line 894
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result v3
  .line 895
    if-lt v3, v2, :L6
    array-length v2, p0
    if-le v3, v2, :L1
    goto :L6
  :L1
  .line 897
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result v2
    add-int/lit8 v4, v3, -1
    if-ge v2, v4, :L5
  .line 898
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->get()B
    move-result v2
    and-int/lit16 v2, v2, 255
  .line 899
    invoke-static { v1, v3 }, Lcom/project7/localmanager/BsonLite;->readCString(Ljava/nio/ByteBuffer;I)Ljava/lang/String;
    move-result-object v4
  .line 900
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result v5
  .line 901
    if-eqz v4, :L5
    invoke-static { v1, v2, v3 }, Lcom/project7/localmanager/BsonLite;->skipValue(Ljava/nio/ByteBuffer;II)Z
    move-result v6
    if-nez v6, :L2
    goto :L5
  :L2
  .line 902
    const/4 v6, 3
    if-eq v2, v6, :L3
    const/4 v6, 4
    if-ne v2, v6, :L4
  :L3
  .line 903
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result v2
    invoke-static { p0, v5, v2 }, Ljava/util/Arrays;->copyOfRange([BII)[B
    move-result-object v2
    invoke-interface { v0, v4, v2 }, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
  :L4
  .line 904
    goto :L1
  :L5
  .line 905
    return-object v0
  :L6
  .line 895
    return-object v0
  :L7
  .line 892
    return-object v0
.end method

.method static documentValue([BLjava/lang/String;)[B
  .registers 3
  .line 89
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->findElement([BLjava/lang/String;)Lcom/project7/localmanager/BsonLite$Element;
    move-result-object p0
  .line 90
    if-eqz p0, :L1
    iget p1, p0, Lcom/project7/localmanager/BsonLite$Element;->type:I
    const/4 v0, 3
    if-eq p1, v0, :L0
    iget p1, p0, Lcom/project7/localmanager/BsonLite$Element;->type:I
    const/4 v0, 4
    if-eq p1, v0, :L0
    goto :L1
  :L0
  .line 93
    iget-object p0, p0, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    return-object p0
  :L1
  .line 91
    const/4 p0, 0
    return-object p0
.end method

.method static emptyEventListsDocument()[B
  .registers 1
  .line 700
    const/4 v0, 0
    invoke-static { v0, v0 }, Lcom/project7/localmanager/BsonLite;->eventListsDocument(II)[B
    move-result-object v0
    return-object v0
.end method

.method static eventDocument(I)[B
  .registers 2
  .line 749
    const-string v0, "e"
    invoke-static { v0, p0 }, Lcom/project7/localmanager/BsonLite;->intDocument(Ljava/lang/String;I)[B
    move-result-object p0
    return-object p0
.end method

.method static eventListsDocument(II)[B
  .registers 2
  .line 704
    if-nez p0, :L0
  .line 705
    invoke-static { }, Ljava/util/Collections;->emptyList()Ljava/util/List;
    move-result-object p0
    goto :L1
  :L0
    invoke-static { p0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object p0
    invoke-static { p0 }, Ljava/util/Collections;->singletonList(Ljava/lang/Object;)Ljava/util/List;
    move-result-object p0
  :L1
  .line 706
    if-nez p1, :L2
  .line 707
    invoke-static { }, Ljava/util/Collections;->emptyList()Ljava/util/List;
    move-result-object p1
    goto :L3
  :L2
    invoke-static { p1 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object p1
    invoke-static { p1 }, Ljava/util/Collections;->singletonList(Ljava/lang/Object;)Ljava/util/List;
    move-result-object p1
  :L3
  .line 708
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->eventListsDocument(Ljava/lang/Iterable;Ljava/lang/Iterable;)[B
    move-result-object p0
    return-object p0
.end method

.method static eventListsDocument(Ljava/lang/Iterable;Ljava/lang/Iterable;)[B
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Ljava/lang/Iterable<",
      "Ljava/lang/Integer;",
      ">;",
      "Ljava/lang/Iterable<",
      "Ljava/lang/Integer;",
      ">;)[B"
    }
  .end annotation
  .registers 4
  .line 715
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 716
    const-string v1, "a"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeEventAvailabilityArray(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/Iterable;)V
  .line 717
    const-string p0, "p"
    invoke-static { v0, p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeIntArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/Iterable;)V
  .line 718
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static eventReplyDocument(II)[B
  .registers 4
  .line 722
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 723
    const-string v1, "e"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 724
    const-string p0, "r"
    invoke-static { v0, p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 725
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static eventRewardDocument(I)[B
  .registers 4
  .line 729
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 730
    const-string v1, "e"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 731
    new-instance v1, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v1 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 732
    const/16 v2, 1001
    if-ne p0, v2, :L0
  .line 733
    const/16 p0, 24
    invoke-static { p0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object p0
    invoke-static { p0 }, Ljava/util/Collections;->singletonList(Ljava/lang/Object;)Ljava/util/List;
    move-result-object p0
    const-string v2, "hero"
    invoke-static { v1, v2, p0 }, Lcom/project7/localmanager/BsonLite;->writeIntArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/Iterable;)V
  :L0
  .line 737
    invoke-static { v1 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    const-string v1, "r"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 738
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method private static findElement([BLjava/lang/String;)Lcom/project7/localmanager/BsonLite$Element;
  .registers 11
    if-eqz p1, :legacy
    const/4 v0, 0
  :keycheck
    invoke-virtual { p1 }, Ljava/lang/String;->length()I
    move-result v1
    if-ge v0, v1, :fast
    invoke-virtual { p1, v0 }, Ljava/lang/String;->charAt(I)C
    move-result v1
    const/16 v2, 127
    if-gt v1, v2, :legacy
    add-int/lit8 v0, v0, 1
    goto :keycheck
  :fast
    const/4 v0, 0
    if-eqz p0, :null
    array-length v1, p0
    const/4 v2, 5
    if-lt v1, v2, :null
    invoke-static { p0 }, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;
    move-result-object v1
    sget-object v2, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { v1, v2 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object v1
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result v2
    const/4 v3, 5
    if-lt v2, v3, :null
    array-length v3, p0
    if-gt v2, v3, :null
    sget-object v3, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;
    invoke-virtual { p1, v3 }, Ljava/lang/String;->getBytes(Ljava/nio/charset/Charset;)[B
    move-result-object v3
    add-int/lit8 v4, v2, -1
  :loop
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result v8
    if-ge v8, v4, :null
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->get()B
    move-result v5
    and-int/lit16 v5, v5, 255
    const/4 v6, 0
    const/4 v7, 1
  :cstring
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result v8
    if-ge v8, v2, :null
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->get()B
    move-result v8
    and-int/lit16 v8, v8, 255
    if-eqz v8, :keydone
    if-nez v7, :compare
    goto :cnext
  :compare
    move v0, v8
    array-length v8, v3
    if-lt v6, v8, :comparebyte
    const/4 v7, 0
    goto :cnext
  :comparebyte
    aget-byte v8, v3, v6
    and-int/lit16 v8, v8, 255
    if-eq v8, v0, :cnext
    const/4 v7, 0
  :cnext
    add-int/lit8 v6, v6, 1
    goto :cstring
  :keydone
    if-eqz v7, :nonmatch
    array-length v8, v3
    if-ne v6, v8, :nonmatch
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result v6
    invoke-static { v1, v5, v2 }, Lcom/project7/localmanager/BsonLite;->skipValue(Ljava/nio/ByteBuffer;II)Z
    move-result v7
    if-eqz v7, :null
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result v8
    sub-int v7, v8, v6
    new-array v0, v7, [B
    invoke-virtual { v1, v6 }, Ljava/nio/ByteBuffer;->position(I)Ljava/nio/Buffer;
    invoke-virtual { v1, v0 }, Ljava/nio/ByteBuffer;->get([B)Ljava/nio/ByteBuffer;
    invoke-virtual { v1, v8 }, Ljava/nio/ByteBuffer;->position(I)Ljava/nio/Buffer;
    new-instance v8, Lcom/project7/localmanager/BsonLite$Element;
    invoke-direct { v8, v5, v0 }, Lcom/project7/localmanager/BsonLite$Element;-><init>(I[B)V
    return-object v8
  :nonmatch
    invoke-static { v1, v5, v2 }, Lcom/project7/localmanager/BsonLite;->skipValue(Ljava/nio/ByteBuffer;II)Z
    move-result v7
    if-eqz v7, :null
    goto :loop
  :legacy
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->findElementString([BLjava/lang/String;)Lcom/project7/localmanager/BsonLite$Element;
    move-result-object v0
    return-object v0
  :null
    const/4 v0, 0
    return-object v0
.end method

.method private static findElementString([BLjava/lang/String;)Lcom/project7/localmanager/BsonLite$Element;
  .registers 8
  .line 1344
    const/4 v0, 0
    if-eqz p0, :L7
    array-length v1, p0
    const/4 v2, 5
    if-ge v1, v2, :L0
    goto :L7
  :L0
  .line 1347
    invoke-static { p0 }, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;
    move-result-object v1
    sget-object v3, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { v1, v3 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object v1
  .line 1348
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result v3
  .line 1349
    if-lt v3, v2, :L6
    array-length p0, p0
    if-le v3, p0, :L1
    goto :L6
  :L1
  .line 1352
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result p0
    add-int/lit8 v2, v3, -1
    if-ge p0, v2, :L5
  .line 1353
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->get()B
    move-result p0
    and-int/lit16 p0, p0, 255
  .line 1354
    invoke-static { v1, v3 }, Lcom/project7/localmanager/BsonLite;->readCString(Ljava/nio/ByteBuffer;I)Ljava/lang/String;
    move-result-object v2
  .line 1355
    if-nez v2, :L2
  .line 1356
    return-object v0
  :L2
  .line 1358
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result v4
  .line 1359
    invoke-static { v1, p0, v3 }, Lcom/project7/localmanager/BsonLite;->skipValue(Ljava/nio/ByteBuffer;II)Z
    move-result v5
    if-nez v5, :L3
  .line 1360
    return-object v0
  :L3
  .line 1362
    invoke-virtual { p1, v2 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v2
    if-eqz v2, :L4
  .line 1363
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result p1
    sub-int/2addr p1, v4
    new-array p1, p1, [B
  .line 1364
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result v0
  .line 1365
    invoke-virtual { v1, v4 }, Ljava/nio/ByteBuffer;->position(I)Ljava/nio/Buffer;
    move-result-object v2
    check-cast v2, Ljava/nio/ByteBuffer;
  .line 1366
    invoke-virtual { v1, p1 }, Ljava/nio/ByteBuffer;->get([B)Ljava/nio/ByteBuffer;
  .line 1367
    invoke-virtual { v1, v0 }, Ljava/nio/ByteBuffer;->position(I)Ljava/nio/Buffer;
    move-result-object v0
    check-cast v0, Ljava/nio/ByteBuffer;
  .line 1368
    new-instance v0, Lcom/project7/localmanager/BsonLite$Element;
    invoke-direct { v0, p0, p1 }, Lcom/project7/localmanager/BsonLite$Element;-><init>(I[B)V
    return-object v0
  :L4
  .line 1370
    goto :L1
  :L5
  .line 1371
    return-object v0
  :L6
  .line 1350
    return-object v0
  :L7
  .line 1345
    return-object v0
.end method

# Project7 local optimization: build the finished BSON document in one exact-size array
# (int32 LE length + body + 0x00 terminator) instead of a second ByteArrayOutputStream
# that copies the body twice. Emitted bytes are identical to the legacy implementation.
.method private static finishDocument(Ljava/io/ByteArrayOutputStream;)[B
  .registers 5
    invoke-virtual { p0 }, Ljava/io/ByteArrayOutputStream;->toByteArray()[B
    move-result-object v0
    array-length v1, v0
    add-int/lit8 v2, v1, 5
    new-array v3, v2, [B
    const/4 v1, 0
    int-to-byte v4, v2
    aput-byte v4, v3, v1
    const/4 v1, 1
    ushr-int/lit8 v4, v2, 8
    int-to-byte v4, v4
    aput-byte v4, v3, v1
    const/4 v1, 2
    ushr-int/lit8 v4, v2, 16
    int-to-byte v4, v4
    aput-byte v4, v3, v1
    const/4 v1, 3
    ushr-int/lit8 v4, v2, 24
    int-to-byte v4, v4
    aput-byte v4, v3, v1
    const/4 v1, 0
    const/4 v4, 4
    array-length v2, v0
    invoke-static { v0, v1, v3, v4, v2 }, Ljava/lang/System;->arraycopy(Ljava/lang/Object;ILjava/lang/Object;II)V
    return-object v3
.end method

.method static friendlyRewardDocument(Ljava/util/Map;)[B
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Ljava/util/Map<",
      "Ljava/lang/Integer;",
      "Ljava/lang/Integer;",
      ">;)[B"
    }
  .end annotation
  .registers 4
  .line 561
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 562
    invoke-interface { p0 }, Ljava/util/Map;->entrySet()Ljava/util/Set;
    move-result-object p0
    invoke-interface { p0 }, Ljava/util/Set;->iterator()Ljava/util/Iterator;
    move-result-object p0
  :L0
    invoke-interface { p0 }, Ljava/util/Iterator;->hasNext()Z
    move-result v1
    if-eqz v1, :L1
    invoke-interface { p0 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Ljava/util/Map$Entry;
  .line 563
    invoke-interface { v1 }, Ljava/util/Map$Entry;->getKey()Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Ljava/lang/Integer;
    invoke-virtual { v2 }, Ljava/lang/Integer;->toString()Ljava/lang/String;
    move-result-object v2
    invoke-interface { v1 }, Ljava/util/Map$Entry;->getValue()Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Ljava/lang/Integer;
    invoke-virtual { v1 }, Ljava/lang/Integer;->intValue()I
    move-result v1
    invoke-static { v0, v2, v1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 564
    goto :L0
  :L1
  .line 565
    new-instance p0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { p0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 566
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object v0
    const-string v1, "fr"
    invoke-static { p0, v1, v0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 567
    sget-object v0, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    const-string v1, "n"
    invoke-static { p0, v1, v0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 568
    invoke-static { p0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static gamePlaySwitchReplyDocument(Ljava/lang/String;ILjava/lang/String;)[B
  .registers 6
  .line 692
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 693
    const-string v1, ""
    if-nez p0, :L0
    move-object p0, v1
  :L0
    const-string v2, "g"
    invoke-static { v0, v2, p0 }, Lcom/project7/localmanager/BsonLite;->writeStringElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/String;)V
  .line 694
    const-string p0, "s"
    invoke-static { v0, p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 695
    if-nez p2, :L1
    move-object p2, v1
  :L1
    const-string p0, "m"
    invoke-static { v0, p0, p2 }, Lcom/project7/localmanager/BsonLite;->writeStringElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/String;)V
  .line 696
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method private static hasBattle(Lcom/project7/localmanager/LocalTutorialStore$Progress;I)Z
  .registers 3
  .line 623
    if-nez p0, :L0
    const/4 p0, 0
    goto :L1
  :L0
    iget-object p0, p0, Lcom/project7/localmanager/LocalTutorialStore$Progress;->eventConditions:Ljava/util/Map;
    const-string v0, "battle"
    invoke-interface { p0, v0 }, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object p0
    check-cast p0, Ljava/util/Set;
  :L1
  .line 624
    if-eqz p0, :L2
    invoke-static { p1 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object p1
    invoke-interface { p0, p1 }, Ljava/util/Set;->contains(Ljava/lang/Object;)Z
    move-result p0
    if-eqz p0, :L2
    const/4 p0, 1
    goto :L3
  :L2
    const/4 p0, 0
  :L3
    return p0
.end method

.method private static heroCombatDataDocument(I[[I[[ILjava/util/Map;)[B
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(I[[I[[I",
      "Ljava/util/Map<",
      "Ljava/lang/String;",
      "Ljava/lang/Double;",
      ">;)[B"
    }
  .end annotation
  .registers 10
  .line 293
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 294
    const-string v1, "0"
    invoke-static { v0, v1, p1 }, Lcom/project7/localmanager/BsonLite;->writeSkillPairsElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[[I)V
  .line 295
    const-string p1, "1"
    invoke-static { v0, p1, p2 }, Lcom/project7/localmanager/BsonLite;->writeSkillPairsElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[[I)V
  .line 297
    new-instance p2, Ljava/io/ByteArrayOutputStream;
    invoke-direct { p2 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 298
    const/4 v2, 0
    invoke-static { p2, v1, v2 }, Lcom/project7/localmanager/BsonLite;->writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
  .line 299
    invoke-static { p2, p1, v2 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 301
    new-instance p1, Ljava/io/ByteArrayOutputStream;
    invoke-direct { p1 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 303
    const-string v1, "id"
    invoke-static { p1, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 304
    new-instance p0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { p0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 305
    invoke-interface { p3 }, Ljava/util/Map;->entrySet()Ljava/util/Set;
    move-result-object p3
    invoke-interface { p3 }, Ljava/util/Set;->iterator()Ljava/util/Iterator;
    move-result-object p3
  :L0
    invoke-interface { p3 }, Ljava/util/Iterator;->hasNext()Z
    move-result v1
    if-eqz v1, :L1
    invoke-interface { p3 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Ljava/util/Map$Entry;
  .line 306
    const/4 v3, 1
    invoke-virtual { p0, v3 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 307
    invoke-interface { v1 }, Ljava/util/Map$Entry;->getKey()Ljava/lang/Object;
    move-result-object v3
    check-cast v3, Ljava/lang/String;
    invoke-static { p0, v3 }, Lcom/project7/localmanager/BsonLite;->writeCString(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 308
    const/16 v3, 8
    invoke-static { v3 }, Ljava/nio/ByteBuffer;->allocate(I)Ljava/nio/ByteBuffer;
    move-result-object v3
    sget-object v4, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { v3, v4 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object v3
  .line 309
    invoke-interface { v1 }, Ljava/util/Map$Entry;->getValue()Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Ljava/lang/Double;
    invoke-virtual { v1 }, Ljava/lang/Double;->doubleValue()D
    move-result-wide v4
    invoke-virtual { v3, v4, v5 }, Ljava/nio/ByteBuffer;->putDouble(D)Ljava/nio/ByteBuffer;
    move-result-object v1
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->array()[B
    move-result-object v1
  .line 310
    array-length v3, v1
    invoke-virtual { p0, v1, v2, v3 }, Ljava/io/ByteArrayOutputStream;->write([BII)V
  .line 311
    goto :L0
  :L1
  .line 312
    invoke-static { p0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    const-string p3, "d"
    invoke-static { p1, p3, p0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 313
    sget-object p0, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    const-string p3, "a"
    invoke-static { p1, p3, p0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 314
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p3
    const-string v0, "s"
    invoke-static { p1, v0, p3 }, Lcom/project7/localmanager/BsonLite;->writeArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 315
    const-string p3, "t"
    invoke-static { p1, p3, p0 }, Lcom/project7/localmanager/BsonLite;->writeArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 316
    invoke-static { p2 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    const-string p2, "ai"
    invoke-static { p1, p2, p0 }, Lcom/project7/localmanager/BsonLite;->writeArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 317
    const-string p0, "as"
    invoke-static { p1, p0, v2 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 318
    invoke-static { p1 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method private static heroDataDocument(I)[B
  .registers 12
  .line 1159
    const/4 v0, 2
    const/4 v1, 1
    const/16 v2, 24
    if-ne p0, v2, :L0
    move v2, v0
    goto :L1
  :L0
    move v2, v1
  :L1
  .line 1160
    new-instance v3, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v3 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 1161
    const-string v4, "o"
    invoke-static { v3, v4, v1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 1162
    const/4 v4, 3
    const-string v5, "ss"
    invoke-static { v3, v5, v4 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 1163
    sget-object v4, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    const-string v5, "oa"
    invoke-static { v3, v5, v4 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 1164
    new-instance v4, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v4 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 1165
    sget-object v5, Lcom/project7/localmanager/LocalArtifactEngine;->ATTRS:[Ljava/lang/String;
    array-length v6, v5
    const/4 v7, 0
    move v8, v7
  :L2
    if-ge v8, v6, :L3
    aget-object v9, v5, v8
    const/16 v10, 60
    invoke-static { v4, v9, v10 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
    add-int/lit8 v8, v8, 1
    goto :L2
  :L3
  .line 1166
    invoke-static { v4 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object v4
    const-string v5, "ot"
    invoke-static { v3, v5, v4 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 1167
    sget-object v4, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    const-string v5, "rotc"
    invoke-static { v3, v5, v4 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 1168
    const-string v4, "sl"
    invoke-static { v3, v4 }, Lcom/project7/localmanager/BsonLite;->writeEmptyArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 1170
    new-instance v5, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v5 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 1171
    const-string v6, "items"
    invoke-static { v5, v6 }, Lcom/project7/localmanager/BsonLite;->writeEmptyArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 1172
    const/16 v6, 25
    const-string v8, "mc"
    invoke-static { v5, v8, v6 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 1174
    sget-object v6, Ljava/util/Locale;->ROOT:Ljava/util/Locale;
    new-array v0, v0, [Ljava/lang/Object;
    invoke-static { p0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v8
    aput-object v8, v0, v7
    invoke-static { p0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v8
    aput-object v8, v0, v1
    const-string v8, "%08x%016x"
    invoke-static { v6, v8, v0 }, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;
    move-result-object v0
  .line 1175
    new-instance v6, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v6 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 1176
    const-string v8, "i"
    invoke-static { v6, v8, p0 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 1177
    const-string v8, "u"
    invoke-static { v6, v8, v0 }, Lcom/project7/localmanager/BsonLite;->writeStringElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/String;)V
  .line 1178
    const-string v8, "fb"
    invoke-static { v6, v8, v7 }, Lcom/project7/localmanager/BsonLite;->writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
  .line 1179
    new-instance v8, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v8 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 1180
    invoke-static { v6 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object v6
    invoke-static { v8, v0, v6 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 1182
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 1183
    invoke-static { v0, v4, v2 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 1184
    const-string v2, "so"
    invoke-static { v0, v2, v1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 1185
    const/16 v1, 100
    const-string v2, "cf"
    invoke-static { v0, v2, v1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 1186
    invoke-static { v3 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object v1
    const-string v2, "ar"
    invoke-static { v0, v2, v1 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 1187
    const-string v1, "ef"
    invoke-static { v0, v1, v7 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 1188
    invoke-static { v5 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object v1
    const-string v2, "ti"
    invoke-static { v0, v2, v1 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 1189
    const-string v1, "cat"
    invoke-static { v0, v1 }, Lcom/project7/localmanager/BsonLite;->writeNullElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 1190
    invoke-static { p0 }, Lcom/project7/localmanager/BsonLite;->objectIdBytes(I)[B
    move-result-object p0
    const-string v1, "cs"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeObjectIdElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 1191
    invoke-static { v8 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    const-string v1, "sk"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 1192
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static heroValueDocument(II)[B
  .registers 4
  .line 554
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 555
    const-string v1, "h"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 556
    const-string p0, "v"
    invoke-static { v0, p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 557
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method private static hex([BI)Ljava/lang/String;
  .registers 8
  .line 1320
    new-instance v0, Ljava/lang/StringBuilder;
    array-length v1, p0
    invoke-static { v1, p1 }, Ljava/lang/Math;->min(II)I
    move-result v1
    mul-int/lit8 v1, v1, 2
    invoke-direct { v0, v1 }, Ljava/lang/StringBuilder;-><init>(I)V
  .line 1321
    const/4 v1, 0
    move v2, v1
  :L0
    array-length v3, p0
    if-ge v2, v3, :L1
    if-ge v2, p1, :L1
  .line 1322
    sget-object v3, Ljava/util/Locale;->US:Ljava/util/Locale;
    const/4 v4, 1
    new-array v4, v4, [Ljava/lang/Object;
    aget-byte v5, p0, v2
    and-int/lit16 v5, v5, 255
    invoke-static { v5 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v5
    aput-object v5, v4, v1
    const-string v5, "%02x"
    invoke-static { v3, v5, v4 }, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;
    move-result-object v3
    invoke-virtual { v0, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  .line 1321
    add-int/lit8 v2, v2, 1
    goto :L0
  :L1
  .line 1324
    invoke-virtual { v0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p0
    return-object p0
.end method

.method private static intArrayBytes(Ljava/lang/Iterable;)[B
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Ljava/lang/Iterable<",
      "Ljava/lang/Integer;",
      ">;)[B"
    }
  .end annotation
  .registers 5
  .line 1518
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 1519
    nop
  .line 1520
    invoke-interface { p0 }, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;
    move-result-object p0
    const/4 v1, 0
  :L0
    invoke-interface { p0 }, Ljava/util/Iterator;->hasNext()Z
    move-result v2
    if-eqz v2, :L2
    invoke-interface { p0 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Ljava/lang/Integer;
  .line 1521
    if-eqz v2, :L1
    invoke-virtual { v2 }, Ljava/lang/Integer;->intValue()I
    move-result v3
    if-eqz v3, :L1
  .line 1522
    add-int/lit8 v3, v1, 1
    invoke-static { v1 }, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object v1
    invoke-virtual { v2 }, Ljava/lang/Integer;->intValue()I
    move-result v2
    invoke-static { v0, v1, v2 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
    move v1, v3
  :L1
  .line 1524
    goto :L0
  :L2
  .line 1525
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static intArrayValues([BLjava/lang/String;)Ljava/util/List;
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "([B",
      "Ljava/lang/String;",
      ")",
      "Ljava/util/List<",
      "Ljava/lang/Integer;",
      ">;"
    }
  .end annotation
  .registers 9
  .line 102
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object p0
  .line 103
    new-instance p1, Ljava/util/ArrayList;
    invoke-direct { p1 }, Ljava/util/ArrayList;-><init>()V
  .line 104
    if-eqz p0, :L9
    array-length v0, p0
    const/4 v1, 5
    if-ge v0, v1, :L0
    goto/16 :L9
  :L0
  .line 107
    invoke-static { p0 }, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;
    move-result-object v0
    sget-object v2, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { v0, v2 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object v0
  .line 108
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result v2
  .line 109
    if-lt v2, v1, :L8
    array-length p0, p0
    if-le v2, p0, :L1
    goto :L8
  :L1
  .line 112
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->position()I
    move-result p0
    add-int/lit8 v1, v2, -1
    if-ge p0, v1, :L7
  .line 113
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->get()B
    move-result p0
    and-int/lit16 p0, p0, 255
  .line 114
    invoke-static { v0, v2 }, Lcom/project7/localmanager/BsonLite;->readCString(Ljava/nio/ByteBuffer;I)Ljava/lang/String;
    move-result-object v1
    if-nez v1, :L2
  .line 115
    goto :L7
  :L2
  .line 117
    const/16 v1, 16
    if-ne p0, v1, :L3
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->remaining()I
    move-result v1
    const/4 v3, 4
    if-lt v1, v3, :L3
  .line 118
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result p0
    invoke-static { p0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object p0
    invoke-interface { p1, p0 }, Ljava/util/List;->add(Ljava/lang/Object;)Z
    goto :L6
  :L3
  .line 119
    const/16 v1, 18
    if-ne p0, v1, :L4
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->remaining()I
    move-result v1
    const/16 v3, 8
    if-lt v1, v3, :L4
  .line 120
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->getLong()J
    move-result-wide v3
  .line 121
    const-wide/32 v5, 0x80000000
    cmp-long p0, v3, v5
    if-ltz p0, :L5
    const-wide/32 v5, 2147483647
    cmp-long p0, v3, v5
    if-gtz p0, :L5
  .line 122
    long-to-int p0, v3
    invoke-static { p0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object p0
    invoke-interface { p1, p0 }, Ljava/util/List;->add(Ljava/lang/Object;)Z
    goto :L5
  :L4
  .line 124
    invoke-static { v0, p0, v2 }, Lcom/project7/localmanager/BsonLite;->skipValue(Ljava/nio/ByteBuffer;II)Z
    move-result p0
    if-nez p0, :L5
  .line 125
    goto :L7
  :L5
  .line 124
    nop
  :L6
  .line 127
    goto :L1
  :L7
  .line 128
    return-object p1
  :L8
  .line 110
    return-object p1
  :L9
  .line 105
    return-object p1
.end method

.method private static intBytes(I)[B
  .registers 2
  .line 1508
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 1509
    invoke-static { v0, p0 }, Lcom/project7/localmanager/BsonLite;->writeLeInt(Ljava/io/ByteArrayOutputStream;I)V
  .line 1510
    invoke-virtual { v0 }, Ljava/io/ByteArrayOutputStream;->toByteArray()[B
    move-result-object p0
    return-object p0
.end method

.method static intDocument(Ljava/lang/String;I)[B
  .registers 4
  .line 132
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 133
    const/16 v1, 16
    invoke-virtual { v0, v1 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 134
    invoke-static { v0, p0 }, Lcom/project7/localmanager/BsonLite;->writeCString(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 135
    invoke-static { v0, p1 }, Lcom/project7/localmanager/BsonLite;->writeLeInt(Ljava/io/ByteArrayOutputStream;I)V
  .line 136
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static intListDocument(Ljava/lang/String;Ljava/lang/Iterable;)[B
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Ljava/lang/String;",
      "Ljava/lang/Iterable<",
      "Ljava/lang/Integer;",
      ">;)[B"
    }
  .end annotation
  .registers 7
  .line 753
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 754
    new-instance v1, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v1 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 755
    nop
  .line 756
    invoke-interface { p1 }, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;
    move-result-object p1
    const/4 v2, 0
  :L0
    invoke-interface { p1 }, Ljava/util/Iterator;->hasNext()Z
    move-result v3
    if-eqz v3, :L1
    invoke-interface { p1 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v3
    check-cast v3, Ljava/lang/Integer;
  .line 757
    add-int/lit8 v4, v2, 1
    invoke-static { v2 }, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object v2
    invoke-virtual { v3 }, Ljava/lang/Integer;->intValue()I
    move-result v3
    invoke-static { v1, v2, v3 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 758
    move v2, v4
    goto :L0
  :L1
  .line 759
    invoke-static { v1 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p1
    invoke-static { v0, p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 760
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static intValue([BLjava/lang/String;)Ljava/lang/Integer;
  .registers 6
  .line 35
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->findElement([BLjava/lang/String;)Lcom/project7/localmanager/BsonLite$Element;
    move-result-object p0
  .line 36
    const/4 p1, 0
    if-nez p0, :L0
  .line 37
    return-object p1
  :L0
  .line 39
    iget-object v0, p0, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    invoke-static { v0 }, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;
    move-result-object v0
    sget-object v1, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { v0, v1 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object v0
  .line 40
    iget v1, p0, Lcom/project7/localmanager/BsonLite$Element;->type:I
    const/16 v2, 16
    if-ne v1, v2, :L1
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->remaining()I
    move-result v1
    const/4 v2, 4
    if-ne v1, v2, :L1
  .line 41
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result p0
    invoke-static { p0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object p0
    return-object p0
  :L1
  .line 43
    iget p0, p0, Lcom/project7/localmanager/BsonLite$Element;->type:I
    const/16 v1, 18
    if-ne p0, v1, :L3
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->remaining()I
    move-result p0
    const/16 v1, 8
    if-ne p0, v1, :L3
  .line 44
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->getLong()J
    move-result-wide v0
  .line 45
    const-wide/32 v2, 0x80000000
    cmp-long p0, v0, v2
    if-ltz p0, :L2
    const-wide/32 v2, 2147483647
    cmp-long p0, v0, v2
    if-gtz p0, :L2
    long-to-int p0, v0
    invoke-static { p0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object p1
  :L2
    return-object p1
  :L3
  .line 47
    return-object p1
.end method

.method static keys([B)Ljava/util/List;
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "([B)",
      "Ljava/util/List<",
      "Ljava/lang/String;",
      ">;"
    }
  .end annotation
  .registers 5
  .line 876
    new-instance v0, Ljava/util/ArrayList;
    invoke-direct { v0 }, Ljava/util/ArrayList;-><init>()V
  .line 877
    if-eqz p0, :L5
    array-length v1, p0
    const/4 v2, 5
    if-ge v1, v2, :L0
    goto :L5
  :L0
  .line 878
    invoke-static { p0 }, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;
    move-result-object v1
    sget-object v3, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { v1, v3 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object v1
  .line 879
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result v3
  .line 880
    if-lt v3, v2, :L4
    array-length p0, p0
    if-le v3, p0, :L1
    goto :L4
  :L1
  .line 881
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result p0
    add-int/lit8 v2, v3, -1
    if-ge p0, v2, :L3
  .line 882
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->get()B
    move-result p0
    and-int/lit16 p0, p0, 255
  .line 883
    invoke-static { v1, v3 }, Lcom/project7/localmanager/BsonLite;->readCString(Ljava/nio/ByteBuffer;I)Ljava/lang/String;
    move-result-object v2
  .line 884
    if-eqz v2, :L3
    invoke-static { v1, p0, v3 }, Lcom/project7/localmanager/BsonLite;->skipValue(Ljava/nio/ByteBuffer;II)Z
    move-result p0
    if-nez p0, :L2
    goto :L3
  :L2
  .line 885
    invoke-interface { v0, v2 }, Ljava/util/List;->add(Ljava/lang/Object;)Z
  .line 886
    goto :L1
  :L3
  .line 887
    return-object v0
  :L4
  .line 880
    return-object v0
  :L5
  .line 877
    return-object v0
.end method

.method private static listBytes(Ljava/util/List;)[B
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Ljava/util/List<",
      "*>;)[B"
    }
  .end annotation
  .registers 5
  .line 934
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 935
    const/4 v1, 0
  :L0
    invoke-interface { p0 }, Ljava/util/List;->size()I
    move-result v2
    if-ge v1, v2, :L1
    invoke-static { v1 }, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object v2
    invoke-interface { p0, v1 }, Ljava/util/List;->get(I)Ljava/lang/Object;
    move-result-object v3
    invoke-static { v0, v2, v3 }, Lcom/project7/localmanager/BsonLite;->writeValue(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/Object;)V
    add-int/lit8 v1, v1, 1
    goto :L0
  :L1
  .line 936
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static loginFailureDocument(Ljava/lang/String;)[B
  .registers 4
  .line 685
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 686
    const-string v1, "e"
    const/4 v2, 5
    invoke-static { v0, v1, v2 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 687
    if-nez p0, :L0
    const-string p0, ""
  :L0
    const-string v1, "m"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeStringElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/String;)V
  .line 688
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static luckyDrawCardReplyDocument(ZII)[B
  .registers 6
  .line 661
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 662
    const-string v1, "index"
    invoke-static { v0, v1, p1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 663
    const-string p1, "is_open"
    invoke-static { v0, p1, p0 }, Lcom/project7/localmanager/BsonLite;->writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
  .line 664
    const/16 p1, 24
    invoke-static { p1 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object p1
    invoke-static { p1 }, Ljava/util/Collections;->singletonList(Ljava/lang/Object;)Ljava/util/List;
    move-result-object p1
    const-string v1, "hero"
    invoke-static { v0, v1, p1 }, Lcom/project7/localmanager/BsonLite;->writeIntArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/Iterable;)V
  .line 665
    const-string p1, "hero_file"
    const/4 v1, 1
    invoke-static { v0, p1, v1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 666
    const-string p1, "get_hero"
    const/4 v1, 0
    invoke-static { v0, p1, v1 }, Lcom/project7/localmanager/BsonLite;->writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
  .line 667
    sget-object p1, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    const-string v1, "other_reward"
    invoke-static { v0, v1, p1 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 668
    const-string v1, "jiaozhi"
    invoke-static { v0, v1, p1 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 670
    new-instance v1, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v1 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 671
    const-string v2, "rt"
    invoke-static { v1, v2, p0 }, Lcom/project7/localmanager/BsonLite;->writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
  .line 672
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    const-string v0, "info"
    invoke-static { v1, v0, p0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 673
    const-string p0, "prog"
    invoke-static { v1, p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 674
    const-string p0, "t"
    invoke-static { v1, p0, p2 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 675
    invoke-static { v1 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static luckyDrawFileContentsReplyDocument(ZI)[B
  .registers 8
  .line 642
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 643
    const/4 v1, 0
    move v2, v1
  :L0
    const/4 v3, 6
    if-ge v2, v3, :L1
  .line 644
    new-instance v3, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v3 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 645
    const-string v4, "index"
    invoke-static { v3, v4, v2 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 646
    const-string v4, "is_open"
    invoke-static { v3, v4, v1 }, Lcom/project7/localmanager/BsonLite;->writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
  .line 647
    const/16 v4, 24
    invoke-static { v4 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v4
    invoke-static { v4 }, Ljava/util/Collections;->singletonList(Ljava/lang/Object;)Ljava/util/List;
    move-result-object v4
    const-string v5, "hero"
    invoke-static { v3, v5, v4 }, Lcom/project7/localmanager/BsonLite;->writeIntArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/Iterable;)V
  .line 648
    const-string v4, "hero_file"
    const/4 v5, 1
    invoke-static { v3, v4, v5 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 649
    const-string v4, "get_hero"
    invoke-static { v3, v4, v1 }, Lcom/project7/localmanager/BsonLite;->writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
  .line 650
    invoke-static { v2 }, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object v4
    invoke-static { v3 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object v3
    invoke-static { v0, v4, v3 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 643
    add-int/lit8 v2, v2, 1
    goto :L0
  :L1
  .line 653
    new-instance v1, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v1 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 654
    const-string v2, "rt"
    invoke-static { v1, v2, p0 }, Lcom/project7/localmanager/BsonLite;->writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
  .line 655
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    const-string v0, "info"
    invoke-static { v1, v0, p0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 656
    const-string p0, "t"
    invoke-static { v1, p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 657
    invoke-static { v1 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static luckyDrawFileReplyDocument(ZI)[B
  .registers 4
  .line 628
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 629
    const-string v1, "rt"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
  .line 630
    const-string p0, "t"
    invoke-static { v0, p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 631
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static luckyDrawQuitReplyDocument(ZI)[B
  .registers 4
  .line 635
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 636
    const-string v1, "rt"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
  .line 637
    const-string p0, "t"
    invoke-static { v0, p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 638
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static messagePackValue([BZ)Ljava/lang/Object;
  .registers 11
  .line 827
    new-instance v0, Ljava/util/LinkedHashMap;
    invoke-direct { v0 }, Ljava/util/LinkedHashMap;-><init>()V
  .line 828
    invoke-static { p0 }, Lcom/project7/localmanager/BsonLite;->keys([B)Ljava/util/List;
    move-result-object v1
    invoke-interface { v1 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v1
  :L0
    invoke-interface { v1 }, Ljava/util/Iterator;->hasNext()Z
    move-result v2
    if-eqz v2, :L16
    invoke-interface { v1 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Ljava/lang/String;
  .line 829
    invoke-static { p0, v2 }, Lcom/project7/localmanager/BsonLite;->findElement([BLjava/lang/String;)Lcom/project7/localmanager/BsonLite$Element;
    move-result-object v3
  .line 830
    iget-object v4, v3, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    invoke-static { v4 }, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;
    move-result-object v4
    sget-object v5, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { v4, v5 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object v4
  .line 832
    iget v5, v3, Lcom/project7/localmanager/BsonLite$Element;->type:I
    const/4 v6, 1
    const/4 v7, 0
    packed-switch v5, :L18
  :L1
  .line 853
    new-instance p0, Ljava/lang/IllegalArgumentException;
    new-instance p1, Ljava/lang/StringBuilder;
    invoke-direct { p1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string v0, "unsupported avatar BSON type "
    invoke-virtual { p1, v0 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    iget v0, v3, Lcom/project7/localmanager/BsonLite$Element;->type:I
    invoke-virtual { p1, v0 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { p1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p1
    invoke-direct { p0, p1 }, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V
    throw p0
  :L2
  .line 843
    invoke-virtual { v4 }, Ljava/nio/ByteBuffer;->getLong()J
    move-result-wide v3
    invoke-static { v3, v4 }, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;
    move-result-object v3
    goto/16 :L15
  :L3
  .line 842
    invoke-virtual { v4 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result v3
    invoke-static { v3 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v3
    goto/16 :L15
  :L4
  .line 841
    const/4 v3, 0
    goto/16 :L15
  :L5
  .line 845
    new-instance v3, Ljava/util/LinkedHashMap;
    invoke-direct { v3 }, Ljava/util/LinkedHashMap;-><init>()V
  .line 846
    invoke-virtual { v4 }, Ljava/nio/ByteBuffer;->getLong()J
    move-result-wide v4
    invoke-static { v4, v5 }, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;
    move-result-object v4
    const-string v5, "$date"
    invoke-interface { v3, v5, v4 }, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    goto/16 :L15
  :L6
  .line 840
    iget-object v3, v3, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    aget-byte v3, v3, v7
    if-eqz v3, :L7
    goto :L8
  :L7
    move v6, v7
  :L8
    invoke-static { v6 }, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
    move-result-object v3
    goto :L15
  :L9
  .line 838
    new-instance v3, Ljava/util/LinkedHashMap;
    invoke-direct { v3 }, Ljava/util/LinkedHashMap;-><init>()V
  .line 839
    invoke-static { p0, v2 }, Lcom/project7/localmanager/BsonLite;->uuidValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v4
    const-string v5, "$oid"
    invoke-interface { v3, v5, v4 }, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    goto :L15
  :L10
  .line 848
    invoke-virtual { v4 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result v3
    invoke-virtual { v4 }, Ljava/nio/ByteBuffer;->get()B
    move-result v5
    and-int/lit16 v5, v5, 255
  .line 849
    new-array v3, v3, [B
    invoke-virtual { v4, v3 }, Ljava/nio/ByteBuffer;->get([B)Ljava/nio/ByteBuffer;
  .line 850
    new-instance v4, Ljava/util/LinkedHashMap;
    invoke-direct { v4 }, Ljava/util/LinkedHashMap;-><init>()V
  .line 851
    invoke-static { }, Ljava/util/Base64;->getEncoder()Ljava/util/Base64$Encoder;
    move-result-object v8
    invoke-virtual { v8, v3 }, Ljava/util/Base64$Encoder;->encodeToString([B)Ljava/lang/String;
    move-result-object v3
    const-string v8, "$binary"
    invoke-interface { v4, v8, v3 }, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
  .line 852
    sget-object v3, Ljava/util/Locale;->ROOT:Ljava/util/Locale;
    new-array v6, v6, [Ljava/lang/Object;
    invoke-static { v5 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v5
    aput-object v5, v6, v7
    const-string v5, "%02x"
    invoke-static { v3, v5, v6 }, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;
    move-result-object v3
    const-string v5, "$type"
    invoke-interface { v4, v5, v3 }, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    move-object v3, v4
    goto :L15
  :L11
  .line 836
    iget-object v3, v3, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    invoke-static { v3, v6 }, Lcom/project7/localmanager/BsonLite;->messagePackValue([BZ)Ljava/lang/Object;
    move-result-object v3
    goto :L15
  :L12
  .line 835
    iget-object v3, v3, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    invoke-static { v3, v7 }, Lcom/project7/localmanager/BsonLite;->messagePackValue([BZ)Ljava/lang/Object;
    move-result-object v3
    goto :L15
  :L13
  .line 834
    invoke-static { p0, v2 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object v3
    goto :L15
  :L14
  .line 833
    invoke-virtual { v4 }, Ljava/nio/ByteBuffer;->getDouble()D
    move-result-wide v3
    invoke-static { v3, v4 }, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;
    move-result-object v3
  :L15
  .line 855
    invoke-interface { v0, v2, v3 }, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
  .line 856
    goto/16 :L0
  :L16
  .line 857
    if-eqz p1, :L17
    new-instance p0, Ljava/util/ArrayList;
    invoke-interface { v0 }, Ljava/util/Map;->values()Ljava/util/Collection;
    move-result-object p1
    invoke-direct { p0, p1 }, Ljava/util/ArrayList;-><init>(Ljava/util/Collection;)V
    move-object v0, p0
  :L17
    return-object v0
  :L18
  .packed-switch 1
    :L14
    :L13
    :L12
    :L11
    :L10
    :L1
    :L9
    :L6
    :L5
    :L4
    :L1
    :L1
    :L1
    :L1
    :L1
    :L3
    :L1
    :L2
  .end packed-switch
.end method

.method static numericValue([BLjava/lang/String;)Ljava/lang/Number;
  .registers 6
  .line 59
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->findElement([BLjava/lang/String;)Lcom/project7/localmanager/BsonLite$Element;
    move-result-object p0
  .line 60
    const/4 p1, 0
    if-nez p0, :L0
    return-object p1
  :L0
  .line 61
    iget-object v0, p0, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    invoke-static { v0 }, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;
    move-result-object v0
    sget-object v1, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { v0, v1 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object v0
  .line 62
    iget v1, p0, Lcom/project7/localmanager/BsonLite$Element;->type:I
    const/4 v2, 1
    const/16 v3, 8
    if-ne v1, v2, :L1
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->remaining()I
    move-result v1
    if-ne v1, v3, :L1
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->getDouble()D
    move-result-wide p0
    invoke-static { p0, p1 }, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;
    move-result-object p0
    return-object p0
  :L1
  .line 63
    iget v1, p0, Lcom/project7/localmanager/BsonLite$Element;->type:I
    const/16 v2, 16
    if-ne v1, v2, :L2
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->remaining()I
    move-result v1
    const/4 v2, 4
    if-ne v1, v2, :L2
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result p0
    invoke-static { p0 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object p0
    return-object p0
  :L2
  .line 64
    iget p0, p0, Lcom/project7/localmanager/BsonLite$Element;->type:I
    const/16 v1, 18
    if-ne p0, v1, :L3
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->remaining()I
    move-result p0
    if-ne p0, v3, :L3
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->getLong()J
    move-result-wide p0
    invoke-static { p0, p1 }, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;
    move-result-object p0
    return-object p0
  :L3
  .line 65
    return-object p1
.end method

.method private static objectIdBytes(I)[B
  .registers 3
  .line 1196
    const/16 v0, 12
    new-array v0, v0, [B
  .line 1197
    int-to-byte p0, p0
    const/4 v1, 3
    aput-byte p0, v0, v1
  .line 1198
    const/16 v1, 11
    aput-byte p0, v0, v1
  .line 1199
    return-object v0
.end method

.method static patrolReplyDocument(ZLjava/lang/Iterable;)[B
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(Z",
      "Ljava/lang/Iterable<",
      "Ljava/lang/Integer;",
      ">;)[B"
    }
  .end annotation
  .registers 4
  .line 531
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 532
    const-string v1, "s"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
  .line 533
    const-string v1, "rs"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
  .line 534
    sget-object p0, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    const-string v1, "ext"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 535
    const-string p0, "ev"
    invoke-static { v0, p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeIntArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/Iterable;)V
  .line 536
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method private static persistedAreas(ZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
  .registers 16
  .line 434
    invoke-static { p0, p1, p2 }, Lcom/project7/localmanager/BsonLite;->areasDocument(ZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
    move-result-object p0
  .line 435
    invoke-static { p2 }, Lcom/project7/localmanager/LocalServiceEngine;->cores([B)Ljava/util/Map;
    move-result-object p1
  .line 436
    const-string v0, "city"
    invoke-static { p2, v0 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v0
    const-string v1, "areas"
    invoke-static { v0, v1 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v0
  .line 437
    invoke-static { p0 }, Lcom/project7/localmanager/BsonLite;->keys([B)Ljava/util/List;
    move-result-object v1
    invoke-interface { v1 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v1
  :L0
    invoke-interface { v1 }, Ljava/util/Iterator;->hasNext()Z
    move-result v2
    if-eqz v2, :L8
    invoke-interface { v1 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Ljava/lang/String;
  .line 438
    invoke-static { v0, v2 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v3
    invoke-static { p0, v2 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v4
  .line 439
    const-string v5, "st"
    invoke-static { v4, v5 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v6
  .line 440
    const/4 v7, 2
    invoke-static { v7 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v7
    const-string v8, "id"
    invoke-static { v4, v8 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v9
    invoke-interface { p1, v9 }, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v9
    invoke-virtual { v7, v9 }, Ljava/lang/Integer;->equals(Ljava/lang/Object;)Z
    move-result v7
    const-string v9, "1"
    invoke-static { v6, v9, v7 }, Lcom/project7/localmanager/BsonLite;->withProfileBool([BLjava/lang/String;Z)[B
    move-result-object v6
  .line 441
    invoke-static { v4, v8 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v7
    invoke-virtual { v7 }, Ljava/lang/Integer;->intValue()I
    move-result v7
    invoke-static { p2, v7 }, Lcom/project7/localmanager/LocalChapterCityEngine;->locked([BI)Z
    move-result v7
    const-string v9, "2"
    invoke-static { v6, v9, v7 }, Lcom/project7/localmanager/BsonLite;->withProfileBool([BLjava/lang/String;Z)[B
    move-result-object v6
  .line 442
    const/4 v7, 4
    invoke-static { v4, v5, v7, v6 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v4
  .line 443
    invoke-static { p0, v2, v4 }, Lcom/project7/localmanager/BsonLite;->withProfileDocument([BLjava/lang/String;[B)[B
    move-result-object p0
  .line 444
    if-nez v3, :L1
    goto :L0
  :L1
  .line 446
    const-string v6, "stage"
    filled-new-array { v8, v5, v6 }, [Ljava/lang/String;
    move-result-object v6
    const/4 v9, 0
  :L2
    const/4 v10, 3
    if-ge v9, v10, :L7
    aget-object v11, v6, v9
  .line 447
    invoke-virtual { v11, v5 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v12
    if-eqz v12, :L3
    move v10, v7
    goto :L4
  :L3
    invoke-virtual { v11, v8 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v12
    if-eqz v12, :L4
    const/16 v10, 16
  :L4
  .line 448
    invoke-virtual { v11, v8 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v12
    if-eqz v12, :L5
    invoke-static { v4, v11 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v12
    invoke-virtual { v12 }, Ljava/lang/Integer;->intValue()I
    move-result v12
    invoke-static { v12 }, Lcom/project7/localmanager/BsonLite;->intBytes(I)[B
    move-result-object v12
    goto :L6
  :L5
    invoke-static { v4, v11 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v12
  :L6
  .line 447
    invoke-static { v3, v11, v10, v12 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v3
  .line 446
    add-int/lit8 v9, v9, 1
    goto :L2
  :L7
  .line 449
    invoke-static { p0, v2, v3 }, Lcom/project7/localmanager/BsonLite;->withProfileDocument([BLjava/lang/String;[B)[B
    move-result-object p0
  .line 450
    goto/16 :L0
  :L8
  .line 451
    return-object p0
.end method

.method private static persistedCityValues([BLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
  .registers 5
  .line 540
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->withPatrolProgress([BLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object p0
    const-string v0, "city"
    invoke-static { p0, v0 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object p0
  .line 541
    if-nez p0, :L0
    sget-object p0, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
  :L0
  .line 542
    invoke-static { p1 }, Lcom/project7/localmanager/BsonLite;->cityValuesDocument(Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object p1
  .line 543
    invoke-static { p1 }, Lcom/project7/localmanager/BsonLite;->keys([B)Ljava/util/List;
    move-result-object v0
    invoke-interface { v0 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v0
  :L1
    invoke-interface { v0 }, Ljava/util/Iterator;->hasNext()Z
    move-result v1
    if-eqz v1, :L3
    invoke-interface { v0 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Ljava/lang/String;
  .line 544
    invoke-static { p0, v1 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v2
    if-nez v2, :L2
    invoke-static { p1, v1 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v2
    invoke-virtual { v2 }, Ljava/lang/Integer;->intValue()I
    move-result v2
    invoke-static { p0, v1, v2 }, Lcom/project7/localmanager/BsonLite;->withProfileInt([BLjava/lang/String;I)[B
    move-result-object p0
  :L2
  .line 545
    goto :L1
  :L3
  .line 546
    return-object p0
.end method

.method static playerNameReplyDocument(ZZ)[B
  .registers 4
  .line 1232
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 1233
    const-string v1, "r"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
  .line 1234
    const-string p0, "in"
    invoke-static { v0, p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
  .line 1235
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static profileHeroDocument([BI)[B
  .registers 8
  .line 271
    if-nez p0, :L0
    sget-object p0, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    return-object p0
  :L0
  .line 272
    sget-object v0, Lcom/project7/localmanager/BsonLite;->HERO_INDEX:Ljava/lang/ThreadLocal;
    invoke-virtual { v0 }, Ljava/lang/ThreadLocal;->get()Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Ljava/util/LinkedHashMap;
  .line 273
    invoke-virtual { v0, p0 }, Ljava/util/LinkedHashMap;->get(Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Ljava/util/Map;
  .line 274
    if-nez v1, :L5
  .line 275
    new-instance v1, Ljava/util/HashMap;
    invoke-direct { v1 }, Ljava/util/HashMap;-><init>()V
  .line 276
    const-string v2, "heromgr"
    invoke-static { p0, v2 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v2
    const-string v3, "hrs"
    invoke-static { v2, v3 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v2
  .line 277
    invoke-static { v2 }, Lcom/project7/localmanager/BsonLite;->documentEntries([B)Ljava/util/Map;
    move-result-object v2
    invoke-interface { v2 }, Ljava/util/Map;->values()Ljava/util/Collection;
    move-result-object v2
    invoke-interface { v2 }, Ljava/util/Collection;->iterator()Ljava/util/Iterator;
    move-result-object v2
  :L1
    invoke-interface { v2 }, Ljava/util/Iterator;->hasNext()Z
    move-result v3
    if-eqz v3, :L3
    invoke-interface { v2 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v3
    check-cast v3, [B
  .line 278
    const-string v4, "0"
    invoke-static { v3, v4 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v4
    const-string v5, "1"
    invoke-static { v3, v5 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v3
  .line 279
    if-eqz v4, :L2
    if-eqz v3, :L2
    invoke-interface { v1, v4, v3 }, Ljava/util/Map;->putIfAbsent(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
  :L2
  .line 280
    goto :L1
  :L3
  .line 282
    array-length v2, p0
    const/high16 v3, 64
    if-gt v2, v3, :L5
  .line 283
    invoke-virtual { v0 }, Ljava/util/LinkedHashMap;->size()I
    move-result v2
    const/4 v3, 2
    if-lt v2, v3, :L4
    invoke-virtual { v0 }, Ljava/util/LinkedHashMap;->keySet()Ljava/util/Set;
    move-result-object v2
    invoke-interface { v2 }, Ljava/util/Set;->iterator()Ljava/util/Iterator;
    move-result-object v2
    invoke-interface { v2 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v2
    invoke-virtual { v0, v2 }, Ljava/util/LinkedHashMap;->remove(Ljava/lang/Object;)Ljava/lang/Object;
  :L4
  .line 284
    invoke-virtual { v0, p0, v1 }, Ljava/util/LinkedHashMap;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
  :L5
  .line 287
    invoke-static { p1 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object p0
    sget-object p1, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    invoke-interface { v1, p0, p1 }, Ljava/util/Map;->getOrDefault(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object p0
    check-cast p0, [B
    return-object p0
.end method

.method private static profileIntArrayBytes(Ljava/lang/Iterable;)[B
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Ljava/lang/Iterable<",
      "Ljava/lang/Integer;",
      ">;)[B"
    }
  .end annotation
  .registers 5
  .line 981
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 982
    nop
  .line 983
    invoke-interface { p0 }, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;
    move-result-object p0
    const/4 v1, 0
  :L0
    invoke-interface { p0 }, Ljava/util/Iterator;->hasNext()Z
    move-result v2
    if-eqz v2, :L2
    invoke-interface { p0 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Ljava/lang/Integer;
  .line 984
    if-eqz v2, :L1
    add-int/lit8 v3, v1, 1
    invoke-static { v1 }, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object v1
    invoke-virtual { v2 }, Ljava/lang/Integer;->intValue()I
    move-result v2
    invoke-static { v0, v1, v2 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
    move v1, v3
  :L1
  .line 985
    goto :L0
  :L2
  .line 986
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static synthetic q7OriginalAllAreaInfoReplyDocument(ZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
  .registers 6
  .line 391
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->allAreaInfoReplyDocument(ZLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v0
    invoke-static { p2, p1 }, Lcom/project7/localmanager/BsonLite;->persistedCityValues([BLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object v1
    const-string v2, "cd"
    invoke-static { v0, v2, v1 }, Lcom/project7/localmanager/BsonLite;->withProfileDocument([BLjava/lang/String;[B)[B
    move-result-object v0
  .line 392
    invoke-static { p0, p1, p2 }, Lcom/project7/localmanager/BsonLite;->persistedAreas(ZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
    move-result-object p0
    const-string p1, "ais"
    invoke-static { v0, p1, p0 }, Lcom/project7/localmanager/BsonLite;->withProfileDocument([BLjava/lang/String;[B)[B
    move-result-object p0
    return-object p0
.end method

.method private static readCString(Ljava/nio/ByteBuffer;I)Ljava/lang/String;
  .registers 4
  .line 1328
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->position()I
    move-result v0
  :L0
  .line 1329
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->position()I
    move-result v1
    if-ge v1, p1, :L1
  .line 1330
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->get()B
    move-result v1
    if-nez v1, :L0
  .line 1331
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->position()I
    move-result p1
    add-int/lit8 p1, p1, -1
  .line 1332
    sub-int/2addr p1, v0
    new-array p1, p1, [B
  .line 1333
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->position()I
    move-result v1
  .line 1334
    invoke-virtual { p0, v0 }, Ljava/nio/ByteBuffer;->position(I)Ljava/nio/Buffer;
    move-result-object v0
    check-cast v0, Ljava/nio/ByteBuffer;
  .line 1335
    invoke-virtual { p0, p1 }, Ljava/nio/ByteBuffer;->get([B)Ljava/nio/ByteBuffer;
  .line 1336
    invoke-virtual { p0, v1 }, Ljava/nio/ByteBuffer;->position(I)Ljava/nio/Buffer;
    move-result-object p0
    check-cast p0, Ljava/nio/ByteBuffer;
  .line 1337
    new-instance p0, Ljava/lang/String;
    sget-object v0, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;
    invoke-direct { p0, p1, v0 }, Ljava/lang/String;-><init>([BLjava/nio/charset/Charset;)V
    return-object p0
  :L1
  .line 1340
    const/4 p0, 0
    return-object p0
.end method

# Project7 local optimization: conservative no-op detector for replaceElement.
# Returns true only when the document is canonical (declared length == byte length,
# zero terminator), every top-level key is ASCII (so the rebuilt key bytes would be
# identical), the whole document validates, and every element with the target key has
# the requested type and byte-identical payload. In that case the legacy rebuild of
# finishDocument/ByteArrayOutputStream would emit exactly the input bytes, so
# replaceElement returns a fresh copy of the input instead of rebuilding it.
# Anything else (absent key, changed payload/type, duplicates that differ, malformed
# document, non-ASCII key, trailing bytes) returns false and the legacy path runs.
.method private static replaceElementUnchanged([BLjava/lang/String;I[B)Z
  .registers 16
    if-eqz p0, :NO
    array-length v0, p0
    const/4 v1, 5
    if-lt v0, v1, :NO
    invoke-static { p0 }, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;
    move-result-object v0
    sget-object v2, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { v0, v2 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result v2
    if-lt v2, v1, :NO
    array-length v1, p0
    if-gt v2, v1, :NO
    array-length v1, p0
    if-ne v2, v1, :NO
    array-length v1, p0
    add-int/lit8 v1, v1, -1
    aget-byte v1, p0, v1
    if-nez v1, :NO
    if-eqz p1, :NO
    if-eqz p3, :NO
    const/4 v3, 0
    const/4 v4, 1
  :LOOP
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->position()I
    move-result v1
    add-int/lit8 v5, v2, -1
    if-ge v1, v5, :SCANEND
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->get()B
    move-result v1
    and-int/lit16 v1, v1, 255
    invoke-static { v0, v2 }, Lcom/project7/localmanager/BsonLite;->readCString(Ljava/nio/ByteBuffer;I)Ljava/lang/String;
    move-result-object v5
    if-nez v5, :KEYOK
    new-instance p0, Ljava/lang/IllegalArgumentException;
    const-string p1, "truncated BSON key"
    invoke-direct { p0, p1 }, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V
    throw p0
  :KEYOK
    const/4 v6, 0
  :ALOOP
    invoke-virtual { v5 }, Ljava/lang/String;->length()I
    move-result v7
    if-ge v6, v7, :ASCIIDONE
    invoke-virtual { v5, v6 }, Ljava/lang/String;->charAt(I)C
    move-result v7
    const/16 v8, 128
    if-lt v7, v8, :ACHAROK
    const/4 v4, 0
  :ACHAROK
    add-int/lit8 v6, v6, 1
    goto :ALOOP
  :ASCIIDONE
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->position()I
    move-result v6
    invoke-static { v0, v1, v2 }, Lcom/project7/localmanager/BsonLite;->skipValue(Ljava/nio/ByteBuffer;II)Z
    move-result v7
    if-nez v7, :VALOK
    new-instance p0, Ljava/lang/IllegalArgumentException;
    new-instance p1, Ljava/lang/StringBuilder;
    invoke-direct { p1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string p2, "unsupported BSON value type "
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, v1 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { p1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p1
    invoke-direct { p0, p1 }, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V
    throw p0
  :VALOK
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->position()I
    move-result v7
    invoke-virtual { p1, v5 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v8
    if-eqz v8, :NEXT
    const/4 v3, 1
    if-eq v1, p2, :TYPEMATCH
    const/4 v4, 0
    goto :NEXT
  :TYPEMATCH
    sub-int v8, v7, v6
    array-length v9, p3
    if-ne v8, v9, :LENNE
    const/4 v9, 0
  :CLOOP
    if-ge v9, v8, :NEXT
    add-int v10, v6, v9
    aget-byte v10, p0, v10
    aget-byte v11, p3, v9
    if-ne v10, v11, :CNE
    add-int/lit8 v9, v9, 1
    goto :CLOOP
  :CNE
    const/4 v4, 0
    goto :NEXT
  :LENNE
    const/4 v4, 0
  :NEXT
    goto :LOOP
  :SCANEND
    # Strict canonical check: the full scan must land exactly on the terminator byte.
    # If a value consumed the terminator or left a gap, the legacy rebuild would emit
    # different bytes, so fall back.
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->position()I
    move-result v1
    add-int/lit8 v5, v2, -1
    if-ne v1, v5, :NO
    if-eqz v3, :NO
    return v4
  :NO
    const/4 v0, 0
    return v0
.end method

.method private static replaceElement([BLjava/lang/String;I[B)[B
  .registers 16
    invoke-static { p0, p1, p2, p3 }, Lcom/project7/localmanager/BsonLite;->replaceElementUnchanged([BLjava/lang/String;I[B)Z
    move-result v0
    if-eqz v0, :LLEGACY
    array-length v0, p0
    invoke-static { p0, v0 }, Ljava/util/Arrays;->copyOf([BI)[B
    move-result-object v0
    return-object v0
  :LLEGACY
  .line 1457
    if-eqz p0, :L8
    array-length v0, p0
    const/4 v1, 5
    if-lt v0, v1, :L8
  .line 1460
    invoke-static { p0 }, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;
    move-result-object v0
    sget-object v2, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { v0, v2 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object v0
  .line 1461
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result v2
  .line 1462
    if-lt v2, v1, :L7
    array-length v1, p0
    if-gt v2, v1, :L7
  .line 1466
    new-instance v1, Ljava/io/ByteArrayOutputStream;
    # Project7 local optimization: presize the rebuild buffer to the document size so the
    # 32-byte doubling chain (Arrays.copyOf per growth step) is skipped.
    array-length v9, p0
    add-int/lit8 v9, v9, 8
    invoke-direct { v1, v9 }, Ljava/io/ByteArrayOutputStream;-><init>(I)V
  .line 1467
    const/4 v3, 0
    move v4, v3
  :L0
  .line 1468
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->position()I
    move-result v5
    add-int/lit8 v6, v2, -1
    if-ge v5, v6, :L5
  .line 1469
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->get()B
    move-result v5
    and-int/lit16 v5, v5, 255
  .line 1470
    invoke-static { v0, v2 }, Lcom/project7/localmanager/BsonLite;->readCString(Ljava/nio/ByteBuffer;I)Ljava/lang/String;
    move-result-object v6
  .line 1471
    if-eqz v6, :L4
  .line 1474
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->position()I
    move-result v7
  .line 1475
    invoke-static { v0, v5, v2 }, Lcom/project7/localmanager/BsonLite;->skipValue(Ljava/nio/ByteBuffer;II)Z
    move-result v8
    if-eqz v8, :L3
  .line 1478
    invoke-virtual { v0 }, Ljava/nio/ByteBuffer;->position()I
    move-result v8
  .line 1479
    invoke-virtual { p1, v6 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v9
    if-eqz v9, :L1
  .line 1480
    invoke-virtual { v1, p2 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1481
    invoke-static { v1, v6 }, Lcom/project7/localmanager/BsonLite;->writeCString(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 1482
    array-length v4, p3
    invoke-virtual { v1, p3, v3, v4 }, Ljava/io/ByteArrayOutputStream;->write([BII)V
  .line 1483
    const/4 v4, 1
    goto :L2
  :L1
  .line 1485
    invoke-virtual { v1, v5 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1486
    invoke-static { v1, v6 }, Lcom/project7/localmanager/BsonLite;->writeCString(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 1487
    sub-int/2addr v8, v7
    invoke-virtual { v1, p0, v7, v8 }, Ljava/io/ByteArrayOutputStream;->write([BII)V
  :L2
  .line 1489
    goto :L0
  :L3
  .line 1476
    new-instance p0, Ljava/lang/IllegalArgumentException;
    new-instance p1, Ljava/lang/StringBuilder;
    invoke-direct { p1 }, Ljava/lang/StringBuilder;-><init>()V
    const-string p2, "unsupported BSON value type "
    invoke-virtual { p1, p2 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual { p1, v5 }, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    invoke-virtual { p1 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p1
    invoke-direct { p0, p1 }, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V
    throw p0
  :L4
  .line 1472
    new-instance p0, Ljava/lang/IllegalArgumentException;
    const-string p1, "truncated BSON key"
    invoke-direct { p0, p1 }, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V
    throw p0
  :L5
  .line 1490
    if-nez v4, :L6
  .line 1491
    invoke-virtual { v1, p2 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1492
    invoke-static { v1, p1 }, Lcom/project7/localmanager/BsonLite;->writeCString(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 1493
    array-length p0, p3
    invoke-virtual { v1, p3, v3, p0 }, Ljava/io/ByteArrayOutputStream;->write([BII)V
  :L6
  .line 1495
    invoke-static { v1 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
  :L7
  .line 1463
    new-instance p0, Ljava/lang/IllegalArgumentException;
    const-string p1, "invalid BSON document length"
    invoke-direct { p0, p1 }, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V
    throw p0
  :L8
  .line 1458
    new-instance p0, Ljava/lang/IllegalArgumentException;
    const-string p1, "invalid BSON document"
    invoke-direct { p0, p1 }, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V
    throw p0
.end method

.method private static skipCString(Ljava/nio/ByteBuffer;I)Z
  .registers 3
  :L0
  .line 1434
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->position()I
    move-result v0
    if-ge v0, p1, :L1
  .line 1435
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->get()B
    move-result v0
    if-nez v0, :L0
  .line 1436
    const/4 p0, 1
    return p0
  :L1
  .line 1439
    const/4 p0, 0
    return p0
.end method

.method private static skipValue(Ljava/nio/ByteBuffer;II)Z
  .registers 6
  .line 1375
    nop
  .line 1376
    const/4 v0, 1
    const/4 v1, 4
    const/4 v2, 0
    sparse-switch p1, :L17
  .line 1424
    return v2
  :L0
  .line 1393
    const/16 v1, 16
  .line 1394
    goto :L15
  :L1
  .line 1390
    nop
  .line 1391
    goto :L15
  :L2
  .line 1417
    invoke-static { p0, p2 }, Lcom/project7/localmanager/BsonLite;->skipCString(Ljava/nio/ByteBuffer;I)Z
    move-result p1
    if-eqz p1, :L3
    invoke-static { p0, p2 }, Lcom/project7/localmanager/BsonLite;->skipCString(Ljava/nio/ByteBuffer;I)Z
    move-result p0
    if-eqz p0, :L3
    goto :L4
  :L3
    move v0, v2
  :L4
    return v0
  :L5
  .line 1421
    nop
  .line 1422
    move v1, v2
    goto :L15
  :L6
  .line 1387
    nop
  .line 1388
    move v1, v0
    goto :L15
  :L7
  .line 1384
    const/16 v1, 12
  .line 1385
    goto :L15
  :L8
  .line 1411
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->remaining()I
    move-result p1
    const/4 p2, 5
    if-ge p1, p2, :L9
  .line 1412
    return v2
  :L9
  .line 1414
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->position()I
    move-result p1
    invoke-virtual { p0, p1 }, Ljava/nio/ByteBuffer;->getInt(I)I
    move-result p1
    add-int/lit8 v1, p1, 5
  .line 1415
    goto :L15
  :L10
  .line 1405
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->remaining()I
    move-result p1
    if-ge p1, v1, :L11
  .line 1406
    return v2
  :L11
  .line 1408
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->position()I
    move-result p1
    invoke-virtual { p0, p1 }, Ljava/nio/ByteBuffer;->getInt(I)I
    move-result v1
  .line 1409
    goto :L15
  :L12
  .line 1398
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->remaining()I
    move-result p1
    if-ge p1, v1, :L13
  .line 1399
    return v2
  :L13
  .line 1401
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->position()I
    move-result p1
    invoke-virtual { p0, p1 }, Ljava/nio/ByteBuffer;->getInt(I)I
    move-result p1
    add-int/2addr v1, p1
  .line 1402
    goto :L15
  :L14
  .line 1381
    const/16 v1, 8
  .line 1382
    nop
  :L15
  .line 1426
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->remaining()I
    move-result p1
    if-le v1, p1, :L16
  .line 1427
    return v2
  :L16
  .line 1429
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->position()I
    move-result p1
    add-int/2addr p1, v1
    invoke-virtual { p0, p1 }, Ljava/nio/ByteBuffer;->position(I)Ljava/nio/Buffer;
    move-result-object p0
    check-cast p0, Ljava/nio/ByteBuffer;
  .line 1430
    return v0
  :L17
  .sparse-switch
    1 -> :L14
    2 -> :L12
    3 -> :L10
    4 -> :L10
    5 -> :L8
    7 -> :L7
    8 -> :L6
    9 -> :L14
    10 -> :L5
    11 -> :L2
    13 -> :L12
    14 -> :L12
    16 -> :L1
    17 -> :L14
    18 -> :L14
    19 -> :L0
    127 -> :L5
    255 -> :L5
  .end sparse-switch
.end method

.method static statusSwitchReplyDocument(Ljava/lang/String;)[B
  .registers 4
  .line 140
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 141
    const-string v1, "r"
    const-string v2, "ok"
    invoke-static { v0, v1, v2 }, Lcom/project7/localmanager/BsonLite;->writeStringElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/String;)V
  .line 142
    const-string v1, "s"
    invoke-static { v0, v1, p0 }, Lcom/project7/localmanager/BsonLite;->writeStringElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/String;)V
  .line 143
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method private static stringBytes(Ljava/lang/String;)[B
  .registers 4
  .line 1499
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 1500
    sget-object v1, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;
    invoke-virtual { p0, v1 }, Ljava/lang/String;->getBytes(Ljava/nio/charset/Charset;)[B
    move-result-object p0
  .line 1501
    array-length v1, p0
    add-int/lit8 v1, v1, 1
    invoke-static { v0, v1 }, Lcom/project7/localmanager/BsonLite;->writeLeInt(Ljava/io/ByteArrayOutputStream;I)V
  .line 1502
    array-length v1, p0
    const/4 v2, 0
    invoke-virtual { v0, p0, v2, v1 }, Ljava/io/ByteArrayOutputStream;->write([BII)V
  .line 1503
    invoke-virtual { v0, v2 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1504
    invoke-virtual { v0 }, Ljava/io/ByteArrayOutputStream;->toByteArray()[B
    move-result-object p0
    return-object p0
.end method

.method static stringDocument(Ljava/lang/String;Ljava/lang/String;)[B
  .registers 3
  .line 679
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 680
    if-nez p1, :L0
    const-string p1, ""
  :L0
    invoke-static { v0, p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeStringElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/String;)V
  .line 681
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method static stringValue([BLjava/lang/String;)Ljava/lang/String;
  .registers 5
  .line 20
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->findElement([BLjava/lang/String;)Lcom/project7/localmanager/BsonLite$Element;
    move-result-object p0
  .line 21
    const/4 p1, 0
    if-eqz p0, :L3
    iget v0, p0, Lcom/project7/localmanager/BsonLite$Element;->type:I
    const/4 v1, 2
    if-ne v0, v1, :L3
    iget-object v0, p0, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    array-length v0, v0
    const/4 v1, 5
    if-ge v0, v1, :L0
    goto :L3
  :L0
  .line 24
    iget-object p0, p0, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    invoke-static { p0 }, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;
    move-result-object p0
    sget-object v0, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { p0, v0 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object p0
  .line 25
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result v0
  .line 26
    const/4 v1, 1
    if-lt v0, v1, :L2
    invoke-virtual { p0 }, Ljava/nio/ByteBuffer;->remaining()I
    move-result v2
    if-le v0, v2, :L1
    goto :L2
  :L1
  .line 29
    sub-int/2addr v0, v1
    new-array p1, v0, [B
  .line 30
    invoke-virtual { p0, p1 }, Ljava/nio/ByteBuffer;->get([B)Ljava/nio/ByteBuffer;
  .line 31
    new-instance p0, Ljava/lang/String;
    sget-object v0, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;
    invoke-direct { p0, p1, v0 }, Ljava/lang/String;-><init>([BLjava/nio/charset/Charset;)V
    return-object p0
  :L2
  .line 27
    return-object p1
  :L3
  .line 22
    return-object p1
.end method

.method static uuidValue([BLjava/lang/String;)Ljava/lang/String;
  .registers 8
  .line 865
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->findElement([BLjava/lang/String;)Lcom/project7/localmanager/BsonLite$Element;
    move-result-object v0
  .line 866
    if-eqz v0, :L2
    iget v1, v0, Lcom/project7/localmanager/BsonLite$Element;->type:I
    const/4 v2, 7
    if-ne v1, v2, :L2
    iget-object v1, v0, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    array-length v1, v1
    const/16 v2, 12
    if-ne v1, v2, :L2
  .line 867
    new-instance p0, Ljava/lang/StringBuilder;
    invoke-direct { p0 }, Ljava/lang/StringBuilder;-><init>()V
  .line 868
    iget-object p1, v0, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    array-length v0, p1
    const/4 v1, 0
    move v2, v1
  :L0
    if-ge v2, v0, :L1
    aget-byte v3, p1, v2
    sget-object v4, Ljava/util/Locale;->ROOT:Ljava/util/Locale;
    const/4 v5, 1
    new-array v5, v5, [Ljava/lang/Object;
    and-int/lit16 v3, v3, 255
    invoke-static { v3 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v3
    aput-object v3, v5, v1
    const-string v3, "%02x"
    invoke-static { v4, v3, v5 }, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;
    move-result-object v3
    invoke-virtual { p0, v3 }, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    add-int/lit8 v2, v2, 1
    goto :L0
  :L1
  .line 869
    invoke-virtual { p0 }, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p0
    return-object p0
  :L2
  .line 871
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->stringValue([BLjava/lang/String;)Ljava/lang/String;
    move-result-object p0
  .line 872
    if-eqz p0, :L3
    const-string p1, "[0-9a-fA-F]{24}"
    invoke-virtual { p0, p1 }, Ljava/lang/String;->matches(Ljava/lang/String;)Z
    move-result p1
    if-eqz p1, :L3
    sget-object p1, Ljava/util/Locale;->ROOT:Ljava/util/Locale;
    invoke-virtual { p0, p1 }, Ljava/lang/String;->toLowerCase(Ljava/util/Locale;)Ljava/lang/String;
    move-result-object p0
    goto :L4
  :L3
    const/4 p0, 0
  :L4
    return-object p0
.end method

.method static withAccountCredentials([BLjava/lang/String;I)[B
  .registers 6
  .line 769
    nop
  .line 770
    invoke-static { p1 }, Lcom/project7/localmanager/BsonLite;->stringBytes(Ljava/lang/String;)[B
    move-result-object v0
    const-string v1, "an"
    const/4 v2, 2
    invoke-static { p0, v1, v2, v0 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
  .line 771
    invoke-static { p1 }, Lcom/project7/localmanager/BsonLite;->stringBytes(Ljava/lang/String;)[B
    move-result-object p1
    const-string v0, "account"
    invoke-static { p0, v0, v2, p1 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
  .line 772
    invoke-static { p2 }, Lcom/project7/localmanager/BsonLite;->intBytes(I)[B
    move-result-object p1
    const-string p2, "st"
    const/16 v0, 16
    invoke-static { p0, p2, v0, p1 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
    return-object p0
.end method

.method static withAccountIdentity([BLjava/lang/String;I)[B
  .registers 6
  .line 764
    invoke-static { p1 }, Lcom/project7/localmanager/BsonLite;->stringBytes(Ljava/lang/String;)[B
    move-result-object v0
    const-string v1, "name"
    const/4 v2, 2
    invoke-static { p0, v1, v2, v0 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
  .line 765
    invoke-static { p0, p1, p2 }, Lcom/project7/localmanager/BsonLite;->withAccountCredentials([BLjava/lang/String;I)[B
    move-result-object p0
    return-object p0
.end method

.method static withCanonicalHeroPairs([B)[B
  .registers 20
  .line 1005
    move-object/from16 v0, p0
    const-string v1, "heromgr"
    invoke-static { v0, v1 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v2
  .line 1006
    if-nez v2, :L0
    return-object v0
  :L0
  .line 1007
    nop
  .line 1008
    const/4 v3, 2
    const-string v4, "hrs"
    const-string v5, "bhrs"
    filled-new-array { v4, v5 }, [Ljava/lang/String;
    move-result-object v4
    move-object v7, v2
    const/4 v6, 0
  :L1
    if-ge v6, v3, :L12
    aget-object v8, v4, v6
  .line 1009
    invoke-static { v2, v8 }, Lcom/project7/localmanager/BsonLite;->findElement([BLjava/lang/String;)Lcom/project7/localmanager/BsonLite$Element;
    move-result-object v9
  .line 1010
    if-eqz v9, :L10
    iget v10, v9, Lcom/project7/localmanager/BsonLite$Element;->type:I
    const/4 v11, 4
    if-eq v10, v11, :L2
    move-object/from16 v17, v4
    goto/16 :L11
  :L2
  .line 1011
    new-instance v10, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v10 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 1012
    iget-object v12, v9, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    invoke-static { v12 }, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;
    move-result-object v12
    sget-object v13, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { v12, v13 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object v12
  .line 1013
    invoke-virtual { v12 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result v13
    const/4 v15, 0
  :L3
  .line 1014
    invoke-virtual { v12 }, Ljava/nio/ByteBuffer;->position()I
    move-result v3
    add-int/lit8 v5, v13, -1
    if-ge v3, v5, :L9
  .line 1015
    invoke-virtual { v12 }, Ljava/nio/ByteBuffer;->position()I
    move-result v3
    invoke-virtual { v12 }, Ljava/nio/ByteBuffer;->get()B
    move-result v5
    and-int/lit16 v5, v5, 255
  .line 1016
    invoke-static { v12, v13 }, Lcom/project7/localmanager/BsonLite;->readCString(Ljava/nio/ByteBuffer;I)Ljava/lang/String;
    move-result-object v16
    invoke-virtual { v12 }, Ljava/nio/ByteBuffer;->position()I
    move-result v14
  .line 1017
    if-eqz v16, :L8
    invoke-static { v12, v5, v13 }, Lcom/project7/localmanager/BsonLite;->skipValue(Ljava/nio/ByteBuffer;II)Z
    move-result v16
    if-eqz v16, :L8
  .line 1018
    const/4 v11, 3
    if-ne v5, v11, :L6
  .line 1019
    iget-object v5, v9, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    invoke-virtual { v12 }, Ljava/nio/ByteBuffer;->position()I
    move-result v11
    invoke-static { v5, v14, v11 }, Ljava/util/Arrays;->copyOfRange([BII)[B
    move-result-object v5
  .line 1020
    const-string v11, "0"
    invoke-static { v5, v11 }, Lcom/project7/localmanager/BsonLite;->findElement([BLjava/lang/String;)Lcom/project7/localmanager/BsonLite$Element;
    move-result-object v14
    move-object/from16 v17, v4
    const-string v4, "1"
    move/from16 v18, v13
    invoke-static { v5, v4 }, Lcom/project7/localmanager/BsonLite;->findElement([BLjava/lang/String;)Lcom/project7/localmanager/BsonLite$Element;
    move-result-object v13
  .line 1021
    invoke-static { v5 }, Lcom/project7/localmanager/BsonLite;->keys([B)Ljava/util/List;
    move-result-object v0
    filled-new-array { v11, v4 }, [Ljava/lang/String;
    move-result-object v4
    invoke-static { v4 }, Ljava/util/Arrays;->asList([Ljava/lang/Object;)Ljava/util/List;
    move-result-object v4
    invoke-interface { v0, v4 }, Ljava/util/List;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :L5
    if-eqz v14, :L5
    iget v0, v14, Lcom/project7/localmanager/BsonLite$Element;->type:I
    const/16 v4, 16
    if-ne v0, v4, :L5
  .line 1022
    invoke-static { v5, v11 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v0
    invoke-virtual { v0 }, Ljava/lang/Integer;->intValue()I
    move-result v0
    if-lez v0, :L4
    if-eqz v13, :L4
    iget v0, v13, Lcom/project7/localmanager/BsonLite$Element;->type:I
    const/4 v4, 3
    if-ne v0, v4, :L4
  .line 1023
    const/4 v0, 4
    invoke-virtual { v10, v0 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1024
    iget-object v0, v9, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    add-int/lit8 v4, v3, 1
    invoke-virtual { v12 }, Ljava/nio/ByteBuffer;->position()I
    move-result v5
    sub-int/2addr v5, v3
    const/4 v11, 1
    sub-int/2addr v5, v11
    invoke-virtual { v10, v0, v4, v5 }, Ljava/io/ByteArrayOutputStream;->write([BII)V
  .line 1025
    const/4 v3, 2
    move-object/from16 v0, p0
    move v15, v11
    move-object/from16 v4, v17
    move/from16 v13, v18
    const/4 v11, 4
    goto/16 :L3
  :L4
  .line 1022
    const/4 v11, 1
    goto :L7
  :L5
  .line 1021
    const/4 v11, 1
    goto :L7
  :L6
  .line 1018
    move-object/from16 v17, v4
    move/from16 v18, v13
    const/4 v11, 1
  :L7
  .line 1028
    iget-object v0, v9, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    invoke-virtual { v12 }, Ljava/nio/ByteBuffer;->position()I
    move-result v4
    sub-int/2addr v4, v3
    invoke-virtual { v10, v0, v3, v4 }, Ljava/io/ByteArrayOutputStream;->write([BII)V
  .line 1029
    const/4 v3, 2
    const/4 v11, 4
    move-object/from16 v0, p0
    move-object/from16 v4, v17
    move/from16 v13, v18
    goto/16 :L3
  :L8
  .line 1017
    new-instance v0, Ljava/lang/IllegalArgumentException;
    const-string v1, "invalid hero population BSON"
    invoke-direct { v0, v1 }, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V
    throw v0
  :L9
  .line 1030
    move-object/from16 v17, v4
    if-eqz v15, :L11
    invoke-static { v10 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object v0
    const/4 v3, 4
    invoke-static { v7, v8, v3, v0 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v7
    goto :L11
  :L10
  .line 1010
    move-object/from16 v17, v4
  :L11
  .line 1008
    add-int/lit8 v6, v6, 1
    const/4 v3, 2
    move-object/from16 v0, p0
    move-object/from16 v4, v17
    goto/16 :L1
  :L12
  .line 1032
    move-object/from16 v0, p0
    if-ne v7, v2, :L13
    goto :L14
  :L13
    invoke-static { v0, v1, v7 }, Lcom/project7/localmanager/BsonLite;->withProfileDocument([BLjava/lang/String;[B)[B
    move-result-object v0
  :L14
    return-object v0
.end method

.method static withCopiedValue([BLjava/lang/String;[BLjava/lang/String;)[B
  .registers 4
  .line 798
    invoke-static { p2, p3 }, Lcom/project7/localmanager/BsonLite;->findElement([BLjava/lang/String;)Lcom/project7/localmanager/BsonLite$Element;
    move-result-object p2
  .line 799
    if-eqz p2, :L0
  .line 800
    iget p3, p2, Lcom/project7/localmanager/BsonLite$Element;->type:I
    iget-object p2, p2, Lcom/project7/localmanager/BsonLite$Element;->value:[B
    invoke-static { p0, p1, p3, p2 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
    return-object p0
  :L0
  .line 799
    new-instance p0, Ljava/lang/IllegalArgumentException;
    const-string p1, "missing BSON source value"
    invoke-direct { p0, p1 }, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V
    throw p0
.end method

.method static withHero([BI)[B
  .registers 23
  .line 1096
    move-object/from16 v0, p0
    const-string v1, "heromgr"
    invoke-static { v0, v1 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v2
  .line 1097
    if-nez v2, :L0
  .line 1098
    sget-object v2, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
  :L0
  .line 1100
    const-string v3, "hrs"
    invoke-static { v2, v3 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v4
  .line 1101
    if-nez v4, :L1
  .line 1102
    sget-object v4, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
  :L1
  .line 1104
    const/4 v6, 0
  :L2
  .line 1106
    invoke-static { v6 }, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object v7
    invoke-static { v4, v7 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v7
  .line 1107
    const-string v8, "0"
    if-nez v7, :L10
  .line 1108
    nop
  .line 1116
    new-instance v7, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v7 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 1117
    move/from16 v9, p1
    invoke-static { v7, v8, v9 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 1118
    invoke-static/range { p1 .. p1 }, Lcom/project7/localmanager/BsonLite;->heroDataDocument(I)[B
    move-result-object v8
  .line 1119
    const-string v10, "ps"
    invoke-static { v2, v10 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v11
  .line 1120
    invoke-static/range { p1 .. p1 }, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object v12
    invoke-static { v11, v12 }, Lcom/project7/localmanager/BsonLite;->intArrayValues([BLjava/lang/String;)Ljava/util/List;
    move-result-object v12
  .line 1121
    invoke-interface { v12 }, Ljava/util/List;->isEmpty()Z
    move-result v13
    if-nez v13, :L5
  .line 1122
    const-string v13, "sk"
    invoke-static { v8, v13 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v14
  .line 1123
    invoke-interface { v12 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v12
  :L3
    invoke-interface { v12 }, Ljava/util/Iterator;->hasNext()Z
    move-result v15
    if-eqz v15, :L4
    invoke-interface { v12 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v15
    check-cast v15, Ljava/lang/Integer;
    invoke-virtual { v15 }, Ljava/lang/Integer;->intValue()I
    move-result v15
  .line 1124
    invoke-static { }, Ljava/util/UUID;->randomUUID()Ljava/util/UUID;
    move-result-object v16
    invoke-virtual/range { v16 .. v16 }, Ljava/util/UUID;->toString()Ljava/lang/String;
    move-result-object v5
    const-string v9, "-"
    move-object/from16 v16, v12
    const-string v12, ""
    invoke-virtual { v5, v9, v12 }, Ljava/lang/String;->replace(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Ljava/lang/String;
    move-result-object v5
    const/16 v9, 24
    const/4 v12, 0
    invoke-virtual { v5, v12, v9 }, Ljava/lang/String;->substring(II)Ljava/lang/String;
    move-result-object v5
  .line 1125
    nop
  .line 1126
    invoke-static { }, Ljava/lang/System;->currentTimeMillis()J
    move-result-wide v17
    const-wide/16 v19, 1000
    move-object v9, v13
    div-long v12, v17, v19
  .line 1125
    invoke-static { v15, v5, v12, v13 }, Lcom/project7/localmanager/LocalCommerceEngine;->purchasedSkin(ILjava/lang/String;J)[B
    move-result-object v12
    invoke-static { v14, v5, v12 }, Lcom/project7/localmanager/BsonLite;->withProfileDocument([BLjava/lang/String;[B)[B
    move-result-object v14
  .line 1127
    move-object v13, v9
    move-object/from16 v12, v16
    move/from16 v9, p1
    goto :L3
  :L4
  .line 1128
    move-object v9, v13
    invoke-static { v8, v9, v14 }, Lcom/project7/localmanager/BsonLite;->withProfileDocument([BLjava/lang/String;[B)[B
    move-result-object v8
  .line 1129
    nop
  .line 1130
    invoke-static/range { p1 .. p1 }, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object v5
    invoke-static { }, Ljava/util/Collections;->emptyList()Ljava/util/List;
    move-result-object v9
  .line 1129
    invoke-static { v11, v5, v9 }, Lcom/project7/localmanager/BsonLite;->withProfileArray([BLjava/lang/String;Ljava/util/List;)[B
    move-result-object v5
    invoke-static { v2, v10, v5 }, Lcom/project7/localmanager/BsonLite;->withProfileDocument([BLjava/lang/String;[B)[B
    move-result-object v2
  :L5
  .line 1132
    invoke-static/range { p1 .. p1 }, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object v5
  .line 1133
    const-string v9, "pp"
    invoke-static { v2, v9 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v10
  .line 1134
    invoke-static { v10, v5 }, Lcom/project7/localmanager/BsonLite;->intArrayValues([BLjava/lang/String;)Ljava/util/List;
    move-result-object v11
  .line 1135
    invoke-interface { v11 }, Ljava/util/List;->isEmpty()Z
    move-result v12
    if-nez v12, :L8
  .line 1136
    const-string v12, "pa"
    invoke-static { v8, v12, v11 }, Lcom/project7/localmanager/BsonLite;->withProfileIntArray([BLjava/lang/String;Ljava/lang/Iterable;)[B
    move-result-object v8
  .line 1137
    const-string v11, "ppc"
    invoke-static { v2, v11 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v12
    invoke-static { v12, v5 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v12
  .line 1138
    new-instance v13, Ljava/util/ArrayList;
    invoke-direct { v13 }, Ljava/util/ArrayList;-><init>()V
  .line 1139
    invoke-static { v12 }, Lcom/project7/localmanager/LocalResourceEngine;->array([B)Ljava/util/List;
    move-result-object v12
    invoke-interface { v12 }, Ljava/util/List;->iterator()Ljava/util/Iterator;
    move-result-object v12
  :L6
    invoke-interface { v12 }, Ljava/util/Iterator;->hasNext()Z
    move-result v14
    if-eqz v14, :L7
    invoke-interface { v12 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v14
    check-cast v14, [B
    new-instance v15, Lcom/project7/localmanager/BsonLite$ArrayValue;
    invoke-direct { v15, v14 }, Lcom/project7/localmanager/BsonLite$ArrayValue;-><init>([B)V
    invoke-interface { v13, v15 }, Ljava/util/List;->add(Ljava/lang/Object;)Z
    goto :L6
  :L7
  .line 1140
    const-string v12, "pat"
    invoke-static { v8, v12, v13 }, Lcom/project7/localmanager/BsonLite;->withProfileArray([BLjava/lang/String;Ljava/util/List;)[B
    move-result-object v8
  .line 1141
    invoke-static { v10, v5 }, Lcom/project7/localmanager/BsonLite;->withoutProfileKey([BLjava/lang/String;)[B
    move-result-object v10
    invoke-static { v2, v9, v10 }, Lcom/project7/localmanager/BsonLite;->withProfileDocument([BLjava/lang/String;[B)[B
    move-result-object v2
  .line 1142
    invoke-static { v2, v11 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v9
    invoke-static { v9, v5 }, Lcom/project7/localmanager/BsonLite;->withoutProfileKey([BLjava/lang/String;)[B
    move-result-object v5
    invoke-static { v2, v11, v5 }, Lcom/project7/localmanager/BsonLite;->withProfileDocument([BLjava/lang/String;[B)[B
    move-result-object v2
  :L8
  .line 1144
    const-string v5, "1"
    invoke-static { v7, v5, v8 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 1145
    nop
  .line 1147
    invoke-static { v6 }, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object v5
  .line 1149
    invoke-static { v7 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object v6
  .line 1145
    const/4 v7, 4
    invoke-static { v4, v5, v7, v6 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v4
  .line 1151
    invoke-static { v2, v3, v7, v4 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v2
  .line 1152
    const-string v3, "cfs"
    invoke-static { v2, v3 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v4
    const/4 v5, 3
    if-nez v4, :L9
  .line 1153
    sget-object v4, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    invoke-static { v2, v3, v5, v4 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v2
  :L9
  .line 1155
    invoke-static { v0, v1, v5, v2 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v0
    return-object v0
  :L10
  .line 1110
    invoke-static/range { p1 .. p1 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v5
    invoke-static { v7, v8 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v7
    invoke-virtual { v5, v7 }, Ljava/lang/Integer;->equals(Ljava/lang/Object;)Z
    move-result v5
    if-eqz v5, :L11
  .line 1111
    return-object v0
  :L11
  .line 1113
    add-int/lit8 v6, v6, 1
  .line 1114
    goto/16 :L2
.end method

.method static withHeroDocument([BI[B)[B
  .registers 12
  .line 909
    const-string v0, "heromgr"
    invoke-static { p0, v0 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v1
  .line 910
    const-string v2, "hrs"
    invoke-static { v1, v2 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v3
  .line 911
    invoke-static { v3 }, Lcom/project7/localmanager/BsonLite;->documentEntries([B)Ljava/util/Map;
    move-result-object v4
    invoke-interface { v4 }, Ljava/util/Map;->entrySet()Ljava/util/Set;
    move-result-object v4
    invoke-interface { v4 }, Ljava/util/Set;->iterator()Ljava/util/Iterator;
    move-result-object v4
  :L0
    invoke-interface { v4 }, Ljava/util/Iterator;->hasNext()Z
    move-result v5
    if-eqz v5, :L2
    invoke-interface { v4 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v5
    check-cast v5, Ljava/util/Map$Entry;
  .line 912
    invoke-interface { v5 }, Ljava/util/Map$Entry;->getKey()Ljava/lang/Object;
    move-result-object v6
    check-cast v6, Ljava/lang/String;
  .line 913
    invoke-interface { v5 }, Ljava/util/Map$Entry;->getValue()Ljava/lang/Object;
    move-result-object v5
    check-cast v5, [B
  .line 914
    invoke-static { p1 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v7
    const-string v8, "0"
    invoke-static { v5, v8 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v8
    invoke-virtual { v7, v8 }, Ljava/lang/Integer;->equals(Ljava/lang/Object;)Z
    move-result v7
    if-eqz v7, :L1
  .line 915
    const/4 p1, 3
    const-string v4, "1"
    invoke-static { v5, v4, p1, p2 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p1
  .line 916
    const/4 p2, 4
    invoke-static { v3, v6, p2, p1 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p1
  .line 917
    nop
  .line 918
    invoke-static { v1, v2, p2, p1 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p1
  .line 917
    invoke-static { p0, v0, p1 }, Lcom/project7/localmanager/BsonLite;->withProfileDocument([BLjava/lang/String;[B)[B
    move-result-object p0
    return-object p0
  :L1
  .line 920
    goto :L0
  :L2
  .line 921
    new-instance p0, Ljava/lang/IllegalArgumentException;
    const-string p1, "hero is not owned"
    invoke-direct { p0, p1 }, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V
    throw p0
.end method

.method static withLocalCityState([BLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
  .registers 11
  .line 415
    if-eqz p1, :L5
    iget-object v0, p1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->completedEvents:Ljava/util/Set;
    const/16 v1, 1004
    invoke-static { v1 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object v1
    invoke-interface { v0, v1 }, Ljava/util/Set;->contains(Ljava/lang/Object;)Z
    move-result v0
    if-nez v0, :L0
    goto :L5
  :L0
  .line 418
    const-string v0, "city"
    invoke-static { p0, v0 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v1
  .line 419
    if-nez v1, :L1
  .line 420
    sget-object v1, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
  :L1
  .line 422
    const/4 v2, 1
    invoke-static { v2, p1, p0 }, Lcom/project7/localmanager/BsonLite;->persistedAreas(ZLcom/project7/localmanager/LocalTutorialStore$Progress;[B)[B
    move-result-object v2
    const-string v3, "areas"
    const/4 v4, 3
    invoke-static { v1, v3, v4, v2 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v1
  .line 423
    invoke-static { p1 }, Lcom/project7/localmanager/BsonLite;->cityValuesDocument(Lcom/project7/localmanager/LocalTutorialStore$Progress;)[B
    move-result-object p1
  .line 424
    const/4 v2, 2
    const-string v3, "av"
    const-string v5, "pn"
    filled-new-array { v3, v5 }, [Ljava/lang/String;
    move-result-object v3
    const/4 v5, 0
  :L2
    if-ge v5, v2, :L4
    aget-object v6, v3, v5
  .line 425
    invoke-static { p1, v6 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v7
  .line 426
    if-eqz v7, :L3
  .line 427
    const/16 v8, 16
    invoke-virtual { v7 }, Ljava/lang/Integer;->intValue()I
    move-result v7
    invoke-static { v7 }, Lcom/project7/localmanager/BsonLite;->intBytes(I)[B
    move-result-object v7
    invoke-static { v1, v6, v8, v7 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v1
  :L3
  .line 424
    add-int/lit8 v5, v5, 1
    goto :L2
  :L4
  .line 430
    invoke-static { p0, v0, v4, v1 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
    return-object p0
  :L5
  .line 416
    return-object p0
.end method

.method static withPatrolProgress([BLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
  .registers 19
  .line 572
    move-object/from16 v0, p0
    move-object/from16 v1, p1
    if-nez v1, :L0
    return-object v0
  :L0
  .line 573
    iget v2, v1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->sandglassActions:I
    if-ltz v2, :L1
  .line 574
    const-string v2, "weeknum"
    invoke-static { v0, v2 }, Lcom/project7/localmanager/LocalResourceEngine;->doc([BLjava/lang/String;)[B
    move-result-object v3
    iget v4, v1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->sandglassActions:I
    const-string v5, "sgw"
    invoke-static { v3, v5, v4 }, Lcom/project7/localmanager/BsonLite;->withProfileInt([BLjava/lang/String;I)[B
    move-result-object v3
  .line 573
    invoke-static { v0, v2, v3 }, Lcom/project7/localmanager/BsonLite;->withProfileDocument([BLjava/lang/String;[B)[B
    move-result-object v0
  :L1
  .line 575
    const-string v2, "heromgr"
    invoke-static { v0, v2 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v3
  .line 576
    const-string v4, "hrs"
    invoke-static { v3, v4 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v5
  .line 577
    if-eqz v5, :L10
    iget-object v9, v1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolFatigue:Ljava/util/Map;
    invoke-interface { v9 }, Ljava/util/Map;->isEmpty()Z
    move-result v9
    if-eqz v9, :L2
    iget-object v9, v1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolFriendly:Ljava/util/Map;
    invoke-interface { v9 }, Ljava/util/Map;->isEmpty()Z
    move-result v9
    if-nez v9, :L10
  :L2
  .line 580
    new-instance v9, Ljava/io/ByteArrayOutputStream;
    array-length v10, v5
    invoke-direct { v9, v10 }, Ljava/io/ByteArrayOutputStream;-><init>(I)V
  .line 581
    nop
  .line 582
    invoke-static { v5 }, Lcom/project7/localmanager/BsonLite;->documentEntries([B)Ljava/util/Map;
    move-result-object v5
    invoke-interface { v5 }, Ljava/util/Map;->entrySet()Ljava/util/Set;
    move-result-object v5
    invoke-interface { v5 }, Ljava/util/Set;->iterator()Ljava/util/Iterator;
    move-result-object v5
    const/4 v11, 0
  :L3
    invoke-interface { v5 }, Ljava/util/Iterator;->hasNext()Z
    move-result v12
    if-eqz v12, :L9
    invoke-interface { v5 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v12
    check-cast v12, Ljava/util/Map$Entry;
  .line 583
    invoke-interface { v12 }, Ljava/util/Map$Entry;->getKey()Ljava/lang/Object;
    move-result-object v14
    check-cast v14, Ljava/lang/String;
  .line 584
    invoke-interface { v12 }, Ljava/util/Map$Entry;->getValue()Ljava/lang/Object;
    move-result-object v12
    check-cast v12, [B
  .line 585
    const-string v15, "0"
    invoke-static { v12, v15 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v15
  .line 586
    const-string v6, "1"
    invoke-static { v12, v6 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v10
  .line 587
    nop
  .line 588
    if-eqz v10, :L4
    iget-object v13, v1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolFatigue:Ljava/util/Map;
    invoke-interface { v13, v15 }, Ljava/util/Map;->containsKey(Ljava/lang/Object;)Z
    move-result v13
    if-eqz v13, :L4
  .line 589
    const-string v13, "cf"
    invoke-static { v10, v13 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v7
    iget-object v8, v1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolFatigue:Ljava/util/Map;
    invoke-interface { v8, v15 }, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v8
    invoke-static { v7, v8 }, Ljava/util/Objects;->equals(Ljava/lang/Object;Ljava/lang/Object;)Z
    move-result v7
    if-nez v7, :L4
  .line 590
    iget-object v7, v1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolFatigue:Ljava/util/Map;
    invoke-interface { v7, v15 }, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v7
    check-cast v7, Ljava/lang/Integer;
    invoke-virtual { v7 }, Ljava/lang/Integer;->intValue()I
    move-result v7
    invoke-static { v7 }, Lcom/project7/localmanager/BsonLite;->intBytes(I)[B
    move-result-object v7
    const/16 v8, 16
    invoke-static { v10, v13, v8, v7 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v7
    goto :L5
  :L4
  .line 592
    move-object v7, v10
  :L5
    if-eqz v7, :L6
    iget-object v8, v1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolFriendly:Ljava/util/Map;
    invoke-interface { v8, v15 }, Ljava/util/Map;->containsKey(Ljava/lang/Object;)Z
    move-result v8
    if-eqz v8, :L6
  .line 593
    const-string v8, "ef"
    invoke-static { v7, v8 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v13
    move-object/from16 v16, v5
    iget-object v5, v1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolFriendly:Ljava/util/Map;
    invoke-interface { v5, v15 }, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v5
    invoke-static { v13, v5 }, Ljava/util/Objects;->equals(Ljava/lang/Object;Ljava/lang/Object;)Z
    move-result v5
    if-nez v5, :L7
  .line 594
    iget-object v5, v1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolFriendly:Ljava/util/Map;
    invoke-interface { v5, v15 }, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v5
    check-cast v5, Ljava/lang/Integer;
    invoke-virtual { v5 }, Ljava/lang/Integer;->intValue()I
    move-result v5
    invoke-static { v5 }, Lcom/project7/localmanager/BsonLite;->intBytes(I)[B
    move-result-object v5
    const/16 v13, 16
    invoke-static { v7, v8, v13, v5 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v7
    goto :L7
  :L6
  .line 592
    move-object/from16 v16, v5
  :L7
  .line 596
    if-eq v7, v10, :L8
  .line 597
    const/4 v5, 3
    invoke-static { v12, v6, v5, v7 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v12
  .line 598
    const/4 v11, 1
  :L8
  .line 600
    const/4 v5, 4
    invoke-virtual { v9, v5 }, Ljava/io/ByteArrayOutputStream;->write(I)V
    invoke-static { v9, v14 }, Lcom/project7/localmanager/BsonLite;->writeCString(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 601
    array-length v5, v12
    const/4 v6, 0
    invoke-virtual { v9, v12, v6, v5 }, Ljava/io/ByteArrayOutputStream;->write([BII)V
  .line 602
    move-object/from16 v5, v16
    goto/16 :L3
  :L9
  .line 603
    const/4 v5, 4
    if-eqz v11, :L10
  .line 604
    invoke-static { v9 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object v6
    invoke-static { v3, v4, v5, v6 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v3
  .line 605
    const/4 v4, 3
    invoke-static { v0, v2, v4, v3 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v0
  :L10
  .line 608
    iget v2, v1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolActions:I
    if-ltz v2, :L12
  .line 609
    const-string v2, "city"
    invoke-static { v0, v2 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v3
  .line 610
    if-nez v3, :L11
    sget-object v3, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
  :L11
  .line 611
    iget v4, v1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolActions:I
    invoke-static { v4 }, Lcom/project7/localmanager/BsonLite;->intBytes(I)[B
    move-result-object v4
    const-string v5, "av"
    const/16 v6, 16
    invoke-static { v3, v5, v6, v4 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v3
  .line 612
    iget v1, v1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->patrolCount:I
    const/4 v4, 1
    add-int/2addr v1, v4
    invoke-static { v1 }, Lcom/project7/localmanager/BsonLite;->intBytes(I)[B
    move-result-object v1
    const-string v4, "pn"
    invoke-static { v3, v4, v6, v1 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v1
  .line 613
    const/4 v3, 3
    invoke-static { v0, v2, v3, v1 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v0
  :L12
  .line 615
    return-object v0
.end method

.method static withPlayerName([BLjava/lang/String;I)[B
  .registers 5
  .line 997
    invoke-static { p1 }, Lcom/project7/localmanager/BsonLite;->stringBytes(Ljava/lang/String;)[B
    move-result-object p1
    const-string v0, "name"
    const/4 v1, 2
    invoke-static { p0, v0, v1, p1 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
  .line 998
    invoke-static { p2 }, Lcom/project7/localmanager/BsonLite;->intBytes(I)[B
    move-result-object p1
    const-string p2, "st"
    const/16 v0, 16
    invoke-static { p0, p2, v0, p1 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
    return-object p0
.end method

.method static withProfileArray([BLjava/lang/String;Ljava/util/List;)[B
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "([B",
      "Ljava/lang/String;",
      "Ljava/util/List<",
      "*>;)[B"
    }
  .end annotation
  .registers 4
  .line 794
    invoke-static { p2 }, Lcom/project7/localmanager/BsonLite;->listBytes(Ljava/util/List;)[B
    move-result-object p2
    const/4 v0, 4
    invoke-static { p0, p1, v0, p2 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
    return-object p0
.end method

.method static withProfileBool([BLjava/lang/String;Z)[B
  .registers 4
  .line 786
    invoke-static { p2 }, Lcom/project7/localmanager/BsonLite;->boolBytes(Z)[B
    move-result-object p2
    const/16 v0, 8
    invoke-static { p0, p1, v0, p2 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
    return-object p0
.end method

.method static withProfileDocument([BLjava/lang/String;[B)[B
  .registers 4
  .line 790
    const/4 v0, 3
    invoke-static { p0, p1, v0, p2 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
    return-object p0
.end method

.method static withProfileDouble([BLjava/lang/String;D)[B
  .registers 7
  .line 780
    invoke-static { p2, p3 }, Ljava/lang/Double;->isFinite(D)Z
    move-result v0
    if-eqz v0, :L0
  .line 781
    const/4 v0, 1
    const/16 v1, 8
  .line 782
    invoke-static { v1 }, Ljava/nio/ByteBuffer;->allocate(I)Ljava/nio/ByteBuffer;
    move-result-object v1
    sget-object v2, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { v1, v2 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object v1
    invoke-virtual { v1, p2, p3 }, Ljava/nio/ByteBuffer;->putDouble(D)Ljava/nio/ByteBuffer;
    move-result-object p2
    invoke-virtual { p2 }, Ljava/nio/ByteBuffer;->array()[B
    move-result-object p2
  .line 781
    invoke-static { p0, p1, v0, p2 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
    return-object p0
  :L0
  .line 780
    new-instance p0, Ljava/lang/IllegalArgumentException;
    const-string p1, "finite BSON number required"
    invoke-direct { p0, p1 }, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V
    throw p0
.end method

.method static withProfileInt([BLjava/lang/String;I)[B
  .registers 4
  .line 776
    invoke-static { p2 }, Lcom/project7/localmanager/BsonLite;->intBytes(I)[B
    move-result-object p2
    const/16 v0, 16
    invoke-static { p0, p1, v0, p2 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
    return-object p0
.end method

.method static withProfileIntArray([BLjava/lang/String;Ljava/lang/Iterable;)[B
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "([B",
      "Ljava/lang/String;",
      "Ljava/lang/Iterable<",
      "Ljava/lang/Integer;",
      ">;)[B"
    }
  .end annotation
  .registers 4
  .line 977
    invoke-static { p2 }, Lcom/project7/localmanager/BsonLite;->profileIntArrayBytes(Ljava/lang/Iterable;)[B
    move-result-object p2
    const/4 v0, 4
    invoke-static { p0, p1, v0, p2 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
    return-object p0
.end method

.method static withProfileString([BLjava/lang/String;Ljava/lang/String;)[B
  .registers 4
  .line 973
    invoke-static { p2 }, Lcom/project7/localmanager/BsonLite;->stringBytes(Ljava/lang/String;)[B
    move-result-object p2
    const/4 v0, 2
    invoke-static { p0, p1, v0, p2 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
    return-object p0
.end method

.method static withProfileUuid([BLjava/lang/String;Ljava/lang/String;)[B
  .registers 4
  .line 861
    new-instance v0, Lcom/project7/localmanager/BsonLite$UuidValue;
    invoke-direct { v0, p2 }, Lcom/project7/localmanager/BsonLite$UuidValue;-><init>(Ljava/lang/String;)V
    iget-object p2, v0, Lcom/project7/localmanager/BsonLite$UuidValue;->bytes:[B
    const/4 v0, 7
    invoke-static { p0, p1, v0, p2 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
    return-object p0
.end method

.method static withRequiredClientDefaults([B)[B
  .registers 13
  .line 1036
    invoke-static { p0 }, Lcom/project7/localmanager/BsonLite;->withCanonicalHeroPairs([B)[B
    move-result-object p0
  .line 1037
    const-string v0, "city"
    invoke-static { p0, v0 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v1
  .line 1038
    const-string v2, "dvc"
    invoke-static { v1, v2 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v3
    const/4 v4, 0
    if-nez v3, :L1
  .line 1039
    if-nez v1, :L0
    sget-object v1, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
  :L0
    invoke-static { v1, v2, v4 }, Lcom/project7/localmanager/BsonLite;->withProfileInt([BLjava/lang/String;I)[B
    move-result-object v1
  .line 1038
    invoke-static { p0, v0, v1 }, Lcom/project7/localmanager/BsonLite;->withProfileDocument([BLjava/lang/String;[B)[B
    move-result-object p0
  :L1
  .line 1040
    const-string v0, "fnd"
    invoke-static { p0, v0 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v1
  .line 1041
    if-nez v1, :L2
  .line 1042
    sget-object v1, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
  :L2
  .line 1044
    const-string v2, "s"
    invoke-static { v1, v2 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v3
  .line 1045
    if-nez v3, :L3
  .line 1046
    sget-object v3, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
  :L3
  .line 1048
    const-string v5, "player_home"
    invoke-static { v3, v5 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v6
    if-nez v6, :L4
  .line 1049
    new-instance v6, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v6 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 1050
    const-string v7, "cur"
    const-string v8, "local_default"
    invoke-static { v6, v7, v8 }, Lcom/project7/localmanager/BsonLite;->writeStringElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/String;)V
  .line 1051
    nop
  .line 1055
    invoke-static { v6 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object v6
  .line 1051
    const/4 v7, 3
    invoke-static { v3, v5, v7, v6 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v3
  .line 1057
    invoke-static { v1, v2, v7, v3 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v1
  .line 1058
    invoke-static { p0, v0, v7, v1 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
  :L4
  .line 1060
    const-string v0, "heromgr"
    invoke-static { p0, v0 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v0
    const-string v1, "hrs"
    invoke-static { v0, v1 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v0
  .line 1061
    move v1, v4
  :L5
    if-eqz v0, :L14
  .line 1062
    invoke-static { v1 }, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object v2
    invoke-static { v0, v2 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v2
  .line 1063
    if-nez v2, :L6
    goto :L14
  :L6
  .line 1064
    const-string v3, "1"
    invoke-static { v2, v3 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v3
  .line 1065
    const-string v5, "clm"
    invoke-static { v3, v5 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v6
  .line 1066
    if-nez v6, :L7
    goto :L13
  :L7
  .line 1068
    new-instance v7, Ljava/util/ArrayList;
    invoke-direct { v7 }, Ljava/util/ArrayList;-><init>()V
  .line 1069
    move v8, v4
  :L8
    const/16 v9, 19
    if-ge v8, v9, :L12
  .line 1070
    invoke-static { v8 }, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object v9
  .line 1071
    invoke-static { v6, v9 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v10
  .line 1072
    sget-object v11, Ljava/lang/Boolean;->TRUE:Ljava/lang/Boolean;
    invoke-static { v6, v9 }, Lcom/project7/localmanager/BsonLite;->boolValue([BLjava/lang/String;)Ljava/lang/Boolean;
    move-result-object v9
    invoke-virtual { v11, v9 }, Ljava/lang/Boolean;->equals(Ljava/lang/Object;)Z
    move-result v9
    if-nez v9, :L10
    if-eqz v10, :L9
    invoke-virtual { v10 }, Ljava/lang/Integer;->intValue()I
    move-result v9
    if-eqz v9, :L9
    goto :L10
  :L9
    move v9, v4
    goto :L11
  :L10
    const/4 v9, 1
  :L11
    invoke-static { v9 }, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
    move-result-object v9
    invoke-interface { v7, v9 }, Ljava/util/List;->add(Ljava/lang/Object;)Z
  .line 1069
    add-int/lit8 v8, v8, 1
    goto :L8
  :L12
  .line 1074
    invoke-static { v3, v5, v7 }, Lcom/project7/localmanager/BsonLite;->withProfileArray([BLjava/lang/String;Ljava/util/List;)[B
    move-result-object v5
  .line 1075
    invoke-static { v3, v5 }, Ljava/util/Arrays;->equals([B[B)Z
    move-result v3
    if-nez v3, :L13
    const-string v3, "0"
    invoke-static { v2, v3 }, Lcom/project7/localmanager/BsonLite;->intValue([BLjava/lang/String;)Ljava/lang/Integer;
    move-result-object v2
    invoke-virtual { v2 }, Ljava/lang/Integer;->intValue()I
    move-result v2
    invoke-static { p0, v2, v5 }, Lcom/project7/localmanager/BsonLite;->withHeroDocument([BI[B)[B
    move-result-object p0
  :L13
  .line 1061
    add-int/lit8 v1, v1, 1
    goto :L5
  :L14
  .line 1077
    return-object p0
.end method

.method static withTutorialHeroes([BLcom/project7/localmanager/LocalTutorialStore$Progress;Ljava/lang/String;)[B
  .registers 3
  .line 1085
    if-nez p1, :L0
  .line 1086
    return-object p0
  :L0
  .line 1088
    nop
  .line 1089
    iget-object p1, p1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->completedEvents:Ljava/util/Set;
    const/16 p2, 1001
    invoke-static { p2 }, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
    move-result-object p2
    invoke-interface { p1, p2 }, Ljava/util/Set;->contains(Ljava/lang/Object;)Z
    move-result p1
    if-eqz p1, :L1
  .line 1090
    const/16 p1, 24
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->withHero([BI)[B
    move-result-object p0
  :L1
  .line 1092
    return-object p0
.end method

.method static withTutorialProgress([BLcom/project7/localmanager/LocalTutorialStore$Progress;)[B
  .registers 10
  .line 1206
    const-string v0, "eventTrigger"
    invoke-static { p0, v0 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v1
  .line 1207
    if-nez v1, :L0
  .line 1208
    sget-object v1, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
  :L0
  .line 1210
    iget-object v2, p1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->completedEvents:Ljava/util/Set;
  .line 1211
    invoke-static { v2 }, Lcom/project7/localmanager/BsonLite;->intArrayBytes(Ljava/lang/Iterable;)[B
    move-result-object v2
  .line 1210
    const-string v3, "ecm"
    const/4 v4, 4
    invoke-static { v1, v3, v4, v2 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v1
  .line 1212
    iget-object v2, p1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->processingEvents:Ljava/util/Set;
  .line 1213
    invoke-static { v2 }, Lcom/project7/localmanager/BsonLite;->intArrayBytes(Ljava/lang/Iterable;)[B
    move-result-object v2
  .line 1212
    const-string v3, "pe"
    invoke-static { v1, v3, v4, v2 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v1
  .line 1214
    new-instance v2, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v2 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 1215
    iget-object v5, p1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->availableEvents:Ljava/util/Set;
    const-string v6, "ae"
    invoke-static { v2, v6, v5 }, Lcom/project7/localmanager/BsonLite;->writeEventAvailabilityArray(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/Iterable;)V
  .line 1216
    nop
  .line 1217
    invoke-static { v2 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object v2
    invoke-static { v2, v6 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v2
  .line 1216
    invoke-static { v1, v6, v4, v2 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v1
  .line 1219
    const-string v2, "nbd"
    invoke-static { p0, v2 }, Lcom/project7/localmanager/BsonLite;->documentValue([BLjava/lang/String;)[B
    move-result-object v5
  .line 1220
    if-nez v5, :L1
  .line 1221
    sget-object v5, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
  :L1
  .line 1223
    iget-object v6, p1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->finishedNewbees:Ljava/util/Set;
    invoke-static { v6 }, Lcom/project7/localmanager/BsonLite;->intArrayBytes(Ljava/lang/Iterable;)[B
    move-result-object v6
    const-string v7, "fn"
    invoke-static { v5, v7, v4, v6 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v5
  .line 1224
    iget-object v6, p1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->processingNewbees:Ljava/util/Set;
    invoke-static { v6 }, Lcom/project7/localmanager/BsonLite;->intArrayBytes(Ljava/lang/Iterable;)[B
    move-result-object v6
    invoke-static { v5, v3, v4, v6 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object v3
  .line 1225
    const/16 v4, 8
    iget-boolean p1, p1, Lcom/project7/localmanager/LocalTutorialStore$Progress;->initPrologue:Z
    invoke-static { p1 }, Lcom/project7/localmanager/BsonLite;->boolBytes(Z)[B
    move-result-object p1
    const-string v5, "ip"
    invoke-static { v3, v5, v4, p1 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p1
  .line 1227
    const/4 v3, 3
    invoke-static { p0, v0, v3, v1 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
  .line 1228
    invoke-static { p0, v2, v3, p1 }, Lcom/project7/localmanager/BsonLite;->replaceElement([BLjava/lang/String;I[B)[B
    move-result-object p0
    return-object p0
.end method

.method static withoutProfileKey([BLjava/lang/String;)[B
  .registers 8
  .line 804
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 805
    invoke-static { p0 }, Ljava/nio/ByteBuffer;->wrap([B)Ljava/nio/ByteBuffer;
    move-result-object v1
    sget-object v2, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { v1, v2 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object v1
  .line 806
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->getInt()I
    move-result v2
  :L0
  .line 807
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result v3
    add-int/lit8 v4, v2, -1
    if-ge v3, v4, :L3
  .line 808
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result v3
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->get()B
    move-result v4
    and-int/lit16 v4, v4, 255
  .line 809
    invoke-static { v1, v2 }, Lcom/project7/localmanager/BsonLite;->readCString(Ljava/nio/ByteBuffer;I)Ljava/lang/String;
    move-result-object v5
  .line 810
    if-eqz v5, :L2
    invoke-static { v1, v4, v2 }, Lcom/project7/localmanager/BsonLite;->skipValue(Ljava/nio/ByteBuffer;II)Z
    move-result v4
    if-eqz v4, :L2
  .line 811
    invoke-virtual { p1, v5 }, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v4
    if-nez v4, :L1
    invoke-virtual { v1 }, Ljava/nio/ByteBuffer;->position()I
    move-result v4
    sub-int/2addr v4, v3
    invoke-virtual { v0, p0, v3, v4 }, Ljava/io/ByteArrayOutputStream;->write([BII)V
  :L1
  .line 812
    goto :L0
  :L2
  .line 810
    new-instance p0, Ljava/lang/IllegalArgumentException;
    const-string p1, "invalid BSON"
    invoke-direct { p0, p1 }, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V
    throw p0
  :L3
  .line 813
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p0
    return-object p0
.end method

.method private static writeArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .registers 4
  .line 1590
    const/4 v0, 4
    invoke-virtual { p0, v0 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1591
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeCString(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 1592
    array-length p1, p2
    const/4 v0, 0
    invoke-virtual { p0, p2, v0, p1 }, Ljava/io/ByteArrayOutputStream;->write([BII)V
  .line 1593
    return-void
.end method

.method private static writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
  .registers 4
  .line 1616
    const/16 v0, 8
    invoke-virtual { p0, v0 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1617
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeCString(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 1618
    invoke-virtual { p0, p2 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1619
    return-void
.end method

.method private static writeCString(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .registers 4
  .line 1529
    sget-object v0, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;
    invoke-virtual { p1, v0 }, Ljava/lang/String;->getBytes(Ljava/nio/charset/Charset;)[B
    move-result-object p1
  .line 1530
    array-length v0, p1
    const/4 v1, 0
    invoke-virtual { p0, p1, v1, v0 }, Ljava/io/ByteArrayOutputStream;->write([BII)V
  .line 1531
    invoke-virtual { p0, v1 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1532
    return-void
.end method

.method private static writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .registers 4
  .line 1600
    const/4 v0, 3
    invoke-virtual { p0, v0 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1601
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeCString(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 1602
    array-length p1, p2
    const/4 v0, 0
    invoke-virtual { p0, p2, v0, p1 }, Ljava/io/ByteArrayOutputStream;->write([BII)V
  .line 1603
    return-void
.end method

.method private static writeEmptyArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .registers 3
  .line 1548
    sget-object v0, Lcom/project7/localmanager/BsonLite;->EMPTY_DOCUMENT:[B
    invoke-static { p0, p1, v0 }, Lcom/project7/localmanager/BsonLite;->writeArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 1549
    return-void
.end method

.method private static writeEventAvailabilityArray(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/Iterable;)V
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Ljava/io/ByteArrayOutputStream;",
      "Ljava/lang/String;",
      "Ljava/lang/Iterable<",
      "Ljava/lang/Integer;",
      ">;)V"
    }
  .end annotation
  .registers 9
  .line 1556
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 1557
    nop
  .line 1558
    invoke-interface { p2 }, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;
    move-result-object p2
    const/4 v1, 0
    move v2, v1
  :L0
    invoke-interface { p2 }, Ljava/util/Iterator;->hasNext()Z
    move-result v3
    if-eqz v3, :L2
    invoke-interface { p2 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v3
    check-cast v3, Ljava/lang/Integer;
  .line 1559
    if-eqz v3, :L0
    invoke-virtual { v3 }, Ljava/lang/Integer;->intValue()I
    move-result v4
    if-nez v4, :L1
  .line 1560
    goto :L0
  :L1
  .line 1562
    new-instance v4, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v4 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 1563
    invoke-virtual { v3 }, Ljava/lang/Integer;->intValue()I
    move-result v3
    const-string v5, "0"
    invoke-static { v4, v5, v3 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 1564
    const-string v3, "1"
    invoke-static { v4, v3, v1 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 1565
    add-int/lit8 v3, v2, 1
    invoke-static { v2 }, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object v2
    invoke-static { v4 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object v4
    invoke-static { v0, v2, v4 }, Lcom/project7/localmanager/BsonLite;->writeArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 1566
    move v2, v3
    goto :L0
  :L2
  .line 1567
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p2
    invoke-static { p0, p1, p2 }, Lcom/project7/localmanager/BsonLite;->writeArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 1568
    return-void
.end method

.method private static writeIntArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/Iterable;)V
  .annotation system Ldalvik/annotation/Signature;
    value = {
      "(",
      "Ljava/io/ByteArrayOutputStream;",
      "Ljava/lang/String;",
      "Ljava/lang/Iterable<",
      "Ljava/lang/Integer;",
      ">;)V"
    }
  .end annotation
  .registers 7
  .line 1575
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 1576
    nop
  .line 1577
    invoke-interface { p2 }, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;
    move-result-object p2
    const/4 v1, 0
  :L0
    invoke-interface { p2 }, Ljava/util/Iterator;->hasNext()Z
    move-result v2
    if-eqz v2, :L2
    invoke-interface { p2 }, Ljava/util/Iterator;->next()Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Ljava/lang/Integer;
  .line 1578
    if-eqz v2, :L1
    invoke-virtual { v2 }, Ljava/lang/Integer;->intValue()I
    move-result v3
    if-eqz v3, :L1
  .line 1579
    add-int/lit8 v3, v1, 1
    invoke-static { v1 }, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object v1
    invoke-virtual { v2 }, Ljava/lang/Integer;->intValue()I
    move-result v2
    invoke-static { v0, v1, v2 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
    move v1, v3
  :L1
  .line 1581
    goto :L0
  :L2
  .line 1582
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p2
    invoke-static { p0, p1, p2 }, Lcom/project7/localmanager/BsonLite;->writeArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 1583
    return-void
.end method

.method private static writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .registers 4
  .line 1606
    const/16 v0, 16
    invoke-virtual { p0, v0 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1607
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeCString(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 1608
    invoke-static { p0, p2 }, Lcom/project7/localmanager/BsonLite;->writeLeInt(Ljava/io/ByteArrayOutputStream;I)V
  .line 1609
    return-void
.end method

.method private static writeLeInt(Ljava/io/ByteArrayOutputStream;I)V
  .registers 3
  .line 1640
    and-int/lit16 v0, p1, 255
    invoke-virtual { p0, v0 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1641
    ushr-int/lit8 v0, p1, 8
    and-int/lit16 v0, v0, 255
    invoke-virtual { p0, v0 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1642
    ushr-int/lit8 v0, p1, 16
    and-int/lit16 v0, v0, 255
    invoke-virtual { p0, v0 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1643
    ushr-int/lit8 p1, p1, 24
    and-int/lit16 p1, p1, 255
    invoke-virtual { p0, p1 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1644
    return-void
.end method

.method private static writeNullElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .registers 3
  .line 1622
    const/16 v0, 10
    invoke-virtual { p0, v0 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1623
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeCString(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 1624
    return-void
.end method

.method private static writeObjectIdElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .registers 5
  .line 1631
    array-length v0, p2
    const/16 v1, 12
    if-ne v0, v1, :L0
  .line 1634
    const/4 v0, 7
    invoke-virtual { p0, v0 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1635
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeCString(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 1636
    const/4 p1, 0
    array-length v0, p2
    invoke-virtual { p0, p2, p1, v0 }, Ljava/io/ByteArrayOutputStream;->write([BII)V
  .line 1637
    return-void
  :L0
  .line 1632
    new-instance p0, Ljava/lang/IllegalArgumentException;
    const-string p1, "ObjectId must contain 12 bytes"
    invoke-direct { p0, p1 }, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V
    throw p0
.end method

.method private static writeSkillPairsElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[[I)V
  .registers 9
  .line 326
    new-instance v0, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v0 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 327
    const/4 v1, 0
    move v2, v1
  :L0
    array-length v3, p2
    if-ge v2, v3, :L1
  .line 328
    new-instance v3, Ljava/io/ByteArrayOutputStream;
    invoke-direct { v3 }, Ljava/io/ByteArrayOutputStream;-><init>()V
  .line 329
    aget-object v4, p2, v2
    aget v4, v4, v1
    const-string v5, "0"
    invoke-static { v3, v5, v4 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 330
    aget-object v4, p2, v2
    const/4 v5, 1
    aget v4, v4, v5
    const-string v5, "1"
    invoke-static { v3, v5, v4 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
  .line 331
    invoke-static { v2 }, Ljava/lang/Integer;->toString(I)Ljava/lang/String;
    move-result-object v4
    invoke-static { v3 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object v3
    invoke-static { v0, v4, v3 }, Lcom/project7/localmanager/BsonLite;->writeArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 327
    add-int/lit8 v2, v2, 1
    goto :L0
  :L1
  .line 333
    invoke-static { v0 }, Lcom/project7/localmanager/BsonLite;->finishDocument(Ljava/io/ByteArrayOutputStream;)[B
    move-result-object p2
    invoke-static { p0, p1, p2 }, Lcom/project7/localmanager/BsonLite;->writeArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
  .line 334
    return-void
.end method

.method private static writeStringElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/String;)V
  .registers 4
  .line 1539
    const/4 v0, 2
    invoke-virtual { p0, v0 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1540
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeCString(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 1541
    sget-object p1, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;
    invoke-virtual { p2, p1 }, Ljava/lang/String;->getBytes(Ljava/nio/charset/Charset;)[B
    move-result-object p1
  .line 1542
    array-length p2, p1
    add-int/lit8 p2, p2, 1
    invoke-static { p0, p2 }, Lcom/project7/localmanager/BsonLite;->writeLeInt(Ljava/io/ByteArrayOutputStream;I)V
  .line 1543
    array-length p2, p1
    const/4 v0, 0
    invoke-virtual { p0, p1, v0, p2 }, Ljava/io/ByteArrayOutputStream;->write([BII)V
  .line 1544
    invoke-virtual { p0, v0 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 1545
    return-void
.end method

.method private static writeValue(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/Object;)V
  .registers 7
  .line 940
    instance-of v0, p2, Ljava/lang/Integer;
    if-eqz v0, :L0
    check-cast p2, Ljava/lang/Integer;
    invoke-virtual { p2 }, Ljava/lang/Integer;->intValue()I
    move-result p2
    invoke-static { p0, p1, p2 }, Lcom/project7/localmanager/BsonLite;->writeIntElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;I)V
    goto/16 :L9
  :L0
  .line 941
    instance-of v0, p2, Ljava/lang/Double;
    const/4 v1, 0
    if-eqz v0, :L1
  .line 942
    const/4 v0, 1
    invoke-virtual { p0, v0 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 943
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeCString(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 944
    const/16 p1, 8
    invoke-static { p1 }, Ljava/nio/ByteBuffer;->allocate(I)Ljava/nio/ByteBuffer;
    move-result-object p1
    sget-object v0, Ljava/nio/ByteOrder;->LITTLE_ENDIAN:Ljava/nio/ByteOrder;
    invoke-virtual { p1, v0 }, Ljava/nio/ByteBuffer;->order(Ljava/nio/ByteOrder;)Ljava/nio/ByteBuffer;
    move-result-object p1
    check-cast p2, Ljava/lang/Double;
  .line 945
    invoke-virtual { p2 }, Ljava/lang/Double;->doubleValue()D
    move-result-wide v2
    invoke-virtual { p1, v2, v3 }, Ljava/nio/ByteBuffer;->putDouble(D)Ljava/nio/ByteBuffer;
    move-result-object p1
    invoke-virtual { p1 }, Ljava/nio/ByteBuffer;->array()[B
    move-result-object p1
  .line 946
    array-length p2, p1
    invoke-virtual { p0, p1, v1, p2 }, Ljava/io/ByteArrayOutputStream;->write([BII)V
  .line 947
    goto/16 :L9
  :L1
  .line 948
    instance-of v0, p2, Ljava/lang/Boolean;
    if-eqz v0, :L2
    check-cast p2, Ljava/lang/Boolean;
    invoke-virtual { p2 }, Ljava/lang/Boolean;->booleanValue()Z
    move-result p2
    invoke-static { p0, p1, p2 }, Lcom/project7/localmanager/BsonLite;->writeBoolElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Z)V
    goto :L9
  :L2
  .line 949
    instance-of v0, p2, Ljava/lang/String;
    if-eqz v0, :L3
    check-cast p2, Ljava/lang/String;
    invoke-static { p0, p1, p2 }, Lcom/project7/localmanager/BsonLite;->writeStringElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;Ljava/lang/String;)V
    goto :L9
  :L3
  .line 950
    instance-of v0, p2, [B
    if-eqz v0, :L4
    check-cast p2, [B
    invoke-static { p0, p1, p2 }, Lcom/project7/localmanager/BsonLite;->writeDocumentElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
    goto :L9
  :L4
  .line 951
    instance-of v0, p2, Lcom/project7/localmanager/BsonLite$BinaryValue;
    if-eqz v0, :L5
  .line 952
    const/4 v0, 5
    invoke-virtual { p0, v0 }, Ljava/io/ByteArrayOutputStream;->write(I)V
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeCString(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  .line 953
    check-cast p2, Lcom/project7/localmanager/BsonLite$BinaryValue;
    iget-object p1, p2, Lcom/project7/localmanager/BsonLite$BinaryValue;->bytes:[B
  .line 954
    array-length p2, p1
    invoke-static { p0, p2 }, Lcom/project7/localmanager/BsonLite;->writeLeInt(Ljava/io/ByteArrayOutputStream;I)V
    invoke-virtual { p0, v1 }, Ljava/io/ByteArrayOutputStream;->write(I)V
  .line 955
    array-length p2, p1
    invoke-virtual { p0, p1, v1, p2 }, Ljava/io/ByteArrayOutputStream;->write([BII)V
  .line 956
    goto :L9
  :L5
  .line 957
    instance-of v0, p2, Lcom/project7/localmanager/BsonLite$ArrayValue;
    if-eqz v0, :L6
    check-cast p2, Lcom/project7/localmanager/BsonLite$ArrayValue;
    iget-object p2, p2, Lcom/project7/localmanager/BsonLite$ArrayValue;->bytes:[B
    invoke-static { p0, p1, p2 }, Lcom/project7/localmanager/BsonLite;->writeArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
    goto :L9
  :L6
  .line 958
    instance-of v0, p2, Lcom/project7/localmanager/BsonLite$UuidValue;
    if-eqz v0, :L7
    check-cast p2, Lcom/project7/localmanager/BsonLite$UuidValue;
    iget-object p2, p2, Lcom/project7/localmanager/BsonLite$UuidValue;->bytes:[B
    invoke-static { p0, p1, p2 }, Lcom/project7/localmanager/BsonLite;->writeObjectIdElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
    goto :L9
  :L7
  .line 959
    instance-of v0, p2, Ljava/util/List;
    if-eqz v0, :L8
    check-cast p2, Ljava/util/List;
    invoke-static { p2 }, Lcom/project7/localmanager/BsonLite;->listBytes(Ljava/util/List;)[B
    move-result-object p2
    invoke-static { p0, p1, p2 }, Lcom/project7/localmanager/BsonLite;->writeArrayElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;[B)V
    goto :L9
  :L8
  .line 960
    if-nez p2, :L10
    invoke-static { p0, p1 }, Lcom/project7/localmanager/BsonLite;->writeNullElement(Ljava/io/ByteArrayOutputStream;Ljava/lang/String;)V
  :L9
  .line 962
    return-void
  :L10
  .line 961
    new-instance p0, Ljava/lang/IllegalArgumentException;
    const-string p1, "unsupported BSON value"
    invoke-direct { p0, p1 }, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V
    throw p0
.end method
