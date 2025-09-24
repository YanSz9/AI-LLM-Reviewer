import * as core from '@actions/core';
import * as github from '@actions/github';
import { Octokit } from '@octokit/rest';
import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';

const MAX_FILE_BYTES = 200_000; // skip huge diffs (per file)
const BINARY_EXT = [
  '.png','.jpg','.jpeg','.gif','.webp','.svg','.pdf','.zip','.gz','.rar','.7z','.ico','.lock','.bin'
];

function isBinary(filename: string) {
  const ext = path.extname(filename).toLowerCase();
  return BINARY_EXT.includes(ext);
}

function loadRules(rulesPath: string): string {
  try {
    if (!fs.existsSync(rulesPath)) return '';
    const doc = yaml.load(fs.readFileSync(rulesPath, 'utf8')) as any;
    return `\nRepo rules & conventions:\n${JSON.stringify(doc, null, 2)}`;
  } catch (e) {
    core.warning(`Failed to load rules from ${rulesPath}: ${String(e)}`);
    return '';
  }
}

function redactSecrets(text: string): string {
  return text
    .replace(/(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[^'\"\n]+/gi, '$1: [REDACTED]')
    .replace(/AIza[0-9A-Za-z\-_]{35}/g, '[REDACTED_GOOGLE_KEY]');
}

function extractJsonFromResponse(content: string): any {
  try {
    // First try to parse as direct JSON
    return JSON.parse(content);
  } catch (e) {
    // If that fails, try to extract JSON from markdown code blocks
    const jsonMatch = content.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/);
    if (jsonMatch) {
      try {
        return JSON.parse(jsonMatch[1]);
      } catch (e2) {
        // If markdown extraction fails, try to find any JSON-like structure
        const jsonStart = content.indexOf('{');
        const jsonEnd = content.lastIndexOf('}');
        if (jsonStart !== -1 && jsonEnd !== -1 && jsonEnd > jsonStart) {
          try {
            return JSON.parse(content.substring(jsonStart, jsonEnd + 1));
          } catch (e3) {
            // Last resort: return a basic structure
            console.warn('Failed to parse JSON response, using fallback');
            return {
              summary: "Failed to parse AI response properly",
              risks: ["Could not extract structured review"],
              actions: ["Please check the AI response format"],
              checks: {
                correctness: "Unable to analyze",
                security: "Unable to analyze", 
                performance: "Unable to analyze",
                tests: "Unable to analyze",
                style: "Unable to analyze",
                docs: "Unable to analyze"
              },
              inline: []
            };
          }
        }
      }
    }
    
    // If no JSON structure found, return fallback
    return {
      summary: "AI response received but could not be parsed as JSON",
      risks: ["Response parsing failed"],
      actions: ["Check AI model response format"],
      checks: {
        correctness: "Parse error",
        security: "Parse error",
        performance: "Parse error", 
        tests: "Parse error",
        style: "Parse error",
        docs: "Parse error"
      },
      inline: []
    };
  }
}

async function getPRDiff(octokit: Octokit, owner: string, repo: string, pr: number) {
  const files = await octokit.pulls.listFiles({ owner, repo, pull_number: pr, per_page: 300 });
  const parts: string[] = [];
  const fileInfo: Array<{filename: string, patch: string, additions: number, deletions: number}> = [];
  
  for (const f of files.data) {
    if (!f.patch) continue;
    if (isBinary(f.filename)) continue;
    if ((f.changes ?? 0) > 5000) continue; // extremely large file changes
    if ((f.additions ?? 0) + (f.deletions ?? 0) > 5000) continue;
    const patch = f.patch.length > MAX_FILE_BYTES ? f.patch.slice(0, MAX_FILE_BYTES) + '\n[truncated]\n' : f.patch;
    parts.push(`FILE: ${f.filename}\nSTATUS: ${f.status}\n${patch}`);
    
    // Store file info for inline comments
    fileInfo.push({
      filename: f.filename,
      patch: patch,
      additions: f.additions ?? 0,
      deletions: f.deletions ?? 0
    });
  }
  
  let diffText = parts.join('\n\n---\n\n');
  
  // Estimate token count (rough approximation: 1 token ≈ 4 characters)
  const estimatedTokens = diffText.length / 4;
  const MAX_DIFF_TOKENS = 2500; // Leave room for prompt and response
  
  if (estimatedTokens > MAX_DIFF_TOKENS) {
    // Truncate diff to stay within token limits
    const maxChars = MAX_DIFF_TOKENS * 4;
    diffText = diffText.slice(0, maxChars) + '\n\n[DIFF TRUNCATED DUE TO SIZE - Showing first ' + MAX_DIFF_TOKENS + ' tokens]';
    core.warning(`Diff truncated due to size: ${estimatedTokens} tokens > ${MAX_DIFF_TOKENS} limit`);
  }
  
  return {
    diffText,
    files: fileInfo
  };
}

function buildPrompt(opts: {
  title: string; body: string; author: string; base: string; head: string;
  rules: string; diff: string; includeTests: boolean; includeStyle: boolean;
  files: Array<{filename: string, patch: string, additions: number, deletions: number}>;
  enableInlineComments: boolean; maxInlineComments: number;
}) {
  const { title, body, author, base, head, rules, diff, includeTests, includeStyle, files, enableInlineComments, maxInlineComments } = opts;
  
  const fileList = files.map(f => `- ${f.filename} (+${f.additions}/-${f.deletions})`).join('\n');
  
  const inlineInstructions = enableInlineComments ? 
    `For inline comments, analyze the diff and provide line-specific feedback. Focus on the most critical issues first. Limit to ${maxInlineComments} inline comments maximum.` :
    'Do not provide inline comments, focus on the overall summary and checks.';
  
  return `You are a senior code reviewer. Provide thoughtful, actionable feedback on security, performance, code quality, and best practices.

- Focus: correctness, security, performance, readability, maintainability
- Only comment on real issues; avoid nitpicks
- Propose concrete fixes with code examples when helpful
- Keep explanations clear and specific

PR: ${title} by ${author} (${head} → ${base})
${body ? `Description: ${body}` : ''}
${rules}

Files: ${fileList}

Code diff:
${diff}

${inlineInstructions}

IMPORTANT: You must respond with ONLY a valid JSON object. No markdown blocks, no extra text.

Response format:
{
  "summary": "Brief assessment of the changes with key findings",
  "risks": ["List of security or correctness issues found"],
  "actions": ["Prioritized list of specific actions to take"],
  "checks": {
    "correctness": "PASS/FAIL - Brief explanation",
    "security": "PASS/FAIL - Brief explanation", 
    "performance": "PASS/FAIL - Brief explanation",
    "tests": "PASS/FAIL - Brief explanation",
    "style": "PASS/FAIL - Brief explanation",
    "docs": "PASS/FAIL - Brief explanation"
  },
  "inline": [
    { 
      "path": "filename",
      "line": "line number", 
      "side": "RIGHT",
      "body": "Issue description with specific fix suggestion"
    }
  ]
}`;
}

async function callLLM(provider: string, model: string, prompt: string, maxTokens: number, temperature: number): Promise<any> {
  if (provider === 'openai') {
    const key = process.env.OPENAI_API_KEY;
    if (!key) throw new Error('OPENAI_API_KEY missing');
    const res = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model,
        messages: [ { role: 'system', content: 'You are an expert software reviewer.' }, { role: 'user', content: prompt } ],
        temperature,
        max_tokens: maxTokens
      })
    });
    if (!res.ok) throw new Error(`OpenAI error ${res.status}: ${await res.text()}`);
    const data = await res.json();
    const content = data.choices?.[0]?.message?.content || '{}';
    return extractJsonFromResponse(content);
  }
  
  if (provider === 'anthropic') {
    const key = process.env.ANTHROPIC_API_KEY;
    if (!key) throw new Error('ANTHROPIC_API_KEY missing');
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${key}`, 
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model,
        max_tokens: maxTokens,
        temperature,
        messages: [{ role: 'user', content: prompt }]
      })
    });
    if (!res.ok) throw new Error(`Anthropic error ${res.status}: ${await res.text()}`);
    const data = await res.json();
    const content = data.content?.[0]?.text || '{}';
    return extractJsonFromResponse(content);
  }
  
  if (provider === 'azure-openai') {
    const key = process.env.AZURE_OPENAI_API_KEY;
    const endpoint = process.env.AZURE_OPENAI_ENDPOINT;
    if (!key || !endpoint) throw new Error('AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT required');
    const res = await fetch(`${endpoint}/openai/deployments/${model}/chat/completions?api-version=2023-12-01-preview`, {
      method: 'POST',
      headers: { 'api-key': key, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: [ { role: 'system', content: 'You are an expert software reviewer.' }, { role: 'user', content: prompt } ],
        temperature,
        max_tokens: maxTokens
      })
    });
    if (!res.ok) throw new Error(`Azure OpenAI error ${res.status}: ${await res.text()}`);
    const data = await res.json();
    const content = data.choices?.[0]?.message?.content || '{}';
    return extractJsonFromResponse(content);
  }
  
  if (provider === 'ollama') {
    const host = process.env.OLLAMA_HOST || 'http://localhost:11434';
    const res = await fetch(`${host}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model,
        prompt,
        stream: false,
        options: {
          temperature,
          num_predict: maxTokens
        }
      })
    });
    if (!res.ok) throw new Error(`Ollama error ${res.status}: ${await res.text()}`);
    const data = await res.json();
    const content = data.response || '{}';
    return extractJsonFromResponse(content);
  }

  if (provider === 'groq') {
    const key = process.env.GROQ_API_KEY;
    if (!key) throw new Error('GROQ_API_KEY missing');
    const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${key}`, 
        'Content-Type': 'application/json' 
      },
      body: JSON.stringify({
        model,
        messages: [ 
          { 
            role: 'system', 
            content: 'You are a senior code reviewer focused on security, performance, and code quality. Always respond with valid JSON only.' 
          }, 
          { role: 'user', content: prompt } 
        ],
        temperature,
        max_tokens: maxTokens
      })
    });
    if (!res.ok) throw new Error(`Groq error ${res.status}: ${await res.text()}`);
    const data = await res.json();
    const content = data.choices?.[0]?.message?.content || '{}';
    return extractJsonFromResponse(content);
  }
  
  throw new Error(`Provider ${provider} not supported. Available: openai, anthropic, azure-openai, ollama, groq`);
}

function renderMarkdown(review: any): string {
  const checks = review.checks || {};
  const list = (arr?: string[]) => (arr && arr.length ? arr.map(x => `- ${x}`).join('\n') : '- (none)');
  const inlineCount = review.inline?.length || 0;

  return `### 🤖 AI Review Summary

${review.summary || 'No summary provided.'}

---
**Key Risks**
${list(review.risks)}

**Recommended Actions**
${list(review.actions)}

**Checks**
- Correctness: ${checks.correctness || 'n/a'}
- Security: ${checks.security || 'n/a'}
- Performance: ${checks.performance || 'n/a'}
- Tests: ${checks.tests || 'n/a'}
- Style: ${checks.style || 'n/a'}
- Docs: ${checks.docs || 'n/a'}

**Inline Comments**
${inlineCount > 0 ? `📍 ${inlineCount} specific issues identified and commented on individual lines` : '- No line-specific issues found'}
`;
}

async function run() {
  try {
    const token = core.getInput('github-token', { required: true });
    const provider = core.getInput('provider') || 'openai';
    const model = core.getInput('model') || 'gpt-4o-mini';
    const maxTokens = parseInt(core.getInput('max-tokens') || '2500', 10);
    const temperature = parseFloat(core.getInput('temperature') || '0.2');
    const rulesPath = core.getInput('rules-path');
    const includeTests = core.getInput('include-tests') === 'true';
    const includeStyle = core.getInput('include-style') === 'true';
    const enableInlineComments = core.getInput('inline-comments') === 'true';
    const maxInlineComments = parseInt(core.getInput('max-inline-comments') || '10', 10);

    const octokit = new Octokit({ auth: token });
    const ctx = github.context;

    const pr = ctx.payload.pull_request;
    if (!pr) throw new Error('This action must run on pull_request events');

    const owner = ctx.repo.owner;
    const repo = ctx.repo.repo;
    const number = pr.number;

    const { data: prData } = await octokit.pulls.get({ owner, repo, pull_number: number });

    const rules = loadRules(rulesPath);
    const diffData = await getPRDiff(octokit, owner, repo, number);
    const diff = redactSecrets(diffData.diffText);

    const prompt = buildPrompt({
      title: prData.title,
      body: prData.body || '',
      author: prData.user?.login || 'unknown',
      base: prData.base.ref,
      head: prData.head.ref,
      rules,
      diff,
      includeTests,
      includeStyle,
      files: diffData.files,
      enableInlineComments,
      maxInlineComments
    });

    const review = await callLLM(provider, model, prompt, maxTokens, temperature);
    
    // Create the pull request review first
    const { data: reviewData } = await octokit.pulls.createReview({
      owner, repo, pull_number: number,
      event: 'COMMENT',
      body: renderMarkdown(review)
    });

    // Add inline comments if enabled and provided
    if (enableInlineComments && review.inline && Array.isArray(review.inline) && review.inline.length > 0) {
      const commentsToCreate = review.inline.slice(0, maxInlineComments);
      let successCount = 0;
      
      for (const comment of commentsToCreate) {
        if (comment.path && comment.line && comment.body) {
          try {
            await octokit.pulls.createReviewComment({
              owner,
              repo,
              pull_number: number,
              body: `🤖 **AI Review**: ${comment.body}`,
              path: comment.path,
              line: parseInt(comment.line.toString()),
              side: comment.side || 'RIGHT',
              commit_id: prData.head.sha
            });
            successCount++;
            core.info(`Added inline comment for ${comment.path}:${comment.line}`);
          } catch (error: any) {
            core.warning(`Failed to add inline comment for ${comment.path}:${comment.line}: ${error.message}`);
          }
        }
      }
      
      core.info(`Review posted successfully with ${successCount}/${commentsToCreate.length} inline comments.`);
    } else {
      core.info('Review posted successfully (inline comments disabled).');
    }
  } catch (err: any) {
    core.setFailed(err?.message || String(err));
  }
}

run();