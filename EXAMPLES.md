# Example Configurations

## Different Provider Configurations

### OpenAI Configuration
```yaml
with:
  provider: "openai"
  model: "gpt-4o-mini"  # or "gpt-4", "gpt-3.5-turbo"
  max-tokens: "2500"
  temperature: "0.2"
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Anthropic Configuration
```yaml
with:
  provider: "anthropic"
  model: "claude-3-5-sonnet-20241022"  # or "claude-3-haiku-20240307"
  max-tokens: "2500"
  temperature: "0.2"
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Azure OpenAI Configuration
```yaml
with:
  provider: "azure-openai"
  model: "gpt-4"  # your deployment name
  max-tokens: "2500"
  temperature: "0.2"
env:
  AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
  AZURE_OPENAI_ENDPOINT: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
```

### Ollama Configuration
```yaml
with:
  provider: "ollama"
  model: "llama2"  # or "codellama", "mistral"
  max-tokens: "2500"
  temperature: "0.2"
env:
  OLLAMA_HOST: ${{ secrets.OLLAMA_HOST }}  # e.g., http://localhost:11434
```

## Advanced Rules Examples

### Python Project Rules
```yaml
languages:
  primary: [python]
  secondary: [yaml, dockerfile]

style:
  formatter: black
  linter: flake8
  type_hints: required
  naming: snake_case

security:
  secrets: forbid hardcoded credentials
  imports: avoid dangerous imports like eval, exec
  sql: check for injection vulnerabilities

tests:
  framework: pytest
  coverage: 80
  location: tests/

documentation:
  docstrings: required for public functions
  type_hints: required
  readme: keep updated
```

### React/TypeScript Project Rules
```yaml
languages:
  primary: [typescript, tsx]
  secondary: [css, scss, json]

style:
  eslint: true
  prettier: true
  naming: 
    components: PascalCase
    hooks: camelCase starting with 'use'
    constants: SCREAMING_SNAKE_CASE

security:
  xss: check for dangerouslySetInnerHTML
  deps: review new dependencies
  env: no secrets in client code

tests:
  framework: jest + testing-library
  coverage: 75
  component_tests: required for new components

performance:
  bundle_size: monitor impact
  lazy_loading: use for large components
  memoization: consider for expensive calculations
```

### Backend API Rules
```yaml
languages:
  primary: [typescript, javascript]
  secondary: [sql, yaml]

security:
  auth: verify authentication on all endpoints
  input: validate all user inputs
  sql: use parameterized queries
  cors: configure properly
  rate_limiting: implement for public endpoints

architecture:
  layers: controller -> service -> repository
  error_handling: consistent error responses
  logging: structured logging for debugging

tests:
  unit: 80% coverage
  integration: test all endpoints
  mocking: mock external dependencies

documentation:
  openapi: keep swagger updated
  endpoints: document all public APIs
```

## Workflow Variations

### Review Only on Main Branch PRs
```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches: ["main", "develop"]
```

### Different Rules for Different Paths
```yaml
# In your workflow, you could have multiple jobs
jobs:
  review-frontend:
    if: contains(github.event.pull_request.changed_files, 'frontend/')
    steps:
      - uses: ./.github/actions/ai-pr-reviewer
        with:
          rules-path: ".github/ai-reviewer/frontend-rules.yml"
  
  review-backend:
    if: contains(github.event.pull_request.changed_files, 'backend/')
    steps:
      - uses: ./.github/actions/ai-pr-reviewer
        with:
          rules-path: ".github/ai-reviewer/backend-rules.yml"
```

### Skip Reviews for Documentation-Only Changes
```yaml
jobs:
  review:
    if: >-
      !contains(github.event.pull_request.title, '[skip ai]') &&
      !contains(join(github.event.pull_request.labels.*.name, ','), 'skip-ai') &&
      !contains(github.event.pull_request.title, '[docs only]')
```
