#!/bin/bash

timestamp=$(date +%Y%m%d_%H%M%S)
test_dir="../../gitloom-tests/test_run_${timestamp}/test2"
mkdir -p "$test_dir"
cd "$test_dir"

echo "Test 2: Base mode with existing file"
echo "==================================="

# Create initial file
echo "Initial content in the file." > "untitled.txt"

# Run gitloom
echo "Running gitloom..."
gitloom --mode base

# Print final content
echo -e "\nFinal file content:"
cat "untitled.txt"