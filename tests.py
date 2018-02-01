#!/usr/bin/python3

# Copyright © 2018 Nicolás Alvarez <nicolas.alvarez@gmail.com>
# Licensed under the GPLv3 or later version.

import unittest
import io

import jpegparser

MARKER_SOI = b'\xff\xd8'
MARKER_SOS = b'\xff\xDA'
MARKER_EOI = b'\xff\xd9'

def MARKER_APP(n):
    if 0 <= n <= 0xf:
        return bytes([0xff, 0xe0 | n])
    else:
        raise ValueError()

class BasicTest(unittest.TestCase):
    def test_basic(self):
        """
        Tests a basic JFIF structure.
        """
        #                 2     +      2        +            16              + 2
        data = bytes(MARKER_SOI + MARKER_APP(0) + b'\x00\x10' + 14*b'a' + MARKER_EOI + b'garbage')
        result = jpegparser.read_jpeg(io.BytesIO(data))

        self.assertEqual(result, {'size': 2+2+16+2})

    def test_embedded_ff(self):
        """
        Tests a segment containing a FFD9 marker inside, which should be ignored.
        """
        #                 2     +      2        +       2     +       9            + 2
        data = bytes(MARKER_SOI + MARKER_APP(0) + b'\x00\x0b' + b'asd\xff\xd9quux' + MARKER_EOI + b'garbage')
        result = jpegparser.read_jpeg(io.BytesIO(data))

        self.assertEqual(result, {'size': 2+2+2+9+2})

    def test_entropy_basic(self):
        """
        Tests a SOS segment followed by entropy data.
        """
        data = bytes(MARKER_SOI +           # 2
                     MARKER_APP(0) +        # 2
                     b'\x00\x05' + b'asd' + # 5
                     MARKER_SOS +           # 2
                     b'\x00\x06' + b'foox'+ # 6
                     b'entropydata' +       # 11
                     MARKER_EOI +           # 2
                     b'garbage')
        result = jpegparser.read_jpeg(io.BytesIO(data))

        self.assertEqual(result, {'size': 2+2+5+2+6+11+2})

    def test_real(self):
        with open("/home/nicolas/Mapillary/photos/2017_10_10_16_49_24_691/2017_10_10_16_49_48_117.jpg", "rb") as f:
            print(jpegparser.read_jpeg(f))


if __name__ == '__main__':
    unittest.main()
