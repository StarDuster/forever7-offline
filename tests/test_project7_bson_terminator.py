import os
import pathlib
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEX = ROOT / 'runtime/project7_bson_fast/BsonLite-fast.dex'
MANAGER = ROOT / 'analysis/project7/story-city-coc-v38-fresh-recovery/manager-translated-frames.jar'
JAVA = ROOT / 'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
DEX2JAR = ROOT / 'toolchains/dex2jar-v2.4/dex-tools-v2.4/d2j-dex2jar.sh'
HELPER = ROOT / 'tests/java/BsonTerminatorRegression.java'


@unittest.skipUnless(DEX.is_file() and MANAGER.is_file() and JAVA.is_dir() and DEX2JAR.is_file(),
                     'BsonLite production regression tools unavailable')
class BsonTerminatorRegressionTest(unittest.TestCase):
    def test_payload_does_not_consume_document_terminator(self):
        with tempfile.TemporaryDirectory(prefix='p7-bson-terminator-') as temporary:
            work = pathlib.Path(temporary)
            jar = work / 'BsonLite.jar'
            classes = work / 'classes'
            classes.mkdir()
            environment = dict(os.environ)
            environment['JAVA_HOME'] = str(JAVA.parents[1])
            environment['PATH'] = str(JAVA) + os.pathsep + environment.get('PATH', '')
            subprocess.run(
                ['/bin/sh', str(DEX2JAR), '-f', '-o', str(jar), str(DEX)],
                check=True, cwd=ROOT, env=environment, stdout=subprocess.DEVNULL,
            )
            subprocess.run(
                [str(JAVA / 'javac'), '-d', str(classes), str(HELPER)],
                check=True, cwd=ROOT, env=environment,
            )
            result = subprocess.run(
                [str(JAVA / 'java'), '-cp', os.pathsep.join([str(classes), str(jar), str(MANAGER)]),
                 'BsonTerminatorRegression'],
                check=True, cwd=ROOT, env=environment, text=True, capture_output=True,
            )
            self.assertIn('PASS terminator_rebuild=12', result.stdout)
