#!/usr/bin/env python3
"""
AI Model Benchmark Analysis Tool
Generates comprehensive comparison reports with graphs and metrics
"""

import json
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from pathlib import Path
import argparse
from datetime import datetime
import requests
import os
from typing import Dict, List, Any
import re

class BenchmarkAnalyzer:
    def __init__(self, github_token=None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.repo_owner = "YanSz9"
        self.repo_name = "AI-LLM-Reviewer"
        self.known_issues = self._load_known_issues()
        
    def _load_known_issues(self) -> Dict[str, List[Dict]]:
        """Define the known issues in benchmark-test.ts for evaluation"""
        return {
            "security": [
                {"line": 8, "type": "hardcoded_secret", "severity": "high", "description": "Hardcoded API key"},
                {"line": 15, "type": "sql_injection", "severity": "critical", "description": "SQL injection in getUserData"},
                {"line": 19, "type": "sql_injection", "severity": "critical", "description": "SQL injection in filters"},
                {"line": 30, "type": "xss", "severity": "high", "description": "XSS in user profile generation"},
                {"line": 33, "type": "xss", "severity": "high", "description": "XSS in script tag"},
                {"line": 65, "type": "command_injection", "severity": "critical", "description": "Command injection in exec"},
                {"line": 75, "type": "hardcoded_secret", "severity": "high", "description": "Hardcoded database password"},
                {"line": 85, "type": "crypto_weakness", "severity": "medium", "description": "Weak cryptographic implementation"},
                {"line": 95, "type": "auth_bypass", "severity": "critical", "description": "Authentication bypass vulnerability"},
                {"line": 105, "type": "info_disclosure", "severity": "medium", "description": "Information disclosure in error messages"},
                {"line": 115, "type": "hardcoded_secret", "severity": "high", "description": "Hardcoded JWT secret"},
                {"line": 125, "type": "command_injection", "severity": "critical", "description": "Command injection in file operations"},
                {"line": 135, "type": "crypto_weakness", "severity": "medium", "description": "Insecure random number generation"},
                {"line": 145, "type": "info_disclosure", "severity": "medium", "description": "Sensitive data exposure"},
                {"line": 155, "type": "auth_bypass", "severity": "high", "description": "Missing authentication check"}
            ],
            "performance": [
                {"line": 38, "type": "race_condition", "severity": "high", "description": "Race condition in balance update"},
                {"line": 45, "type": "memory_leak", "severity": "medium", "description": "Memory leak in monitoring"},
                {"line": 55, "type": "inefficient_algorithm", "severity": "medium", "description": "O(n²) complexity in search"},
                {"line": 165, "type": "memory_leak", "severity": "medium", "description": "Unclosed resources"},
                {"line": 175, "type": "blocking_operation", "severity": "medium", "description": "Synchronous heavy computation"}
            ],
            "quality": [
                {"line": 12, "type": "no_input_validation", "severity": "medium", "description": "Missing input validation"},
                {"line": 22, "type": "no_error_handling", "severity": "medium", "description": "Missing error handling"},
                {"line": 68, "type": "type_safety", "severity": "low", "description": "Any type usage"},
                {"line": 78, "type": "type_safety", "severity": "low", "description": "Missing type annotations"},
                {"line": 88, "type": "type_safety", "severity": "low", "description": "Unsafe type casting"},
                {"line": 98, "type": "type_safety", "severity": "low", "description": "Missing null checks"},
                {"line": 108, "type": "no_error_handling", "severity": "medium", "description": "Unhandled promise rejection"}
            ]
        }

    def fetch_pr_reviews(self, pr_number: int) -> List[Dict]:
        """Fetch AI review comments from GitHub PR"""
        if not self.github_token:
            print("⚠️  GitHub token not found. Please set GITHUB_TOKEN environment variable.")
            return []
            
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Fetch PR comments
        comments_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}/comments"
        reviews_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}/reviews"
        
        all_reviews = []
        
        try:
            # Fetch review comments (line-specific)
            response = requests.get(comments_url, headers=headers)
            if response.status_code == 200:
                comments = response.json()
                for comment in comments:
                    all_reviews.append({
                        'type': 'line_comment',
                        'body': comment['body'],
                        'line': comment.get('line'),
                        'path': comment['path'],
                        'user': comment['user']['login'],
                        'created_at': comment['created_at']
                    })
            
            # Fetch general reviews
            response = requests.get(reviews_url, headers=headers)
            if response.status_code == 200:
                reviews = response.json()
                for review in reviews:
                    if review['body']:
                        all_reviews.append({
                            'type': 'general_review',
                            'body': review['body'],
                            'user': review['user']['login'],
                            'state': review['state'],
                            'created_at': review['submitted_at']
                        })
                        
        except Exception as e:
            print(f"Error fetching reviews: {e}")
            
        return all_reviews

    def analyze_model_performance(self, reviews: List[Dict]) -> Dict[str, Any]:
        """Analyze how well each model performed"""
        results = {}
        
        # Group reviews by model (user)
        models = {}
        for review in reviews:
            user = review['user']
            if user not in models:
                models[user] = []
            models[user].append(review)
        
        for model_name, model_reviews in models.items():
            if 'github-actions' in model_name.lower() or 'bot' in model_name.lower():
                # This is likely an AI model
                analysis = self._analyze_single_model(model_reviews)
                results[model_name] = analysis
                
        return results

    def _analyze_single_model(self, reviews: List[Dict]) -> Dict[str, Any]:
        """Analyze performance of a single model"""
        total_issues = sum(len(category) for category in self.known_issues.values())
        detected_issues = {
            'security': 0,
            'performance': 0, 
            'quality': 0
        }
        
        false_positives = 0
        issue_details = []
        
        # Analyze each review
        for review in reviews:
            body = review['body'].lower()
            
            # Check for security issue detection
            security_keywords = ['sql injection', 'xss', 'hardcoded', 'secret', 'api key', 
                               'command injection', 'crypto', 'authentication', 'vulnerability']
            if any(keyword in body for keyword in security_keywords):
                detected_issues['security'] += 1
                
            # Check for performance issue detection  
            performance_keywords = ['race condition', 'memory leak', 'performance', 
                                  'inefficient', 'blocking', 'async']
            if any(keyword in body for keyword in performance_keywords):
                detected_issues['performance'] += 1
                
            # Check for quality issue detection
            quality_keywords = ['type', 'error handling', 'validation', 'null check']
            if any(keyword in body for keyword in quality_keywords):
                detected_issues['quality'] += 1
                
            issue_details.append({
                'line': review.get('line'),
                'type': 'detected',
                'content': review['body'][:200] + '...' if len(review['body']) > 200 else review['body']
            })
        
        # Calculate metrics
        total_detected = sum(detected_issues.values())
        detection_rate = (total_detected / total_issues) * 100 if total_issues > 0 else 0
        
        return {
            'total_comments': len(reviews),
            'detected_issues': detected_issues,
            'total_detected': total_detected,
            'detection_rate': detection_rate,
            'false_positives': false_positives,
            'issue_details': issue_details,
            'security_score': (detected_issues['security'] / len(self.known_issues['security'])) * 100,
            'performance_score': (detected_issues['performance'] / len(self.known_issues['performance'])) * 100,
            'quality_score': (detected_issues['quality'] / len(self.known_issues['quality'])) * 100
        }

    def generate_comparison_report(self, pr_number: int, output_dir: str = "benchmark_results"):
        """Generate comprehensive comparison report with graphs"""
        print(f"🔍 Analyzing PR #{pr_number}...")
        
        # Fetch reviews
        reviews = self.fetch_pr_reviews(pr_number)
        if not reviews:
            print("❌ No reviews found. Make sure the PR has AI comments and GITHUB_TOKEN is set.")
            return
            
        print(f"📊 Found {len(reviews)} reviews to analyze...")
        
        # Analyze performance
        results = self.analyze_model_performance(reviews)
        if not results:
            print("❌ No AI model reviews detected.")
            return
            
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)
        
        # Generate report
        self._generate_html_report(results, pr_number, output_dir)
        self._generate_graphs(results, output_dir)
        self._generate_json_report(results, pr_number, output_dir)
        
        print(f"✅ Analysis complete! Check {output_dir}/ for results:")
        print(f"   📄 {output_dir}/benchmark_report.html - Interactive HTML report")
        print(f"   📊 {output_dir}/comparison_graphs.png - Performance graphs")  
        print(f"   📋 {output_dir}/detailed_results.json - Raw data")

    def _generate_html_report(self, results: Dict[str, Any], pr_number: int, output_dir: str):
        """Generate interactive HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Model Benchmark Report - PR #{pr_number}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f6fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .model-name {{ font-size: 1.5em; font-weight: bold; color: #2c3e50; margin-bottom: 15px; }}
        .score {{ font-size: 2em; font-weight: bold; margin: 10px 0; }}
        .score.excellent {{ color: #27ae60; }}
        .score.good {{ color: #f39c12; }}
        .score.poor {{ color: #e74c3c; }}
        .chart-container {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 30px; }}
        .summary-table {{ background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .summary-table table {{ width: 100%; border-collapse: collapse; }}
        .summary-table th {{ background: #34495e; color: white; padding: 15px; text-align: left; }}
        .summary-table td {{ padding: 15px; border-bottom: 1px solid #ecf0f1; }}
        .badge {{ padding: 5px 10px; border-radius: 20px; font-size: 0.8em; font-weight: bold; }}
        .badge.high {{ background: #e74c3c; color: white; }}
        .badge.medium {{ background: #f39c12; color: white; }}
        .badge.low {{ background: #27ae60; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 AI Model Benchmark Report</h1>
            <p>Pull Request #{pr_number} | Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Comprehensive analysis of AI code review performance on intentional vulnerabilities</p>
        </div>

        <div class="metrics-grid">
"""
        
        # Add model cards
        for model_name, data in results.items():
            detection_rate = data['detection_rate']
            score_class = 'excellent' if detection_rate >= 70 else 'good' if detection_rate >= 40 else 'poor'
            
            html_content += f"""
            <div class="metric-card">
                <div class="model-name">{model_name}</div>
                <div class="score {score_class}">{detection_rate:.1f}%</div>
                <p><strong>Detection Rate</strong></p>
                <div style="margin-top: 15px;">
                    <p>📊 <strong>Issues Found:</strong> {data['total_detected']}/27</p>
                    <p>🔒 <strong>Security:</strong> {data['security_score']:.1f}%</p>
                    <p>⚡ <strong>Performance:</strong> {data['performance_score']:.1f}%</p>
                    <p>✨ <strong>Quality:</strong> {data['quality_score']:.1f}%</p>
                    <p>💬 <strong>Comments:</strong> {data['total_comments']}</p>
                </div>
            </div>
"""
        
        # Add charts and summary table
        html_content += f"""
        </div>

        <div class="chart-container">
            <h2>📊 Performance Comparison</h2>
            <canvas id="comparisonChart" width="400" height="200"></canvas>
        </div>

        <div class="summary-table">
            <h2 style="padding: 20px; margin: 0; background: #34495e; color: white;">📋 Detailed Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Model</th>
                        <th>Overall Score</th>
                        <th>Security</th>
                        <th>Performance</th>
                        <th>Quality</th>
                        <th>Comments</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for model_name, data in results.items():
            html_content += f"""
                    <tr>
                        <td><strong>{model_name}</strong></td>
                        <td><span class="badge {'high' if data['detection_rate'] >= 70 else 'medium' if data['detection_rate'] >= 40 else 'low'}">{data['detection_rate']:.1f}%</span></td>
                        <td>{data['security_score']:.1f}%</td>
                        <td>{data['performance_score']:.1f}%</td>
                        <td>{data['quality_score']:.1f}%</td>
                        <td>{data['total_comments']}</td>
                    </tr>
