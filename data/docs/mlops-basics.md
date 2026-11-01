# MLOps Basics

## What is MLOps?

MLOps is a set of practices for building, deploying and maintaining machine learning systems in production in a reliable and repeatable way. It combines ideas from machine learning, DevOps and data engineering.

## Continuous integration

Continuous integration (CI) means that every change pushed to the repository is automatically built and tested. In machine learning projects, CI can also check data quality and verify that model performance has not dropped below an agreed threshold.

## Model monitoring

After deployment, a model must be monitored. Data drift happens when the input data in production starts to differ from the training data, which can make predictions worse over time. Monitoring tracks metrics such as latency, error rate and prediction quality so problems are detected early.

## Reproducibility

A machine learning result is reproducible when someone else can get the same result using the same code, data and configuration. Pinning package versions, versioning data and running code in containers are common ways to improve reproducibility.