import unittest
from ab_codec import compact_pack,compact_unpack
class CompactTests(unittest.TestCase):
    def test_owner_mapping(self):
        self.assertEqual(compact_pack(b'\xf8'),b'ABC1:8:GN')
        self.assertEqual(compact_pack(b'\xff'),b'ABC1:8:J')
        self.assertEqual(compact_pack(b'\x00'),b'ABC1:8:S')
        self.assertEqual(compact_pack(b'\xff\xff'),b'ABC1:16:KI')
    def test_exhaustive(self):
        for n in range(65536):
            raw=n.to_bytes(2,'big');self.assertEqual(compact_unpack(compact_pack(raw)),raw)
    def test_empty_long_and_cascade(self):
        for raw in [b'',b'\0'*1024,bytes(range(256))]:
            outer=compact_pack(compact_pack(raw))
            self.assertEqual(compact_unpack(compact_unpack(outer)),raw)
    def test_invalid(self):
        for frame in [b'ABC1:8:CCQ',b'ABC1:8:Z',b'ABC1:8:K',b'ABC1:08:S',b'ABC1:0:C']:
            with self.assertRaises(ValueError):compact_unpack(frame)
if __name__=='__main__':unittest.main()
