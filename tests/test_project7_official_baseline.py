"""Entry-patch binary tests. No native/game execution or network."""
import hashlib,io,json,pathlib,struct,sys,tempfile,unittest,warnings,zipfile,zlib
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import project7_official_baseline as b

def archive(items,table_order=None,opaque=b'\x12\x34\x56\x78'):
    # Independently encode physical payload layout and separately ordered seven-word index.
    out=bytearray(b'\0'*28);rows={}
    for fid,payload,flags in items:
        offset=len(out);out.extend(payload);out.extend(b'\0'*(-len(out)%4));rows[fid]=(fid,offset,len(payload),4096 if flags==2 else len(payload),0xdeadbeef,0x12345678,flags)
    table=len(out)
    for fid in table_order or list(rows):out.extend(struct.pack('<7I',*rows[fid]))
    out[:28]=struct.pack('<4s5I',b'NXPK',len(rows),0,0,2,table)+opaque
    return bytes(out)
def zip_bytes(items):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w') as z:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',UserWarning)
            for n,data in items:z.writestr(n,data)
    return out.getvalue()
def unpack(patch_bytes):
    with zipfile.ZipFile(io.BytesIO(patch_bytes)) as z:return {n:z.read(n) for n in z.namelist()}
def alter_manifest(component,edit):
    files=unpack(component);m=json.loads(zlib.decompress(files['manifest.zlib']));edit(m);raw=json.dumps(m,sort_keys=True,separators=(',',':')).encode();files['manifest.zlib']=zlib.compress(raw,9);files['manifest-size.txt']=str(len(raw)).encode();return zip_bytes(files.items())

