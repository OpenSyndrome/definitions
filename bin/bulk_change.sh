#!/bin/bash

# Directory to search for JSON files (current directory by default)
SEARCH_DIR="${1:-.}"

# Find all JSON files in the directory and subdirectories
find "$SEARCH_DIR" -type f -name "*.json" | while read -r json_file; do
  echo "Processing: $json_file"
  
  # Check if the file already has the "status" property
  if grep -q '"status":' "$json_file"; then
    echo "  Status property already exists, skipping..."
  else
    # Create a temporary file
    temp_file=$(mktemp)
    
    # Use jq to add the status property if it doesn't exist
    # First, check if we have jq installed
    if command -v jq >/dev/null 2>&1; then
      jq '. + {"status": "draft"}' "$json_file" > "$temp_file"
      
      # Only replace if jq command succeeded
      if [ $? -eq 0 ]; then
        mv "$temp_file" "$json_file"
        echo "  Added status property using jq"
      else
        echo "  Error processing with jq, file not modified"
        rm "$temp_file"
      fi
    else
      echo "  jq not found, using alternative method"
      
      # Alternative method if jq is not available
      # This is a basic approach that works for simple JSON files
      # It inserts "status": "draft" after the first opening brace
      sed '0,/{/{s/{/{\"status\": \"draft\", /}' "$json_file" > "$temp_file"
      
      # Check if the file still looks like valid JSON (very basic check)
      if grep -q "^{" "$temp_file" && grep -q "}$" "$temp_file"; then
        mv "$temp_file" "$json_file"
        echo "  Added status property using sed"
      else
        echo "  Error processing with sed, file not modified"
        rm "$temp_file"
      fi
    fi
  fi
done

echo "Processing complete!"
