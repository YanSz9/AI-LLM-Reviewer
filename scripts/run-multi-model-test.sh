#!/bin/bash

# Multi-Model AI Benchmark Runner
# Runs tests for each model individually and compares results

set -e

echo "🎯 MULTI-MODEL AI BENCHMARK TESTING SYSTEM"
echo "=========================================="

# Check requirements
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git is required"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a git repository"
    exit 1
fi

# Function to show usage
show_usage() {
    echo ""
    echo "🔧 Usage:"
    echo "  $0 [OPTIONS] [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  run-all              Run tests for all available models"
    echo "  run-selected         Run tests for selected models interactively"
    echo "  run-openai-only      Run tests for OpenAI models only"
    echo "  collect-results      Collect and analyze results from completed tests"
    echo "  status              Show status of all test branches"
    echo ""
    echo "Options:"
    echo "  --models MODEL1,MODEL2   Comma-separated list of specific models"
    echo "  --token TOKEN           GitHub token (or use GITHUB_TOKEN env var)"
    echo "  --help                  Show this help message"
    echo ""
    echo "Available Models:"
    echo "  • gpt-4-turbo"
    echo "  • gpt-4o"  
    echo "  • gpt-4o-mini"
    echo "  • o1-preview"
    echo "  • o1-mini"
    echo "  • claude-3-5-sonnet"
    echo "  • groq-llama-3.1"
}

# Function to run interactive model selection
select_models() {
    echo "🤖 Available AI Models:"
    echo "1. gpt-4-turbo"
    echo "2. gpt-4o"
    echo "3. gpt-4o-mini"
    echo "4. o1-preview"
    echo "5. o1-mini"
    echo "6. claude-3-5-sonnet"
    echo "7. groq-llama-3.1"
    echo "8. All OpenAI models (1-5)"
    echo "9. All models (1-7)"
    echo ""
    
    read -p "Enter your choices (comma-separated numbers, e.g., 1,2,3): " choices
    
    declare -a selected_models=()
    
    IFS=',' read -ra NUMBERS <<< "$choices"
    for num in "${NUMBERS[@]}"; do
        case $num in
            1) selected_models+=("gpt-4-turbo") ;;
            2) selected_models+=("gpt-4o") ;;
            3) selected_models+=("gpt-4o-mini") ;;
            4) selected_models+=("o1-preview") ;;
            5) selected_models+=("o1-mini") ;;
            6) selected_models+=("claude-3-5-sonnet") ;;
            7) selected_models+=("groq-llama-3.1") ;;
            8) selected_models+=("gpt-4-turbo" "gpt-4o" "gpt-4o-mini" "o1-preview" "o1-mini") ;;
            9) selected_models+=("gpt-4-turbo" "gpt-4o" "gpt-4o-mini" "o1-preview" "o1-mini" "claude-3-5-sonnet" "groq-llama-3.1") ;;
            *) echo "⚠️  Invalid choice: $num" ;;
        esac
    done
    
    if [ ${#selected_models[@]} -eq 0 ]; then
        echo "❌ No valid models selected"
        exit 1
    fi
    
    echo "📋 Selected models: ${selected_models[*]}"
    echo ""
    
    # Convert array to comma-separated string for Python script
    IFS=',' eval 'models_string="${selected_models[*]}"'
    echo "$models_string"
}

# Function to run multi-model testing
run_multi_model_test() {
    local models_arg=""
    
    if [ ! -z "$1" ]; then
        models_arg="--models $1"
    fi
    
    local token_arg=""
    if [ ! -z "$GITHUB_TOKEN" ]; then
        token_arg="--token $GITHUB_TOKEN"
    fi
    
    echo "🚀 Starting multi-model benchmark testing..."
    echo "📊 This will create separate test branches for each model"
    echo ""
    
    # Confirm before proceeding
    read -p "Continue? This will create multiple branches and workflows (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
    
    # Run the multi-model tester
    python3 scripts/multi-model-tester.py $models_arg $token_arg
}

# Function to collect and analyze results
collect_results() {
    local token_arg=""
    if [ ! -z "$    " ]; then
        token_arg="--token $GITHUB_TOKEN"
    fi
    
    echo "📊 Collecting results from all test branches..."
    python3 scripts/collect-results.py $token_arg
}

# Function to show status of test branches
show_status() {
    echo "🔍 Checking status of test branches..."
    
    # Get all remote test branches
    git fetch --all > /dev/null 2>&1 || true
    
    test_branches=$(git branch -r | grep "origin/test-" | grep -E "202[0-9]" || true)
    
    if [ -z "$test_branches" ]; then
        echo "❌ No test branches found"
        return
    fi
    
    echo "📋 Found test branches:"
    echo "$test_branches" | sed 's/origin\///g' | sed 's/^/   • /'
    echo ""
    echo "💡 To collect detailed results, run:"
    echo "   $0 collect-results"
}

# Parse command line arguments
MODELS=""
GITHUB_TOKEN=${GITHUB_TOKEN:-""}

while [[ $# -gt 0 ]]; do
    case $1 in
        --models)
            MODELS="$2"
            shift 2
            ;;
        --token)
            GITHUB_TOKEN="$2"
            shift 2
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        run-all)
            COMMAND="run-all"
            shift
            ;;
        run-selected)
            COMMAND="run-selected"
            shift
            ;;
        run-openai-only)
            COMMAND="run-openai-only"
            shift
            ;;
        collect-results)
            COMMAND="collect-results"
            shift
            ;;
        status)
            COMMAND="status"
            shift
            ;;
        *)
            echo "❌ Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Set default command if none provided
if [ -z "$COMMAND" ]; then
    COMMAND="run-selected"
fi

# Execute command
case $COMMAND in
    run-all)
        echo "🤖 Running tests for ALL available models..."
        run_multi_model_test
        ;;
    run-selected)
        echo "📋 Select models to test:"
        selected_models=$(select_models)
        run_multi_model_test "$selected_models"
        ;;
    run-openai-only)
        echo "🤖 Running tests for OpenAI models only..."
        run_multi_model_test "gpt-4-turbo,gpt-4o,gpt-4o-mini,o1-preview,o1-mini"
        ;;
    collect-results)
        collect_results
        ;;
    status)
        show_status
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac

echo ""
echo "🎯 Multi-Model Benchmark System Complete!"
echo ""
echo "📚 What happens next:"
echo "1. Each selected model gets its own test branch"
echo "2. GitHub Actions runs AI review workflows on each branch"
echo "3. Use 'collect-results' to gather and compare all results"
echo "4. Generate comparative analysis reports"
echo ""
echo "💡 Pro tip: Wait 5-10 minutes for workflows to complete, then run:"
echo "   $0 collect-results"