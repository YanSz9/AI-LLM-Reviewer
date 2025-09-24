#!/bin/bash

# AI Model Benchmark Script
# This script helps run benchmarks across different OpenAI models

set -e

echo "🎯 AI Model Benchmark Tool"
echo "=========================="

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Function to create a benchmark PR
create_benchmark_pr() {
    local branch_name="benchmark-$(date +%Y%m%d-%H%M%S)"
    local model_list="$1"
    
    echo "📝 Creating benchmark branch: $branch_name"
    
    # Create new branch
    git checkout -b "$branch_name"
    
    # Make a small change to trigger the workflow
    echo "// Benchmark run at $(date)" >> src/benchmark-test.ts
    
    # Commit changes
    git add .
    git commit -m "benchmark: AI model comparison test

🎯 BENCHMARK SETUP:
- Test file: src/benchmark-test.ts (27+ intentional issues)
- Models to test: $model_list
- Categories: Security, Performance, Code Quality, TypeScript issues

📊 EVALUATION CRITERIA:
- Detection rate: How many of the 27 issues are found
- Accuracy: Quality of issue identification  
- Solution quality: Helpfulness of suggested fixes
- Performance: Speed and token efficiency

🔍 KNOWN ISSUES TO DETECT:
- SQL injection vulnerabilities (5 instances)
- XSS vulnerabilities (2 instances)  
- Hardcoded secrets (3 instances)
- Race conditions (1 instance)
- Memory leaks (2 instances)
- Command injection (2 instances)
- Cryptographic weaknesses (2 instances)
- Performance issues (3 instances)
- Type safety problems (4 instances)
- Authentication bypass (2 instances)
- Information disclosure (2 instances)

Each model will review the same code and provide inline comments.
Compare results to evaluate which model provides the best code review quality."
    
    # Push branch
    git push origin "$branch_name"
    
    # Create PR
    gh pr create \
        --title "🎯 AI Model Benchmark: $model_list" \
        --body "# AI Model Benchmark Test

This PR is designed to benchmark different AI models on the same codebase.

## Test File: \`src/benchmark-test.ts\`

Contains **27+ intentional issues** across multiple categories:

### Security Issues (15):
- 🔴 SQL injection vulnerabilities (5x)
- 🔴 XSS vulnerabilities (2x)
- 🔴 Hardcoded API keys and secrets (3x)
- 🔴 Command injection (2x)
- 🔴 Insecure cryptographic implementation (2x)
- 🔴 Authentication bypass (1x)

### Performance Issues (5):
- 🟡 Race conditions (1x)
- 🟡 Memory leaks (2x)
- 🟡 Inefficient algorithms O(n²) (1x)
- 🟡 Synchronous heavy computation (1x)

### Code Quality Issues (7+):
- 🟢 Type safety violations (4x)
- 🟢 Information disclosure (2x)
- 🟢 Missing error handling (1x)

## Models Being Tested:
$model_list

## Evaluation Criteria:

1. **Detection Rate**: How many of the 27 issues are identified
2. **Accuracy**: Quality of issue identification (no false positives)
3. **Solution Quality**: Helpfulness and correctness of suggested fixes
4. **Performance**: Speed of analysis and token efficiency
5. **Inline Comments**: Quality of line-specific feedback

## How to Analyze Results:

1. Check the PR comments from each model
2. Count how many real issues were detected
3. Evaluate the quality of explanations and fixes
4. Compare response times and token usage
5. Rate the overall usefulness for developers

Each model will provide both summary reviews and inline comments on specific lines." \
        --head "$branch_name" \
        --base "main"
    
    echo "✅ Benchmark PR created successfully!"
    echo "🔗 The PR will trigger workflows for: $model_list"
    echo ""
    echo "📊 To analyze results:"
    echo "1. Wait for all workflows to complete"
    echo "2. Review the PR comments from each model" 
    echo "3. Compare detection rates and solution quality"
    echo "4. Check GitHub Actions for performance metrics"
}

# Function to run specific model benchmark
run_single_model() {
    local model="$1"
    echo "🚀 Running benchmark for model: $model"
    
    # Trigger the specific workflow
    gh workflow run "AI PR Review" \
        --field "model=$model" \
        --field "provider=openai"
    
    echo "✅ Benchmark triggered for $model"
}

# Main menu
echo ""
echo "Select benchmark type:"
echo "1. 🔥 Full benchmark (all OpenAI models)"
echo "2. 🎯 Quick benchmark (GPT-4o, GPT-4o-mini, o1-preview)"
echo "3. 🧪 Custom model selection"
echo "4. 📊 Create benchmark PR (recommended)"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        model_list="GPT-4 Turbo, GPT-4o, GPT-4o Mini, o1-preview, o1-mini"
        create_benchmark_pr "$model_list"
        ;;
    2)
        model_list="GPT-4o, GPT-4o Mini, o1-preview"
        create_benchmark_pr "$model_list"
        ;;
    3)
        echo "Available models:"
        echo "- gpt-4-turbo"
        echo "- gpt-4o" 
        echo "- gpt-4o-mini"
        echo "- o1-preview"
        echo "- o1-mini"
        echo ""
        read -p "Enter model name: " model
        run_single_model "$model"
        ;;
    4)
        model_list="All Compatible OpenAI Models"
        create_benchmark_pr "$model_list"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎯 Benchmark Tips:"
echo "• Each model will analyze the same src/benchmark-test.ts file"  
echo "• Look for differences in detection rates and solution quality"
echo "• o1 models may provide more thorough reasoning"
echo "• GPT-4o models balance speed and accuracy"
echo "• Check both summary reviews and inline comments"
echo ""
echo "📊 Happy benchmarking!"