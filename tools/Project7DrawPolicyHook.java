import com.googlecode.d2j.DexConstants;
import com.googlecode.d2j.Method;
import com.googlecode.d2j.dex.writer.DexFileWriter;
import com.googlecode.d2j.reader.DexFileReader;
import com.googlecode.d2j.reader.Op;
import com.googlecode.d2j.visitors.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.Arrays;

/** Maintainer-only, pinned ordinary-draw seams; preserves the original engine. */
public final class Project7DrawPolicyHook {
    private static final String INPUT_SHA = "dfb15ecd8e12ff99c3f3595ecc680b014a0233943eacd3aca3c81555709f8e10";
    private static final String OUTPUT_SHA = "20f19471d1e73f3b32b4cc28300973eb3168cdfea8ddb1c46fe1ccd1e1306eae";
    private static final String DRAW = "Lcom/project7/localmanager/LocalDrawEngine;";
    private static final String POLICY = "Lcom/project7/localmanager/CoreDrawPolicy;";
    private static final String CATALOG = "Lcom/project7/localmanager/LocalResourceCatalog;";
    private static final String RESULT = "Lcom/project7/localmanager/LocalResourceEngine$Result;";
    private static final String RANDOM = "Ljava/util/Random;";
    private static int drawClasses, applyMethods, saveMethods, makeCalls, tutorialCalls, revealCalls;

    private static String sha(byte[] data) throws Exception {
        StringBuilder value = new StringBuilder();
        for (byte b : MessageDigest.getInstance("SHA-256").digest(data))
            value.append(String.format("%02x", b & 255));
        return value.toString();
    }
    private static boolean target(Method method, String name, String desc) {
        return DRAW.equals(method.getOwner()) && name.equals(method.getName()) && desc.equals(method.getDesc());
    }
    private static void require(boolean ok, String message) {
        if (!ok) throw new IllegalStateException(message);
    }
    public static void main(String[] arguments) throws Exception {
        if (arguments.length != 2 || Files.exists(Paths.get(arguments[1])))
            throw new IllegalArgumentException("Require pinned input and unused output paths");
        byte[] input = Files.readAllBytes(Paths.get(arguments[0]));
        require(INPUT_SHA.equals(sha(input)), "Manager core-RPC baseline differs");
        DexFileReader reader = new DexFileReader(input);
        require(reader.getDexVersion() == DexConstants.DEX_038 && reader.getClassSize() == 649,
            "Manager DEX format/class count differs");
        DexFileWriter writer = new DexFileWriter();
        writer.cp.dex038();
        reader.accept(new DexFileVisitor(writer) {
            @Override public DexClassVisitor visit(int flags, String name, String parent, String[] interfaces) {
                DexClassVisitor delegate = super.visit(flags, name, parent, interfaces);
                if (!DRAW.equals(name)) return delegate;
                require(++drawClasses == 1, "Duplicate draw class");
                return new DexClassVisitor(delegate) {
                    @Override public DexMethodVisitor visitMethod(int access, Method method) {
                        require(!method.getName().startsWith("q7Original"), "Input already contains a draw bridge");
                        DexMethodVisitor original = super.visitMethod(access, method);
                        boolean apply = target(method, "applyCurrent", "([B" + CATALOG +
                            "Ljava/lang/String;[B" + RANDOM + ")" + RESULT);
                        boolean save = target(method, "saveState", "(" + RESULT + "[BI)V");
                        if (!apply && !save) return original;
                        require((access & DexConstants.ACC_STATIC) != 0, "Expected static engine methods");
                        if (apply) require(++applyMethods == 1, "Duplicate applyCurrent");
                        if (save) require(++saveMethods == 1, "Duplicate saveState");
                        return new DexMethodVisitor(original) {
                            @Override public DexCodeVisitor visitCode() {
                                return new DexCodeVisitor(super.visitCode()) {
                                    @Override public void visitRegister(int count) {
                                        require(count == (apply ? 47 : 14), "Pinned register layout differs");
                                        super.visitRegister(count);
                                        if (save) {
                                            super.visitMethodStmt(Op.INVOKE_STATIC, new int[]{12, 13},
                                                new Method(POLICY, "stateForSave", new String[]{"[B", "I"}, "[B"));
                                            super.visitStmt1R(Op.MOVE_RESULT_OBJECT, 12);
                                        }
                                    }
                                    @Override public void visitMethodStmt(Op op, int[] regs, Method called) {
                                        if (apply && target(called, "makeFile", "(" + CATALOG + RANDOM + "Z)[B")) {
                                            require(op == Op.INVOKE_STATIC && Arrays.equals(regs, new int[]{8,3,2}) && ++makeCalls == 1,
                                                "Pinned ordinary makeFile call differs");
                                            super.visitMethodStmt(op, new int[]{8,3,2,5},
                                                new Method(POLICY, "makeFile", new String[]{CATALOG,RANDOM,"Z","[B"}, "[B"));
                                            return;
                                        }
                                        if (apply && target(called, "tutorialCard", "(I)[B")) {
                                            require(op == Op.INVOKE_STATIC && Arrays.equals(regs, new int[]{12}) && ++tutorialCalls == 1,
                                                "Pinned tutorial candidate call differs");
                                            super.visitMethodStmt(op, new int[]{12,1},
                                                new Method(POLICY, "tutorialCandidate", new String[]{"I","[B"}, "[B"));
                                            return;
                                        }
                                        if (apply && target(called, "reveal", "(" + RESULT + CATALOG + "[B)[B")) {
                                            require(op == Op.INVOKE_STATIC && Arrays.equals(regs, new int[]{7,8,1}) && ++revealCalls == 1,
                                                "Pinned stock reveal call differs");
                                            super.visitMethodStmt(op, regs,
                                                new Method(POLICY, "reveal", new String[]{RESULT,CATALOG,"[B"}, "[B"));
                                            return;
                                        }
                                        super.visitMethodStmt(op, regs, called);
                                    }
                                };
                            }
                        };
                    }
                    @Override public void visitEnd() {
                        DexMethodVisitor bridge = super.visitMethod(
                            DexConstants.ACC_PUBLIC | DexConstants.ACC_STATIC | DexConstants.ACC_SYNTHETIC,
                            new Method(DRAW, "q7OriginalTutorialCard", new String[]{"I"}, "[B"));
                        DexCodeVisitor code = bridge.visitCode();
                        code.visitRegister(1);
                        code.visitMethodStmt(Op.INVOKE_STATIC, new int[]{0},
                            new Method(DRAW, "tutorialCard", new String[]{"I"}, "[B"));
                        code.visitStmt1R(Op.MOVE_RESULT_OBJECT, 0);
                        code.visitStmt1R(Op.RETURN_OBJECT, 0);
                        code.visitEnd();
                        bridge.visitEnd();
                        super.visitEnd();
                    }
                };
            }
        });
        require(drawClasses == 1 && applyMethods == 1 && saveMethods == 1 &&
            makeCalls == 1 && tutorialCalls == 1 && revealCalls == 1, "Missing exact draw seams");
        byte[] output = writer.toByteArray();
        require(OUTPUT_SHA.equals(sha(output)), "Draw DEX producer output differs from the reviewed target");
        Files.write(Paths.get(arguments[1]), output, StandardOpenOption.CREATE_NEW);
        System.out.println("modified_existing_methods=2; added_tutorial_bridge=1; unchanged_registers=true; original_grant_and_commit_preserved=true");
    }
}
