DOCUMENTATION = '''
---
module: s3_terraform_backend
short_description: Get output variables from Terraform s3 backend
'''

EXAMPLES = '''
- name: Get Terraform EFS backend variables
  s3_terraform_backend:
    bucket: "example-bucket"
    key: "storage/terraform.tfstate"
  register: storage

- name: Mount EFS storage
  mount:
    state: "mounted"
	path: /mnt
    src: "{{ storage.meta.efs_id }}"
    fstype: efs
    opts: rw
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
	obj = s3.Object(data['bucket'], data['key'])
	raw_data = obj.get()['Body'].read().decode('utf-8') 
	return format_data(raw_data)


def build_client(data, ansible_module):
	aws_access_key = data['aws_access_key']
	aws_secret_access_key = data['aws_secret_access_key']
	aws_profile = data['aws_profile']
	aws_region = data['aws_region']
	if aws_access_key and aws_secret_access_key:
		return boto3.session.Session(aws_access_key_id=aws_access_key, 
									 aws_secret_access_key=aws_secret_access_key,
									 region_name=aws_region)
	elif not aws_access_key and not aws_secret_access_key:
		return boto3.session.Session(profile_name=aws_profile)
	else:
		return False


def main():

	arguments = {
		"bucket": {"required": True, "type": "str"},
		"key": {"required": True, "type": "str"},
		"aws_profile": {"default": "default", "type": "str"},
		"aws_access_key": {"default": "", "type": "str"},
		"aws_secret_access_key": {"default": "", "type": "str"},
		"aws_region": {"default": "us-east-1", "type": "str"}
	}

	module = AnsibleModule(argument_spec=arguments)
	s3_client = build_client(module.params, module)

	if s3_client:
		result = backend_pull(s3_client, module.params)
		module.exit_json(changed=False, meta=result)
	else:
		module.fail_json(msg="Wrong AWS credentials")

if __name__ == '__main__':
    main()