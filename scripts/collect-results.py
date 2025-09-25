#!/usr/bin/env python3
"""
Results Collector for Multi-Model Benchmark Tests
Collects and analyzes results from individual model test runs
"""

import json
import os
import sys
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import time

class BenchmarkResultsCollector:
    def __init__(self, github_token=None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.repo_owner = "YanSz9"
        self.repo_name = "AI-LLM-Reviewer"
        
    def get_test_branches(self) -> List[str]:
        """Get all test branches from the repository"""
        try:
            result = subprocess.run(['git', 'branch', '-r'], capture_output=True, text=True)
            branches = []
            
            for line in result.stdout.strip().split('\n'):
                branch = line.strip()
                if branch.startswith('origin/test-') and '-202' in branch:  # Test branches
                    branches.append(branch.replace('origin/', ''))
                    
            return branches
        except Exception as e:
            print(f"Error getting branches: {e}")
            return []
    
    def fetch_branch_commits(self, branch_name: str) -> List[Dict]:
        """Fetch commits for a specific branch"""
        if not self.github_token:
            return []
            
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Benchmark-Results-Collector/1.0'
        }
        
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits?sha={branch_name}&per_page=10"
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
            return data
            
        except Exception as e:
            print(f"Error fetching commits for {branch_name}: {e}")
            return []
    
    def fetch_workflow_runs(self, branch_name: str) -> List[Dict]:
        """Fetch workflow runs for a specific branch"""
        if not self.github_token:
            return []
            
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Benchmark-Results-Collector/1.0'
        }
        
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/runs?branch={branch_name}&per_page=10"
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
            return data.get('workflow_runs', [])
            
        except Exception as e:
            print(f"Error fetching workflow runs for {branch_name}: {e}")
            return []
    
    def analyze_branch_results(self, branch_name: str) -> Dict[str, Any]:
        """Analyze results from a single test branch"""
        print(f"🔍 Analyzing branch: {branch_name}")
        
        # Extract model name from branch
        model_name = branch_name.replace('test-', '').split('-202')[0]  # Remove timestamp
        
        # Fetch commits
        commits = self.fetch_branch_commits(branch_name)
        
        # Fetch workflow runs
        workflow_runs = self.fetch_workflow_runs(branch_name)
        
        analysis = {
            'branch_name': branch_name,
            'model_name': model_name,
            'commits_count': len(commits),
            'workflow_runs_count': len(workflow_runs),
            'latest_commit': None,
            'latest_workflow': None,
            'status': 'unknown'
        }
        
        if commits:
            latest_commit = commits[0]
            analysis['latest_commit'] = {
                'sha': latest_commit['sha'][:8],
                'message': latest_commit['commit']['message'],
                'date': latest_commit['commit']['committer']['date'],
                'author': latest_commit['commit']['author']['name']
            }
        
        if workflow_runs:
            latest_workflow = workflow_runs[0]
            analysis['latest_workflow'] = {
                'id': latest_workflow['id'],
                'name': latest_workflow['name'],
                'status': latest_workflow['status'],
                'conclusion': latest_workflow.get('conclusion'),
                'created_at': latest_workflow['created_at'],
                'updated_at': latest_workflow['updated_at'],
                'html_url': latest_workflow['html_url']
            }
            
            # Determine overall status
            if latest_workflow['status'] == 'completed':
                if latest_workflow.get('conclusion') == 'success':
                    analysis['status'] = 'success'
                else:
                    analysis['status'] = 'failed'
            else:
                analysis['status'] = 'running'
        
        return analysis
    
    def collect_all_results(self) -> Dict[str, Any]:
        """Collect results from all test branches"""
        print("🔍 Collecting results from all test branches...")
        
        branches = self.get_test_branches()
        if not branches:
            print("❌ No test branches found")
            return {'error': 'No test branches found'}
        
        print(f"📊 Found {len(branches)} test branches")
        
        results = {
            'collection_timestamp': datetime.now().isoformat(),
            'total_branches': len(branches),
            'branch_results': {},
            'summary': {
                'completed_tests': 0,
                'running_tests': 0,
                'failed_tests': 0,
                'unknown_tests': 0
            }
        }
        
        for branch in branches:
            try:
                analysis = self.analyze_branch_results(branch)
                results['branch_results'][branch] = analysis
                
                # Update summary
                status = analysis['status']
                if status == 'success':
                    results['summary']['completed_tests'] += 1
                elif status == 'running':
                    results['summary']['running_tests'] += 1
                elif status == 'failed':
                    results['summary']['failed_tests'] += 1
                else:
                    results['summary']['unknown_tests'] += 1
                    
            except Exception as e:
                print(f"⚠️  Error analyzing {branch}: {e}")
                results['branch_results'][branch] = {
                    'error': str(e),
                    'branch_name': branch
                }
        
        return results
    
    def generate_results_report(self, results: Dict[str, Any], output_dir: str = "collected_results"):
        """Generate comprehensive results report"""
        Path(output_dir).mkdir(exist_ok=True)
        
        # Generate text report
        report_lines = [
            "🎯 MULTI-MODEL BENCHMARK RESULTS COLLECTION",
            "=" * 55,
            f"📊 Collection Time: {results['collection_timestamp']}",
            f"🔍 Total Branches Analyzed: {results['total_branches']}",
            "",
            "📈 SUMMARY",
            "-" * 55,
            f"✅ Completed Tests: {results['summary']['completed_tests']}",
            f"🏃 Running Tests: {results['summary']['running_tests']}",
            f"❌ Failed Tests: {results['summary']['failed_tests']}",
            f"❓ Unknown Status: {results['summary']['unknown_tests']}",
            "",
            "📋 DETAILED RESULTS",
            "-" * 55
        ]
        
        # Sort branches by model name for better readability
        sorted_branches = sorted(results['branch_results'].items(), 
                               key=lambda x: x[1].get('model_name', x[0]))
        
        for branch_name, analysis in sorted_branches:
            if 'error' in analysis:
                report_lines.extend([
                    f"❌ {branch_name}",
                    f"   Error: {analysis['error']}",
                    ""
                ])
                continue
                
            status_icon = {
                'success': '✅',
                'running': '🏃',
                'failed': '❌',
                'unknown': '❓'
            }.get(analysis['status'], '❓')
            
            report_lines.extend([
                f"{status_icon} {analysis['model_name']} ({branch_name})",
                f"   Status: {analysis['status'].upper()}",
                f"   Commits: {analysis['commits_count']}"
            ])
            
            if analysis['latest_commit']:
                commit = analysis['latest_commit']
                report_lines.extend([
                    f"   Latest Commit: {commit['sha']} - {commit['message'][:50]}...",
                    f"   Commit Date: {commit['date']}"
                ])
            
            if analysis['latest_workflow']:
                workflow = analysis['latest_workflow']
                report_lines.extend([
                    f"   Workflow: {workflow['name']} - {workflow['status']}",
                    f"   Conclusion: {workflow.get('conclusion', 'N/A')}",
                    f"   URL: {workflow['html_url']}"
                ])
                
            report_lines.append("")
        
        # Add next steps
        if results['summary']['completed_tests'] > 0:
            report_lines.extend([
                "🔍 NEXT STEPS FOR COMPLETED TESTS",
                "-" * 55,
                "Run individual analysis on completed tests:",
                ""
            ])
            
            for branch_name, analysis in sorted_branches:
                if analysis.get('status') == 'success':
                    model_name = analysis['model_name']
                    report_lines.append(f"# Analyze {model_name} results")
                    report_lines.append(f"git checkout {branch_name}")
                    report_lines.append(f"python3 scripts/analyze-benchmark.py --branch {branch_name}")
                    report_lines.append("")
        
        if results['summary']['running_tests'] > 0:
            report_lines.extend([
                "⏳ TESTS STILL RUNNING",
                "-" * 55,
                f"{results['summary']['running_tests']} tests are still in progress.",
                "Wait for completion and run this collector again.",
                ""
            ])
        
        # Save reports
        with open(f"{output_dir}/collection_report.txt", "w") as f:
            f.write("\n".join(report_lines))
        
        # Save JSON
        with open(f"{output_dir}/collection_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        # Generate HTML report
        self.generate_html_collection_report(results, output_dir)
        
        return output_dir
    
    def generate_html_collection_report(self, results: Dict[str, Any], output_dir: str):
        """Generate HTML collection report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Multi-Model Benchmark Results Collection</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .summary {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 15px; padding: 15px; border-radius: 5px; text-align: center; min-width: 100px; }}
        .completed {{ background: #d5f4e6; color: #27ae60; }}
        .running {{ background: #fff3cd; color: #856404; }}
        .failed {{ background: #f8d7da; color: #721c24; }}
        .unknown {{ background: #e2e3e5; color: #6c757d; }}
        .result-card {{ border: 2px solid #dee2e6; margin: 15px 0; padding: 20px; border-radius: 8px; }}
        .success {{ border-color: #28a745; }}
        .running-border {{ border-color: #ffc107; }}
        .failed-border {{ border-color: #dc3545; }}
        .status {{ font-weight: bold; padding: 5px 10px; border-radius: 15px; color: white; }}
        .status.success {{ background: #28a745; }}
        .status.running {{ background: #ffc107; color: #212529; }}
        .status.failed {{ background: #dc3545; }}
        .status.unknown {{ background: #6c757d; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Multi-Model Benchmark Results Collection</h1>
        
        <div class="summary">
            <h2>📊 Collection Summary</h2>
            <p><strong>Collection Time:</strong> {results['collection_timestamp']}</p>
            <p><strong>Total Branches:</strong> {results['total_branches']}</p>
            
            <div style="text-align: center; margin: 20px 0;">
                <div class="metric completed">
                    <div style="font-size: 2em; font-weight: bold;">{results['summary']['completed_tests']}</div>
                    <div>Completed</div>
                </div>
                <div class="metric running">
                    <div style="font-size: 2em; font-weight: bold;">{results['summary']['running_tests']}</div>
                    <div>Running</div>
                </div>
                <div class="metric failed">
                    <div style="font-size: 2em; font-weight: bold;">{results['summary']['failed_tests']}</div>
                    <div>Failed</div>
                </div>
                <div class="metric unknown">
                    <div style="font-size: 2em; font-weight: bold;">{results['summary']['unknown_tests']}</div>
                    <div>Unknown</div>
                </div>
            </div>
        </div>
        
        <h2>📋 Detailed Results</h2>
"""
        
        # Sort and display results
        sorted_branches = sorted(results['branch_results'].items(), 
                               key=lambda x: x[1].get('model_name', x[0]))
        
        for branch_name, analysis in sorted_branches:
            if 'error' in analysis:
                html_content += f"""
        <div class="result-card failed-border">
            <h3>❌ {branch_name}</h3>
            <p><strong>Error:</strong> {analysis['error']}</p>
        </div>
"""
                continue
            
            status = analysis.get('status', 'unknown')
            border_class = {
                'success': 'success',
                'running': 'running-border', 
                'failed': 'failed-border',
                'unknown': ''
            }.get(status, '')
            
            status_icon = {
                'success': '✅',
                'running': '🏃',
                'failed': '❌',
                'unknown': '❓'
            }.get(status, '❓')
            
            html_content += f"""
        <div class="result-card {border_class}">
            <h3>{status_icon} {analysis.get('model_name', 'Unknown')} 
                <span class="status {status}">{status.upper()}</span>
            </h3>
            <p><strong>Branch:</strong> {branch_name}</p>
            <p><strong>Commits:</strong> {analysis.get('commits_count', 0)}</p>
"""
            
            if analysis.get('latest_commit'):
                commit = analysis['latest_commit']
                html_content += f"""
            <p><strong>Latest Commit:</strong> {commit['sha']} - {commit['message'][:80]}...</p>
            <p><strong>Commit Date:</strong> {commit['date']}</p>
"""
            
            if analysis.get('latest_workflow'):
                workflow = analysis['latest_workflow']
                html_content += f"""
            <p><strong>Workflow:</strong> {workflow['name']}</p>
            <p><strong>Conclusion:</strong> {workflow.get('conclusion', 'N/A')}</p>
            <p><strong>URL:</strong> <a href="{workflow['html_url']}" target="_blank">View Workflow</a></p>
"""
            
            html_content += "        </div>"
        
        html_content += """
    </div>
</body>
</html>"""
        
        with open(f"{output_dir}/collection_results.html", "w") as f:
            f.write(html_content)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Collect Multi-Model Benchmark Results')
    parser.add_argument('--token', help='GitHub token')
    parser.add_argument('--output', default='collected_results', help='Output directory')
    
    args = parser.parse_args()
    
    collector = BenchmarkResultsCollector(github_token=args.token)
    results = collector.collect_all_results()
    
    if 'error' in results:
        print(f"❌ {results['error']}")
        return
    
    output_dir = collector.generate_results_report(results, args.output)
    
    print(f"\n✅ Results collection complete!")
    print(f"📁 Reports saved to: {output_dir}/")
    print(f"   📄 collection_report.txt - Text summary")
    print(f"   🌐 collection_results.html - Interactive report")
    print(f"   📋 collection_results.json - Raw data")
    
    # Show summary
    summary = results['summary']
    if summary['completed_tests'] > 0:
        print(f"\n🎉 {summary['completed_tests']} tests completed and ready for analysis!")
    if summary['running_tests'] > 0:
        print(f"⏳ {summary['running_tests']} tests still running...")
    if summary['failed_tests'] > 0:
        print(f"❌ {summary['failed_tests']} tests failed")

if __name__ == "__main__":
    main()