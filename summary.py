import datetime
import os.path
import pandas as pd
import sys

from hdrh.histogram import HdrHistogram

def process_hdrfile(histo, filename):
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('#') or line.startswith('"'):
                continue

            words = line.split(",")
            blob = words[3]
            if histo is None:
                return HdrHistogram.decode(blob)
            else:
                histo.decode_and_add(blob)
                return histo


def summarize(test_dir, test_name):
    parent_directory = os.path.join(test_dir, 'runs', test_name)    
    runs = os.listdir(parent_directory)
    # pass over all directories and finde the one representing the latest run
    # could do this with a sort but the directory can contain extra junk folders which 
    # cannot be converted to a datetime and which we would break a datetime based sort
    last_run = None
    last_ts = None
    for run in runs:
        if not os.path.isdir(os.path.join(parent_directory,run)):
            continue  # CONTINUE if this is not a directory

        # determine whether this is the latest run seen so far
        try:
            ts = datetime.datetime.strptime(run, '%d-%m-%Y_%H-%M-%S')
            if last_run is None:
                last_run = run
                last_ts = ts
            else:
                if ts > last_ts:
                    last_run = run
                    last_ts = ts
        except ValueError as e:
            print(f'skipping {os.path.join(parent_directory, run)} because it has an unexpected format')
            continue

    if last_run is None:
        sys.exit(f'Could not find any runs in "{parent_directory}"')

    ts = last_ts
    run = last_run

    # now that we've found the latest run, determine, find all of the *client directories
    rundir = os.path.join(parent_directory, run)
    clientdirs = []
    for d in os.listdir(rundir):
        if not os.path.isdir(os.path.join(rundir, d)):
            continue

        if d.endswith("client"):
            clientdirs.append(os.path.join(rundir,d))

    # run through each client directory and compute the throughput for the whole test as well as the 99% latency
    elapsed = 0
    opcount = 0
    get_histo = None
    put_histo = None
    for clientdir in clientdirs:
        opfile = os.path.join(clientdir,'operations.csv')
        print(f'reading {opfile}')
        df = pd.read_csv(opfile)
        
        # assuming 1 sample per second, elapsed is just number of rows
        elapsed = max(elapsed, df.shape[0])
        opcount += df.operations.max()

        gethistofile = os.path.join(clientdir, 'map.get.hdr')
        puthistofile = os.path.join(clientdir, 'map.put.hdr')

        print(f'reading {gethistofile}')            
        get_histo = process_hdrfile(get_histo, gethistofile)

        print(f'reading {puthistofile}')            
        put_histo = process_hdrfile(put_histo, puthistofile)

    ops_per_second = int(opcount / elapsed)
    get_latency_99 = get_histo.get_value_at_percentile(99.0) / 1_000_000
    put_latency_99 = put_histo.get_value_at_percentile(99.0) / 1_000_000

    return ops_per_second, get_latency_99, put_latency_99

