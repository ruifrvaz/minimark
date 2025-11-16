#!/usr/bin/env python3
"""
Visualization tool for LLM comprehension benchmark results.
Generates charts showing comprehension preservation across strategies and models.
"""

import json
from pathlib import Path
from typing import Dict, List
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np

# Use non-interactive backend for headless environments
matplotlib.use('Agg')


class LLMBenchmarkVisualizer:
    """Visualize LLM comprehension benchmark results."""
    
    def __init__(self, json_path: Path):
        """
        Initialize visualizer with LLM benchmark results.
        
        Args:
            json_path: Path to LLM benchmark results JSON
        """
        self.json_path = json_path
        with open(json_path, 'r') as f:
            self.data = json.load(f)
        
        # Extract run info from filename (e.g., run_002_gpt4o.json)
        self.run_number = json_path.stem.split('_')[1] if '_' in json_path.stem else '001'
        model_part = json_path.stem.split('_', 2)[2] if json_path.stem.count('_') >= 2 else 'unknown'
        self.model_name = model_part
    
    def generate_all_visualizations(self, output_dir: Path) -> None:
        """Generate all visualizations and save to output directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Generating LLM visualizations for run {self.run_number} ({self.model_name})...")
        
        # 1. Comprehension preservation by file
        self.plot_comprehension_by_file(output_dir / f'run_{self.run_number}_comprehension_by_file.png')
        
        # 2. Similarity scores distribution
        self.plot_similarity_distribution(output_dir / f'run_{self.run_number}_similarity_distribution.png')
        
        # 3. Token savings vs comprehension
        self.plot_token_savings_tradeoff(output_dir / f'run_{self.run_number}_token_savings_tradeoff.png')
        
        # 4. Question type analysis
        self.plot_question_type_analysis(output_dir / f'run_{self.run_number}_question_type_analysis.png')
        
        # 5. Generate summary JSON
        self.generate_summary_json(output_dir / f'run_{self.run_number}_summary.json')
        
        print(f"All visualizations saved to {output_dir}")
    
    def plot_comprehension_by_file(self, output_path: Path) -> None:
        """Plot comprehension preservation percentage by file."""
        files = [item['file'] for item in self.data]
        comprehension = [item.get('comprehension_preserved', 0) * 100 for item in self.data]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.barh(files, comprehension, color='steelblue')
        
        # Color bars based on threshold
        for bar, comp in zip(bars, comprehension):
            if comp >= 85:
                bar.set_color('green')
            elif comp >= 70:
                bar.set_color('orange')
            else:
                bar.set_color('red')
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2,
                   f'{width:.1f}%', ha='left', va='center', fontsize=9)
        
        ax.axvline(x=85, color='red', linestyle='--', alpha=0.5, label='Threshold (85%)')
        ax.set_xlabel('Comprehension Preserved (%)', fontsize=12)
        ax.set_ylabel('Document', fontsize=12)
        ax.set_title(f'LLM Comprehension by File - {self.model_name.upper()}', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Comprehension by file chart saved")
    
    def plot_similarity_distribution(self, output_path: Path) -> None:
        """Plot distribution of similarity scores."""
        all_similarities = []
        for item in self.data:
            for q in item.get('questions', []):
                if not q.get('error'):
                    all_similarities.append(q.get('similarity_score', 0))
        
        if not all_similarities:
            print("  ⚠ Skipping similarity distribution (no data)")
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Histogram
        n, bins, patches = ax.hist(all_similarities, bins=20, color='steelblue', 
                                   alpha=0.7, edgecolor='black')
        
        # Color bars based on threshold
        threshold = 0.85
        for patch, left_edge in zip(patches, bins[:-1]):
            if left_edge >= threshold:
                patch.set_facecolor('green')
            elif left_edge >= 0.7:
                patch.set_facecolor('orange')
            else:
                patch.set_facecolor('red')
        
        ax.axvline(x=threshold, color='red', linestyle='--', alpha=0.7, 
                  label=f'Threshold ({threshold})')
        ax.axvline(x=np.mean(all_similarities), color='blue', linestyle='-', alpha=0.7,
                  label=f'Mean ({np.mean(all_similarities):.3f})')
        
        ax.set_xlabel('Similarity Score', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title(f'Answer Similarity Distribution - {self.model_name.upper()}', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Similarity distribution chart saved")
    
    def plot_token_savings_tradeoff(self, output_path: Path) -> None:
        """Plot token savings vs comprehension preservation."""
        files = []
        comprehension = []
        token_savings = []
        
        for item in self.data:
            files.append(item['file'].replace('.md', ''))
            comprehension.append(item.get('comprehension_preserved', 0) * 100)
            token_savings.append(item.get('total_token_savings', 0))
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        scatter = ax.scatter(token_savings, comprehension, s=150, alpha=0.6, 
                           c=comprehension, cmap='RdYlGn', edgecolors='black',
                           vmin=0, vmax=100)
        
        # Add file labels
        for i, file in enumerate(files):
            ax.annotate(file, (token_savings[i], comprehension[i]),
                       fontsize=8, alpha=0.7, ha='right')
        
        # Threshold line
        ax.axhline(y=85, color='red', linestyle='--', alpha=0.5, 
                  label='Comprehension Threshold (85%)')
        
        ax.set_xlabel('Token Savings', fontsize=12)
        ax.set_ylabel('Comprehension Preserved (%)', fontsize=12)
        ax.set_title(f'Token Savings vs Comprehension - {self.model_name.upper()}', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Comprehension %', rotation=270, labelpad=20)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Token savings tradeoff chart saved")
    
    def plot_question_type_analysis(self, output_path: Path) -> None:
        """Plot success rate by question type."""
        question_types = {}
        
        for item in self.data:
            for q in item.get('questions', []):
                if not q.get('error'):
                    qtype = q.get('type', 'unknown')
                    if qtype not in question_types:
                        question_types[qtype] = {'equivalent': 0, 'total': 0}
                    
                    question_types[qtype]['total'] += 1
                    if q.get('equivalent', False):
                        question_types[qtype]['equivalent'] += 1
        
        if not question_types:
            print("  ⚠ Skipping question type analysis (no data)")
            return
        
        # Calculate percentages
        types = list(question_types.keys())
        success_rates = [
            (question_types[t]['equivalent'] / question_types[t]['total'] * 100)
            for t in types
        ]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(types, success_rates, color='steelblue', alpha=0.7, edgecolor='black')
        
        # Color bars
        for bar, rate in zip(bars, success_rates):
            if rate >= 85:
                bar.set_color('green')
            elif rate >= 70:
                bar.set_color('orange')
            else:
                bar.set_color('red')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height,
                   f'{height:.1f}%', ha='center', va='bottom', fontsize=10)
        
        ax.axhline(y=85, color='red', linestyle='--', alpha=0.5, 
                  label='Threshold (85%)')
        ax.set_xlabel('Question Type', fontsize=12)
        ax.set_ylabel('Success Rate (%)', fontsize=12)
        ax.set_title(f'Comprehension by Question Type - {self.model_name.upper()}', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(0, 105)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Question type analysis chart saved")
    
    def generate_summary_json(self, output_path: Path) -> None:
        """Generate summary statistics as JSON."""
        # Calculate overall metrics
        total_files = len(self.data)
        avg_comprehension = np.mean([item.get('comprehension_preserved', 0) for item in self.data])
        avg_similarity = np.mean([item.get('avg_similarity', 0) for item in self.data])
        total_token_savings = sum([item.get('total_token_savings', 0) for item in self.data])
        
        # Per-question-type metrics
        question_metrics = {}
        for item in self.data:
            for q in item.get('questions', []):
                if not q.get('error'):
                    qtype = q.get('type', 'unknown')
                    if qtype not in question_metrics:
                        question_metrics[qtype] = {
                            'total': 0,
                            'equivalent': 0,
                            'avg_similarity': []
                        }
                    
                    question_metrics[qtype]['total'] += 1
                    if q.get('equivalent', False):
                        question_metrics[qtype]['equivalent'] += 1
                    question_metrics[qtype]['avg_similarity'].append(q.get('similarity_score', 0))
        
        # Calculate averages
        for qtype in question_metrics:
            success_rate = question_metrics[qtype]['equivalent'] / question_metrics[qtype]['total']
            avg_sim = np.mean(question_metrics[qtype]['avg_similarity'])
            question_metrics[qtype]['success_rate'] = success_rate
            question_metrics[qtype]['avg_similarity'] = avg_sim
            del question_metrics[qtype]['avg_similarity']  # Remove list
        
        summary = {
            'run': self.run_number,
            'model': self.model_name,
            'total_files_tested': total_files,
            'avg_comprehension_preserved': float(avg_comprehension),
            'avg_similarity': float(avg_similarity),
            'total_token_savings': int(total_token_savings),
            'question_type_metrics': question_metrics,
            'pass_threshold': 0.85,
            'status': 'PASS' if avg_comprehension >= 0.85 else 'FAIL'
        }
        
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"  ✓ Summary JSON saved")
        
        # Print to console
        print("\n" + "="*70)
        print("LLM BENCHMARK SUMMARY")
        print("="*70)
        print(f"Run: {self.run_number}")
        print(f"Model: {self.model_name}")
        print(f"Files tested: {total_files}")
        print(f"Avg comprehension: {avg_comprehension*100:.1f}%")
        print(f"Avg similarity: {avg_similarity:.3f}")
        print(f"Total token savings: {total_token_savings:,}")
        print(f"Status: {summary['status']}")
        print("="*70 + "\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Visualize LLM comprehension benchmark results'
    )
    parser.add_argument(
        '--input',
        help='Input JSON file with LLM benchmark results (auto-detects latest if omitted)'
    )
    parser.add_argument(
        '--output-dir',
        default='results/visualizations/llm_comprehension',
        help='Output directory for visualizations'
    )
    
    args = parser.parse_args()
    
    # Auto-detect latest LLM benchmark if not specified
    if args.input:
        input_path = Path(args.input)
    else:
        results_dir = Path('results') / 'llm_comprehension'
        json_files = list(results_dir.glob('run_*.json'))
        if not json_files:
            print("Error: No LLM benchmark results found in results/llm_comprehension/")
            print("Run benchmark first: python3 scripts/llm_benchmark.py testdata/samples")
            return 1
        input_path = max(json_files, key=lambda p: p.stem)
        print(f"Using latest result: {input_path.name}")
    
    output_dir = Path(args.output_dir)
    
    if not input_path.exists():
        print(f"Error: Results file '{input_path}' not found")
        return 1
    
    visualizer = LLMBenchmarkVisualizer(input_path)
    visualizer.generate_all_visualizations(output_dir)
    
    return 0


if __name__ == '__main__':
    exit(main())
