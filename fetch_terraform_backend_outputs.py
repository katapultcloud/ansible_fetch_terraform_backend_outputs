#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Stefan Roman <stefan.roman@katapult.cloud>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'status': ['preview'],
    'supported_by': 'community',
    'metadata_version': '1.1'
}

DOCUMENTATION = '''
---
module: fetch_terraform_backend_outputs
short_description: Get output variables from Terraform s3 backend.
description:
  - Get output variables from Terraform s3 backend.
version_added: "2.4"
author: Stefan Roman (@katapultcloud)
options: 
  bucket:
    description: 
      - Name of the s3 bucket where Terraform state is stored.
    required: true
  object:
    description: 
      - Name of the s3 object where Terraform state is stored.
    required: true
  aws_profile:
    description: 
      - Name of the aws profile to be used.
    default: "default"
  aws_access_key:
    description: 
      - AWS access key to be used for bucket access.
      - If declared aws_profile option is ignored and aws_secret_access_key option is required. 
    default: ""
  aws_secret_access_key:
    description: 
      - AWS secret access key to be used for bucket access.
      - If declared aws_profile option is ignored and aws_access_key option is required.
    default: ""
  aws_region:
    description: 
      - ID of AWS region to connect to s3 bucket from.
    default: "us-east-1"
...
'''

EXAMPLES = '''
---
- name: Get Terraform EFS backend variables
  fetch_terraform_backend_outputs:
    bucket: "example-bucket"
    object: "storage/terraform.tfstate"
  register: terraform_storage

- name: Mount EFS storage
  mount:
    state: "mounted"
	path: /mnt
    src: "{{ terraform_storage.vars.efs_id }}"
    fstype: efs
    opts: rw
...
'''

RETURN = '''
---
vars:
  description: 
    - Outputs from Terraform backend in JSON format are returned upon successful execution.
  type: json
  returned: success
  version_added: "2.4"
...
'''

from ansible.module_utils.basic import *
import pprint
import boto3
import json


def format_data(data):
    pretty_data = json.loads(data)
    buffer = {}
    result = {}
    for element in pretty_data['modules']:
        buffer = {}
        buffer = element['outputs']
        permanent = buffer.copy()
        permanent.update(buffer)

    for key, value in permanent.iteritems():
        result[key] = value['value']
    return result


def backend_pull(client, data):
    s3 = client.resource('s3')
    obj = s3.Object(data['bucket'], data['object'])
    raw_data = obj.get()['Body'].read().decode('utf-8')
    return format_data(raw_data)


def build_client(data, ansible_module):
    aws_access_key = data['aws_access_key']
    aws_secret_access_key = data['aws_secret_access_key']
    aws_profile = data['aws_profile']
    aws_region = data['aws_region']
    if aws_access_key and aws_secret_access_key:
        return boto3.session.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region)
    elif not aws_access_key and not aws_secret_access_key:
        return boto3.session.Session(profile_name=aws_profile)
    else:
        return False


def main():

    arguments = {
        "bucket": {
            "required": True,
            "type": "str"
        },
        "object": {
            "required": True,
            "type": "str"
        },
        "aws_profile": {
            "default": "default",
            "type": "str"
        },
        "aws_access_key": {
            "default": "",
            "type": "str"
        },
        "aws_secret_access_key": {
            "default": "",
            "type": "str"
        },
        "aws_region": {
            "default": "us-east-1",
            "type": "str"
        }
    }

    module = AnsibleModule(argument_spec=arguments)
    s3_client = build_client(module.params, module)

    if s3_client:
        result = backend_pull(s3_client, module.params)
        module.exit_json(changed=False, vars=result)
    else:
        module.fail_json(msg="Wrong AWS credentials")


if __name__ == '__main__':
    main()
