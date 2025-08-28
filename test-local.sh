#!/bin/bash

echo "🧪 Testing AI PR Reviewer Locally with Act"
echo "=========================================="

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo "❌ Act is not installed. Installing act..."
    echo "Please install act from: https://github.com/nektos/act#installation"
    echo ""
    echo "Quick install options:"
    echo "  # macOS"
    echo "  brew install act"
    echo ""
    echo "  # Linux"
    echo "  curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash"
    echo ""
    echo "  # Or download from: https://github.com/nektos/act/releases"
    exit 1
fi

echo "✅ Act is installed: $(act --version)"

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Check if we have the required files
if [ ! -f ".github/workflows/ai-pr-review.yml" ]; then
    echo "❌ Workflow file not found"
    exit 1
fi

echo "✅ Workflow file found"

# Create a test event with your API key
echo "🔧 Setting up test environment..."

# Check for API key in environment
if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  No API key found in environment variables."
    echo "Please set one of the following:"
    echo "  export OPENAI_API_KEY='your-key-here'"
    echo "  export ANTHROPIC_API_KEY='your-key-here'"
    echo ""
    echo "Or create a .env file with:"
    echo "  OPENAI_API_KEY=your-key-here"
    echo ""
    read -p "Continue without API key? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run the workflow with act
echo "🚀 Running AI PR Review workflow with act..."
echo "This will simulate a pull request event..."

# Create a more complete test event
cat > .github/act-events/test-pull-request.json << EOF
{
  "pull_request": {
    "number": 1,
    "title": "Add authentication service with security vulnerabilities",
    "body": "This PR adds a new authentication service. Please review for security issues.",
    "user": {
      "login": "testuser"
    },
    "base": {
      "ref": "main",
      "sha": "$(git rev-parse main)"
    },
    "head": {
      "ref": "test-ai-reviewer",
      "sha": "$(git rev-parse test-ai-reviewer)"
    },
    "labels": []
  },
  "repository": {
    "name": "AI-LLM-Reviewer",
    "owner": {
      "login": "YanSz9"
    }
  },
  "action": "opened"
}
EOF

echo "📝 Created test event file"

# Run act with the pull request event
act pull_request \
    --eventpath .github/act-events/test-pull-request.json \
    --secret-file .env \
    --verbose

echo ""
echo "🎉 Test completed!"
echo ""
echo "What the test does:"
echo "- Simulates a GitHub pull request event"
echo "- Runs your AI PR Reviewer action"
echo "- Shows what the AI would comment on the PR"
echo ""
echo "If successful, you should see:"
echo "- The action building and running"
echo "- API calls to your chosen LLM provider"
echo "- AI-generated review output"
