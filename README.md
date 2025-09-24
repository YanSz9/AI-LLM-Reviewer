# AI Pull Request Reviewer

This project implements an AI-powered pull request reviewer that automatically analyzes code changes and provides comprehensive feedback on GitHub pull requests.

## Features

- 🤖 **Automated AI Reviews**: Get instant, intelligent feedback on every pull request
- 🔍 **Multi-Provider Support**: Works with OpenAI, Anthropic, Azure OpenAI, Ollama, and Groq
- 📋 **Structured Analysis**: Comprehensive checklist covering security, performance, tests, and style
- 🛡️ **Security-First**: Automatically redacts secrets and sensitive information
- ⚙️ **Configurable Rules**: Custom repository-specific guidelines and conventions
- 🚫 **Smart Filtering**: Skip binary files, huge diffs, and respect `[skip ai]` tags

## Quick Setup

1. **Add API Key**: Add your LLM provider API key as a repository secret:
   - `OPENAI_API_KEY` for OpenAI
   - `ANTHROPIC_API_KEY` for Anthropic
   - `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_ENDPOINT` for Azure
   - `OLLAMA_HOST` for Ollama
   - `GROQ_API_KEY` for Groq

2. **Build the Action**: Run the following commands:
   ```bash
   cd .github/actions/ai-pr-reviewer
   npm install
   npm run build
   ```

3. **Commit and Push**: The workflow will automatically trigger on new pull requests.

## Configuration

### Provider Configuration

Edit `.github/workflows/ai-pr-review.yml` to customize:

```yaml
- name: Run AI review
  uses: ./.github/actions/ai-pr-reviewer
  with:
    provider: "openai"        # openai|anthropic|azure-openai|ollama|groq
    model: "gpt-4o-mini"      # model name (for groq: llama3-8b-8192, mixtral-8x7b-32768)
    max-tokens: "2500"        # response length
    temperature: "0.2"        # creativity (0.0-1.0)
```

### Repository Rules

Customize `.github/ai-reviewer/rules.yml` to set project-specific guidelines:

```yaml
languages:
  primary: [typescript, javascript]
  secondary: [python, java]

security:
  secrets: forbid new plaintext keys
  deps: require review for new high-risk deps

tests:
  require: true
  coverage_hint: 70
```

## Skipping Reviews

- Add `[skip ai]` to PR title
- Add `skip-ai` label to PR
- Binary files and huge diffs are automatically skipped

## Review Output

Each review includes:
- **Summary**: High-level assessment of the changes
- **Key Risks**: Important security or correctness issues
- **Recommended Actions**: Prioritized list of improvements
- **Checks**: Pass/fail for correctness, security, performance, tests, style, docs
- **Inline Notes**: File-specific suggestions and improvements

## Supported Providers

### OpenAI
```bash
# Set in GitHub Secrets
OPENAI_API_KEY=sk-...
```

### Anthropic
```bash
# Set in GitHub Secrets  
ANTHROPIC_API_KEY=sk-ant-...
```

### Azure OpenAI
```bash
# Set in GitHub Secrets
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
```

### Ollama
```bash
# Set in GitHub Secrets
OLLAMA_HOST=http://your-ollama-server:11434
```

### Groq
```bash
# Set in GitHub Secrets
GROQ_API_KEY=gsk_...
```

**Popular Groq Models:**
- `llama3-8b-8192` - Fast Llama 3 8B model
- `mixtral-8x7b-32768` - Mixtral 8x7B model 
- `llama3-70b-8192` - Llama 3 70B model

## Development

### Building Locally
```bash
cd .github/actions/ai-pr-reviewer
npm install
npm run build
```

### Testing with Act
```bash
# Install act: https://github.com/nektos/act
act pull_request -e .github/act-events/pull_request.json
```

### Debugging
- Check workflow logs in GitHub Actions tab
- Verify API key is set correctly
- Ensure `pull-requests: write` permission is granted

## Roadmap

- [ ] **Per-file annotations**: Inline comments on specific lines
- [ ] **Multi-language support**: Better language-specific rules
- [ ] **Performance optimization**: Diff chunking for large PRs
- [ ] **GitHub App**: Move from Action to App for better integration
- [ ] **Caching**: Skip unchanged files between pushes
- [ ] **Custom prompts**: User-defined review templates

## Troubleshooting

### No review posted
- Check GitHub Actions logs
- Verify API key is set in repository secrets
- Ensure workflow has `pull-requests: write` permission

### Rate limiting
- Reduce `max-tokens` or increase `temperature`
- Consider using a different model tier
- Implement request queuing for high-traffic repos

### Large PRs
- Action automatically truncates large diffs
- Consider implementing diff chunking for comprehensive reviews
- Use file filtering to focus on important changes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with `act`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
