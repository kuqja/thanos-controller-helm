# Use an appropriate base image with kubectl and bash
FROM bitnami/kubectl:latest

# Switch to root user to perform operations that require elevated privileges
USER root

# Create the scripts directory
RUN mkdir -p /scripts

# Copy the script into the image
COPY configmap_cloner.sh /scripts/configmap_cloner.sh

# Ensure the script is executable
RUN chmod +x /scripts/configmap_cloner.sh

# Set the entrypoint to the script
ENTRYPOINT ["/scripts/configmap_cloner.sh"]
