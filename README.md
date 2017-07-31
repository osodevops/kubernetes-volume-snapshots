Kubernetes Persistent Volume Backup / AWS
==================================================================

What it does
------------

After being seeded with a variable ``namespace`` and ``app name`` (set as environment variables), this script will navigate through the Kubernetes api, and locate any underlying ``Persistent Volumes`` and create a snapshot of each of these volumes.

Presently, only AWS is supported.


How it works
------------

#### Running externally (non Docker image)
* The script will authenticate with AWS and K8 by looking for ``~/.aws/credentials`` and ``~/.kube/config`` respectively.

#### Running within Kubernetes cluster
* The script will authenticate with *Kubernetes* by using the local service account token attached to the pod that is deployed.  See  [Accessing API from a Pod](https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster/#accessing-the-api-from-a-pod)
* The script will authenticate with AWS via a [secret](https://kubernetes.io/docs/concepts/configuration/secret/) which will mount a ``config`` and ``credentials`` file to ``/root/.aws``  **For this, a secret will have to already of been created.**  One method of creating this secret would be via _Kubectl_: 

> kubectl create secret --namespace=dev generic aws-key-secret --from-file=config=$HOME/.aws/config --from-file=credentials=$HOME/.aws/credentials



Usage
------------

#### External usage (non Docker image)
* Install dependencies
* Ensure ``$HOME/.aws/`` & ``$HOME/.kube/`` store the appropriate credentials to your environment.
* From command line, run:
    * ``export $K8_NAMESPACE=<<your namespace>>``
    * ``export $K8_APP_NAME=<<the application name>>``
* From the root of this project:
    * Install dependencies:
        * ``pip install -r ./requirements.txt``
    * Launch the script:
        * ``python -m kubernetes-pvc-snapshot``

#### Internal (within the K8 cluster) usage
###### Helm Deployment (via CLI)
* Ensure aws 'secret' has been created on the cluster (see above _How it works: running within Kubernetes cluster_)
* in *./templates/helm/kubernetes-pvc-snapshot/values.yaml*, update the following values:
    * env.name_space
    * env.app_name
    * secret_name
* Package the helm chart.  From within *./templates/helm*, run: ``helm package kubernetes-pvc-snapshot``
* Deploy the helm chart.  ``helm install kubernetes-pvc-snapshot``
    


###### Standard K8 Deployment

To create a standard Kubernetes 'job':

* Provide a value to the keys ``K8_NAMESPACE`` & ``K8_APP_NAME`` in *./templates/k8/kubernetes-volume-snapshot.yml*
* Create a new job via CLI:
> kubectl --namespace dev create -f ./templates/k8/job--cassandra-backup.yml