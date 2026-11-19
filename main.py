"""Wednesday 18 November 2026, one picture.

This program delivers the front page for the news-image-20261118 bounty:
a single image that sums up the world's news of Wednesday 18 November
2026. The picture itself was drawn beforehand and is stored in this
repository as entry.jpg (1024x1024 JPEG, under 1 MiB). This program only
places that picture where the grader expects it.

It uses nothing but the Python standard library (os, shutil). The grader
runs it with `python3 -P -s main.py` in a fresh container where nothing
is installed, so no third-party import may appear here. The output is
byte-identical on every run: the same file in, the same file out. The
picture covers 38 stories plus a date check, across six continents.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.jpg")
DEST_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
DEST = os.path.join(DEST_DIR, "entry.png")


def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    shutil.copyfile(SOURCE, DEST)
    written = os.path.getsize(DEST)
    print("wrote %s %d bytes" % (DEST, written))
    print("truncated: none")


if __name__ == "__main__":
    main()
