# Multi-Model AI Testing System

This directory contains scripts for running comprehensive multi-model AI testing and analysis.

## Scripts Overview

### `multi-model-tester.py`
- **Purpose**: Creates test branches and PRs for different AI models
- **Features**: 
  - Generates benchmark test file with 27+ security vulnerabilities
  - Creates PR-specific GitHub Actions workflows
  - Sets up test branches for priority AI models
  - Creates PRs with detailed descriptions

### `collect-results.py`  
- **Purpose**: Collects and analyzes results from AI model PR reviews
- **Features**:
  - Fetches PR reviews and comments via GitHub API
  - Analyzes security vulnerability detection patterns  
  - Generates comparative performance charts
  - Creates detailed HTML report with rankings

### `run-multi-model-test.sh`
- **Purpose**: Interactive interface for running tests and collecting results
- **Features**:
  - Dependency checking and installation
  - Menu-driven interface
  - Status checking for PRs and workflows
  - Cleanup utilities

## Usage

### Quick Start
```bash
# Run the interactive menu
./scripts/run-multi-model-test.sh
```

### Manual Execution
```bash
# 1. Run multi-model test setup
python3 scripts/multi-model-tester.py

# 2. Wait for GitHub Actions to complete (5-10 minutes)

# 3. Collect and analyze results  
python3 scripts/collect-results.py
```

## AI Models Tested

- **GPT-4-Turbo** (OpenAI)
- **GPT-4o** (OpenAI) 
- **O1-Preview** (OpenAI)
- **Claude-3.5-Sonnet** (Anthropic)
- **Groq Llama 3.1** (Groq)
- **GPT-4o-Mini** (OpenAI)
- **O1-Mini** (OpenAI)

## Security Vulnerabilities in Benchmark

The benchmark test file contains 27+ intentional security issues:

1. SQL Injection
2. Cross-Site Scripting (XSS)
3. Command Injection  
4. Path Traversal
5. Insecure Direct Object Reference
6. Weak Password Hashing
7. Hardcoded Secrets
8. Insecure Random Number Generation
9. Missing Input Validation
10. Information Disclosure
11. Insecure File Upload
12. Missing Authentication
13. Race Condition
14. Insecure Deserialization
15. Missing Rate Limiting
16. Insecure HTTP Headers
17. Open Redirect
18. LDAP Injection
19. XML External Entity (XXE)
20. Insecure Cryptographic Storage
21. Missing CSRF Protection
22. Insecure Session Management
23. Buffer Overflow Risk
24. Time-Based Attacks
25. Insecure Configuration
26. Missing Input Sanitization (ReDoS)
27. Privilege Escalation

## Output Files

### `multi_model_results/`
- `test_session.json` - Test session metadata and PR tracking
- `detailed_results.json` - Raw analysis data for all models
- `comparison_report.html` - Interactive HTML report with charts
- `comparison_charts.png` - Performance comparison visualizations

## Dependencies

### Python Packages
```bash
pip3 install requests pandas matplotlib seaborn
```

### System Requirements
- Python 3.x
- GitHub CLI (`gh`)
- Git
- Active GitHub authentication (`gh auth login`)

## Analysis Metrics

- **Detection Rate**: Percentage of security issue types detected
- **Total Comments**: Number of review comments generated
- **Security Mentions**: Total security-related mentions
- **Issue Coverage**: Which specific vulnerabilities were identified

## Workflow Integration

The system creates PR-specific GitHub Actions workflows that trigger on pull requests:
- `.github/workflows/pr-gpt-4-turbo.yml`
- `.github/workflows/pr-gpt-4o.yml`
- `.github/workflows/pr-o1-preview.yml`
- `.github/workflows/pr-claude-3-5-sonnet.yml`

Each workflow uses the main AI reviewer action with model-specific configurations.