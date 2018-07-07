# ansible_fetch_terraform_backend_outputs
Ansible module that fetches output dictionary from Terraform tfstate file from s3 backend.

## Requirements
* boto3 
* json 

## Module Options
* bucket - Name of the s3 bucket where Terraform state is stored. Required.
* object - Name of the s3 object where Terraform state is stored. Required.
* aws_profile - Name of the aws profile to be used. Default "default".
* aws_access_key - AWS access key to be used for bucket access. If declared aws_profile option is ignored and aws_secret_access_key option is required. Default "".
* aws_secret_access_key - AWS secret access key to be used for bucket access. If declared aws_profile option is ignored and aws_access_key option is required. Default "".
* aws_region - ID of AWS region to connect to s3 bucket from. Default "us-east-1".


## Examples
The following play fetches Terraform outputs from arn:aws:s3:::terraform-state-repository/ireland/katapult_cloud_networking.tfstate using default AWS profile in `~/.aws/credentials`.
```yaml
---
- hosts: localhost
  become: false
  tasks:
    - name: fetch Terraform networking outputs from Ireland region
      fetch_terraform_backend_outputs:
        bucket: "terraform-state-repository"
        object: "ireland/katapult_cloud_networking.tfstate"
      register: vpc_networking

    - name: set vpc id
      set_fact:
        vpc_id: "{{ vpc_networking.vars.katapult_cloud_vpc_id }}"
...
```
The following play fetches Terraform outputs from arn:aws:s3:::terraform-state-repository/ireland/katapult_cloud_networking.tfstate using AWS access and secret access keys.
```yaml
---
- hosts: localhost
  become: false
  tasks:
    - name: fetch Terraform networking outputs from Ireland region
      fetch_terraform_backend_outputs:
        bucket: "terraform-state-repository"
        object: "ireland/katapult_cloud_networking.tfstate"
        aws_access_key: AAABBBTTGSSSS45
        aws_secret_access_key: jbd63ij2bdft/812ebud1f2623m2837rmmqj
      register: vpc_networking

    - name: set vpc id
      set_fact:
        vpc_id: "{{ vpc_networking.vars.katapult_cloud_vpc_id }}"
...
```
## Recommendations
Utilize profile or access keys with minimal privileges to AWS resources. If possible utilize credentials with read only access to the Terraform state bucket.

## License
MIT

## Author Information
Stefan Roman (stefan.roman@katapult.cloud)
