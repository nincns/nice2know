#!/bin/bash
# Test LLM Connection and Extraction

echo "=========================================="
echo "Nice2Know - LLM Test Suite"
echo "=========================================="
echo ""

# 1. Test Connection
echo "1. Testing Ollama connection..."
python agents/llm_request.py --test
if [ $? -ne 0 ]; then
    echo "✗ Connection test failed"
    exit 1
fi
echo ""

# 2. Simple prompt test
echo "2. Testing simple prompt..."
python agents/llm_request.py --prompt "Say hello in one sentence."
echo ""

# 3. Extract asset from mail
echo "3. Extracting asset from mail..."
python agents/llm_request.py \
    --pre_prompt config/prompts/extract_asset.txt \
    --mailbody storage/mails/*.eml \
    --export storage/processed/test_asset.json
echo ""

# 4. Extract problem
echo "4. Extracting problem..."
python agents/llm_request.py \
    --pre_prompt config/prompts/extract_problem.txt \
    --mailbody storage/mails/*.eml \
    --export storage/processed/test_problem.json
echo ""

# 5. Extract solution
echo "5. Extracting solution..."
python agents/llm_request.py \
    --pre_prompt config/prompts/extract_solution.txt \
    --mailbody storage/mails/*.eml \
    --export storage/processed/test_solution.json
echo ""

echo "=========================================="
echo "✓ All tests complete"
echo "Check storage/processed/ for results"
echo "=========================================="
