# Copyright © 2018 Nicolás Alvarez <nicolas.alvarez@gmail.com>
# Licensed under the GPLv3 or later version.

import io
import struct
import logging

logger = logging.getLogger(__name__)

MARKER_SOI = 0xd8
MARKER_EOI = 0xd9
MARKER_SOS = 0xda

STANDALONE_MARKERS = (
    [MARKER_SOI, MARKER_EOI, 0x01] +
    [0xd0 + n for n in range(8)] # RST markers
)

class JpegReader:
    def __init__(self, data):
        self.buf = data
        self.ptr = 0

    def skip_segment(self):
        """
        Returns the segment type and size, but skips over the data.
        Leaves the stream ready to read the next marker, including the 0xff.
        """
        logger.debug("Location: %d", self.ptr)
        has_ff = False
        while self.buf[self.ptr] == 0xff:
            logger.debug("Saw a ff...")
            has_ff = True
            self.ptr += 1

        if not has_ff:
            raise RuntimeError("wtf? found %02x instead" % self.buf[self.ptr])

        marker = self.buf[self.ptr]
        self.ptr += 1

        if marker in STANDALONE_MARKERS:
            return (marker, 0)
        else:
            length_bytes = self.buf[self.ptr : self.ptr+2]
            # this length includes the 2 length bytes
            length = struct.unpack('>H', length_bytes)[0]

            # skip over the segment contents
            self.ptr += length
            return (marker, length)

    def skip_entropy(self):
        while True:
            # Fast skip of non-FF bytes
            idx = self.buf.find(b'\xff', self.ptr)
            if idx != -1:
                self.ptr = idx

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
                # Is it even possible to get a non-FF here?
                # Surely the fast-skip would land us on one.
                # Perhaps on an invalid, truncated file?
                logger.warning("Non-FF found at %d (corrupted file?)" % self.ptr)
                self.ptr += 1

    def read_jpeg(self):
        marker, length = self.skip_segment()
        while marker != MARKER_EOI:
            logger.debug("Marker %02X length %d", marker, length)
            if marker == MARKER_EOI:
                break
            elif marker == MARKER_SOS:
                # skip until the next segment
                prev_pos = self.ptr
                self.skip_entropy()
                logger.debug("Skipped %d bytes of entropy data", self.ptr - prev_pos)

            marker, length = self.skip_segment()

        return {'size': self.ptr}

def read_jpeg(data):
    reader = JpegReader(data)
    return reader.read_jpeg()
