#!/bin/bash

# Directory to search for JSON files (current directory by default)
SEARCH_DIR="${2:-.}"

# Schema file path (default: ./schema/schemas/v1/schema.json)
SCHEMA_FILE="${1:-./schema/schemas/v1/schema.json}"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BOLD='\033[1m'
RESET='\033[0m'

# Use command substitution to properly capture the output of find
find "$SEARCH_DIR" -type f -name "*.json" | while read -r file; do
    if [[ -f "$file" ]]; then
        echo "Validating: $file"
        ajv validate --spec draft2020 -c ajv-formats -s "${SCHEMA_FILE}" -d "$file"

        # Capture the exit status to provide a summary
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ ${BOLD}Valid:${RESET} $file"
        else
            echo -e "${RED}✗ ${BOLD}Invalid:${RESET} $file"
        fi
    fi
done
