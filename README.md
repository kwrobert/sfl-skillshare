# Local Development

Local development is all done using docker compose. To quickly get a development environment up and running, execute:

```
docker compose up
```

To start but run services in the background, execute

```
docker compose up -d
```

# Deploying to Production

Once things have been developed locally and are working, they can easily be
deployed to AWS at production scale using a combination of Terraform,
Kubernetes, and Helm.

Terraform is the main driver for deploying all infrastructure, and in its
current form deploys everything to AWS. It deploys the following things:

  - A VPC, subnets, and IAM policies to support an EKS Kubernetes cluster. 
  - An EKS cluster
  - An [AWS Load Balancer Controller](https://artifacthub.io/packages/helm/aws/aws-load-balancer-controller) via Helm Charts and the Terraform Helm Provider

## Deploying the Cluster

To deploy a cluster of 2 nodes using t2.medium instances right off the bat, simply run the following from the root of the repo 

```bash
cd infra/tf
terraform init
terraform plan
terraform apply
```

You can provision multiple EKS clusters with a single `terraform apply`. First, edit the `infra/tf/main.tf` file and copy and paste the `module` section therein. Make sure to change the module name from `dev_cluster` and also change the `cluster_name` variable within the module block.

## Deploying Test Applications

To test that all actually worked, you can deploy some simple test K8s applications. The Kubernetes manifests for these applications are all found in `infra/k8s`. To try one out, first configure your `kubectl` command line client to speak to the cluster(s) you just deployed. After a successful Terraform deployment, there should be `kubectl` configuration files in `infra/tf/kubeconfig_eks-${cluster_name}`. Pick the cluster you want to interact with, then configure `kubectl` to use it within

```bash
export export KUBECONFIG=path/to/infra/tf/kubeconfig_eks-${cluster_name}`
```

NOTE: This will only persist for your current shell session.

With your `kubectl` client configured, run the following command to deploy [an
application that displays a message, the name of the pod and details of the
node it's deployed to.](https://github.com/paulbouwer/hello-kubernetes):

```bash
kubectl apply -f infra/k8s/hello-world-full.yaml
```

This deploys a few Kubernetes resources:

  1. A Deployment, which contains a single Pod 
  2. A Service of type Nodeport, which exposes ports on the K8s worker nodes and maps them to target ports exposed by your Pods
  3. An Ingress Controller that uses the AWS Load Balancer Controller to route internet traffic hitting an external service port on the AWS Load Balancer to ports exposed on worker nodes 

To see them, run the following commands:

```
$ kubectl get pods
NAME                                READY   STATUS    RESTARTS   AGE
hello-kubernetes-79b94d97c7-mgm4h   1/1     Running   0          28m

$ kubectl get deployments
NAME               READY   UP-TO-DATE   AVAILABLE   AGE
hello-kubernetes   1/1     1            1           29m

$ kubectl get service
NAME               TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
hello-kubernetes   NodePort    10.100.82.52   <none>        80:31648/TCP   29m
kubernetes         ClusterIP   10.100.0.1     <none>        443/TCP        113m

$ kubectl get ingress
NAME               HOSTS   ADDRESS                                                                  PORTS   AGE
hello-kubernetes   *       k8s-default-hellokub-1c645ae349-2013837538.us-east-1.elb.amazonaws.com   80      66m
```

To see if your appplication works, copy and paste the `ADDRESS` field of the `hello-kubernetes` Ingress controller into your browser. You should see something like the following: 

![](./docs/figures/hello-kubernetes-success.png)