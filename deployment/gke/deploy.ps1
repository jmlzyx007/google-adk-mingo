# Module 33 - deploy to GKE (NOT YET RUN - needs GCP setup)
# WARNING: GKE clusters cost money while they exist. Delete after the lab.

$PROJECT = "your-gcp-project-id"
$REGION = "us-central1"
$CLUSTER = "adk-cluster"
$IMAGE = "$REGION-docker.pkg.dev/$PROJECT/adk-repo/adk-agent:latest"

gcloud config set project $PROJECT

# 1. Artifact Registry repo + build/push the image (Dockerfile in this folder)
gcloud artifacts repositories create adk-repo --repository-format=docker --location=$REGION
gcloud builds submit --tag $IMAGE ../..   # repo root as build context

# 2. Create an Autopilot cluster (simplest managed option)
gcloud container clusters create-auto $CLUSTER --region $REGION
gcloud container clusters get-credentials $CLUSTER --region $REGION

# 3. Deploy the manifests
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl get service adk-agent-service --watch   # wait for EXTERNAL-IP

# Troubleshooting: ImagePullBackOff = registry perms/API; CrashLoopBackOff =
# kubectl logs <pod>; Pending IP = quota/networking.

# 4. CLEANUP (do not skip)
# kubectl delete -f service.yaml -f deployment.yaml
# gcloud container clusters delete $CLUSTER --region $REGION
