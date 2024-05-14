import os.path
import sys

from hdrh.histogram import HdrHistogram

scriptdir = os.path.abspath(os.path.dirname(__file__))
testfile = os.path.join(scriptdir,'..','pto-sample-test','./runs/read_write/14-05-2024_14-14-54/A6_W1-54.218.106.220-javaclient/map.get.hdr')

histo = None
with open(testfile, 'r') as f:
    for line in f:
        if line.startswith('#'):
            continue

        if line.startswith('"'):
            continue

        words = line.split(",")
        blob = words[3]
        if histo is None:
            histo = HdrHistogram.decode(blob)
        else:
            histo.decode_and_add(blob)

HdrHistogram.dump(histo.encode(), output_value_unit_scaling_ratio=1_000_000)
