#!/bin/bash

# Test 1: Multiple runs in base mode with input text
timestamp=$(date +%Y%m%d_%H%M%S)
test_dir="../../gitloom-tests/test_run_${timestamp}/test1"
mkdir -p "$test_dir"
cd "$test_dir"

echo "Test 1: Multiple base mode runs"
echo "=============================="

# First run with initial text
echo "Running first command..."
gitloom --mode base "Hello, this is a test."

# Second run with continuation
echo -e "\nRunning second command..."
gitloom --mode base " This is a"

# Print final content
echo -e "\nFinal file content:"
cat "untitled.txt"