class EntryPatchTests(unittest.TestCase):
    def setUp(self):
        self.base=archive([(1,b'ABC',0),(2,b'keep',0),(3,b'removed',1)])
        self.target=archive([(2,b'keep',0),(1,b'ABD!',2),(4,b'added',0)],[4,1,2],b'\x00\x10\x6b\x00')
        self.component,self.manifest=b._make_patch(self.base,self.target)
    def test_exact_bytes_metadata_layout_added_removed_and_determinism(self):
        result,m=b._restore(self.base,self.component,b.sha(self.component));self.assertEqual(result,self.target)
        self.assertEqual(result[:28],self.target[:28]);self.assertEqual(result[-84:],self.target[-84:])
        self.assertEqual(m['removed_fids'],[3]);self.assertEqual(m['statistics']['added_fids'],[4]);self.assertEqual(m['statistics']['changed_payloads'],1);self.assertEqual(m['statistics']['copied_payloads'],1)
        self.assertEqual(self.component,b._make_patch(self.base,self.target)[0])
        files=unpack(self.component);self.assertEqual({n for n in files if n.startswith('payload/')},{'payload/00000001.zlib','payload/00000004.zlib'})
        self.assertEqual(zlib.decompress(files['payload/00000001.zlib']),b'\0\0\x07!')
    def test_wrong_base_and_tampered_component(self):
        wrong=archive([(1,b'BAD',0),(2,b'keep',0),(3,b'removed',1)])
        with self.assertRaisesRegex(ValueError,'hash'):b._restore(wrong,self.component,b.sha(self.component))
        corrupt=bytearray(self.component);corrupt[len(corrupt)//2]^=1
        with self.assertRaisesRegex(ValueError,'component SHA'):b._restore(self.base,bytes(corrupt),b.sha(self.component))
        files=unpack(self.component);files['payload/00000001.zlib']=zlib.compress(b'evil')
        tampered=zip_bytes(files.items())
        with self.assertRaisesRegex(ValueError,'hash'):b._restore(self.base,tampered,b.sha(tampered))
    def test_unsupported_duplicate_paths_and_members(self):
        for name in ['../bad','/bad','payload//bad','payload\\bad','extra-file']:
            files=list(unpack(self.component).items());files.append((name,b'x'));modified=zip_bytes(files)
            with self.assertRaises(ValueError):b._restore(self.base,modified,b.sha(modified))
        files=list(unpack(self.component).items());files.append(files[0]);modified=zip_bytes(files)
        with self.assertRaisesRegex(ValueError,'duplicate ZIP'):b._restore(self.base,modified,b.sha(modified))
    def test_record_fid_partition_and_hashes(self):
        edits=[lambda m:m['records'].append(m['records'][0]),lambda m:m['removed_fids'].append(999),lambda m:m['records'][0].update(target={'bytes':999,'sha256':'0'*64}),lambda m:m['records'][0].update(kind='unknown-codec'),lambda m:m['records'][0].update(fid=True),lambda m:m['records'][0]['target'].update(bytes=True)]
        for edit in edits:
            changed=alter_manifest(self.component,edit)
            with self.assertRaises(ValueError):b._restore(self.base,changed,b.sha(changed))
    def test_nonzero_gaps_duplicate_fids_and_overlap(self):
        data=bytearray(archive([(1,b'abc',0)]));data[31]=1
        with self.assertRaisesRegex(ValueError,'padding/gap'):b.parse_npk(bytes(data))
        with self.assertRaisesRegex(ValueError,'padding/gap'):b._make_patch(self.base,bytes(data))
        table=struct.unpack_from('<I',self.target,20)[0];duplicate=bytearray(self.target);duplicate[table+28:table+32]=duplicate[table:table+4]
        with self.assertRaisesRegex(ValueError,'duplicate FID'):b.parse_npk(bytes(duplicate))
        overlap=bytearray(self.target);struct.pack_into('<I',overlap,table+28+4,28)
        with self.assertRaisesRegex(ValueError,'overlapping'):b.parse_npk(bytes(overlap))
    def test_bounded_decompression(self):
        packed=zlib.compress(b'a'*100000)
        for data,size in [(packed,10),(zlib.compress(b'abc')[:-1],3),(zlib.compress(b'abc')+b'junk',3),(zlib.compress(b'abc'),4)]:
            with self.assertRaises(ValueError):b.bounded_zlib(data,size,100000)
        with self.assertRaises(ValueError):b.bounded_zlib(packed,100001,100000)
        files=unpack(self.component);files['manifest-size.txt']=str(b.MAX_MANIFEST+1).encode();modified=zip_bytes(files.items())
        with self.assertRaisesRegex(ValueError,'bound'):b._restore(self.base,modified,b.sha(modified))
    def test_atomic_nonoverwrite_race_and_cleanup(self):
        with tempfile.TemporaryDirectory() as temp:
            out=pathlib.Path(temp)/'out';b.publish_new(out,b'old')
            with self.assertRaisesRegex(ValueError,'output exists'):b.publish_new(out,b'new')
            self.assertEqual(out.read_bytes(),b'old');out.unlink()
            link=b.os.link
            def race(source,target):
                pathlib.Path(target).write_bytes(b'other-writer');return link(source,target)
            with patch.object(b.os,'link',side_effect=race):
                with self.assertRaises(FileExistsError):b.publish_new(out,b'new')
            self.assertEqual(out.read_bytes(),b'other-writer');self.assertEqual([p.name for p in pathlib.Path(temp).iterdir()],['out'])
    def test_public_unsupported_apk_tamper_and_existing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp);fake=root/'fake.apk';fake.write_bytes(b'bad-apk');out=root/'out'
            with self.assertRaisesRegex(ValueError,'unsupported original APK'):b.reconstruct(fake,out)
            self.assertFalse(out.exists())
            bad_component=root/'bad-component';bad_component.write_bytes(b'tamper')
            with self.assertRaisesRegex(ValueError,'component SHA'):b.reconstruct(fake,out,bad_component)
            out.write_bytes(b'keep')
            with self.assertRaisesRegex(ValueError,'output exists'):b.reconstruct('missing',out)
            self.assertEqual(out.read_bytes(),b'keep')
    def test_real_full_original_apk_only_reconstruction(self):
        apk=ROOT/'originals/forever7-netease-83.apk';target=ROOT/'analysis/private-project-build/script640-original.npk'
        if not apk.is_file():self.skipTest('Pinned official APK fixture unavailable')
        before=apk.stat()
        with tempfile.TemporaryDirectory() as temp:
            out=pathlib.Path(temp)/'official640.npk';report=b.reconstruct(apk,out)
            self.assertEqual(report['sha256'],b.TARGET_SHA256)
            if target.is_file():self.assertEqual(out.read_bytes(),target.read_bytes())
            self.assertEqual(report['statistics']['changed_payloads'],66);self.assertEqual(report['statistics']['target_entries'],28754)
        after=apk.stat();self.assertEqual((before.st_size,before.st_mtime_ns,before.st_ino),(after.st_size,after.st_mtime_ns,after.st_ino))
        with apk.open('rb') as f:self.assertEqual(hashlib.file_digest(f,'sha256').hexdigest(),b.APK_SHA256)
if __name__=='__main__':unittest.main()
