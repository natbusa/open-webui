#!/bin/bash
# Convert CRLF to LF for all text files, skipping .git and binary files
find . -type f -not -path './.git/*' -print0 | while IFS= read -r -d '' file; do
  if file "$file" | grep -q 'text'; then
    sed -i 's/\r$//' "$file"
  fi
done
