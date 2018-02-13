# Copyright © 2018 Nicolás Alvarez <nicolas.alvarez@gmail.com>
# Licensed under the GPLv3 or later version.

def human_readable_size(b):
    format_strings = ["%d bytes", "%.1f KiB", "%.2f MiB", "%.2f GiB", "%.2f TiB"]
    unitn = 0
    for unit in format_strings:
        if b > 1024:
            b /= 1024
        else:
            break
    return unit % b
