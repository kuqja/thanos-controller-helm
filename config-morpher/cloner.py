import os
import sys
import signal
import time
import logging
import argparse
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Global Variables for CLI args
args = None

def parse_args():
    parser = argparse.ArgumentParser(description="ConfigMap and Secret Cloner")
    parser.add_argument("--configmap-name", help="Name of the ConfigMap to clone")
    parser.add_argument("--secret-name", help="Name of the Secret to clone")
    parser.add_argument("--target-namespace", help="Target namespace for the clone")
    parser.add_argument("--namespaces", help="Comma-separated list of namespaces to watch", required=True)
    parser.add_argument("--resource-type", choices=['configmap', 'secret'], help="Resource type to clone", required=True)
    return parser.parse_args()

def process_resource(resource, resource_type):
    if args.configmap_name and args.configmap_name != resource.metadata.name:
        logger.info(f"Skipping {resource_type} {resource.metadata.namespace}/{resource.metadata.name}: Name does not match the specified flag")
        return

    annotations = resource.metadata.annotations
    if annotations and "scrape" in annotations and annotations["scrape"] == "true":
        clone_resource(resource, resource_type)

def clone_resource(resource, resource_type):
    tns = args.target_namespace if args.target_namespace else resource.metadata.annotations.get("target-namespace", resource.metadata.namespace)
    
    if resource_type == "configmap":
        cloned_resource = client.V1ConfigMap(
            api_version="v1",
            kind="ConfigMap",
            metadata=client.V1ObjectMeta(name=f"{resource.metadata.name}-clone", namespace=tns),
            data=resource.data
        )
    elif resource_type == "secret":
        cloned_resource = client.V1Secret(
            api_version="v1",
            kind="Secret",
            metadata=client.V1ObjectMeta(name=f"{resource.metadata.name}-clone", namespace=tns),
            data=resource.data,
            type=resource.type
        )

    api_instance = client.CoreV1Api()
    retries = 3
    for i in range(retries):
        try:
            if resource_type == "configmap":
                api_instance.create_namespaced_config_map(namespace=tns, body=cloned_resource)
            elif resource_type == "secret":
                api_instance.create_namespaced_secret(namespace=tns, body=cloned_resource)
            logger.info(f"Successfully cloned {resource_type} to {tns}/{cloned_resource.metadata.name}")
            return
        except ApiException as e:
            if e.status in [500, 502, 503, 504] and i < retries - 1:
                logger.warning(f"Retrying cloning {resource_type} due to API error: {e}")
                time.sleep(2 ** i)
            else:
                logger.error(f"Error creating cloned {resource_type} {tns}/{cloned_resource.metadata.name}: {e}")
                return

def watch_resources():
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()

    v1 = client.CoreV1Api()
    w = watch.Watch()
    for ns in args.namespaces.split(','):
        logger.info(f"Watching {args.resource_type}s in namespace: {ns}")
        if args.resource_type == "configmap":
            for event in w.stream(v1.list_namespaced_config_map, namespace=ns):
                if event["type"] in ["ADDED", "MODIFIED"]:
                    process_resource(event["object"], "configmap")
        elif args.resource_type == "secret":
            for event in w.stream(v1.list_namespaced_secret, namespace=ns):
                if event["type"] in ["ADDED", "MODIFIED"]:
                    process_resource(event["object"], "secret")

def main():
    global args
    args = parse_args()

    if not args.namespaces:
        logger.error("No target namespaces provided. Exiting.")
        sys.exit(1)

    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))
    signal.signal(signal.SIGINT, lambda signum, frame: sys.exit(0))

    watch_resources()

if __name__ == "__main__":
    main()
