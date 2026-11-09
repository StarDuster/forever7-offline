package com.project7.localmanager;

import java.util.Random;

/** Pure persisted-plan value. No profile, Context, grant, clock or actual-count owner. */
public final class DynamicSlotPlan {
    public static final String POLICY="dynamic-resolve-on-reveal-offline-v1";
    public static final String FAMILY_POLICY="dynamic-charge-extra-offline-v2";
    public static String policyFor(int pool){return pool==485?POLICY:FAMILY_POLICY;}
    public final int pool,epoch,slot;
    public final long ordinal,entropy;
    public final String catalogHash;
    private DynamicSlotPlan(int pool,int epoch,int slot,long ordinal,long entropy,String hash){
        if(pool<=0||epoch<=0||slot<0||slot>=6||ordinal<=0||hash==null||!hash.matches("[0-9a-f]{64}"))
            throw new IllegalArgumentException("离线动态抽卡计划校验失败");
        this.pool=pool;this.epoch=epoch;this.slot=slot;this.ordinal=ordinal;this.entropy=entropy;this.catalogHash=hash;
    }
    /** nextOrdinal is a reservation cursor, never ct/charge/iuc/jzc. */
    public static DynamicSlotPlan[] group(int pool,int epoch,long nextOrdinal,String hash,Random random){
        if(random==null||nextOrdinal<=0||nextOrdinal>Long.MAX_VALUE-5)throw new IllegalArgumentException("离线动态抽卡序位超出范围");
        // Validate every field before consuming caller entropy.
        new DynamicSlotPlan(pool,epoch,0,nextOrdinal,0,hash);
        DynamicSlotPlan[] result=new DynamicSlotPlan[6];
        for(int i=0;i<6;i++)result[i]=new DynamicSlotPlan(pool,epoch,i,nextOrdinal+i,random.nextLong(),hash);
        return result;
    }
    /** Decode only committed plan fields; loading a pending slot never consumes entropy. */
    public static DynamicSlotPlan restore(int pool,int epoch,int slot,long ordinal,long entropy,String hash,String policy){
        if(!policyFor(pool).equals(policy))throw new IllegalArgumentException("离线动态抽卡规则版本不匹配");
        return new DynamicSlotPlan(pool,epoch,slot,ordinal,entropy,hash);
    }
    /** Repeatable first-resolution stream; caller must persist resolved leaf in the same transaction. */
    public Random resolutionEntropy(){return new Random(entropy);}
}
