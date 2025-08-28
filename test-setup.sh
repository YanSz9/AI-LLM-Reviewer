#!/bin/bash

echo "🧪 Testing AI PR Reviewer Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ "$1" = "success" ]; then
        echo -e "${GREEN}✅ $2${NC}"
    elif [ "$1" = "error" ]; then
        echo -e "${RED}❌ $2${NC}"
    elif [ "$1" = "warning" ]; then
        echo -e "${YELLOW}⚠️  $2${NC}"
    else
        echo "$2"
    fi
}

# Check directory structure
echo "📁 Checking directory structure..."

required_files=(
    ".github/workflows/ai-pr-review.yml"
    ".github/actions/ai-pr-reviewer/action.yml"
    ".github/actions/ai-pr-reviewer/package.json"
    ".github/actions/ai-pr-reviewer/tsconfig.json"
    ".github/actions/ai-pr-reviewer/src/index.ts"
    ".github/ai-reviewer/rules.yml"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_status "success" "$file exists"
    else
        print_status "error" "$file is missing"
        exit 1
    fi
done

# Check if dependencies are installed
echo ""
echo "📦 Checking dependencies..."
if [ -d ".github/actions/ai-pr-reviewer/node_modules" ]; then
    print_status "success" "Dependencies are installed"
else
    print_status "warning" "Dependencies not installed. Run 'npm install' in .github/actions/ai-pr-reviewer/"
fi

# Check if built
echo ""
echo "🔨 Checking build output..."
if [ -f ".github/actions/ai-pr-reviewer/dist/index.js" ]; then
    print_status "success" "Action is built"
    
    # Check file size
    size=$(wc -c < ".github/actions/ai-pr-reviewer/dist/index.js")
    if [ "$size" -gt 100000 ]; then
        print_status "success" "Bundle size looks good (${size} bytes)"
    else
        print_status "warning" "Bundle seems small (${size} bytes) - might be incomplete"
    fi
else
    print_status "error" "Action not built. Run 'npm run build' in .github/actions/ai-pr-reviewer/"
fi

# Validate YAML files
echo ""
echo "📋 Validating configuration files..."

# Check if yq is available for YAML validation
if command -v node &> /dev/null; then
    # Use Node.js to validate YAML
    node -e "
        const fs = require('fs');
        const yaml = require('js-yaml');
        
        try {
            // Validate workflow file
            const workflow = yaml.load(fs.readFileSync('.github/workflows/ai-pr-review.yml', 'utf8'));
            console.log('✅ Workflow YAML is valid');
            
            // Validate action file
            const action = yaml.load(fs.readFileSync('.github/actions/ai-pr-reviewer/action.yml', 'utf8'));
            console.log('✅ Action YAML is valid');
            
            // Validate rules file
            const rules = yaml.load(fs.readFileSync('.github/ai-reviewer/rules.yml', 'utf8'));
            console.log('✅ Rules YAML is valid');
            
        } catch (error) {
            console.error('❌ YAML validation failed:', error.message);
            process.exit(1);
        }
    " 2>/dev/null || print_status "warning" "Could not validate YAML files (js-yaml not available)"
fi

# Check for common issues
echo ""
echo "🔍 Checking for common issues..."

# Check if action.yml points to correct main file
if grep -q "main: 'dist/index.js'" .github/actions/ai-pr-reviewer/action.yml; then
    print_status "success" "action.yml points to correct main file"
else
    print_status "error" "action.yml should have 'main: dist/index.js'"
fi

# Check if package.json has build script
if grep -q '"build"' .github/actions/ai-pr-reviewer/package.json; then
    print_status "success" "package.json has build script"
else
    print_status "error" "package.json missing build script"
fi

# Summary
echo ""
echo "📊 Test Summary:"
echo "==============="

if [ -f ".github/actions/ai-pr-reviewer/dist/index.js" ] && [ -d ".github/actions/ai-pr-reviewer/node_modules" ]; then
    print_status "success" "AI PR Reviewer is ready to use!"
    echo ""
    echo "Next steps:"
    echo "1. Add your API key as a repository secret"
    echo "2. Customize .github/ai-reviewer/rules.yml"
    echo "3. Commit and push to your repository"
    echo "4. Create a test pull request"
else
    print_status "error" "Setup incomplete. Please fix the issues above."
    echo ""
    echo "To complete setup:"
    echo "1. cd .github/actions/ai-pr-reviewer"
    echo "2. npm install"
    echo "3. npm run build"
fi

echo ""
echo "For more help, see README.md or EXAMPLES.md"
