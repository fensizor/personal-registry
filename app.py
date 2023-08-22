import boto3
import time
import docker
import os
from dotenv import load_dotenv

load_dotenv()

aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = 'eu-west-1'

dockerhub_username = os.getenv('DOCKERHUB_USERNAME')
dockerhub_password = os.getenv('DOCKERHUB_PASSWORD')

ec2 = boto3.resource(
    'ec2',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)

instance = ec2.create_instances(
    ImageId='ami-01dd271720c1ba44f',
    InstanceType='t2.micro',
    MinCount=1,
    MaxCount=1,
    KeyName='ubuntu',
    SecurityGroupIds=['python'],
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

docker_client = docker.DockerClient(base_url=f"tcp://{instance_ip}:2375")

image_to_pull = input("Enter the Docker image name: ")

client = docker.from_env()
client.login(username=dockerhub_username, password=dockerhub_password)

client.images.pull(image_to_pull)

new_image_tag = f"{instance_ip}:5000/my-registry/{image_to_pull.split(':')[0]}"
client.images.get(image_to_pull).tag(new_image_tag)
client.images.push(new_image_tag)

print(f"Image '{new_image_tag}' pushed to the registry.")



registry_images = docker_client.images.list()
print("Images in the registry:")
for image in registry_images:
    print(image.tags)
