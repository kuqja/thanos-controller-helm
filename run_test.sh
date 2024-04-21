#!/bin/bash

echo "Starting minikub locally"
minikube start

echo "Packaging the Helm chart into tgz"
helm package chart/

exho "Upgrade (or install) the Helm chart thanos receiver controller using the version from Chart.yaml"
helm upgrade --install thanos-receive-controller thanos-receive-controller-0.0.1.tgz -n th-controller --create-namespace -f chart/values.yaml

echo "Upgrade (or install) the Helm chart thanos from bitnami"
helm upgrade --install thanos oci://registry-1.docker.io/bitnamicharts/thanos -n th-controller -f examples/thanos.yaml 
