#!/usr/bin/env python3
"""
Simple AI Model Benchmark Analysis (No External Dependencies)
Generates text-based reports and basic HTML without matplotlib/pandas
"""

import json
import urllib.request
import urllib.parse
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import re

class SimpleBenchmarkAnalyzer:
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
        """Fetch AI review comments from GitHub PR using only standard library"""
        if not self.github_token:
            print("⚠️  GitHub token not found. Please set GITHUB_TOKEN environment variable.")
            return []
            
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'AI-Benchmark-Analyzer/1.0'
        }
        
        all_reviews = []
        
        # URLs to fetch
        urls = [
            f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}/comments",
            f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}/reviews"
        ]
        
        try:
            for url in urls:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
                    
                    if 'comments' in url:
                        # Line comments
                        for comment in data:
                            all_reviews.append({
                                'type': 'line_comment',
                                'body': comment['body'],
                                'line': comment.get('line'),
                                'path': comment['path'],
                                'user': comment['user']['login'],
                                'created_at': comment['created_at']
                            })
                    else:
                        # General reviews
                        for review in data:
                            if review['body']:
                                all_reviews.append({
                                    'type': 'general_review',
                                    'body': review['body'],
                                    'user': review['user']['login'],
                                    'state': review['state'],
                                    'created_at': review.get('submitted_at')
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
        
        issue_details = []
        
        # Keywords for different issue types
        security_keywords = [
            'sql injection', 'xss', 'hardcoded', 'secret', 'api key', 'password',
            'command injection', 'crypto', 'authentication', 'vulnerability',
            'security', 'injection', 'cross-site scripting', 'credential'
        ]
        
        performance_keywords = [
            'race condition', 'memory leak', 'performance', 'inefficient', 
            'blocking', 'async', 'synchronous', 'resource', 'optimization',
            'complexity', 'algorithm', 'bottleneck'
        ]
        
        quality_keywords = [
            'type', 'error handling', 'validation', 'null check', 'exception',
            'input validation', 'type safety', 'annotation', 'casting'
        ]
        
        # Analyze each review
        for review in reviews:
            body = review['body'].lower()
            
            # Count keyword matches (more sophisticated than simple presence)
            security_matches = sum(1 for keyword in security_keywords if keyword in body)
            performance_matches = sum(1 for keyword in performance_keywords if keyword in body)
            quality_matches = sum(1 for keyword in quality_keywords if keyword in body)
            
            if security_matches > 0:
                detected_issues['security'] += min(security_matches, 3)  # Cap to avoid over-counting
                
            if performance_matches > 0:
                detected_issues['performance'] += min(performance_matches, 2)
                
            if quality_matches > 0:
                detected_issues['quality'] += min(quality_matches, 2)
                
            issue_details.append({
                'line': review.get('line'),
                'type': 'detected',
                'content': review['body'][:200] + '...' if len(review['body']) > 200 else review['body'],
                'security_signals': security_matches,
                'performance_signals': performance_matches,
                'quality_signals': quality_matches
            })
        
        # Calculate metrics
        total_detected = sum(detected_issues.values())
        detection_rate = min((total_detected / total_issues) * 100, 100) if total_issues > 0 else 0
        
        # Calculate category scores (capped at 100%)
        security_score = min((detected_issues['security'] / len(self.known_issues['security'])) * 100, 100)
        performance_score = min((detected_issues['performance'] / len(self.known_issues['performance'])) * 100, 100)
        quality_score = min((detected_issues['quality'] / len(self.known_issues['quality'])) * 100, 100)
        
        return {
            'total_comments': len(reviews),
            'detected_issues': detected_issues,
            'total_detected': total_detected,
            'detection_rate': detection_rate,
            'issue_details': issue_details,
            'security_score': security_score,
            'performance_score': performance_score,
            'quality_score': quality_score
        }

    def generate_text_report(self, results: Dict[str, Any], pr_number: int) -> str:
        """Generate a comprehensive text report"""
        report = []
        report.append("🎯 AI MODEL BENCHMARK ANALYSIS REPORT")
        report.append("=" * 50)
        report.append(f"📋 PR Number: #{pr_number}")
        report.append(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"🔍 Total Known Issues: {sum(len(category) for category in self.known_issues.values())}")
        report.append("")
        
        if not results:
            report.append("❌ No AI model reviews detected in this PR.")
            return "\n".join(report)
            
        # Summary table
        report.append("📊 PERFORMANCE SUMMARY")
        report.append("-" * 50)
        report.append(f"{'Model':<25} {'Overall':<10} {'Security':<10} {'Perf':<8} {'Quality':<8} {'Comments':<8}")
        report.append("-" * 50)
        
        for model_name, data in results.items():
            model_short = model_name.replace('github-actions', 'AI').replace('[bot]', '')[:24]
            report.append(f"{model_short:<25} {data['detection_rate']:<9.1f}% {data['security_score']:<9.1f}% {data['performance_score']:<7.1f}% {data['quality_score']:<7.1f}% {data['total_comments']:<8}")
        
        report.append("")
        
        # Detailed analysis for each model
        for model_name, data in results.items():
            report.append(f"🤖 DETAILED ANALYSIS: {model_name}")
            report.append("-" * 50)
            report.append(f"📈 Overall Detection Rate: {data['detection_rate']:.1f}%")
            report.append(f"🔒 Security Issues Found: {data['detected_issues']['security']} (Score: {data['security_score']:.1f}%)")
            report.append(f"⚡ Performance Issues Found: {data['detected_issues']['performance']} (Score: {data['performance_score']:.1f}%)")
            report.append(f"✨ Quality Issues Found: {data['detected_issues']['quality']} (Score: {data['quality_score']:.1f}%)")
            report.append(f"💬 Total Comments: {data['total_comments']}")
            
            # Performance rating
            if data['detection_rate'] >= 70:
                rating = "🟢 EXCELLENT"
            elif data['detection_rate'] >= 40:
                rating = "🟡 GOOD"
            else:
                rating = "🔴 NEEDS IMPROVEMENT"
                
            report.append(f"🏆 Performance Rating: {rating}")
            report.append("")
        
        # Best performers
        if results:
            best_overall = max(results.keys(), key=lambda k: results[k]['detection_rate'])
            best_security = max(results.keys(), key=lambda k: results[k]['security_score'])
            best_performance = max(results.keys(), key=lambda k: results[k]['performance_score'])
            best_quality = max(results.keys(), key=lambda k: results[k]['quality_score'])
            
            report.append("🏅 TOP PERFORMERS")
            report.append("-" * 50)
            report.append(f"🥇 Best Overall: {best_overall} ({results[best_overall]['detection_rate']:.1f}%)")
            report.append(f"🔒 Best Security: {best_security} ({results[best_security]['security_score']:.1f}%)")
            report.append(f"⚡ Best Performance: {best_performance} ({results[best_performance]['performance_score']:.1f}%)")
            report.append(f"✨ Best Quality: {best_quality} ({results[best_quality]['quality_score']:.1f}%)")
            report.append("")
        
        # Issue breakdown
        report.append("📋 KNOWN ISSUES BREAKDOWN")
        report.append("-" * 50)
        for category, issues in self.known_issues.items():
            report.append(f"{category.upper()} ({len(issues)} issues):")
            for issue in issues[:5]:  # Show first 5 of each category
                report.append(f"  Line {issue['line']}: {issue['description']} ({issue['severity']})")
            if len(issues) > 5:
                report.append(f"  ... and {len(issues) - 5} more")
            report.append("")
        
        return "\n".join(report)

    def generate_simple_html(self, results: Dict[str, Any], pr_number: int) -> str:
        """Generate simple HTML report without external dependencies"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI Benchmark Report - PR #{pr_number}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f6fa; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .summary {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .model-card {{ border: 2px solid #bdc3c7; margin: 20px 0; padding: 20px; border-radius: 8px; }}
        .score {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
        .excellent {{ color: #27ae60; }}
        .good {{ color: #f39c12; }}
        .poor {{ color: #e74c3c; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #34495e; color: white; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 AI Model Benchmark Report</h1>
        
        <div class="summary">
            <h2>📋 Summary</h2>
            <p><strong>PR Number:</strong> #{pr_number}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Total Known Issues:</strong> {sum(len(category) for category in self.known_issues.values())}</p>
            <p><strong>Models Analyzed:</strong> {len(results)}</p>
        </div>
"""
        
        if not results:
            html += """
        <div class="model-card">
            <h3>❌ No Results</h3>
            <p>No AI model reviews were detected in this PR. Make sure:</p>
            <ul>
                <li>The PR has AI-generated comments</li>
                <li>GitHub token is properly set</li>
                <li>The workflow has completed successfully</li>
            </ul>
        </div>
"""
        else:
            # Model cards
            for model_name, data in results.items():
                score_class = 'excellent' if data['detection_rate'] >= 70 else 'good' if data['detection_rate'] >= 40 else 'poor'
                
                html += f"""
        <div class="model-card">
            <h3>🤖 {model_name}</h3>
            <div class="score {score_class}">{data['detection_rate']:.1f}%</div>
            <p><strong>Overall Detection Rate</strong></p>
            
            <div class="metric">🔒 Security: {data['security_score']:.1f}%</div>
            <div class="metric">⚡ Performance: {data['performance_score']:.1f}%</div>
            <div class="metric">✨ Quality: {data['quality_score']:.1f}%</div>
            <div class="metric">💬 Comments: {data['total_comments']}</div>
        </div>
"""
            
            # Comparison table
            html += """
        <h2>📊 Detailed Comparison</h2>
        <table>
            <tr>
                <th>Model</th>
                <th>Overall Score</th>
                <th>Security</th>
                <th>Performance</th>
                <th>Quality</th>
                <th>Comments</th>
            </tr>
"""
            
            for model_name, data in results.items():
                html += f"""
            <tr>
                <td>{model_name}</td>
                <td>{data['detection_rate']:.1f}%</td>
                <td>{data['security_score']:.1f}%</td>
                <td>{data['performance_score']:.1f}%</td>
                <td>{data['quality_score']:.1f}%</td>
                <td>{data['total_comments']}</td>
            </tr>
"""
            
            html += "</table>"
        
        html += """
    </div>
</body>
</html>"""
        
        return html

    def analyze_pr(self, pr_number: int, output_dir: str = "simple_benchmark_results"):
        """Main analysis function"""
        print(f"🔍 Analyzing PR #{pr_number}...")
        
        # Create output directory
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Fetch and analyze
        reviews = self.fetch_pr_reviews(pr_number)
        if not reviews:
            print("❌ No reviews found. Check GitHub token and PR number.")
            return
            
        print(f"📊 Found {len(reviews)} reviews to analyze...")
        
        results = self.analyze_model_performance(reviews)
        
        # Generate reports
        text_report = self.generate_text_report(results, pr_number)
        html_report = self.generate_simple_html(results, pr_number)
        
        # Save files
        with open(f"{output_dir}/benchmark_report.txt", "w") as f:
            f.write(text_report)
            
        with open(f"{output_dir}/benchmark_report.html", "w") as f:
            f.write(html_report)
            
        # Save JSON data
        json_data = {
            "metadata": {
                "pr_number": pr_number,
                "generated_at": datetime.now().isoformat(),
                "total_known_issues": sum(len(category) for category in self.known_issues.values())
            },
            "results": results
        }
        
        with open(f"{output_dir}/results.json", "w") as f:
            json.dump(json_data, f, indent=2)
        
        print(f"✅ Analysis complete!")
        print(f"📁 Results saved to: {output_dir}/")
        print(f"   📄 benchmark_report.txt - Text summary")
        print(f"   🌐 benchmark_report.html - HTML report") 
        print(f"   📋 results.json - Raw data")
        
        # Show quick summary
        print("\n📊 Quick Summary:")
        if results:
            for model_name, data in results.items():
                rating = "🟢 Excellent" if data['detection_rate'] >= 70 else "🟡 Good" if data['detection_rate'] >= 40 else "🔴 Poor"
                print(f"   {model_name}: {data['detection_rate']:.1f}% {rating}")
        else:
            print("   No AI model reviews detected")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 simple-analyzer.py <pr_number> [output_dir]")
        sys.exit(1)
        
    pr_number = int(sys.argv[1])
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "simple_benchmark_results"
    
    analyzer = SimpleBenchmarkAnalyzer()
    analyzer.analyze_pr(pr_number, output_dir)

if __name__ == "__main__":
    main()