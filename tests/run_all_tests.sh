#!/bin/bash

# Run all tests
echo "Running all tests..."
echo "==================="

# Make all test scripts executable
chmod +x test*.sh

# Run each test
./test1_base_multiple.sh
echo -e "\n"
./test2_base_existing.sh
echo -e "\n"
./test3_chat_new.sh
echo -e "\n"
./test4_chat_existing.sh