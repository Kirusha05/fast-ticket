#!/bin/bash
set -e
# use the above to stop script if any error occurs

# run tests
docker compose up --build -d
MODE='test' poetry run pytest -vv
docker compose down

# build and push image
# export LATEST_COMMIT_SHORT_SHA=$(git log -1 --pretty=format:"%h")
export REGION='europe-west1'
export PROJECT_ID='fast-ticket-app'
export REPO_NAME='fast-ticket-repo'
export APP_NAME='backend'

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

ENV_VARS=$(
    sed 's/[[:space:]]*#.*$//' .env.prod \
    | grep -Ev '^[[:space:]]*$' \
    | paste -sd, -
)

gcloud run deploy fast-ticket-backend \
    --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$APP_NAME:latest \
    --region=$REGION \
    --min=0 \
    --max=1 \
    --min-instances='default' \
    --max-instances='default' \
    --port=8000 \
    --concurrency=200 \
    --cpu=1 \
    --memory=512Mi \
    --cpu-boost \
    --allow-unauthenticated \
    --timeout=300 \
    --liveness-probe=initialDelaySeconds=10,timeoutSeconds=3,periodSeconds=10,failureThreshold=3,httpGet.path=/health,httpGet.port=8000 \
    --set-env-vars="$ENV_VARS"

# for routing traffic to multiple revisions
# gcloud run services update-traffic demo-backend \
#    --region=europe-west1 \
#    --to-revisions=demo-backend-00010-5k4=90,demo-backend-00009-sqm=10