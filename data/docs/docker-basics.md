# Docker Basics

## Images and containers

A Docker image is a read-only template that contains an application together with its dependencies, such as libraries and runtime. A container is a running instance of an image. Many containers can be started from the same image, and each container gets its own isolated environment.

## Dockerfile

A Dockerfile is a text file with instructions for building an image. Common instructions are FROM, which chooses a base image, COPY, which copies files into the image, RUN, which executes commands during the build, and CMD, which sets the command that runs when the container starts.

## Volumes

Data written inside a container is lost when the container is removed. A volume stores data outside the container's writable layer, so the data survives when the container is deleted or recreated. Volumes are commonly used for databases and other data that must persist.

## Docker Compose

Docker Compose is a tool for running applications that consist of several containers. The services, networks and volumes are described in a file called docker-compose.yml. The command docker compose up starts all services, and services can reach each other using their service names as hostnames.