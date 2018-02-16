#!/usr/bin/python3

# Copyright © 2018 Nicolás Alvarez <nicolas.alvarez@gmail.com>
# Licensed under the GPLv3 or later version.

import sys
import os
import argparse

from tqdm import tqdm

import jpegparser
import util

def parse_args():
    arg_parser = argparse.ArgumentParser(description="Tools to work with Mapillary JPEG files")
    subparsers = arg_parser.add_subparsers(metavar="subcommand", dest="subcommand")

    dir_parser = subparsers.add_parser("dir", help="Show wasted data in a local directory with JPEG files")
    dir_parser.add_argument("dir", metavar="DIR", help="the directory to scan")

    return arg_parser.parse_args()

class JpegScanner:
    def __init__(self):
        self.total_data = 0
        self.total_jpeg = 0
        self.total_waste = 0

    def scan_dir(self, dir_path):
        it = os.scandir(dir_path)
        paths = []
        for entry in sorted(it, key=lambda e: e.name):
            if entry.is_file() and entry.name.lower().endswith('.jpg') and not entry.name.endswith("-thumb.jpg"):
                paths.append(os.path.join(dir_path, entry.name))

        return self.scan_files(paths)

    def scan_files(self, paths):
        paths = tqdm(paths, unit="files")

        for file_path in paths:
            with open(file_path, "rb") as f:
                data = f.read()
            self.scan_buf(data)

            paths.set_postfix({'waste': util.human_readable_size(self.total_waste)})

    def scan_buf(self, buf):
        file_size = len(buf)
        jpeg_size = jpegparser.read_jpeg(buf)['size']
        wasted_size = file_size - jpeg_size

        self.total_data += file_size
        self.total_jpeg += jpeg_size
        self.total_waste += wasted_size

args = parse_args()

if args.subcommand != 'dir':
    raise RuntimeError("???")

scanner = JpegScanner()
scanner.scan_dir(args.dir)

print()

print("total:   %s" % (util.human_readable_size(scanner.total_data)))
print("real:    %s (%.2f%%)" % (util.human_readable_size(scanner.total_jpeg),  scanner.total_jpeg  / scanner.total_data * 100))
print("garbage: %s (%.2f%%)" % (util.human_readable_size(scanner.total_waste), scanner.total_waste / scanner.total_data * 100))
