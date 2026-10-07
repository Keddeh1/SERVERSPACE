import tempfile,unittest
from pathlib import Path
from vfs_library import Library,sha
class LibraryTests(unittest.TestCase):
    def test_identity_revision_and_source_independence(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);p=root/'paper.md';p.write_text('first');lib=Library(root/'vfs')
            i=lib.add(p,'SECTOR_FOUNDATIONS');p.write_text('second')
            self.assertEqual(i,lib.add(p,'SECTOR_FOUNDATIONS'));p.unlink()
            self.assertEqual(lib.get(i),b'second');self.assertEqual(lib.verify(),[])
            self.assertEqual(lib.db.execute('SELECT COUNT(*) FROM revision').fetchone()[0],2);lib.close()
            lib=Library(root/'vfs');self.assertEqual(lib.get(i),b'second');lib.close()
    def test_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'paper';p.write_bytes(b'evidence');lib=Library(Path(t)/'vfs');i=lib.add(p,'SECTOR_FOUNDATIONS')
            (lib.blobs/sha(b'evidence')).write_bytes(b'bad')
            with self.assertRaises(ValueError):lib.get(i)
            self.assertEqual(len(lib.verify()),1);lib.close()
    def test_packed_carrier_requires_exact_decode_and_digest(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'paper';p.write_bytes(b'\0'*64);lib=Library(Path(t)/'vfs');i=lib.add(p,'SECTOR_FOUNDATIONS')
            meta=lib.pack_ab(i,2);self.assertEqual(lib.get_ab(i,2),p.read_bytes())
            Path(meta['carrier']).write_bytes(b'AB1:0:')
            with self.assertRaises(ValueError):lib.get_ab(i,2)
            lib.close()
if __name__=='__main__':unittest.main()
