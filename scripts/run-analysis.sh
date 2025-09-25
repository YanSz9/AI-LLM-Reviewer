#!/bin/bash

# AI Model Benchmark Analysis Script
# Runs the Python analyzer and opens results

set -e

echo "🎯 AI Model Benchmark Analysis"
echo "=============================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Install required Python packages
echo "📦 Installing required Python packages..."
pip3 install --user matplotlib pandas seaborn requests numpy || {
    echo "⚠️  Failed to install some packages. Continuing anyway..."
}

# Get PR number
if [ -z "$1" ]; then
    echo "📝 Enter the PR number to analyze:"
    read -p "PR #: " PR_NUMBER
else
    PR_NUMBER=$1
fi

# Check for GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "🔑 GitHub token not found in environment."
    echo "You can:"
    echo "1. Set GITHUB_TOKEN environment variable"
    echo "2. Create a personal access token at: https://github.com/settings/tokens"
    echo "3. Continue without token (limited functionality)"
    echo ""
    read -p "Continue without token? (y/N): " CONTINUE
    if [[ ! $CONTINUE =~ ^[Yy]$ ]]; then
        echo "Please set GITHUB_TOKEN and run again."
        exit 1
    fi
fi

# Create output directory
OUTPUT_DIR="benchmark_results_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "🔍 Analyzing PR #$PR_NUMBER..."
echo "📊 Output will be saved to: $OUTPUT_DIR"

# Run the analysis
python3 scripts/analyze-benchmark.py "$PR_NUMBER" --output "$OUTPUT_DIR"

# Check if analysis was successful
if [ -f "$OUTPUT_DIR/benchmark_report.html" ]; then
    echo ""
    echo "✅ Analysis complete!"
    echo "📄 Reports generated:"
    echo "   🌐 $OUTPUT_DIR/benchmark_report.html - Interactive HTML report"
    echo "   📊 $OUTPUT_DIR/comparison_graphs.png - Performance graphs"
    echo "   📋 $OUTPUT_DIR/detailed_results.json - Raw data"
    echo ""
    
    # Try to open the HTML report
    if command -v xdg-open &> /dev/null; then
        echo "🚀 Opening HTML report in browser..."
        xdg-open "$OUTPUT_DIR/benchmark_report.html"
    elif command -v open &> /dev/null; then
        echo "🚀 Opening HTML report in browser..."
        open "$OUTPUT_DIR/benchmark_report.html"
    else
        echo "📖 To view the report, open: $OUTPUT_DIR/benchmark_report.html"
    fi
    
    # Show summary
    if [ -f "$OUTPUT_DIR/detailed_results.json" ]; then
        echo ""
        echo "📊 Quick Summary:"
        python3 -c "
import json
with open('$OUTPUT_DIR/detailed_results.json', 'r') as f:
    data = json.load(f)
    
print('🏆 Best Performing Models:')
summary = data.get('summary', {})
for metric, model in summary.items():
    if model:
        print(f'  {metric.replace(\"_\", \" \").title()}: {model}')

print('\\n📈 Detection Rates:')
for model, results in data.get('model_results', {}).items():
    rate = results.get('detection_rate', 0)
    print(f'  {model}: {rate:.1f}%')
"
    fi
    
else
    echo "❌ Analysis failed. Check the output above for errors."
    exit 1
fi