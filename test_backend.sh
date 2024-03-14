#!/bin/bash

# Configuration
REPO_BASE_DIR="AttendanceCloudApp-backend"
OPENAPI_ENDPOINT="http://127.0.0.1:8000/schema/"
OPENAPI_SCHEMA_PATH="./postman/schema.yaml"
POSTMAN_COLLECTION_PATH="./postman/collection.json"
CONVERT_SCRIPT_PATH="./postman/convert_schema.js"
INJECT_TESTS_SCRIPT="./postman/inject_tests.js"

# Ensure the script is run from the base directory of the repository
if [[ "$(basename $(pwd))" != "$REPO_BASE_DIR" ]]; then
    echo "This script must be run inside from the base directory of the repository: $REPO_BASE_DIR"
    exit 1
fi

# Check for Node.js and correct version
REQUIRED_NODE_VERSION="10.0.0" # Example minimum version
if ! command -v node &>/dev/null; then
    echo "Node.js could not be found. Please install Node.js."
    exit 1
fi

CURRENT_NODE_VERSION=$(node -v)
if [[ "$(printf '%s\n' "$REQUIRED_NODE_VERSION" "$CURRENT_NODE_VERSION" | sort -V | head -n1)" != "$REQUIRED_NODE_VERSION" ]]; then
    echo "Current Node.js version is $CURRENT_NODE_VERSION. Please update Node.js to at least $REQUIRED_NODE_VERSION."
    exit 1
fi

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Use a trap to call clean_up function on script exit, error, or interruption.
trap clean_up EXIT

# Function to check the OPENAPI_ENDPOINT accessibility
check_endpoint() {
    curl --output /dev/null --silent --head --fail $OPENAPI_ENDPOINT
    return $?
}

# Function to start Django server
start_django_server() {
    echo "Attempting to start the Django server..."
    python manage.py runserver 127.0.0.1:8000 &
    DJANGO_SERVER_PID=$!
    # Wait a little bit to allow the server to start
    sleep 10
}

# Function for cleanup actions
clean_up() {
    echo "Cleaning up..."
    # Kill the Django server process if it was started by this script
    if [ ! -z "$DJANGO_SERVER_PID" ]; then
        echo "Stopping the Django server..."
        kill $DJANGO_SERVER_PID
    fi

    List of files to check and potentially delete
    files_to_clean=("$OPENAPI_SCHEMA_PATH" "$POSTMAN_COLLECTION_PATH")
    for file in "${files_to_clean[@]}"; do
        if [ -f "$file" ]; then
            echo "Removing $file..."
            rm -f "$file"
        else
            echo "$file does not exist or is not a regular file, skipping..."
        fi
    done

    echo "Cleanup completed."
}

# Check if the OPENAPI_ENDPOINT is reachable
check_endpoint
if [ $? -ne 0 ]; then
    echo "Failed to reach $OPENAPI_ENDPOINT, attempting to start the Django server..."
    start_django_server

    # Check the OPENAPI_ENDPOINT again
    check_endpoint
    if [ $? -ne 0 ]; then
        echo "Failed to reach $OPENAPI_ENDPOINT even after starting the Django server."
        exit 1
    fi
fi

# Fetch the OpenAPI schema
curl $OPENAPI_ENDPOINT -o $OPENAPI_SCHEMA_PATH
if [ $? -ne 0 ]; then
    echo "Failed to fetch OpenAPI schema"
    exit 1
fi

# Execute the conversion script with Node.js
echo "Converting OpenAPI schema to Postman collection..."
node $CONVERT_SCRIPT_PATH $OPENAPI_SCHEMA_PATH $POSTMAN_COLLECTION_PATH

# Check if the Node.js script executed successfully
if [ $? -ne 0 ]; then
    echo "Failed to convert OpenAPI schema to Postman collection."
    exit 1
fi

echo "Conversion completed successfully."

# After generating the Postman collection, add test scripts
echo "Adding test scripts to the Postman collection..."
node $INJECT_TESTS_SCRIPT

if [ $? -ne 0 ]; then
    echo "Failed to add test scripts to the Postman collection."
    exit 1
fi

echo "Test scripts added successfully."

# Run Newman tests with locally installed Newman
echo "Running Newman tests with locally installed Newman..."
npx newman run $POSTMAN_COLLECTION_PATH --env-var baseUrl=http://127.0.0.1:8000

if [ $? -ne 0 ]; then
    echo "Newman tests failed."
    exit 1
fi

echo "Newman tests completed successfully."
exit 0