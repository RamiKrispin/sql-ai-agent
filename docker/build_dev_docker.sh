#!/bin/bash

# Image settings
user_name=rkrispin
project_name="sql-ai-agent"
image_label=python-dev-$project_name
tag=0.0.1
python_ver=3.12.11
venv_name="sql-ai-agent-dev"
ruff_ver="0.12.0"
dockerfile="Dockerfile_Dev"
image_name="$user_name/$image_label:$tag"



echo "Build the docker"

docker buildx build  . -f $dockerfile \
                --platform linux/amd64,linux/arm64 \
                --progress=plain \
                --build-arg VENV_NAME=$venv_name \
                --build-arg PYTHON_VER=$python_ver \
                --build-arg RUFF_VER=$ruff_ver \
                -t $image_name

if [[ $? = 0 ]] ; then
echo "Pushing docker..."
docker push $image_name
else
echo "Docker build failed"
fi