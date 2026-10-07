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
if __name__=='__main__':unittest.main()
