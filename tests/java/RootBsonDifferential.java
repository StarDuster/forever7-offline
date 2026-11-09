import java.lang.reflect.*;
import java.util.*;

/** Run in separate JVMs against original and candidate manager jars; compare stdout. */
public final class RootBsonDifferential {
    static byte[] doc(byte[] fields) {
        byte[] d = new byte[fields.length + 5];
        int n = d.length;
        for (int i = 0; i < 4; i++) d[i] = (byte) (n >>> (8 * i));
        System.arraycopy(fields, 0, d, 4, fields.length);
        return d;
    }
    public static void main(String[] args) throws Exception {
        Class<?> cls = Class.forName("com.project7.localmanager.BsonLite");
        Method find = cls.getDeclaredMethod("findElement", byte[].class, String.class);
        find.setAccessible(true);
        Class<?> element = Class.forName("com.project7.localmanager.BsonLite$Element");
        Field type = element.getDeclaredField("type"), value = element.getDeclaredField("value");
        type.setAccessible(true); value.setAccessible(true);
        List<byte[]> cases = new ArrayList<>();
        cases.add(null); cases.add(new byte[0]); cases.add(doc(new byte[0]));
        cases.add(new byte[]{7,0,0,0,10,97,0});
        cases.add(doc(new byte[]{10,97,0}));
        cases.add(doc(new byte[]{16,97,0,1,0,0,0,16,97,0,2,0,0,0}));
        cases.add(doc(new byte[]{10,(byte)0xc3,0x28,0}));
        cases.add(doc(new byte[]{3,97,0,5,0,0,0,0}));
        Random rng = new Random(64020261106L);
        for (int i = 0; i < 4000; i++) {
            byte[] fields = new byte[rng.nextInt(96)]; rng.nextBytes(fields);
            byte[] d = doc(fields);
            if (i % 2 == 0 && d.length >= 7) {
                d[4] = (byte) new int[]{1,2,3,4,5,8,10,16,18,127,255}[rng.nextInt(11)];
                d[5] = 'a'; d[6] = 0;
            }
            if (i % 5 == 0) d[0] = (byte) rng.nextInt(128);
            cases.add(d);
        }
        String[] keys = {"a", "b", "", "longKey", null, "\uFFFD(", "文本", "a\u0000"};
        int row = 0;
        for (byte[] d : cases) for (String key : keys) {
            String outcome;
            try {
                Object e = find.invoke(null, d, key);
                outcome = e == null ? "null" : type.getInt(e) + ":" +
                        Base64.getEncoder().encodeToString((byte[]) value.get(e));
            } catch (InvocationTargetException ex) {
                outcome = "exception:" + ex.getCause().getClass().getName();
            }
            System.out.println((row++) + "=" + outcome);
        }
    }
}
