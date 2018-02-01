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

def skip_segment(fp):
    """
    Returns the segment type and size, but skips over the data.
    Leaves the stream ready to read the next marker, including the 0xff.
    """
    print("Location: %d" % fp.tell())
    has_ff = False
    b = fp.read(1)[0]
    while b == 0xff:
        print("Saw a ff...")
        has_ff = True
        b = fp.read(1)[0]

    if not has_ff:
        raise RuntimeError("wtf? found %02x instead" % b)

    marker = b

    if marker in STANDALONE_MARKERS:
        print("This is a standalone %02X marker" % marker)
        return (marker, 0)
    else:
        print("This is non-standalone %02X marker, there should be a length next" % marker)
        length_bytes = fp.read(2)
        length = struct.unpack('>H', length_bytes)[0]-2
        if fp.seekable:
            fp.seek(length, io.SEEK_CUR)
        else:
            fp.read(length) # throw away the result
        return (marker, length)

def skip_entropy(fp):
    b = fp.read(1)[0]
    n = 1
    while True:
        if b == 0xff:
            b2 = fp.read(1)[0]
            n += 1
            if b2 == 0x00:
                # this is just an escaped ff in the entropy data
                pass
            elif 0xd0 <= b2 <= 0xd7:
                # this is a restart marker, skip it
                pass
            else:
                # this is an actual marker; rewind
                fp.seek(-2, io.SEEK_CUR)
                return n
        b = fp.read(1)[0]
        n += 1

def read_jpeg(fp):
    segment = skip_segment(fp)
    while segment[0] != MARKER_EOI:
        print("[%02X] length %d" % segment)
        if segment[0] == MARKER_EOI:
            break
        elif segment[0] == MARKER_SOS:
            # skip until the next segment
            entropy_length = skip_entropy(fp)
            print("Skipped %d bytes of entropy data" % entropy_length)

        segment = skip_segment(fp)

    return {'size': fp.tell()}
