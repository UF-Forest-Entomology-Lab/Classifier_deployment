# Classifier_deployment
An attempt to deploy the classifier as a webapp with access to a webcam.

## Docker commands

Build the docker image.
Don't include --no-cache if you want to use cache and build quicker.
"""
docker build --no-cache -t andrew-alpha <path to Dockerfile>
"""
Tag the docker image with the tag indicating the version of the app
"""
docker tag andrew-alpha gcmarais/andrew-alpha:latest
"""
Push the docker image to dockerhub to be pulled by users.
"""
docker push <docker_username>/andrew-alpha:latest
"""
To run the docker image on any machine
"""
docker run -it -p 8000:8000 andrew-alpha
"""