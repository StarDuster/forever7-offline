import com.googlecode.d2j.DexConstants;
import com.googlecode.d2j.Method;
import com.googlecode.d2j.dex.writer.DexFileWriter;
import com.googlecode.d2j.reader.DexFileReader;
import com.googlecode.d2j.reader.Op;
import com.googlecode.d2j.visitors.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.Arrays;

/** Disable only creation of new pool-354 groups. Existing group paths stay original. */
public final class Project7NewbieBlockHook {
    private static final String INPUT_SHA = "20f19471d1e73f3b32b4cc28300973eb3168cdfea8ddb1c46fe1ccd1e1306eae";
    private static final String OUTPUT_SHA = "d16990dff71677c55ecd54225cd1fdc82f06c3785c3258e5053e069f24df341f";
    private static final String DRAW = "Lcom/project7/localmanager/LocalDrawEngine;";
    private static final String NEWBIE = "Lcom/project7/localmanager/LocalNewbieDrawEngine;";
    private static final String CATALOG = "Lcom/project7/localmanager/LocalResourceCatalog;";
    private static final String RESULT = "Lcom/project7/localmanager/LocalResourceEngine$Result;";
    private static final String RANDOM = "Ljava/util/Random;";
    private static int methods, calls;

    private static void require(boolean ok, String message) {
        if (!ok) throw new IllegalStateException(message);
    }
    private static String sha(byte[] data) throws Exception {
        StringBuilder value = new StringBuilder();
        for (byte b : MessageDigest.getInstance("SHA-256").digest(data))
            value.append(String.format("%02x", b & 255));
        return value.toString();
    }
    public static void main(String[] arguments) throws Exception {
        if (arguments.length != 2 || Files.exists(Paths.get(arguments[1])))
            throw new IllegalArgumentException("Require pinned input and unused output paths");
        byte[] source = Files.readAllBytes(Paths.get(arguments[0]));
        require(INPUT_SHA.equals(sha(source)), "Ordinary-policy DEX baseline differs");
        DexFileReader reader = new DexFileReader(source);
        require(reader.getDexVersion() == DexConstants.DEX_038 && reader.getClassSize() == 649,
            "Manager format/class count differs");
        DexFileWriter writer = new DexFileWriter();
        writer.cp.dex038();
        reader.accept(new DexFileVisitor(writer) {
            @Override public DexClassVisitor visit(int access, String name, String parent, String[] interfaces) {
                DexClassVisitor delegate = super.visit(access, name, parent, interfaces);
                if (!DRAW.equals(name)) return delegate;
                return new DexClassVisitor(delegate) {
                    @Override public DexMethodVisitor visitMethod(int access, Method method) {
                        DexMethodVisitor original = super.visitMethod(access, method);
                        if (!"applyCurrent".equals(method.getName()) ||
                            !("([B"+CATALOG+"Ljava/lang/String;[B"+RANDOM+")"+RESULT).equals(method.getDesc()))
                            return original;
                        require(++methods == 1 && (access & DexConstants.ACC_STATIC) != 0, "Unexpected draw dispatch");
                        return new DexMethodVisitor(original) {
                            @Override public DexCodeVisitor visitCode() {
                                return new DexCodeVisitor(super.visitCode()) {
                                    @Override public void visitRegister(int count) {
                                        require(count == 47, "Pinned applyCurrent register layout differs");
                                        super.visitRegister(count);
                                    }
                                    @Override public void visitMethodStmt(Op op, int[] registers, Method called) {
                                        if (NEWBIE.equals(called.getOwner()) && "makeFile".equals(called.getName()) &&
                                            ("("+CATALOG+"I"+RANDOM+")[B").equals(called.getDesc())) {
                                            require(++calls == 1 && op == Op.INVOKE_STATIC &&
                                                Arrays.equals(registers, new int[]{8,2,3}), "Pinned new-group call differs");
                                            super.visitMethodStmt(op, registers,
                                                new Method("Lcom/project7/localmanager/CoreDrawPolicy;", "newbieFile",
                                                    new String[]{CATALOG,"I",RANDOM}, "[B"));
                                            return;
                                        }
                                        super.visitMethodStmt(op, registers, called);
                                    }
                                };
                            }
                        };
                    }
                };
            }
        });
        require(methods == 1 && calls == 1, "Missing exact initial-group call");
        byte[] output = writer.toByteArray();
        require(OUTPUT_SHA.equals(sha(output)), "Producer output differs from the reviewed new-group block");
        Files.write(Paths.get(arguments[1]), output, StandardOpenOption.CREATE_NEW);
        System.out.println("modified_methods=1; modified_invokes=1; new_group_only=true; original_resume_reveal_quit_preserved=true");
    }
}
