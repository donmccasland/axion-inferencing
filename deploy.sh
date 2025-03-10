AR_REPO='axion-inference-repo'
SERVICE_NAME='axion-inference-app'
GOOGLE_CLOUD_REGION=us-central1
GOOGLE_CLOUD_PROJECT=axion-inference-demo
gcloud config set project axion-inference-demo
gcloud builds submit --tag "$GOOGLE_CLOUD_REGION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/$AR_REPO/$SERVICE_NAME"
gcloud run deploy "$SERVICE_NAME"   --port=8080   --image="$GOOGLE_CLOUD_REGION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/$AR_REPO/$SERVICE_NAME"   --allow-unauthenticated   --region=$GOOGLE_CLOUD_REGION   --platform=managed    --project=$GOOGLE_CLOUD_PROJECT   --set-env-vars=GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_REGION=$GOOGLE_CLOUD_REGION

