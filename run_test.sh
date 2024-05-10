#!/bin/bash

echo "Starting minikube locally"
minikube start

echo "Packaging the Helm chart into tgz"
helm package chart/

echo "Upgrade (or install) the Helm chart thanos receiver controller using the version from Chart.yaml"
helm upgrade --install thanos-receive-controller thanos-receive-controller-0.0.1.tgz -n c --create-namespace -f chart/values.yaml

echo "Upgrade (or install) the Helm chart thanos from bitnami"
helm upgrade --install thanos oci://registry-1.docker.io/bitnamicharts/thanos -n t --create-namespace  -f examples/thanos.yaml 
