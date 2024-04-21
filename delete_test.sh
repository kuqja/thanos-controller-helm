#!/bin/bash

echo "Uninstalling thanos receive controller chart and its resources"
helm uninstall thanos-receive-controller  -n th-controller

echo "Uninstalling thanos chart and its resources"
helm uninstall thanos -n th-controller

echo "Delete th-controller namespace"
kubectl delete ns th-controller

echo "Stopping minukube cluster" 
minikube stop

echo "Environment CleanUp is complete"
