#!/usr/bin/env python3
"""
Multi-Model AI Benchmark Testing System
Runs individual tests for each AI model and compares results
"""

import json
import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import urllib.request
import urllib.parse

class MultiModelBenchmarkTester:
    def __init__(self, github_token=None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.repo_owner = "YanSz9"
        self.repo_name = "AI-LLM-Reviewer"
        self.base_branch = "main"
        self.test_models = {
            "gpt-4-turbo": {
                "provider": "openai",
                "model": "gpt-4-turbo",
                "temperature": "0.2",
                "max_tokens": "3000"
            },
            "gpt-4o": {
                "provider": "openai", 
                "model": "gpt-4o",
                "temperature": "0.2",
                "max_tokens": "3000"
            },
            "gpt-4o-mini": {
                "provider": "openai",
                "model": "gpt-4o-mini", 
                "temperature": "0.2",
                "max_tokens": "3000"
            },
            "o1-preview": {
                "provider": "openai",
                "model": "o1-preview",
                "temperature": "1.0",
                "max_completion_tokens": "3000"
            },
            "o1-mini": {
                "provider": "openai",
                "model": "o1-mini",
                "temperature": "1.0", 
                "max_completion_tokens": "3000"
            },
            "claude-3-5-sonnet": {
                "provider": "anthropic",
                "model": "claude-3-5-sonnet-20241022",
                "temperature": "0.2",
                "max_tokens": "3000"
            },
            "groq-llama-3.1": {
                "provider": "groq",
                "model": "llama-3.1-8b-instant",
                "temperature": "0.2",
                "max_tokens": "3000"
            }
        }
        self.known_issues = self._load_known_issues()
        
    def _load_known_issues(self) -> Dict[str, List[Dict]]:
        """Load the comprehensive list of known issues for evaluation"""
        return {
            "security_critical": [
                {"line": 15, "type": "sql_injection", "severity": "critical", "description": "Direct SQL injection in getUserData query"},
                {"line": 19, "type": "sql_injection", "severity": "critical", "description": "SQL injection through filters parameter"},
                {"line": 65, "type": "command_injection", "severity": "critical", "description": "Command injection in exec function"},
                {"line": 95, "type": "auth_bypass", "severity": "critical", "description": "Authentication bypass vulnerability"},
                {"line": 125, "type": "command_injection", "severity": "critical", "description": "Command injection in file operations"},
            ],
            "security_high": [
                {"line": 8, "type": "hardcoded_secret", "severity": "high", "description": "Hardcoded API key in source"},
                {"line": 30, "type": "xss", "severity": "high", "description": "XSS vulnerability in profile generation"},
                {"line": 33, "type": "xss", "severity": "high", "description": "XSS in script tag injection"},
                {"line": 75, "type": "hardcoded_secret", "severity": "high", "description": "Hardcoded database password"},
                {"line": 115, "type": "hardcoded_secret", "severity": "high", "description": "Hardcoded JWT secret"},
                {"line": 155, "type": "auth_bypass", "severity": "high", "description": "Missing authentication check"},
            ],
            "security_medium": [
                {"line": 85, "type": "crypto_weakness", "severity": "medium", "description": "Weak cryptographic implementation"},
                {"line": 105, "type": "info_disclosure", "severity": "medium", "description": "Information disclosure in error messages"},
                {"line": 135, "type": "crypto_weakness", "severity": "medium", "description": "Insecure random number generation"},
                {"line": 145, "type": "info_disclosure", "severity": "medium", "description": "Sensitive data exposure"},
            ],
            "performance": [
                {"line": 38, "type": "race_condition", "severity": "high", "description": "Race condition in balance update"},
                {"line": 45, "type": "memory_leak", "severity": "medium", "description": "Memory leak in event monitoring"},
                {"line": 55, "type": "inefficient_algorithm", "severity": "medium", "description": "O(n²) algorithm complexity"},
                {"line": 165, "type": "memory_leak", "severity": "medium", "description": "Unclosed resource handles"},
                {"line": 175, "type": "blocking_operation", "severity": "medium", "description": "Blocking synchronous operation"},
            ],
            "code_quality": [
                {"line": 12, "type": "input_validation", "severity": "medium", "description": "Missing input validation in constructor"},
                {"line": 22, "type": "error_handling", "severity": "medium", "description": "Missing error handling for async operation"},
                {"line": 68, "type": "type_safety", "severity": "low", "description": "Usage of any type"},
                {"line": 78, "type": "type_safety", "severity": "low", "description": "Missing type annotations"},
                {"line": 88, "type": "type_safety", "severity": "low", "description": "Unsafe type casting"},
                {"line": 98, "type": "type_safety", "severity": "low", "description": "Missing null checks"},
                {"line": 108, "type": "error_handling", "severity": "medium", "description": "Unhandled promise rejection"},
            ]
        }

    def create_test_branch_for_model(self, model_name: str) -> str:
        """Create a dedicated test branch for a specific model"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        branch_name = f"test-{model_name}-{timestamp}"
        
        print(f"📝 Creating test branch for {model_name}: {branch_name}")
        
        # Create and checkout new branch
        subprocess.run(['git', 'checkout', '-b', branch_name], check=True, capture_output=True)
        
        # Add a small change to trigger workflow
        test_comment = f"// Test run for {model_name} at {datetime.now().isoformat()}"
        with open('src/benchmark-test.ts', 'a') as f:
            f.write(f"\n{test_comment}\n")
            
        # Commit changes
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
        commit_msg = f"test: {model_name} benchmark run\n\n🤖 Model: {model_name}\n⏰ Started: {datetime.now().isoformat()}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True, capture_output=True)
        
        return branch_name

    def create_test_workflow_for_model(self, model_name: str, config: Dict[str, str]) -> str:
        """Create a temporary workflow file for testing a specific model"""
        workflow_content = f"""name: Test {model_name}

on:
  workflow_dispatch:
  push:
    branches: [test-{model_name}-*]

permissions:
  contents: read
  pull-requests: write

jobs:
  test-{model_name.replace('.', '-').replace('_', '-')}:
    runs-on: ubuntu-latest
    name: "Test {model_name}"
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 2

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          cd .github/actions/ai-pr-reviewer
          npm ci --ignore-scripts

      - name: Run {model_name} Test
        uses: ./.github/actions/ai-pr-reviewer
        with:
          github-token: ${{{{ secrets.GITHUB_TOKEN }}}}
          provider: "{config['provider']}"
          model: "{config['model']}"
          temperature: "{config['temperature']}"
          {('max-tokens: "' + config['max_tokens'] + '"') if 'max_tokens' in config else ('max-completion-tokens: "' + config['max_completion_tokens'] + '"')}
          include-tests: "true"
          include-style: "true"
          
      - name: Save Results
        run: |
          echo "Model: {model_name}" > test-results-{model_name}.txt
          echo "Timestamp: $(date)" >> test-results-{model_name}.txt
          echo "Configuration:" >> test-results-{model_name}.txt
          echo "  Provider: {config['provider']}" >> test-results-{model_name}.txt
          echo "  Model: {config['model']}" >> test-results-{model_name}.txt
          echo "  Temperature: {config['temperature']}" >> test-results-{model_name}.txt
"""

        workflow_path = f".github/workflows/test-{model_name}.yml"
        with open(workflow_path, 'w') as f:
            f.write(workflow_content)
            
        return workflow_path

    def run_individual_model_test(self, model_name: str, config: Dict[str, str]) -> Dict[str, Any]:
        """Run test for individual model and collect results"""
        print(f"\n🚀 Starting test for {model_name}...")
        
        try:
            # Create test branch
            branch_name = self.create_test_branch_for_model(model_name)
            
            # Create workflow
            workflow_path = self.create_test_workflow_for_model(model_name, config)
            
            # Commit workflow
            subprocess.run(['git', 'add', workflow_path], check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', f'add: workflow for {model_name} test'], check=True, capture_output=True)
            
            # Push branch
            print(f"📤 Pushing branch {branch_name}...")
            result = subprocess.run(['git', 'push', 'origin', branch_name], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Failed to push branch: {result.stderr}")
                
            return {
                'model': model_name,
                'branch': branch_name,
                'workflow': workflow_path,
                'status': 'pushed',
                'timestamp': datetime.now().isoformat(),
                'config': config
            }
            
        except Exception as e:
            print(f"❌ Error testing {model_name}: {e}")
            return {
                'model': model_name,
                'status': 'error', 
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def fetch_test_results(self, branch_name: str, model_name: str) -> Dict[str, Any]:
        """Fetch results from a completed test run"""
        if not self.github_token:
            print("⚠️  GitHub token required to fetch results")
            return {'error': 'No GitHub token'}
            
        # Fetch workflow runs for the branch
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Multi-Model-Benchmark/1.0'
        }
        
        try:
            # Get workflow runs
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/runs?branch={branch_name}"
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
            if not data.get('workflow_runs'):
                return {'error': 'No workflow runs found'}
                
            # Get the latest run
            latest_run = data['workflow_runs'][0]
            
            return {
                'model': model_name,
                'branch': branch_name,
                'workflow_status': latest_run['status'],
                'conclusion': latest_run.get('conclusion'),
                'run_id': latest_run['id'],
                'started_at': latest_run['run_started_at'],
                'completed_at': latest_run.get('updated_at'),
                'url': latest_run['html_url']
            }
            
        except Exception as e:
            return {'error': f'Failed to fetch results: {e}'}

    def analyze_model_results(self, results_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze and compare results from all models"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_models': len(results_data),
            'successful_tests': 0,
            'failed_tests': 0,
            'model_performance': {},
            'comparative_analysis': {},
            'summary': {}
        }
        
        for result in results_data:
            model_name = result.get('model', 'unknown')
            
            if result.get('status') == 'error':
                analysis['failed_tests'] += 1
                analysis['model_performance'][model_name] = {
                    'status': 'failed',
                    'error': result.get('error'),
                    'timestamp': result.get('timestamp')
                }
            else:
                analysis['successful_tests'] += 1
                analysis['model_performance'][model_name] = {
                    'status': 'completed',
                    'branch': result.get('branch'),
                    'workflow': result.get('workflow'),
                    'config': result.get('config'),
                    'timestamp': result.get('timestamp')
                }
        
        # Calculate comparative metrics
        if analysis['successful_tests'] > 0:
            analysis['comparative_analysis'] = {
                'fastest_setup': min([r for r in results_data if r.get('status') != 'error'], 
                                   key=lambda x: x.get('timestamp', ''), default={}).get('model'),
                'most_recent': max([r for r in results_data if r.get('status') != 'error'],
                                 key=lambda x: x.get('timestamp', ''), default={}).get('model'),
                'success_rate': (analysis['successful_tests'] / analysis['total_models']) * 100
            }
        
        return analysis

    def generate_comparison_report(self, analysis: Dict[str, Any], output_dir: str = "multi_model_results"):
        """Generate comprehensive comparison report"""
        Path(output_dir).mkdir(exist_ok=True)
        
        # Generate text report
        report_lines = [
            "🎯 MULTI-MODEL AI BENCHMARK COMPARISON REPORT",
            "=" * 55,
            f"📊 Generated: {analysis['timestamp']}",
            f"🤖 Total Models Tested: {analysis['total_models']}",
            f"✅ Successful Tests: {analysis['successful_tests']}",
            f"❌ Failed Tests: {analysis['failed_tests']}",
            f"📈 Success Rate: {analysis.get('comparative_analysis', {}).get('success_rate', 0):.1f}%",
            "",
            "📋 MODEL TEST RESULTS",
            "-" * 55
        ]
        
        for model_name, performance in analysis['model_performance'].items():
            status_icon = "✅" if performance['status'] == 'completed' else "❌"
            report_lines.append(f"{status_icon} {model_name}")
            
            if performance['status'] == 'completed':
                config = performance.get('config', {})
                report_lines.extend([
                    f"   📝 Branch: {performance.get('branch')}",
                    f"   🔧 Provider: {config.get('provider')}",
                    f"   🎛️  Model: {config.get('model')}",
                    f"   🌡️  Temperature: {config.get('temperature')}",
                    f"   ⏰ Timestamp: {performance.get('timestamp')}",
                ])
            else:
                report_lines.extend([
                    f"   ❌ Error: {performance.get('error')}",
                    f"   ⏰ Failed at: {performance.get('timestamp')}",
                ])
            report_lines.append("")
        
        # Add next steps
        report_lines.extend([
            "🔍 NEXT STEPS TO COMPLETE ANALYSIS",
            "-" * 55,
            "1. Wait for all GitHub Actions workflows to complete",
            "2. Check each test branch for AI-generated comments:",
        ])
        
        for model_name, performance in analysis['model_performance'].items():
            if performance['status'] == 'completed':
                branch = performance.get('branch')
                report_lines.append(f"   • {model_name}: git checkout {branch}")
                
        report_lines.extend([
            "",
            "3. Run results analysis:",
            "   python3 scripts/analyze-benchmark.py <pr_number>",
            "",
            "4. Compare model performance using generated reports",
            "",
            "📊 This creates isolated tests for scientific comparison!",
            "Each model tests the same code independently."
        ])
        
        # Save reports
        with open(f"{output_dir}/multi_model_test_report.txt", "w") as f:
            f.write("\n".join(report_lines))
            
        # Save JSON data
        with open(f"{output_dir}/multi_model_results.json", "w") as f:
            json.dump(analysis, f, indent=2)
            
        # Generate simple HTML report
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Multi-Model Benchmark Test Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .summary {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .model-card {{ border: 2px solid #bdc3c7; margin: 15px 0; padding: 20px; border-radius: 8px; }}
        .success {{ border-color: #27ae60; background: #d5f4e6; }}
        .error {{ border-color: #e74c3c; background: #fadbd8; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; font-weight: bold; }}
        .status-icon {{ font-size: 1.5em; margin-right: 10px; }}
        .next-steps {{ background: #e8f4fd; padding: 20px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Multi-Model AI Benchmark Test Results</h1>
        
        <div class="summary">
            <h2>📊 Test Summary</h2>
            <div class="metric">🤖 Total Models: {analysis['total_models']}</div>
            <div class="metric">✅ Successful: {analysis['successful_tests']}</div>
            <div class="metric">❌ Failed: {analysis['failed_tests']}</div>
            <div class="metric">📈 Success Rate: {analysis.get('comparative_analysis', {}).get('success_rate', 0):.1f}%</div>
        </div>
        
        <h2>🔬 Individual Model Results</h2>
"""
        
        for model_name, performance in analysis['model_performance'].items():
            status_class = "success" if performance['status'] == 'completed' else "error"
            status_icon = "✅" if performance['status'] == 'completed' else "❌"
            
            html_content += f"""
        <div class="model-card {status_class}">
            <h3><span class="status-icon">{status_icon}</span>{model_name}</h3>
"""
            
            if performance['status'] == 'completed':
                config = performance.get('config', {})
                html_content += f"""
            <p><strong>📝 Branch:</strong> {performance.get('branch')}</p>
            <p><strong>🔧 Provider:</strong> {config.get('provider')}</p>
            <p><strong>🎛️ Model:</strong> {config.get('model')}</p>
            <p><strong>🌡️ Temperature:</strong> {config.get('temperature')}</p>
            <p><strong>⏰ Started:</strong> {performance.get('timestamp')}</p>
"""
            else:
                html_content += f"""
            <p><strong>❌ Error:</strong> {performance.get('error')}</p>
            <p><strong>⏰ Failed:</strong> {performance.get('timestamp')}</p>
"""
            
            html_content += "        </div>"
        
        html_content += f"""
        
        <div class="next-steps">
            <h2>🔍 Next Steps</h2>
            <ol>
                <li>Wait for all GitHub Actions workflows to complete</li>
                <li>Check each test branch for AI-generated results</li>
                <li>Run comparative analysis using the benchmark analyzer</li>
                <li>Generate final comparison reports</li>
            </ol>
            <p><strong>📊 Each model now has an isolated test environment for scientific comparison!</strong></p>
        </div>
        
        <div style="margin-top: 30px; padding: 15px; background: #f8f9fa; border-radius: 5px; text-align: center;">
            <small>Generated on {analysis['timestamp']} | Multi-Model Benchmark Testing System v1.0</small>
        </div>
    </div>
</body>
</html>"""
        
        with open(f"{output_dir}/multi_model_test_results.html", "w") as f:
            f.write(html_content)
            
        return output_dir

    def run_multi_model_benchmark(self, models: Optional[List[str]] = None) -> str:
        """Run benchmark tests for multiple models"""
        print("🎯 MULTI-MODEL AI BENCHMARK TESTING SYSTEM")
        print("=" * 50)
        
        # Use specified models or all available models
        models_to_test = models if models else list(self.test_models.keys())
        
        print(f"🤖 Testing {len(models_to_test)} models:")
        for model in models_to_test:
            print(f"   • {model}")
        print()
        
        # Store original branch
        original_branch = subprocess.run(['git', 'branch', '--show-current'], 
                                       capture_output=True, text=True).stdout.strip()
        
        results = []
        
        try:
            # Run tests for each model
            for model_name in models_to_test:
                if model_name not in self.test_models:
                    print(f"⚠️  Unknown model: {model_name}, skipping...")
                    continue
                    
                config = self.test_models[model_name]
                result = self.run_individual_model_test(model_name, config)
                results.append(result)
                
                # Return to original branch
                subprocess.run(['git', 'checkout', original_branch], 
                             check=True, capture_output=True)
                
                print(f"✅ {model_name} test setup complete")
                time.sleep(2)  # Brief pause between tests
            
            # Analyze results
            print(f"\n📊 Analyzing results from {len(results)} tests...")
            analysis = self.analyze_model_results(results)
            
            # Generate reports
            output_dir = self.generate_comparison_report(analysis)
            
            print(f"\n🎉 Multi-model benchmark testing complete!")
            print(f"📁 Results saved to: {output_dir}/")
            print(f"   📄 multi_model_test_report.txt - Detailed text report")
            print(f"   🌐 multi_model_test_results.html - Interactive HTML report")
            print(f"   📋 multi_model_results.json - Raw data")
            
            print(f"\n⏳ Next: Wait for GitHub Actions to complete, then run:")
            print(f"   python3 scripts/collect-results.py --analyze-all")
            
            return output_dir
            
        except Exception as e:
            print(f"❌ Error during multi-model testing: {e}")
            # Try to return to original branch
            try:
                subprocess.run(['git', 'checkout', original_branch], check=True, capture_output=True)
            except:
                pass
            raise

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-Model AI Benchmark Testing')
    parser.add_argument('--models', nargs='+', help='Specific models to test')
    parser.add_argument('--token', help='GitHub token')
    
    args = parser.parse_args()
    
    tester = MultiModelBenchmarkTester(github_token=args.token)
    tester.run_multi_model_benchmark(models=args.models)

if __name__ == "__main__":
    main()