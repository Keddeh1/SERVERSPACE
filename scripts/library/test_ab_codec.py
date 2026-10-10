import unittest
from ab_codec import pack,unpack,cascade,restore
class CodecTests(unittest.TestCase):
    def test_truth_table(self):
        self.assertEqual(pack(bytes([0b11111000])),b'AB1:8:A5B3')
        self.assertEqual(pack(b'\x00'),b'AB1:8:B8')
        self.assertEqual(pack(b'\xff'),b'AB1:8:A8')
        for i in range(256):self.assertEqual(unpack(pack(bytes([i]))),bytes([i]))
    def test_all_two_byte_values(self):
        for i in range(65536):
            raw=i.to_bytes(2,'big');self.assertEqual(unpack(pack(raw)),raw)
    def test_cascade(self):
        for depth in range(1,5):
            for raw in [b'',b'\0'*64,bytes(range(256))]:self.assertEqual(restore(cascade(raw,depth),depth),raw)
    def test_malformed(self):
        for frame in [b'AB1:8:A0B8',b'AB1:8:A4A4',b'AB1:8:A9',b'AB1:8:A7',b'AB1:08:B8',b'AB1:7:B7',b'AB1:8:B08',b'AB1:0:A1',b'AB1:8:B8junk',b'AB1:8388609:B8388609']:
            with self.assertRaises(ValueError):unpack(frame)
        for depth in [0,9,True]:
            with self.assertRaises(ValueError):cascade(b'x',depth)
if __name__=='__main__':unittest.main()
