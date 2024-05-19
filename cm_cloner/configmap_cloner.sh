#!/bin/bash

# Namespace and ConfigMap names
SOURCE_NAMESPACE="source-namespace"
SOURCE_CONFIGMAP="source-configmap"
TARGET_NAMESPACE="target-namespace"
TARGET_CONFIGMAP="target-configmap"

# Function to clone and update ConfigMap
clone_configmap() {
  # Fetch the ConfigMap from the source namespace
  kubectl get configmap $SOURCE_CONFIGMAP -n $SOURCE_NAMESPACE -o yaml > /tmp/source-configmap.yaml

  # Modify the name and namespace in the YAML file
  sed -i "s/name: $SOURCE_CONFIGMAP/name: $TARGET_CONFIGMAP/" /tmp/source-configmap.yaml
  sed -i "/namespace:/d" /tmp/source-configmap.yaml

  # Apply the ConfigMap to the target namespace
  kubectl apply -n $TARGET_NAMESPACE -f /tmp/source-configmap.yaml
}

# Continuously update the ConfigMap
while true; do
  clone_configmap
  sleep 60  # Update every 60 seconds, adjust as needed
done
