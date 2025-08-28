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

async function getPRDiff(octokit: Octokit, owner: string, repo: string, pr: number) {
  const files = await octokit.pulls.listFiles({ owner, repo, pull_number: pr, per_page: 300 });
  const parts: string[] = [];
  for (const f of files.data) {
    if (!f.patch) continue;
    if (isBinary(f.filename)) continue;
    if ((f.changes ?? 0) > 5000) continue; // extremely large file changes
    if ((f.additions ?? 0) + (f.deletions ?? 0) > 5000) continue;
    const patch = f.patch.length > MAX_FILE_BYTES ? f.patch.slice(0, MAX_FILE_BYTES) + '\n[truncated]\n' : f.patch;
    parts.push(`FILE: ${f.filename}\nSTATUS: ${f.status}\n${patch}`);
  }
  return parts.join('\n\n---\n\n');
}

function buildPrompt(opts: {
  title: string; body: string; author: string; base: string; head: string;
  rules: string; diff: string; includeTests: boolean; includeStyle: boolean;
}) {
  const { title, body, author, base, head, rules, diff, includeTests, includeStyle } = opts;
  return `You are a senior code reviewer bot. Provide a thoughtful, concise, and actionable review.
- Focus: correctness, security, performance, readability, and maintainability.
- Only comment on real issues; avoid nitpicks.
- Propose concrete fixes with code snippets when helpful.
- If you are uncertain, say so explicitly.
- Use Markdown. Structure with headings and bullet points.
- Keep tone friendly and specific.

PR metadata:
- Title: ${title}
- Author: ${author}
- From ${head} into ${base}
- Description: ${body || '(none)'}
${rules}

Diff (unified):
${diff}

Deliver this JSON object only:
{
  "summary": string, // high-level assessment
  "risks": string[], // key risks found
  "actions": string[], // prioritized actions for the author
  "checks": { // pass/fail checklist
    "correctness": string,
    "security": string,
    "performance": string,
    "tests": string,
    "style": string,
    "docs": string
  },
  "inline": [ // OPTIONAL: inline suggestions (file-level) rendered in the main comment
    { "file": string, "issue": string, "suggestion": string }
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
    return JSON.parse(content);
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
    return JSON.parse(content);
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
    return JSON.parse(content);
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
    return JSON.parse(content);
  }
  
  throw new Error(`Provider ${provider} not supported. Available: openai, anthropic, azure-openai, ollama`);
}

function renderMarkdown(review: any): string {
  const checks = review.checks || {};
  const list = (arr?: string[]) => (arr && arr.length ? arr.map(x => `- ${x}`).join('\n') : '- (none)');
  const inline = (review.inline || []).map((i: any) => `- **${i.file}** — ${i.issue}\n  - Suggestion: ${i.suggestion}`).join('\n');

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

**Inline Notes**
${inline || '- (none)'}
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

    const octokit = new Octokit({ auth: token });
    const ctx = github.context;

    const pr = ctx.payload.pull_request;
    if (!pr) throw new Error('This action must run on pull_request events');

    const owner = ctx.repo.owner;
    const repo = ctx.repo.repo;
    const number = pr.number;

    const { data: prData } = await octokit.pulls.get({ owner, repo, pull_number: number });

    const rules = loadRules(rulesPath);
    const diff = redactSecrets(await getPRDiff(octokit, owner, repo, number));

    const prompt = buildPrompt({
      title: prData.title,
      body: prData.body || '',
      author: prData.user?.login || 'unknown',
      base: prData.base.ref,
      head: prData.head.ref,
      rules,
      diff,
      includeTests,
      includeStyle
    });

    const review = await callLLM(provider, model, prompt, maxTokens, temperature);
    const body = renderMarkdown(review);

    await octokit.pulls.createReview({
      owner, repo, pull_number: number,
      event: 'COMMENT',
      body
    });

    core.info('Review posted successfully.');
  } catch (err: any) {
    core.setFailed(err?.message || String(err));
  }
}

run();
