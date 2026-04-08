#!/bin/bash
# Generate self-signed SSL certificates for development
# Usage: bash scripts/generate_certs.sh

set -e

echo "Generating self-signed SSL certificates..."

# Check if openssl is installed
if ! command -v openssl &> /dev/null; then
    echo "Error: openssl is not installed"
    exit 1
fi

# Generate private key and certificate
openssl req -x509 -newkey rsa:2048 \
    -nodes \
    -keyout server.key \
    -out server.crt \
    -days 365 \
    -subj "/CN=localhost" \
    2>/dev/null

echo "Certificates generated successfully:"
echo "  - server.key (private key)"
echo "  - server.crt (certificate)"
echo ""
echo "IMPORTANT: Add these files to .gitignore to avoid committing them."
EOFchmod +x "/Users/danny/Documents/code projects/simple_file_sharing_server/scripts/generate_certs.sh"