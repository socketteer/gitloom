#!/bin/bash

timestamp=$(date +%Y%m%d_%H%M%S)
test_dir="../../gitloom-tests/test_run_${timestamp}/test4"
mkdir -p "$test_dir"
cd "$test_dir"

echo "Test 4: Existing chat mode conversation"
echo "======================================"

# Create initial chat history
cat > "chat.jsonl" << EOL
{"role": "user", "content": "What is your favorite color?"}
{"role": "assistant", "content": "I don't actually experience colors, but I'd be happy to discuss colors with you!"}
EOL

# Run gitloom
echo "Running gitloom..."
gitloom --mode chat "Tell me more about colors!"

# Print conversation
echo -e "\nFinal conversation:"
cat "chat.jsonl"