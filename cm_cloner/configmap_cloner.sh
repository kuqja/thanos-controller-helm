#!/bin/bash

# Namespace and ConfigMap names
SOURCE_NAMESPACE="th-controller"
SOURCE_CONFIGMAP="thanos-receive-generated"
TARGET_NAMESPACE="th-controller"
TARGET_CONFIGMAP="thanos-receive-generatsadsafs"

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
