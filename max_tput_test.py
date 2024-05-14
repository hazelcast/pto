import argparse
import sys
import subprocess
import os.path
import yaml

from summary import summarize

MAX_THREADS_PER_CORE = 10
INITIAL_CONCURRENCY_PER_LOADGENERATOR = 1     
MAX_99PCT_LATENCY_MS = 5
RATE_PER_THREAD = 100
TEST_CYCLE_DURATION_S = 100


# Determine the number of load generators available and the number of cores 
# on the load generator machines. This function will call sys.exit if 
# the inventory information cannot be collected
def collect_loadgenerator_info(inventory_file):

    # inspect the inventory file to determin
    with open(inventory_file,'r') as f:
        inventory = yaml.safe_load(f)

    loadgenerators = list(inventory['loadgenerators']['hosts'].keys())
    keyfile = inventory['all']['vars']['ansible_ssh_private_key_file']
    user = inventory['all']['vars']['ansible_user']

    if len(loadgenerators) == 0:
        sys.exit(f'No loadgenerators found in {inventory}')

    result = subprocess.run(f'ssh -i {keyfile} {user}@{loadgenerators[0]} lscpu -e', shell=True, capture_output=True)
    if result.returncode != 0:
        print(result.stdout, sys.stdout)
        print(result.stderr, sys.err)
        sys.exit('An error occurred while checking loadgenerator cpu count')

    lines = result.stdout.splitlines()

    loadgenerator_count = len(loadgenerators)
    loadgenerator_cpu_count = len(lines) - 1
    return loadgenerator_count, loadgenerator_count


def setup_test(test_file, loadgenerator_count, concurrency):
    # overwrite the test.yaml for the initial concurrency 
    with open(test_file,'r') as f:
        test_config = yaml.safe_load(f)

    thread_count = int(concurrency / loadgenerator_count)

    test_config[0]['duration'] = f'{TEST_CYCLE_DURATION_S}s'
    test_config[0]['clients'] = loadgenerator_count
    test_config[0]['test'][0]['threadCount'] = thread_count
    test_config[0]['test'][0]['ratePerSecond'] = thread_count * RATE_PER_THREAD

    with open(test_file,'w') as f:
        yaml.safe_dump(test_config, f)

    return test_config[0]['name']


#
# Begin main program
#
if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser(description='Orcehstrate a maximum throughput test.',
                                    add_help=True)
    parser.add_argument('--test-dir', required=True, help='The directory containing the performance test')
    args = parser.parse_args(sys.argv[1:])

    test_dir = args.test_dir
    if not os.path.isdir(test_dir):
        sys.exit(f'exiting because "{test_dir}" is not a valid directory.')

    test_dir = os.path.abspath(test_dir)
    test_file = os.path.join(test_dir,'tests.yaml')


    # determine how many load generators are available and how many cores on each
    inventory_file = os.path.join(test_dir,'inventory.yaml')
    loadgenerator_count, loadgenerator_cpu_count = collect_loadgenerator_info(inventory_file)
    max_concurrency = loadgenerator_count * loadgenerator_cpu_count * MAX_THREADS_PER_CORE
    print(f'There are {loadgenerator_count} load generators, each with {loadgenerator_cpu_count} cpus', file=sys.stdout)
    print(f'Maximum acheivable throughput: ' + str(max_concurrency * RATE_PER_THREAD), file=sys.stdout)

    # begin seeking highest acceptable throughput
    fastest_success = 0
    slowest_fail = 999_999_999
    next_test = INITIAL_CONCURRENCY_PER_LOADGENERATOR * loadgenerator_count
    while next_test - fastest_success > 1:
        # setup concurrency for next_test
        if next_test >  max_concurrency:
            print("Test reached maximum concurrency.  Exiting")
            break

        test_name = setup_test(test_file, loadgenerator_count, next_test)
        print(f"Test configured for {next_test * RATE_PER_THREAD} tps")

        # run the test
        result = subprocess.run('perftest run --skipReport', shell=True, cwd=test_dir)
        if result.returncode != 0:
            sys.exit(f"Test failed to run.  Exiting.")
         
        # collect the results
        tput, get_latency_99, put_latency_99 = summarize(test_dir, test_name)
        print(f'TEST SUMMARY\nThroughput: {tput} ops/sec\nGet Latency 99: {get_latency_99}ms\nPut Latency 99: {put_latency_99}ms')
        target_tput = next_test * RATE_PER_THREAD
        success = True
        if tput < .95*target_tput or tput > 1.05*target_tput:
            success = False
            print(f'THROUGHPUT: FAILED')
        else:
            print(f'THROUGHPUT: PASSED')

        if get_latency_99 > MAX_99PCT_LATENCY_MS:
            success = False
            print(f'GET LATENCY: FAILED')
        else:
            print(f'GET LATENCY: PASSED')

        if put_latency_99 > MAX_99PCT_LATENCY_MS:
            success = False
            print(f'PUT LATENCY: FAILED')
        else:
            print(f'PUT LATENCY: PASSED')

        # calculate new slowest fail or fastest success and the new next_test
        if success: 
            fastest_success = next_test
            next_test = fastest_success * 2 if slowest_fail == 999_999_999 else int((fastest_success + slowest_fail)/2)
        else:
            slowest_fail = next_test
            next_test = next_test = int((fastest_success + slowest_fail) / 2)


    print(f'MAXIMUM THROUGHPUT ACHIEVED: {fastest_success} ops/sec')
