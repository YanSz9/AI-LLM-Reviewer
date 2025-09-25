#!/bin/bash

# Interactive Multi-Model AI Testing Script
# Provides easy interface for running multi-model tests and collecting results

set -e

echo "🤖 Multi-Model AI Testing System"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check dependencies
check_dependencies() {
    print_info "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check required Python packages
    python3 -c "import requests, pandas, matplotlib, seaborn" 2>/dev/null || {
        print_warning "Installing required Python packages..."
        pip3 install requests pandas matplotlib seaborn || {
            print_error "Failed to install Python packages"
            exit 1
        }
    }
    
    # Check GitHub CLI
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is required but not installed"
        print_info "Install with: sudo apt install gh"
        exit 1
    fi
    
    # Check if authenticated with GitHub
    if ! gh auth status &> /dev/null; then
        print_error "Not authenticated with GitHub CLI"
        print_info "Run: gh auth login"
        exit 1
    fi
    
    print_status "All dependencies are satisfied"
}

# Show menu
show_menu() {
    echo ""
    echo "Select an option:"
    echo "1) 🚀 Run complete multi-model test (create branches, PRs, and workflows)"
    echo "2) 📊 Collect and analyze existing results"
    echo "3) 🔍 Check status of existing PRs"
    echo "4) 🧹 Clean up test branches and results"
    echo "5) 📋 Show test configuration"
    echo "6) ❌ Exit"
    echo ""
}

# Run multi-model test
run_multi_model_test() {
    print_info "Starting multi-model AI testing..."
    
    # Check if we're in the right directory
    if [[ ! -f "package.json" ]] || [[ ! -d ".github" ]]; then
        print_error "Must be run from the root of the AI-TCC project"
        exit 1
    fi
    
    # Run the Python script
    python3 scripts/multi-model-tester.py
    
    print_status "Multi-model test setup complete!"
    print_info "PRs have been created. Wait a few minutes for GitHub Actions to complete, then run option 2 to collect results."
}

# Collect results
collect_results() {
    print_info "Collecting and analyzing results..."
    
    if [[ ! -f "multi_model_results/test_session.json" ]]; then
        print_error "No test session found. Run option 1 first."
        return
    fi
    
    python3 scripts/collect-results.py
    
    print_status "Results analysis complete!"
    print_info "Check multi_model_results/ folder for detailed reports"
    
    # Open report if possible
    if command -v xdg-open &> /dev/null; then
        print_info "Opening HTML report..."
        xdg-open multi_model_results/comparison_report.html 2>/dev/null || true
    fi
}

# Check PR status
check_pr_status() {
    print_info "Checking PR status..."
    
    if [[ ! -f "multi_model_results/test_session.json" ]]; then
        print_error "No test session found"
        return
    fi
    
    # Extract PR URLs from session data
    pr_urls=$(python3 -c "
import json
with open('multi_model_results/test_session.json', 'r') as f:
    data = json.load(f)
for pr in data['created_prs']:
    print(f\"{pr['model']}: {pr['pr_url']}\")
")
    
    echo "📋 Active PRs:"
    echo "$pr_urls"
    echo ""
    
    # Check GitHub Actions status
    print_info "GitHub Actions status:"
    gh run list --limit 10
}

# Clean up
cleanup() {
    print_warning "This will delete all test branches and close PRs. Continue? (y/N)"
    read -r confirmation
    
    if [[ $confirmation =~ ^[Yy]$ ]]; then
        print_info "Cleaning up test branches..."
        
        # Delete local test branches
        git branch | grep "test-" | xargs -r git branch -D 2>/dev/null || true
        
        # Delete remote test branches
        git branch -r | grep "test-" | sed 's/origin\///' | xargs -r -I {} git push origin --delete {} 2>/dev/null || true
        
        # Close open PRs
        gh pr list --state open --json number --jq '.[].number' | xargs -r -I {} gh pr close {} 2>/dev/null || true
        
        # Remove results directory
        rm -rf multi_model_results/
        
        print_status "Cleanup complete!"
    else
        print_info "Cleanup cancelled"
    fi
}

# Show configuration
show_config() {
    print_info "Multi-Model Test Configuration:"
    echo ""
    echo "📋 Models to test:"
    echo "  - GPT-4-Turbo (OpenAI)"
    echo "  - GPT-4o (OpenAI)"
    echo "  - O1-Preview (OpenAI)"
    echo "  - Claude-3.5-Sonnet (Anthropic)"
    echo ""
    echo "🎯 Test objectives:"
    echo "  - Security vulnerability detection"
    echo "  - Code review quality"
    echo "  - Comparative performance analysis"
    echo ""
    echo "📁 Test file: src/benchmark-test.ts"
    echo "🔍 Vulnerabilities: 27+ intentional security issues"
    echo ""
    echo "📊 Analysis includes:"
    echo "  - Detection rate percentage"
    echo "  - Total comments per model"
    echo "  - Security-focused mentions"
    echo "  - Comparative charts and HTML report"
}

# Main script
main() {
    check_dependencies
    
    while true; do
        show_menu
        read -p "Enter your choice (1-6): " choice
        
        case $choice in
            1)
                run_multi_model_test
                ;;
            2)
                collect_results
                ;;
            3)
                check_pr_status
                ;;
            4)
                cleanup
                ;;
            5)
                show_config
                ;;
            6)
                print_info "Exiting..."
                exit 0
                ;;
            *)
                print_error "Invalid option. Please choose 1-6."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main