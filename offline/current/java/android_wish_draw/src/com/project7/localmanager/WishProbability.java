package com.project7.localmanager;
import java.math.*;import java.util.*;
/** Exact rational probability mass; sampling uses unbiased integer rejection. */
public final class WishProbability {
 private WishProbability(){}
 public static final class Fraction {
  public final BigInteger n,d;
  public Fraction(BigInteger n,BigInteger d){if(d.signum()<=0)throw new IllegalArgumentException("denominator");BigInteger g=n.gcd(d);this.n=n.divide(g);this.d=d.divide(g);}
  public Fraction(long n,long d){this(BigInteger.valueOf(n),BigInteger.valueOf(d));}
  public static Fraction decimal(Object value){BigDecimal b=new BigDecimal(value.toString());int s=b.scale();return s<0?new Fraction(b.unscaledValue().multiply(BigInteger.TEN.pow(-s)),BigInteger.ONE):new Fraction(b.unscaledValue(),BigInteger.TEN.pow(s));}
  public Fraction add(Fraction b){return new Fraction(n.multiply(b.d).add(b.n.multiply(d)),d.multiply(b.d));}
  public Fraction multiply(Fraction b){return new Fraction(n.multiply(b.n),d.multiply(b.d));}
  public Fraction divide(Fraction b){return new Fraction(n.multiply(b.d),d.multiply(b.n));}
  public int compare(Fraction b){return n.multiply(b.d).compareTo(b.n.multiply(d));}
 }
 static final Fraction ZERO=new Fraction(0,1),ONE=new Fraction(1,1);
 public static Fraction wish(Object begin,Object step,int times,int misses){if(times<=0||misses<0)throw new IllegalArgumentException("wish counter");Fraction f=Fraction.decimal(begin).add(Fraction.decimal(step).multiply(new Fraction(misses/times,1)));return f.compare(ONE)>0?ONE:f;}
 public static int projected(int f){if(f<0||f>179)throw new IllegalArgumentException("UP counter");return f==0?0:f+1;}
 public static Fraction up(int f){int c=projected(f);if(f+1>=180)return ONE;return new Fraction(1+Math.max(0,c-100)/6,100);}
 static boolean hit(Random random,Fraction p){return pick(random,Arrays.asList(p,ONE.add(new Fraction(p.n.negate(),p.d))))==0;}
 static int pick(Random random,List<Fraction>mass){Fraction sum=ZERO;BigInteger denominator=BigInteger.ONE;for(Fraction p:mass){if(p.n.signum()<0)throw new IllegalArgumentException("negative probability");sum=sum.add(p);denominator=denominator.divide(denominator.gcd(p.d)).multiply(p.d);}if(sum.compare(ONE)!=0)throw new IllegalArgumentException("probability mass");BigInteger draw;do{draw=new BigInteger(denominator.bitLength(),random);}while(draw.compareTo(denominator)>=0);for(int i=0;i<mass.size();i++){Fraction p=mass.get(i);draw=draw.subtract(p.n.multiply(denominator.divide(p.d)));if(draw.signum()<0)return i;}throw new AssertionError();}
}
