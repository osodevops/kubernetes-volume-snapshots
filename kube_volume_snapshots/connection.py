#!/usr/bin/env python

from kubernetes import client, config
import boto3


class Connection:

    def __init__(self, config=None):
        self.config = config
        self.kubernetes = self.kubernetes_client()
        self.s3_client = self.aws_s3_client()
        self.s3_resource = self.aws_s3_resource()
        self.e2_resource = self.aws_ec2_resource()
        self.aws_region_name = self.aws_region_name()
        self.aws_account_id = self.aws_account_id()


    def kubernetes_client(self):
        # K8 Clients
        # Try pods crt files, and in not, look for $USER/.kube/config
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()

        v1 = client.CoreV1Api()

        return v1

    def aws_s3_client(self):
        s3_client = boto3.client('s3')
        return s3_client

    def aws_s3_resource(self):
        s3_resource = boto3.resource('s3')
        return s3_resource

    def aws_ec2_resource(self):
        ec2_resource = boto3.resource('ec2')
        return ec2_resource

    def aws_region_name(self):
        region_name = boto3.session.Session().region_name
        return region_name

    def aws_account_id(self):
        aws_account_id = boto3.client('sts').get_caller_identity()['Account']
        return aws_account_id

