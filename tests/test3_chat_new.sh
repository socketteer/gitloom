#!/bin/bash

timestamp=$(date +%Y%m%d_%H%M%S)
test_dir="../../gitloom-tests/test_run_${timestamp}/test3"
mkdir -p "$test_dir"
cd "$test_dir"

echo "Test 3: New chat mode conversation"
echo "================================="

# Run with initial message
echo "Running gitloom..."
gitloom --mode chat "Hello, Claude! How are you today?"

# Print conversation
echo -e "\nFinal conversation:"
cat "chat.jsonl"