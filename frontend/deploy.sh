#!/bin/bash
set -e
# use the above to stop script if any error occurs

# build and push image
# export LATEST_COMMIT_SHORT_SHA=$(git log -1 --pretty=format:"%h")
export REGION='europe-west1'
export PROJECT_ID='fast-ticket-app'
export REPO_NAME='fast-ticket-repo'
export APP_NAME='frontend'

docker buildx build \
    --platform=linux/amd64 \
    -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$APP_NAME:latest \
    .

    # should also be tagged and pushed with commit sha, but not doing this rn to save artifact repository space
    # -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$APP_NAME:$LATEST_COMMIT_SHORT_SHA \

docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$APP_NAME:latest

# create new Cloud Run revision
# https://docs.cloud.google.com/sdk/gcloud/reference/run/deploy
# --max: The maximum number of container instances to run for this Service
# --max-instances: The maximum number of container instances for this Revision to run or 'default' to remove
gcloud run deploy fast-ticket-frontend \
    --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$APP_NAME:latest \
    --region=$REGION \
    --min=0 \
    --max=1 \
    --min-instances='default' \
    --max-instances='default' \
    --port=80 \
    --concurrency=1000 \
    --cpu=1 \
    --memory=512Mi \
    --cpu-boost \
    --allow-unauthenticated \
    --timeout=30 \
    --liveness-probe=httpGet.path=/health,httpGet.port=80
