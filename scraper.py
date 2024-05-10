import datetime
import os.path
import requests 
import time
import yaml

PROMETHEUS_PORT = 9090
STATS_COLLECTION_PERIOD_S = 10

def get_hosts(group_list):
    scriptdir = os.path.dirname(os.path.realpath(__file__))
    inventory_file = os.path.join(scriptdir, 'inventory.yaml')

    with open(inventory_file, 'r') as f:
        inventory = yaml.safe_load(f)

    hosts = []
    for g in group_list:
        hosts += [ h for h in inventory[g]['hosts'].keys() ] 

    return hosts

def write_cpu_stat(f, t, val, attr_dict):
    print(f'{t},{attr_dict['host']},{val}', file=f)

def write_net_stat(f, t, val, attr_dict):
    print(f'{t},{attr_dict['source']},{attr_dict['destination']},{val}', file=f)

scriptdir = os.path.dirname(os.path.realpath(__file__))
all_hosts = get_hosts(['servers','loadtesters','viewers'])
network_file_name = os.path.join(scriptdir,'network.csv')
cpu_file_name = os.path.join(scriptdir, 'cpu.csv')

now = time.time()
next_run = now + STATS_COLLECTION_PERIOD_S
while True:
    sleep_time = next_run - now
    if sleep_time > .5:
        time.sleep(sleep_time)

    with open(network_file_name,'a') as netfile:
        with open(cpu_file_name,'a') as cpufile:
            for server in all_hosts:
                req = requests.get(f'http://{server}:{PROMETHEUS_PORT}/metrics')
                if req.status_code == 200:
                    timestamp = datetime.datetime.now().isoformat()
                    for line in req.text.splitlines():
                        if not line.startswith('#'):
                            l = line.find('{')
                            r = line.find('}', l+1)
                            metric_name = line[0:l]
                            attr_list = line[l+1:r].split(",")
                            attr_dict = dict()
                            for attr in attr_list:
                                e = attr.find('=')
                                attr_dict[attr[0:e]]=attr[e+2:-1]
                            metric_val = line[r+2:]
                            if metric_name == 'load_average_1m':
                                write_cpu_stat(cpufile,timestamp, metric_val, attr_dict)
                            elif metric_name == 'heartbeat_latency_ms':
                                write_net_stat(netfile, timestamp, metric_val, attr_dict)


    now = time.time()
    next_run += STATS_COLLECTION_PERIOD_S


for host in all_hosts:
    metrics = requests.get(f'http://{host}:{PROMETHEUS_PORT}/metrics')
    if metrics.status_code == 200:
        print(metrics.text)
        print('------------------------------------')


