# AI Model Testing for Academic Comparison

Simple system for testing different AI models and generating comparison graphs for academic analysis.

## 🎯 How It Works (Simplified)

### 1. Manual Model Testing
- Edit `.github/workflows/ai-pr-review.yml` to change the AI model
- Create a PR with security vulnerabilities 
- Let the AI review and comment
- Repeat for different models

### 2. Generate Academic Graphs
- Run the analyzer script to collect results
- Generate comparison graphs for your college presentation

## 🔧 Quick Model Testing

### Step 1: Choose Your AI Model
Edit `.github/workflows/ai-pr-review.yml` and change these lines:

```yaml
# For GPT-4o:
provider: "openai"
model: "gpt-4o"

# For GPT-4-Turbo:
provider: "openai" 
model: "gpt-4-turbo"

# For O1-Preview:
provider: "openai"
model: "o1-preview"

# For Claude:
provider: "anthropic"
model: "claude-3-5-sonnet-20241022"

# For Groq Llama:
provider: "groq"
model: "llama-3.1-8b-instant"
```

### Step 2: Create Test PR
1. Create a branch: `git checkout -b test-gpt-4o`
2. Copy `src/test-vulnerabilities.ts` to your PR
3. Push and create PR
4. AI will review and add comments

### Step 3: Repeat for Other Models
- Change model in workflow file
- Create new branch: `git checkout -b test-claude`
- Create another PR
- Collect results

## 📊 Generate Comparison Graphs

### Install Dependencies
```bash
pip install requests matplotlib seaborn pandas
```

### Run Analysis
```bash
cd scripts
python3 academic-analyzer.py
```

The script will:
- ✅ Collect comments from your test PRs
- ✅ Analyze security detection rates
- ✅ Generate academic-quality graphs
- ✅ Save data as CSV for further analysis
- ✅ Print summary statistics

### Generated Files
- `ai_model_comparison_YYYYMMDD_HHMMSS.png` - Comparison graphs
- `ai_model_data_YYYYMMDD_HHMMSS.csv` - Raw data for analysis

## 📈 Graphs Generated

1. **Total Comments by Model** - Productivity comparison
2. **Security vs Quality Focus** - What each model prioritizes  
3. **Security Detection Rate** - Vulnerability finding accuracy
4. **Comment Detail Level** - Average comment length/depth

## 🎓 For Academic Use

The generated graphs and CSV data are perfect for:
- ✅ College presentations comparing AI models
- ✅ Research papers on AI code review capabilities
- ✅ Academic analysis of different LLM strengths
- ✅ Statistical comparison of model performance

## 📝 Test File Vulnerabilities

The `src/test-vulnerabilities.ts` file contains 27+ security issues:
- SQL Injection
- Cross-Site Scripting (XSS)
- Command Injection  
- Path Traversal
- Hardcoded Credentials
- Authentication Issues
- Cryptographic Weaknesses
- And many more...

## 🚀 Quick Start

1. **Test GPT-4o**: Edit workflow → Create PR with test file
2. **Test Claude**: Change to Claude → Create new PR  
3. **Test O1**: Change to O1-Preview → Create new PR
4. **Generate Graphs**: Run `python3 academic-analyzer.py`
5. **Use in College**: Present the generated comparison graphs!

Simple, clean, and focused on what you need for academic comparison! 🎯