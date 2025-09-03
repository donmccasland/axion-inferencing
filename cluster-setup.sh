export SERVICE_NAME='tpu-vllm-app'
export REGION=asia-northeast1
export PROJECT_ID=aiinfrasummit-demo
export PROJECT_NUMBER=815280284507
export CLUSTER_NAME=vllm-serving
export CLUSTER_VERSION=1.31.2-gke.1384000
export NODE_POOL_NAME=tpu-pool
export NODE_ZONES=asia-northeast1-b
export MACHINE_TYPE=ct6e-standard-4t
gcloud config set project $PROJECT_ID
gcloud container clusters create $CLUSTER_NAME \
  --location $REGION \
  --addons=GcsFuseCsiDriver=ENABLED \
  --workload-pool=aiinfrasummit-demo.svc.id.goog \
  --release-channel=rapid

gcloud container node-pools create $NODE_POOL_NAME \
  --location=$REGION \
  --cluster=$CLUSTER_NAME \
  --node-locations=$NODE_ZONES \
  --machine-type=$MACHINE_TYPE \
  --scopes=cloud-platform \
  --location-policy=ANY \
  --enable-autoscaling \
  --num-nodes=2 \
  --total-min-nodes=0 \
  --total-max-nodes=2

gcloud projects add-iam-policy-binding aiinfrasummit-demo \
    --member "principal://iam.googleapis.com/projects/815280284507/locations/global/workloadIdentityPools/aiinfrasummit-demo.svc.id.goog/subject/ns/default/sa/ksa-demo" \
    --role "roles/storage.objectUser"

gcloud projects add-iam-policy-binding aiinfrasummit-demo \
    --member "principal://iam.googleapis.com/projects/815280284507/locations/global/workloadIdentityPools/aiinfrasummit-demo.svc.id.goog/subject/ns/default/sa/ksa-demo" \
    --role roles/monitoring.metricWriter

kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/k8s-stackdriver/master/custom-metrics-stackdriver-adapter/deploy/production/adapter_new_resource_model.yaml

gcloud projects add-iam-policy-binding projects/${PROJECT_ID} \
    --role roles/monitoring.viewer \
    --member "principal://iam.googleapis.com/projects/815280284507/locations/global/workloadIdentityPools/aiinfrasummit-demo.svc.id.goog/subject/ns/default/sa/ksa-demo" \

#also add monitoring.viewer to compute SA