"""
        
        # Prepare data for chart
        model_names = list(results.keys())
        detection_rates = [results[model]['detection_rate'] for model in model_names]
        security_scores = [results[model]['security_score'] for model in model_names]
        performance_scores = [results[model]['performance_score'] for model in model_names]
        quality_scores = [results[model]['quality_score'] for model in model_names]
        
        html_content += f"""
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('comparisonChart').getContext('2d');
        new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: ['Overall Detection', 'Security Issues', 'Performance Issues', 'Quality Issues'],
                datasets: ["""
        
        # Add datasets for each model
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        for i, (model_name, data) in enumerate(results.items()):
            color = colors[i % len(colors)]
            html_content += f"""
                    {{
                        label: '{model_name}',
                        data: [{data['detection_rate']:.1f}, {data['security_score']:.1f}, {data['performance_score']:.1f}, {data['quality_score']:.1f}],
                        borderColor: '{color}',
                        backgroundColor: '{color}33',
                        borderWidth: 2
                    }},"""
        
        html_content += """
                ]
            },
            options: {
                responsive: true,
                scale: {
                    ticks: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    </script>
</body>
</html>"""
        
        with open(f"{output_dir}/benchmark_report.html", "w") as f:
            f.write(html_content)

    def _generate_graphs(self, results: Dict[str, Any], output_dir: str):
        """Generate comparison graphs using matplotlib"""
        plt.style.use('seaborn-v0_8')
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('AI Model Benchmark Comparison', fontsize=16, fontweight='bold')
        
        models = list(results.keys())
        
        # Overall detection rates
        detection_rates = [results[model]['detection_rate'] for model in models]
        colors = plt.cm.Set3(np.linspace(0, 1, len(models)))
        
        bars1 = ax1.bar(models, detection_rates, color=colors)
        ax1.set_title('Overall Detection Rate (%)')
        ax1.set_ylabel('Detection Rate (%)')
        ax1.set_ylim(0, 100)
        for bar, rate in zip(bars1, detection_rates):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Category breakdown
        categories = ['Security', 'Performance', 'Quality']
        category_data = {
            model: [results[model]['security_score'], results[model]['performance_score'], results[model]['quality_score']]
            for model in models
        }
        
        x = np.arange(len(categories))
        width = 0.8 / len(models)
        
        for i, model in enumerate(models):
            ax2.bar(x + i * width, category_data[model], width, label=model, color=colors[i])
        
        ax2.set_title('Performance by Category')
        ax2.set_ylabel('Score (%)')
        ax2.set_xlabel('Issue Category')
        ax2.set_xticks(x + width * (len(models) - 1) / 2)
        ax2.set_xticklabels(categories)
        ax2.legend()
        ax2.set_ylim(0, 100)
        
        # Comments vs Detection Rate scatter
        comments = [results[model]['total_comments'] for model in models]
        ax3.scatter(comments, detection_rates, c=colors, s=100, alpha=0.7)
        for i, model in enumerate(models):
            ax3.annotate(model.replace('github-actions', 'AI'), (comments[i], detection_rates[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        ax3.set_xlabel('Number of Comments')
        ax3.set_ylabel('Detection Rate (%)')
        ax3.set_title('Comments vs Detection Efficiency')
        
        # Radar chart simulation with polygon
        angles = np.linspace(0, 2 * np.pi, 4, endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle
        
        ax4 = plt.subplot(2, 2, 4, projection='polar')
        ax4.set_theta_offset(np.pi / 2)
        ax4.set_theta_direction(-1)
        
        categories_radar = ['Overall', 'Security', 'Performance', 'Quality']
        ax4.set_thetagrids(np.degrees(angles[:-1]), categories_radar)
        
        for i, model in enumerate(models):
            values = [detection_rates[i], results[model]['security_score'], 
                     results[model]['performance_score'], results[model]['quality_score']]
            values += values[:1]  # Complete the circle
            ax4.plot(angles, values, 'o-', linewidth=2, label=model, color=colors[i])
            ax4.fill(angles, values, alpha=0.25, color=colors[i])
        
        ax4.set_ylim(0, 100)
        ax4.set_title('Multi-Dimensional Performance', pad=20)
        ax4.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/comparison_graphs.png", dpi=300, bbox_inches='tight')
        plt.close()

    def _generate_json_report(self, results: Dict[str, Any], pr_number: int, output_dir: str):
        """Generate detailed JSON report"""
        report = {
            "metadata": {
                "pr_number": pr_number,
                "generated_at": datetime.now().isoformat(),
                "total_known_issues": sum(len(category) for category in self.known_issues.values()),
                "analysis_version": "1.0.0"
            },
            "known_issues_breakdown": {
                category: len(issues) for category, issues in self.known_issues.items()
            },
            "model_results": results,
            "summary": {
                "best_overall": max(results.keys(), key=lambda k: results[k]['detection_rate']) if results else None,
                "best_security": max(results.keys(), key=lambda k: results[k]['security_score']) if results else None,
                "best_performance": max(results.keys(), key=lambda k: results[k]['performance_score']) if results else None,
                "best_quality": max(results.keys(), key=lambda k: results[k]['quality_score']) if results else None,
            }
        }
        
        with open(f"{output_dir}/detailed_results.json", "w") as f:
            json.dump(report, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Analyze AI model benchmark results')
    parser.add_argument('pr_number', type=int, help='Pull request number to analyze')
    parser.add_argument('--output', '-o', default='benchmark_results', help='Output directory')
    parser.add_argument('--token', '-t', help='GitHub token (or use GITHUB_TOKEN env var)')
    
    args = parser.parse_args()
    
    analyzer = BenchmarkAnalyzer(github_token=args.token)
    analyzer.generate_comparison_report(args.pr_number, args.output)

if __name__ == "__main__":
    main()