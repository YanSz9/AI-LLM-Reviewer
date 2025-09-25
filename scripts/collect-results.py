#!/usr/bin/env python3
"""
Results Collection and Analysis System
Collects PR review results from multiple AI models and generates comparative analysis
"""

import os
import sys
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, List, Any
import subprocess

def run_command(cmd: str) -> str:
    """Run a shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""

def get_github_token() -> str:
    """Get GitHub token from environment or gh CLI"""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        token = run_command('gh auth token')
    return token

def fetch_pr_reviews(pr_number: int, repo: str = "YanSz9/AI-LLM-Reviewer") -> Dict[str, Any]:
    """Fetch PR reviews and comments from GitHub API"""
    token = get_github_token()
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Get PR details
    pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    pr_response = requests.get(pr_url, headers=headers)
    pr_data = pr_response.json() if pr_response.status_code == 200 else {}
    
    # Get PR reviews
    reviews_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    reviews_response = requests.get(reviews_url, headers=headers)
    reviews_data = reviews_response.json() if reviews_response.status_code == 200 else []
    
    # Get PR comments
    comments_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"
    comments_response = requests.get(comments_url, headers=headers)
    comments_data = comments_response.json() if comments_response.status_code == 200 else []
    
    return {
        'pr_details': pr_data,
        'reviews': reviews_data,
        'comments': comments_data,
        'total_comments': len(comments_data),
        'total_reviews': len(reviews_data)
    }

def analyze_security_detections(comments: List[Dict]) -> Dict[str, Any]:
    """Analyze which security issues were detected from PR comments"""
    
    # Define security vulnerability patterns to look for
    security_patterns = {
        'sql_injection': ['sql injection', 'sql', 'injection', 'query'],
        'xss': ['xss', 'cross-site scripting', 'script injection', 'html injection'],
        'command_injection': ['command injection', 'exec', 'shell injection'],
        'path_traversal': ['path traversal', 'directory traversal', '../'],
        'hardcoded_secrets': ['hardcoded', 'api key', 'password', 'secret'],
        'weak_crypto': ['md5', 'weak hash', 'crypto', 'encryption'],
        'insecure_random': ['random', 'math.random', 'insecure random'],
        'missing_validation': ['validation', 'input validation', 'sanitization'],
        'information_disclosure': ['stack trace', 'error disclosure', 'information leak'],
        'insecure_upload': ['file upload', 'upload', 'file validation'],
        'missing_auth': ['authentication', 'authorization', 'access control'],
        'race_condition': ['race condition', 'concurrency', 'thread safety'],
        'deserialization': ['deserialization', 'eval', 'unsafe deserialization'],
        'rate_limiting': ['rate limit', 'brute force', 'ddos'],
        'open_redirect': ['redirect', 'open redirect'],
        'ldap_injection': ['ldap', 'ldap injection'],
        'xxe': ['xxe', 'xml external entity', 'xml injection'],
        'insecure_storage': ['base64', 'insecure storage', 'encryption'],
        'csrf': ['csrf', 'cross-site request forgery'],
        'session_management': ['session', 'session management'],
        'buffer_overflow': ['buffer overflow', 'buffer'],
        'timing_attack': ['timing attack', 'side-channel'],
        'insecure_config': ['configuration', 'logging secrets'],
        'redos': ['redos', 'regex', 'regular expression'],
        'privilege_escalation': ['privilege', 'escalation', 'admin role']
    }
    
    detected_issues = {}
    total_security_mentions = 0
    
    for pattern_name, keywords in security_patterns.items():
        detected_issues[pattern_name] = 0
        
        for comment in comments:
            comment_body = comment.get('body', '').lower()
            if any(keyword in comment_body for keyword in keywords):
                detected_issues[pattern_name] += 1
                total_security_mentions += 1
    
    return {
        'detected_issues': detected_issues,
        'total_security_mentions': total_security_mentions,
        'detection_rate': len([v for v in detected_issues.values() if v > 0]) / len(security_patterns) * 100
    }

def generate_comparison_report(results: List[Dict]) -> str:
    """Generate HTML comparison report"""
    
    # Create DataFrame for analysis
    data = []
    for result in results:
        data.append({
            'Model': result['model'],
            'Total Comments': result['analysis']['total_comments'],
            'Security Issues Detected': len([v for v in result['analysis']['security_analysis']['detected_issues'].values() if v > 0]),
            'Detection Rate %': result['analysis']['security_analysis']['detection_rate'],
            'Total Security Mentions': result['analysis']['security_analysis']['total_security_mentions']
        })
    
    df = pd.DataFrame(data)
    
    # Generate plots
    plt.style.use('seaborn-v0_8')
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Total Comments by Model
    ax1.bar(df['Model'], df['Total Comments'], color='skyblue')
    ax1.set_title('Total Comments by AI Model')
    ax1.set_ylabel('Number of Comments')
    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
    
    # Plot 2: Security Issues Detected
    ax2.bar(df['Model'], df['Security Issues Detected'], color='lightcoral')
    ax2.set_title('Security Issues Detected by Model')
    ax2.set_ylabel('Number of Issues Detected')
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    
    # Plot 3: Detection Rate
    ax3.bar(df['Model'], df['Detection Rate %'], color='lightgreen')
    ax3.set_title('Security Detection Rate by Model')
    ax3.set_ylabel('Detection Rate (%)')
    plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')
    
    # Plot 4: Total Security Mentions
    ax4.bar(df['Model'], df['Total Security Mentions'], color='orange')
    ax4.set_title('Total Security Mentions by Model')
    ax4.set_ylabel('Security Mentions Count')
    plt.setp(ax4.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig('/home/yan/projects/AI-TCC/multi_model_results/comparison_charts.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Generate HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Model Performance Comparison Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .model-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .metrics {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .metric {{ text-align: center; padding: 10px; background-color: #f9f9f9; border-radius: 5px; }}
            .best {{ background-color: #d4edda; }}
            .chart {{ text-align: center; margin: 20px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 AI Model Performance Comparison Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Benchmark File: src/benchmark-test.ts (27+ Security Vulnerabilities)</p>
        </div>
        
        <div class="chart">
            <h2>📊 Performance Comparison Charts</h2>
            <img src="comparison_charts.png" alt="Performance Comparison Charts" style="max-width: 100%;">
        </div>
        
        <h2>📈 Summary Metrics</h2>
        <table>
            <thead>
                <tr>
                    <th>Model</th>
                    <th>Total Comments</th>
                    <th>Security Issues Detected</th>
                    <th>Detection Rate (%)</th>
                    <th>Security Mentions</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Add table rows
    for _, row in df.iterrows():
        html_content += f"""
                <tr>
                    <td><strong>{row['Model']}</strong></td>
                    <td>{row['Total Comments']}</td>
                    <td>{row['Security Issues Detected']}</td>
                    <td>{row['Detection Rate %']:.1f}%</td>
                    <td>{row['Total Security Mentions']}</td>
                </tr>
        """
    
    html_content += """
            </tbody>
        </table>
        
        <h2>🏆 Best Performing Models</h2>
    """
    
    # Find best performers
    best_detection = df.loc[df['Detection Rate %'].idxmax()]
    best_comments = df.loc[df['Total Comments'].idxmax()]
    best_security = df.loc[df['Security Mentions'].idxmax()]
    
    html_content += f"""
        <div class="metrics">
            <div class="metric best">
                <h3>🎯 Best Detection Rate</h3>
                <p><strong>{best_detection['Model']}</strong></p>
                <p>{best_detection['Detection Rate %']:.1f}%</p>
            </div>
            <div class="metric best">
                <h3>💬 Most Comments</h3>
                <p><strong>{best_comments['Model']}</strong></p>
                <p>{best_comments['Total Comments']} comments</p>
            </div>
            <div class="metric best">
                <h3>🔒 Most Security Focus</h3>
                <p><strong>{best_security['Model']}</strong></p>
                <p>{best_security['Security Mentions']} mentions</p>
            </div>
        </div>
    """
    
    # Add detailed model sections
    html_content += "<h2>🔍 Detailed Model Analysis</h2>"
    
    for result in results:
        model = result['model']
        analysis = result['analysis']
        security = analysis['security_analysis']
        
        html_content += f"""
        <div class="model-section">
            <h3>🤖 {model.upper()}</h3>
            <div class="metrics">
                <div class="metric">
                    <strong>Total Comments</strong><br>
                    {analysis['total_comments']}
                </div>
                <div class="metric">
                    <strong>Issues Detected</strong><br>
                    {len([v for v in security['detected_issues'].values() if v > 0])}/25
                </div>
                <div class="metric">
                    <strong>Detection Rate</strong><br>
                    {security['detection_rate']:.1f}%
                </div>
            </div>
            
            <h4>Detected Security Issues:</h4>
            <ul>
        """
        
        for issue, count in security['detected_issues'].items():
            if count > 0:
                html_content += f"<li>{issue.replace('_', ' ').title()}: {count} mentions</li>"
        
        html_content += """
            </ul>
        </div>
        """
    
    html_content += """
        <div class="header">
            <h2>📝 Methodology</h2>
            <p>This report analyzes AI model performance on a comprehensive security benchmark containing 27+ intentional vulnerabilities including SQL injection, XSS, command injection, and more. Models are evaluated on their ability to detect and comment on these security issues.</p>
        </div>
    </body>
    </html>
    """
    
    return html_content

def collect_and_analyze_results():
    """Main function to collect results from all PRs and generate analysis"""
    
    print("📊 Collecting Multi-Model AI Review Results...")
    
    # Load test session data
    try:
        with open('/home/yan/projects/AI-TCC/multi_model_results/test_session.json', 'r') as f:
            session_data = json.load(f)
    except FileNotFoundError:
        print("❌ No test session found. Run multi-model-tester.py first.")
        return
    
    results = []
    
    for pr_info in session_data['created_prs']:
        print(f"\n🔍 Analyzing {pr_info['model']}...")
        
        # Extract PR number from URL
        pr_number = int(pr_info['pr_url'].split('/')[-1])
        
        # Fetch PR data
        pr_data = fetch_pr_reviews(pr_number)
        
        # Analyze security detections
        security_analysis = analyze_security_detections(pr_data['comments'])
        
        results.append({
            'model': pr_info['model'],
            'pr_number': pr_number,
            'pr_url': pr_info['pr_url'],
            'analysis': {
                'total_comments': pr_data['total_comments'],
                'total_reviews': pr_data['total_reviews'],
                'security_analysis': security_analysis
            },
            'raw_data': pr_data
        })
        
        print(f"✅ {pr_info['model']}: {pr_data['total_comments']} comments, {security_analysis['detection_rate']:.1f}% detection rate")
    
    # Save detailed results
    results_file = '/home/yan/projects/AI-TCC/multi_model_results/detailed_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Generate comparison report
    html_report = generate_comparison_report(results)
    
    report_file = '/home/yan/projects/AI-TCC/multi_model_results/comparison_report.html'
    with open(report_file, 'w') as f:
        f.write(html_report)
    
    print(f"\n🎉 Analysis Complete!")
    print(f"📊 Detailed results: {results_file}")
    print(f"📋 HTML report: {report_file}")
    print(f"📈 Charts: multi_model_results/comparison_charts.png")
    
    # Print summary
    print(f"\n📈 Quick Summary:")
    for result in sorted(results, key=lambda x: x['analysis']['security_analysis']['detection_rate'], reverse=True):
        model = result['model']
        rate = result['analysis']['security_analysis']['detection_rate']
        comments = result['analysis']['total_comments']
        print(f"  {model}: {rate:.1f}% detection rate ({comments} comments)")

if __name__ == "__main__":
    collect_and_analyze_results()