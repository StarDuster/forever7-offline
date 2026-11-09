"""Host tests and Android-32 javac only. No DEX, APK, emulator or device actions."""
from pathlib import Path
import subprocess, shutil
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
BUILD=ROOT/'analysis/project7/autologin-compile'
JDK=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
ANDROID=ROOT/'toolchains/android-sdk/platforms/android-32/android.jar'
if BUILD.exists(): shutil.rmtree(BUILD)
for name in ('host','compile-only-stubs','production-classes'): (BUILD/name).mkdir(parents=True)
def run(*args): subprocess.run([str(a) for a in args],check=True)
core=HERE/'src/com/netease/qrzd/AutoLoginCore.java'
run(JDK/'javac','--release','8','-d',BUILD/'host',core,*HERE.glob('host_tests/**/*.java'))
run(JDK/'java','-cp',BUILD/'host','com.netease.qrzd.AutoLoginHostTests')
run(JDK/'javac','--release','8','-d',BUILD/'compile-only-stubs',*HERE.glob('compile_stubs/**/*.java'))
run(JDK/'javac','--release','8','-cp',str(ANDROID)+':'+str(BUILD/'compile-only-stubs'),'-d',BUILD/'production-classes',*HERE.glob('src/**/*.java'))
assert not (BUILD/'production-classes/com/netease/neox/NativeInterface.class').exists()
print('PASS Android-32 compile; NativeInterface stub isolated outside production-classes')
