# Classifier_deployment
An attempt to deploy the classifier as a webapp with access to a webcam.

## Docker commands

Build the docker image.
Don't include --no-cache if you want to use cache and build quicker.
"""
docker build --no-cache -t andrew-alpha <path to Dockerfile>
"""
Tag the docker image with the tag indicating the version of the app.
"""
docker tag andrew-alpha <docker_username>/andrew-alpha:latest
"""
Push the docker image to dockerhub to be pulled by users.
"""
docker push <docker_username>/andrew-alpha:latest
"""
Pull the docker iamge to the local machine.
"""
docker pull <docker_username>/andrew-alpha:latest
"""
To run the docker image on any machine.
"""
docker run -it -p 7860:7860 --name andrew-alpha-container <docker_username>/andrew-alpha:latest
"""

Make sure to install pytorch with the following to sue object detection on GPU:

pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118