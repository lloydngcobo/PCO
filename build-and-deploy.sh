#!/bin/bash

# PCO API Wrapper - Build and Deploy Script for OpenShift
# This script automates the build and deployment process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="pco-api-wrapper"
IMAGE_NAME="pco-api-wrapper"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Functions
print_header() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if oc is installed
    if ! command -v oc &> /dev/null; then
        print_error "OpenShift CLI (oc) is not installed"
        exit 1
    fi
    print_success "OpenShift CLI found"
    
    # Check if docker or podman is installed
    if command -v docker &> /dev/null; then
        BUILD_CMD="docker"
        print_success "Docker found"
    elif command -v podman &> /dev/null; then
        BUILD_CMD="podman"
        print_success "Podman found"
    else
        print_error "Neither Docker nor Podman is installed"
        exit 1
    fi
    
    # Check if logged in to OpenShift
    if ! oc whoami &> /dev/null; then
        print_error "Not logged in to OpenShift. Please run: oc login"
        exit 1
    fi
    print_success "Logged in to OpenShift as $(oc whoami)"
}

create_project() {
    print_header "Creating/Selecting OpenShift Project"
    
    if oc project $PROJECT_NAME &> /dev/null; then
        print_info "Project $PROJECT_NAME already exists"
    else
        print_info "Creating project $PROJECT_NAME"
        oc new-project $PROJECT_NAME \
            --display-name="PCO API Wrapper" \
            --description="Planning Center Online API Wrapper Service"
    fi
    
    oc project $PROJECT_NAME
    print_success "Using project: $PROJECT_NAME"
}

create_secrets() {
    print_header "Creating Secrets"
    
    # Check if secret already exists
    if oc get secret pco-credentials &> /dev/null; then
        print_info "Secret pco-credentials already exists"
        read -p "Do you want to update it? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
        oc delete secret pco-credentials
    fi
    
    # Prompt for credentials
    read -p "Enter PCO Application ID: " PCO_APP_ID
    read -sp "Enter PCO Secret: " PCO_SECRET
    echo
    
    # Create secret
    oc create secret generic pco-credentials \
        --from-literal=app-id="$PCO_APP_ID" \
        --from-literal=secret="$PCO_SECRET"
    
    print_success "Secret created successfully"
}

build_image() {
    print_header "Building Container Image"
    
    print_info "Building image: $IMAGE_NAME:$IMAGE_TAG"
    $BUILD_CMD build -t $IMAGE_NAME:$IMAGE_TAG .
    
    print_success "Image built successfully"
}

push_image() {
    print_header "Pushing Image to Registry"
    
    # Get OpenShift internal registry
    REGISTRY=$(oc get route default-route -n openshift-image-registry -o jsonpath='{.spec.host}' 2>/dev/null || echo "")
    
    if [ -z "$REGISTRY" ]; then
        print_info "Using external registry"
        read -p "Enter registry URL (e.g., quay.io/your-org): " REGISTRY
    else
        print_info "Using OpenShift internal registry: $REGISTRY"
        # Login to internal registry
        $BUILD_CMD login -u $(oc whoami) -p $(oc whoami -t) $REGISTRY
    fi
    
    FULL_IMAGE="$REGISTRY/$PROJECT_NAME/$IMAGE_NAME:$IMAGE_TAG"
    
    print_info "Tagging image: $FULL_IMAGE"
    $BUILD_CMD tag $IMAGE_NAME:$IMAGE_TAG $FULL_IMAGE
    
    print_info "Pushing image..."
    $BUILD_CMD push $FULL_IMAGE
    
    print_success "Image pushed successfully"
    
    # Update deployment with new image
    export IMAGE_REFERENCE=$FULL_IMAGE
}

deploy_application() {
    print_header "Deploying Application"
    
    # Apply ConfigMap
    print_info "Applying ConfigMap..."
    oc apply -f openshift/configmap.yaml
    
    # Apply Deployment
    print_info "Applying Deployment..."
    if [ -n "$IMAGE_REFERENCE" ]; then
        # Update image in deployment
        sed "s|image: pco-api-wrapper:latest|image: $IMAGE_REFERENCE|g" openshift/deployment.yaml | oc apply -f -
    else
        oc apply -f openshift/deployment.yaml
    fi
    
    # Apply Service
    print_info "Applying Service..."
    oc apply -f openshift/service.yaml
    
    # Apply Route
    print_info "Applying Route..."
    oc apply -f openshift/route.yaml
    
    print_success "Application deployed successfully"
}

wait_for_deployment() {
    print_header "Waiting for Deployment"
    
    print_info "Waiting for pods to be ready..."
    oc rollout status deployment/$PROJECT_NAME --timeout=5m
    
    print_success "Deployment is ready"
}

verify_deployment() {
    print_header "Verifying Deployment"
    
    # Get route URL
    ROUTE_URL=$(oc get route $PROJECT_NAME -o jsonpath='{.spec.host}')
    
    if [ -z "$ROUTE_URL" ]; then
        print_error "Could not get route URL"
        return 1
    fi
    
    print_info "Application URL: https://$ROUTE_URL"
    
    # Test health endpoint
    print_info "Testing health endpoint..."
    if curl -s -k "https://$ROUTE_URL/health" | grep -q "healthy"; then
        print_success "Health check passed"
    else
        print_error "Health check failed"
        return 1
    fi
    
    # Show pod status
    print_info "Pod status:"
    oc get pods -l app=$PROJECT_NAME
    
    print_success "Deployment verified successfully"
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Deployment Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "Application URL: ${YELLOW}https://$ROUTE_URL${NC}"
    echo ""
    echo "Available endpoints:"
    echo "  - Health Check: https://$ROUTE_URL/health"
    echo "  - Get People:   https://$ROUTE_URL/api/people"
    echo "  - Get Campuses: https://$ROUTE_URL/api/campuses"
    echo ""
    echo "View logs:"
    echo "  oc logs -f deployment/$PROJECT_NAME"
    echo ""
}

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --skip-build     Skip building the container image"
    echo "  --skip-push      Skip pushing the image to registry"
    echo "  --skip-secrets   Skip creating secrets"
    echo "  --help           Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  IMAGE_TAG        Tag for the container image (default: latest)"
    echo ""
}

# Main execution
main() {
    SKIP_BUILD=false
    SKIP_PUSH=false
    SKIP_SECRETS=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --skip-push)
                SKIP_PUSH=true
                shift
                ;;
            --skip-secrets)
                SKIP_SECRETS=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    print_header "PCO API Wrapper - OpenShift Deployment"
    
    check_prerequisites
    create_project
    
    if [ "$SKIP_SECRETS" = false ]; then
        create_secrets
    fi
    
    if [ "$SKIP_BUILD" = false ]; then
        build_image
    fi
    
    if [ "$SKIP_PUSH" = false ]; then
        push_image
    fi
    
    deploy_application
    wait_for_deployment
    verify_deployment
}

# Run main function
main "$@"