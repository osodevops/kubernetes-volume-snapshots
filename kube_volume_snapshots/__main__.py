#!/usr/bin/env python

from kube_volume_snapshots import connection
import os
import time


class Snapshot:

    def __init__(self):
        self.NAMESPACE = os.environ.data['K8_NAMESPACE']
        self.APP_NAME = os.environ.data['K8_APP_NAME']
        self.connection = connection.Connection()
        # Generate timestamp that will be used for tagging.
        self.timestamp = time.strftime("%Y%m%d-%H%M%S")
        self.pods_to_snapshot = self.pods_to_snapshot()
        self.persistent_volume_list = self.persistent_volume_list()

    def persistent_volume_list(self):
        persistent_volume_list = self.connection.kubernetes.list_persistent_volume().items
        return persistent_volume_list

    # Determine nodes in the application cluster (pulling from environment variable)
    def pods_to_snapshot(self):
        # Return list of Pods & Persistent Volumes
        # TODO: Should filter by NAMESPACE here.
        pod_list = self.connection.kubernetes.list_pod_for_all_namespaces(watch=False)
        pods_to_snapshot = list()
        for i in pod_list.items:
            try:
                if i.metadata.labels['app'] == self.APP_NAME:
                    pods_to_snapshot.append(i)
            except:
                pass

        return pods_to_snapshot

    def process_pods(self):
        pods_to_snapshot = self.pods_to_snapshot
        persistent_volume_list = self.persistent_volume_list
        timestamp = self.timestamp

        pods_to_process = pods_to_snapshot.__len__()
        pod_counter = 1

        for pod in pods_to_snapshot:
            pod_ip = pod.status.pod_ip
            pod_node_name = pod.spec.node_name
            pod_name = pod.metadata.name
            claim_names = list()

            for pod_volume in pod.spec.volumes:
                try:
                    claim_names.append(pod_volume.persistent_volume_claim.claim_name)
                except:
                    pass

            # If the volume ID is an EBS volume, capture that value.
            ebs_volume_id = ''
            for pv in persistent_volume_list:
                try:
                    if pv.spec.claim_ref.name in claim_names:
                        ebs_volume_id = pv.spec.aws_elastic_block_store.volume_id
                        pass
                except:
                    pass

            ebs_params = {
                "EBS_VOL_ID": ebs_volume_id,
                "APP_NAME": self.APP_NAME,
                "SNAPSHOT_TIME": timestamp,
                "POD_NAME": pod_name,
                "POD_NODE_NAME": pod_node_name,
                "POD_IP": pod_ip,
                "COUNTER": pod_counter,
                "COUNTER_TOTAL": pods_to_process
            }

            # Create an AWS snapshot
            self.ebs_snapshot(ebs_params)
            pod_counter += 1

    def ebs_snapshot(self, ebs_params):
        print ebs_params['EBS_VOL_ID']
        ebs_volume = ebs_params['EBS_VOL_ID'].split('/')
        ebs_region = ebs_volume[2]
        ebs_volume_id = ebs_volume[3]
        snapshot_description = str(ebs_params['COUNTER']) + '/' + str(ebs_params['COUNTER_TOTAL']) + ' ' + \
                               ebs_params['SNAPSHOT_TIME'] + ' ' + ebs_params['POD_NAME']
        print 'Creating snapshot for ' + ebs_volume_id + ' found in the region ' + ebs_region
        snapshot = self.connection.e2_resource.create_snapshot(VolumeId=ebs_volume_id, Description=snapshot_description)
        print 'Snapshot ' + snapshot.id + ' created successfully'
        backup_number = str(ebs_params['COUNTER']) + ' of ' + str(ebs_params['COUNTER_TOTAL'])
        long_name = ebs_params['SNAPSHOT_TIME'] + ' - ' + backup_number + ' - ' + ebs_params['APP_NAME']
        snapshot_id = list()
        snapshot_id.append(snapshot.id)

        tags = [{"Key": "Name",
                 "Value": long_name},
                {"Key": "ebs_vol_id",
                 "Value": ebs_params['EBS_VOL_ID']},
                {"Key": "s3_key_location",
                 "Value": ebs_params['APP_NAME']},
                {"Key": "snapshot_time",
                 "Value": ebs_params['SNAPSHOT_TIME']},
                {"Key": "pod_name",
                 "Value": ebs_params['POD_NAME']},
                {"Key": "pod_node_name",
                 "Value": ebs_params['POD_NODE_NAME']},
                {"Key": "pod_ip",
                 "Value": ebs_params['POD_IP']},
                {"Key": "backup_number",
                 "Value": backup_number}]

        for tag in tags:
            print 'Tagging ' + snapshot.id + ' with ' + tag['Key'] + ': ' + tag['Value']
        self.connection.e2_resource.create_tags(Resources=snapshot_id, Tags=tags)
        print 'Snapshot ' + snapshot.id + ' tagged successfully'


def main():
    snapshot = Snapshot()
    snapshot.process_pods()


if __name__ == '__main__':
    main()

