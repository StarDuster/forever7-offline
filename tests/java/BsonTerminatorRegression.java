import java.lang.reflect.Method;
import java.util.Arrays;

/** Production regression: a payload must not consume the document terminator. */
public final class BsonTerminatorRegression {
    private static byte[] replace(Method method, byte[] input, String key, int type, byte[] payload) throws Exception {
        return (byte[]) method.invoke(null, input, key, type, payload);
    }

    public static void main(String[] args) throws Exception {
        Class<?> cls = Class.forName("com.project7.localmanager.BsonLite");
        Method method = cls.getDeclaredMethod("replaceElement", byte[].class, String.class, int.class, byte[].class);
        method.setAccessible(true);

        // Document declares length 11. The int16 payload starts at offset 7 and would
        // consume the final (terminator) byte if the scanner does not stop exactly at
        // declaredLength - 1. The correct rebuild is 12 bytes.
        byte[] input = {11, 0, 0, 0, 16, 107, 0, 7, 0, 0, 0};
        byte[] payload = {7, 0, 0, 0};
        byte[] expected = {12, 0, 0, 0, 16, 107, 0, 7, 0, 0, 0, 0};
        byte[] before = input.clone();
        byte[] output = replace(method, input, "k", 16, payload);
        if (!Arrays.equals(input, before)) throw new AssertionError("source mutated");
        if (output == input) throw new AssertionError("aliased terminator input");
        if (output.length != 12) throw new AssertionError("expected 12-byte rebuilt document, got " + output.length);
        if (!Arrays.equals(output, expected)) throw new AssertionError("wrong rebuilt bytes: " + Arrays.toString(output));
        System.out.println("PASS terminator_rebuild=12");
    }
}
