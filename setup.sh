#!/bin/bash

echo "🚀 Setting up AI Pull Request Reviewer..."

# Check if we're in the right directory
if [ ! -f ".github/actions/ai-pr-reviewer/package.json" ]; then
    echo "❌ Error: Please run this script from the root of your repository"
    echo "   Make sure the .github/actions/ai-pr-reviewer directory exists"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "   Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Error: Node.js version 18+ is required"
    echo "   Current version: $(node --version)"
    exit 1
fi

echo "✅ Node.js $(node --version) detected"

# Navigate to action directory
cd .github/actions/ai-pr-reviewer

echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "🔨 Building the action..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Failed to build the action"
    exit 1
fi

echo "✅ Build successful!"

# Navigate back to root
cd ../../..

echo ""
echo "🎉 Setup complete! Your AI PR Reviewer is ready to use."
echo ""
echo "Next steps:"
echo "1. Add your API key as a repository secret:"
echo "   - For OpenAI: OPENAI_API_KEY"
echo "   - For Anthropic: ANTHROPIC_API_KEY"
echo "   - For Azure: AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT"
echo "   - For Ollama: OLLAMA_HOST"
echo ""
echo "2. Customize the rules in .github/ai-reviewer/rules.yml"
echo ""
echo "3. Commit and push these changes to your repository"
echo ""
echo "4. Create a test pull request to see the AI reviewer in action!"
echo ""
echo "📚 For more configuration options, check EXAMPLES.md"
