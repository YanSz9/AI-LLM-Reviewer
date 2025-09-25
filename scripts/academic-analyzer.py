#!/usr/bin/env python3
"""
Simple AI Model Results Collector and Graph Generator
Collects PR review results and generates comparison graphs for academic analysis
"""

import requests
import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
import os

# Sincronização com modelos do switch-ai-model.py
SUPPORTED_MODELS = {
    'o1-mini': 'O1-Mini',
    'gpt-4.1': 'GPT-4.1', 
    'gpt-5': 'GPT-5',
    'gpt-4o': 'GPT-4o',
    'gpt-4-turbo': 'GPT-4-Turbo',
    'o1-preview': 'O1-Preview',
    'claude': 'Claude-3.5-Sonnet',
    'llama': 'Llama-3.1-8B'
}

class AIModelAnalyzer:
    def __init__(self, repo_owner="YanSz9", repo_name="AI-LLM-Reviewer"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.results = []

    def collect_pr_comments(self, pr_number):
        """Collect all comments from a specific PR"""
        headers = {}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        # Get PR details
        pr_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}"
        pr_response = requests.get(pr_url, headers=headers)
        
        if pr_response.status_code != 200:
            print(f"❌ Failed to get PR {pr_number}: {pr_response.status_code}")
            return None
            
        pr_data = pr_response.json()
        
        # Get review comments (inline comments)
        comments_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}/comments"
        comments_response = requests.get(comments_url, headers=headers)
        
        if comments_response.status_code != 200:
            print(f"❌ Failed to get comments for PR {pr_number}")
            return None
            
        comments = comments_response.json()
        
        return {
            'pr_number': pr_number,
            'title': pr_data.get('title', ''),
            'model': self.extract_model_from_title(pr_data.get('title', '')),
            'total_comments': len(comments),
            'comments': comments,
            'created_at': pr_data.get('created_at', ''),
            'body': pr_data.get('body', '')
        }

    def extract_model_from_title(self, title):
        """Extract AI model name from PR title - Sincronizado com switch-ai-model.py"""
        title_lower = title.lower()
        
        # Prioridade de detecção (mais específico primeiro)
        model_patterns = [
            ('o1-mini', 'O1-Mini'),
            ('gpt-4.1', 'GPT-4.1'),
            ('gpt-5', 'GPT-5'),
            ('o1-preview', 'O1-Preview'),
            ('gpt-4-turbo', 'GPT-4-Turbo'),
            ('gpt-4o', 'GPT-4o'),
            ('claude-3-5-sonnet', 'Claude-3.5-Sonnet'),
            ('claude', 'Claude-3.5-Sonnet'),
            ('llama-3.1', 'Llama-3.1-8B'),
            ('llama', 'Llama-3.1-8B'),
            ('groq', 'Llama-3.1-8B')
        ]
        
        # Procura pelos padrões na ordem de prioridade
        for pattern, model_name in model_patterns:
            if pattern in title_lower:
                return model_name
        
        # Fallback para detecção baseada no branch name também
        for model_key, model_display in SUPPORTED_MODELS.items():
            if model_key in title_lower:
                return model_display
        
        return 'Unknown'

    def analyze_comment_quality(self, comment_text):
        """Analyze the quality and type of AI comments"""
        text_lower = comment_text.lower()
        
        # Security vulnerability detection
        security_keywords = [
            'sql injection', 'xss', 'cross-site scripting', 'vulnerability',
            'security', 'injection', 'hardcoded', 'password', 'secret',
            'authentication', 'authorization', 'csrf', 'path traversal'
        ]
        
        security_score = sum(1 for keyword in security_keywords if keyword in text_lower)
        
        # Code quality suggestions  
        quality_keywords = [
            'refactor', 'improve', 'optimize', 'performance', 'maintainability',
            'readability', 'best practice', 'convention', 'pattern'
        ]
        
        quality_score = sum(1 for keyword in quality_keywords if keyword in text_lower)
        
        return {
            'security_focus': security_score > 0,
            'quality_focus': quality_score > 0,
            'security_score': security_score,
            'quality_score': quality_score,
            'length': len(comment_text),
            'detailed': len(comment_text) > 100
        }

    def generate_comparison_graphs(self):
        """Generate comprehensive comparison graphs for academic presentation"""
        if not self.results:
            print("❌ No data to analyze")
            return
            
        # Create DataFrame for analysis
        df_data = []
        for result in self.results:
            model = result['model']
            total_comments = result['total_comments']
            
            security_comments = 0
            quality_comments = 0
            total_length = 0
            detailed_comments = 0
            
            for comment in result['comments']:
                analysis = self.analyze_comment_quality(comment.get('body', ''))
                if analysis['security_focus']:
                    security_comments += 1
                if analysis['quality_focus']:
                    quality_comments += 1
                total_length += analysis['length']
                if analysis['detailed']:
                    detailed_comments += 1
            
            avg_length = total_length / total_comments if total_comments > 0 else 0
            
            df_data.append({
                'Model': model,
                'Total_Comments': total_comments,
                'Security_Comments': security_comments,
                'Quality_Comments': quality_comments,
                'Detailed_Comments': detailed_comments,
                'Avg_Comment_Length': avg_length,
                'Security_Detection_Rate': (security_comments / total_comments * 100) if total_comments > 0 else 0
            })
        
        df = pd.DataFrame(df_data)
        
        if df.empty:
            print("❌ No valid data for analysis")
            return
        
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('AI Model Performance Comparison for Academic Analysis', fontsize=16, fontweight='bold')
        
        # 1. Total Comments Comparison
        sns.barplot(data=df, x='Model', y='Total_Comments', ax=axes[0,0])
        axes[0,0].set_title('Total Comments Generated by Each Model')
        axes[0,0].set_ylabel('Number of Comments')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # 2. Security vs Quality Focus
        df_melted = pd.melt(df, id_vars=['Model'], 
                           value_vars=['Security_Comments', 'Quality_Comments'],
                           var_name='Comment_Type', value_name='Count')
        sns.barplot(data=df_melted, x='Model', y='Count', hue='Comment_Type', ax=axes[0,1])
        axes[0,1].set_title('Security vs Quality Focus')
        axes[0,1].set_ylabel('Number of Comments')
        axes[0,1].tick_params(axis='x', rotation=45)
        axes[0,1].legend(title='Comment Type')
        
        # 3. Security Detection Rate
        sns.barplot(data=df, x='Model', y='Security_Detection_Rate', ax=axes[1,0])
        axes[1,0].set_title('Security Vulnerability Detection Rate (%)')
        axes[1,0].set_ylabel('Detection Rate (%)')
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # 4. Comment Quality (Average Length)
        sns.barplot(data=df, x='Model', y='Avg_Comment_Length', ax=axes[1,1])
        axes[1,1].set_title('Average Comment Length (Detail Level)')
        axes[1,1].set_ylabel('Average Characters')
        axes[1,1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save the graph
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'ai_model_comparison_{timestamp}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 Graph saved as: {filename}")
        
        # Save detailed data as CSV for further analysis
        csv_filename = f'ai_model_data_{timestamp}.csv'
        df.to_csv(csv_filename, index=False)
        print(f"📋 Data saved as: {csv_filename}")
        
        plt.show()
        
        # Print summary statistics
        print("\n📈 SUMMARY STATISTICS FOR ACADEMIC ANALYSIS:")
        print("=" * 60)
        for _, row in df.iterrows():
            print(f"\n🤖 {row['Model']}:")
            print(f"  • Total Comments: {row['Total_Comments']}")
            print(f"  • Security Focus: {row['Security_Comments']} ({row['Security_Detection_Rate']:.1f}%)")
            print(f"  • Quality Focus: {row['Quality_Comments']}")
            print(f"  • Detailed Comments: {row['Detailed_Comments']}")
            print(f"  • Avg Length: {row['Avg_Comment_Length']:.1f} chars")

    def run_analysis(self, pr_numbers):
        """Run complete analysis on list of PR numbers"""
        print("🔍 Collecting AI model review data...")
        print(f"📋 Modelos suportados: {', '.join(SUPPORTED_MODELS.values())}")
        
        for pr_num in pr_numbers:
            print(f"📝 Analyzing PR #{pr_num}...")
            result = self.collect_pr_comments(pr_num)
            if result:
                self.results.append(result)
                print(f"✅ Collected {result['total_comments']} comments from {result['model']}")
            else:
                print(f"❌ Failed to collect data from PR #{pr_num}")
        
        if self.results:
            print(f"\n📊 Generating comparison graphs for {len(self.results)} models...")
            
            # Mostrar modelos detectados
            detected_models = [r['model'] for r in self.results]
            print(f"🎯 Modelos detectados: {', '.join(set(detected_models))}")
            
            self.generate_comparison_graphs()
        else:
            print("❌ No data collected for analysis")

def main():
    """Main function for interactive usage"""
    print("🎓 AI Model Academic Comparison Tool")
    print("=" * 50)
    
    print("📋 Modelos suportados para análise:")
    for key, name in SUPPORTED_MODELS.items():
        print(f"  • {name} (detecta: '{key}')")
    print()
    
    analyzer = AIModelAnalyzer()
    
    # Example usage - replace with your PR numbers
    print("📝 Enter the PR numbers you want to analyze (comma-separated):")
    print("Example: 27,28,29,30")
    
    try:
        pr_input = input("PR Numbers: ").strip()
        if not pr_input:
            # Default to recent test PRs
            pr_numbers = [27, 28, 29, 30]
            print(f"Using default PRs: {pr_numbers}")
        else:
            pr_numbers = [int(x.strip()) for x in pr_input.split(',')]
        
        analyzer.run_analysis(pr_numbers)
        
    except KeyboardInterrupt:
        print("\n👋 Analysis cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()