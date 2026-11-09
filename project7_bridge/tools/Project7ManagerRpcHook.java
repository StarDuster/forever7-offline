import com.googlecode.d2j.DexConstants;
import com.googlecode.d2j.DexLabel;
import com.googlecode.d2j.Method;
import com.googlecode.d2j.dex.writer.DexFileWriter;
import com.googlecode.d2j.reader.DexFileReader;
import com.googlecode.d2j.reader.Op;
import com.googlecode.d2j.visitors.*;
import java.nio.file.*;
import java.util.Arrays;

/** Maintainer-only DEX rewrite: one guarded dispatch prefix, no decompiled source. */
public final class Project7ManagerRpcHook {
    static final String SERVER = "Lcom/project7/localmanager/LocalGatewayServer;";
    static final String DESC = "(Ljava/io/OutputStream;[B[B[BLjava/lang/String;)Z";
    private static int patched;

    public static void main(String[] args) throws Exception {
        if (args.length != 2 || Files.exists(Paths.get(args[1])))
            throw new IllegalArgumentException("Require input and unused output paths");
        DexFileReader reader = new DexFileReader(Paths.get(args[0]));
        if (reader.getDexVersion() != DexConstants.DEX_038 || reader.getClassSize() != 649)
            throw new IllegalArgumentException("Unsupported manager DEX version/class count");
        DexFileWriter writer = new DexFileWriter();
        writer.cp.dex038();
        reader.accept(new DexFileVisitor(writer) {
            @Override public DexClassVisitor visit(int access, String name, String parent, String[] interfaces) {
                DexClassVisitor original = super.visit(access, name, parent, interfaces);
                if (!SERVER.equals(name)) return original;
                return new DexClassVisitor(original) {
                    @Override public DexMethodVisitor visitMethod(int flags, Method method) {
                        DexMethodVisitor delegate = super.visitMethod(flags, method);
                        if (!"handleResourceRpc".equals(method.getName()) || !DESC.equals(method.getDesc()))
                            return delegate;
                        if ((flags & DexConstants.ACC_STATIC) != 0 || ++patched != 1)
                            throw new IllegalStateException("Unexpected dispatch method");
                        return new DexMethodVisitor(delegate) {
                            @Override public DexCodeVisitor visitCode() {
                                DexCodeVisitor code = super.visitCode();
                                return new DexCodeVisitor(code) {
                                    @Override public void visitRegister(int count) {
                                        if (count <= 6 || count > 65535)
                                            throw new IllegalStateException("Need existing scratch local plus six parameter words");
                                        super.visitRegister(count);
                                        int first = count - 6;
                                        int[] args = {first,first+1,first+2,first+3,first+4,first+5};
                                        Method bridge = new Method("Lcom/project7/localmanager/CoreGapBridge;",
                                            "handleResourceRpc", new String[]{SERVER,"Ljava/io/OutputStream;",
                                            "[B","[B","[B","Ljava/lang/String;"}, "Z");
                                        DexLabel resume = new DexLabel();
                                        super.visitMethodStmt(Op.INVOKE_STATIC_RANGE, args, bridge);
                                        super.visitStmt1R(Op.MOVE_RESULT, 0);
                                        super.visitJumpStmt(Op.IF_EQZ, 0, -1, resume);
                                        super.visitConstStmt(Op.CONST_4, 0, 1);
                                        super.visitStmt1R(Op.RETURN, 0);
                                        super.visitLabel(resume);
                                    }
                                };
                            }
                        };
                    }
                };
            }
        });
        if (patched != 1) throw new IllegalStateException("Exact dispatch method missing");
        byte[] output = writer.toByteArray();
        Files.write(Paths.get(args[1]), output, StandardOpenOption.CREATE_NEW);
        System.out.println("patched_methods=1; original_dispatch_fallback_preserved=true");
    }
}
