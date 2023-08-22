import boto3
import time
import docker
import os


aws_access_key = 'AWS_ACCESS_KEY'
aws_secret_key = 'AWS_SECRET_KEY'
aws_region = 'eu-west-1'

dockerhub_username = 'DOCKERHUB_USERNAME'
dockerhub_password = 'DOCKERHUB_PASSWORD'

ec2 = boto3.resource(
    'ec2',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)

instance = ec2.create_instances(
    ImageId='ami-0eb260c4d5475b901',
    InstanceType='t2.micro',
    MinCount=1,
    MaxCount=1,
    KeyName='key-pair',
    SecurityGroupIds=['default'],
    UserData='''#!/bin/bash
                apt-get update -y
                apt-get upgrade -y
                apt-get install install docker -y
                service docker start
                usermod -aG docker ubuntu
                docker run -d -p 5000:5000 --restart=always --name registry registry:2
                '''
)

instance[0].wait_until_running()
instance[0].reload()

instance_ip = instance[0].public_ip_address
print(f"Instance is running at IP: {instance_ip}")

instance_ip = instance[0].public_ip_address
docker_client = docker.DockerClient(base_url=f"tcp://{instance_ip}:2375")

registry_images = docker_client.images.list()
print("Images in the registry:")
for image in registry_images:
    print(image.tags)
