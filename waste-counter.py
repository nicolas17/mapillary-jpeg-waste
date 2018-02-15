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

args = parse_args()

if args.subcommand != 'dir':
    raise RuntimeError("???")

dir_path = args.dir

total_data = 0
total_jpeg = 0
total_waste = 0

it = os.scandir(dir_path)
entries = []
for entry in sorted(it, key=lambda e: e.name):
    if entry.is_file() and entry.name.lower().endswith('.jpg') and not entry.name.endswith("-thumb.jpg"):
        entries.append(entry)

bar = tqdm(entries, unit="files")
for entry in bar:
    file_path = os.path.join(dir_path, entry.name)
    file_size = entry.stat().st_size
    with open(file_path, "rb") as f:
        jpeg_size = jpegparser.read_jpeg(f.read())['size']
    wasted_size = file_size - jpeg_size

    #print("%d\t%.2f%%\t%s" % (wasted_size, wasted_size / file_size * 100, file_path))

    total_data += file_size
    total_jpeg += jpeg_size
    total_waste += wasted_size
    bar.set_postfix({'waste': util.human_readable_size(total_waste)})

print()

print("total:   %s" % (util.human_readable_size(total_data)))
print("real:    %s (%.2f%%)" % (util.human_readable_size(total_jpeg),  total_jpeg  / total_data * 100))
print("garbage: %s (%.2f%%)" % (util.human_readable_size(total_waste), total_waste / total_data * 100))
