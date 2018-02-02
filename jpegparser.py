# Copyright © 2018 Nicolás Alvarez <nicolas.alvarez@gmail.com>
# Licensed under the GPLv3 or later version.

import io
import struct

MARKER_SOI = 0xd8
MARKER_EOI = 0xd9
MARKER_SOS = 0xda

STANDALONE_MARKERS = (
    [MARKER_SOI, MARKER_EOI, 0x01] +
    [0xd0 + n for n in range(8)] # RST markers
)

class JpegReader:
    def __init__(self, fp):
        self.buf = fp.read()
        self.ptr = 0

    def skip_segment(self):
        """
        Returns the segment type and size, but skips over the data.
        Leaves the stream ready to read the next marker, including the 0xff.
        """
        print("Location: %d" % self.ptr)
        has_ff = False
        while self.buf[self.ptr] == 0xff:
            print("Saw a ff...")
            has_ff = True
            self.ptr += 1

        if not has_ff:
            raise RuntimeError("wtf? found %02x instead" % self.buf[self.ptr])

        marker = self.buf[self.ptr]
        self.ptr += 1

        if marker in STANDALONE_MARKERS:
            print("This is a standalone %02X marker" % marker)
            return (marker, 0)
        else:
            print("This is non-standalone %02X marker, there should be a length next" % marker)
            length_bytes = self.buf[self.ptr : self.ptr+2]
            # this length includes the 2 length bytes
            length = struct.unpack('>H', length_bytes)[0]

            # skip over the segment contents
            self.ptr += length
            return (marker, length)

    def skip_entropy(self):
        while True:
            if self.buf[self.ptr] == 0xff:
                b2 = self.buf[self.ptr+1]
                if b2 == 0x00:
                    # this is just an escaped ff in the entropy data
                    self.ptr += 2
                    continue
                elif 0xd0 <= b2 <= 0xd7:
                    # this is a restart marker, skip it
                    self.ptr += 2
                    continue
                else:
                    # this is an actual marker; quit
                    return
            else:
                self.ptr += 1

    def read_jpeg(self):
        segment = self.skip_segment()
        while segment[0] != MARKER_EOI:
            print("[%02X] length %d" % segment)
            if segment[0] == MARKER_EOI:
                break
            elif segment[0] == MARKER_SOS:
                # skip until the next segment
                prev_pos = self.ptr
                self.skip_entropy()
                print("Skipped %d bytes of entropy data" % (self.ptr - prev_pos))

            segment = self.skip_segment()

        return {'size': self.ptr}

def read_jpeg(fp):
    reader = JpegReader(fp)
    return reader.read_jpeg()
