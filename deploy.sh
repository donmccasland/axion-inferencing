export AR_REPO='tpu-vllm-demo'
export SERVICE_NAME='tpu-vllm-app'
export REGION=us-central1
export PROJECT_ID=diesel-patrol-382622
export PROJECT_NUMBER=314837540096
gcloud config set project $PROJECT_ID
docker build -t ${SERVICE_NAME}:latest .
docker tag ${SERVICE_NAME}:latest us-central1-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/${SERVICE_NAME}:latest 
docker push us-central1-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/${SERVICE_NAME}:latest
gcloud beta run deploy "${SERVICE_NAME}" \
	--project=${PROJECT_ID} \
	--region=${REGION} \
	--port=8080 \
	--image="${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO}/${SERVICE_NAME}" \
	--no-allow-unauthenticated \
	--iap \
	--platform=managed \
	--set-env-vars=GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_REGION=${REGION}

gcloud beta services identity create --service=iap.googleapis.com --project=${PROJECT_ID}
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-iap.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

EMAIL_ADDRESS="donmccasland@google.com"

gcloud beta iap web add-iam-policy-binding \
    --resource-type=cloud-run \
    --service=${SERVICE_NAME} \
    --region=${REGION} \
    --member=user:${EMAIL_ADDRESS} \
    --role=roles/iap.httpsResourceAccessor \
    --condition=None
