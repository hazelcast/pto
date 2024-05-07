import argparse
import json
import re
import sys
import subprocess
import os.path

parser = argparse.ArgumentParser(description='Runs a CF template to set up a performance test environment',
                                 add_help=True)
parser.add_argument('--template', required='True', help='path to a cloudformation template')
parser.add_argument('--stack-name', required=True, help='a unique name for the cloud formation stack')
parser.add_argument('--key-name', required=True, help='the name of the ssh key to install on all servers')

args = parser.parse_args(sys.argv[1:])

templatefile = args.template
stack_name = args.stack_name
key_name = args.key_name

if not os.path.isfile(templatefile):
    sys.exit(f'exiting because {templatefile} was not found')

with open(templatefile, 'r') as f:
    template = f.read()

result = subprocess.run(['aws','cloudformation','create-stack', 
                         '--stack-name', stack_name, 
                         '--template-body', template, 
                         '--parameters', f'ParameterKey=KeyName,ParameterValue={key_name}',
                         '--output', 'json'], 
                         capture_output=True)

if result.returncode != 0:
    sys.exit('Cloudformation stack creation failed.  Check the AWS console for details')

stack_id = json.loads(result.stdout)['StackId']
print(f'stack is deploying: {stack_id}')

result = subprocess.run(['aws','cloudformation','wait','stack-create-complete', '--stack-name', stack_name])
if result.returncode != 0:
    sys.exit("Stack creation could not be verified.  Check the AWS console")

result = subprocess.run(
    ['aws','cloudformation','describe-stacks', '--stack-name', stack_name, '--output', 'json'], 
    capture_output=True)

if result.returncode != 0:
    sys.exit("Stack information could not be retrieved but the stack has been created.")

stack_description = json.loads(result.stdout)
if stack_description['Stacks'][0]['StackId'] != stack_id:
    sys.exit('Internal error. Did not retrieve the correct stack information')

# build up a representation of the output values  each is dictionary 
#  where the key is the item number (1 for Server1) and the value is a dicts with the 
# keys being  "PublicIP" or "PrivateIP" and the value being the value of the output variable
pattern = re.compile(r"(\D+)(\d+)(\D+)")

servers = {}
perftesters = {}
viewers = {}
for output in stack_description['Stacks'][0]['Outputs']:
    key = output['OutputKey']
    value = output['OutputValue']
    match = pattern.match(key)
    if not match:
        print(f'WARNING: ignoring unexpected key "{key}" in stack output.')
        continue

    item_type = match.group(1)
    item_num = int(match.group(2))
    item_attr = match.group(3)
    
    if item_type == 'Server':
        selected_dict = servers
    elif item_type == 'LoadTest':
        selected_dict = perftesters
    elif item_type == 'Viewer':
        selected_dict = viewers
    else:
        print(f'WARNING: ignoring nn output key with an unrecognized type "{item_type}"')
        continue

    attrs = selected_dict.setdefault(item_num, dict())
    attrs[item_attr] = value


inventory_file = os.path.join(os.path.dirname(templatefile),'inventory.ini')
with open(inventory_file,'w') as f:
    f.write('[servers]\n')
    for n, attrs in sorted(servers.items()):
        f.write(f"{attrs['PublicIP']} private_ip={attrs['PrivateIP']}\n")

    f.write('\n')
    f.write('[loadtesters]\n')
    for n, attrs in sorted(perftesters.items()):
        f.write(f"{attrs['PublicIP']} private_ip={attrs['PrivateIP']}\n")

    f.write('\n')
    f.write('[viewers]\n')
    for n, attrs in sorted(viewers.items()):
        f.write(f"{attrs['PublicIP']} private_ip={attrs['PrivateIP']}\n")

print(f'wrote inventory to {inventory_file}')







