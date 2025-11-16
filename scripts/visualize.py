#!/usr/bin/env python3
"""
Visualization and analysis tool for MiniMark benchmark results.
Generates charts and summary statistics.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np

# Use non-interactive backend for headless environments
matplotlib.use('Agg')


class BenchmarkVisualizer:
    """Visualize and analyze benchmark results."""
    
    def __init__(self, csv_path: Path):
        """
        Initialize visualizer with benchmark results.
        
        Args:
            csv_path: Path to benchmark results CSV
        """
    def __init__(self, csv_path: Path):
        """
        Initialize visualizer with benchmark results.
        
        Args:
            csv_path: Path to benchmark results CSV
        """
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path)
        
        # Extract run number from filename (e.g., run_003_results.csv)
        self.run_number = csv_path.stem.split('_')[1] if '_' in csv_path.stem else '001'
        
    def generate_all_visualizations(self, output_dir: Path) -> None:
        """Generate all visualizations and save to output directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Generating visualizations for run {self.run_number}...")
        
        # 1. Token reduction comparison
        self.plot_token_reduction(output_dir / f'run_{self.run_number}_token_reduction.png')
        
        # 2. Semantic similarity vs reduction trade-off
        self.plot_similarity_tradeoff(output_dir / f'run_{self.run_number}_similarity_tradeoff.png')
        
        # 3. Processing time comparison
        self.plot_processing_time(output_dir / f'run_{self.run_number}_processing_time.png')
        
        # 4. Per-file breakdown
        self.plot_per_file_analysis(output_dir / f'run_{self.run_number}_per_file_analysis.png')
        
        # 5. Generate summary JSON
        self.generate_summary_json(output_dir / f'run_{self.run_number}_summary.json')
        
        print(f"All visualizations saved to {output_dir}")
    
    def plot_token_reduction(self, output_path: Path) -> None:
        """Plot average token reduction by strategy."""
        # Group by strategy and calculate averages
        strategy_avg = self.df.groupby('strategy')['reduction_pct'].mean().sort_values()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(strategy_avg.index, strategy_avg.values, color='steelblue')
        
        # Add value labels on bars
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2, 
                   f'{width:.1f}%', ha='left', va='center', fontsize=10)
        
        ax.set_xlabel('Average Token Reduction (%)', fontsize=12)
        ax.set_ylabel('Strategy', fontsize=12)
        ax.set_title('Token Reduction by Minification Strategy', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Token reduction chart saved")
    
    def plot_similarity_tradeoff(self, output_path: Path) -> None:
        """Plot semantic similarity vs token reduction trade-off."""
        # Filter out baseline and rows without similarity scores
        df_filtered = self.df[
            (self.df['strategy'] != 'baseline') & 
            (self.df['semantic_similarity'].notna())
        ]
        
        if df_filtered.empty:
            print("  ⚠ Skipping similarity trade-off plot (no semantic data)")
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        strategies = df_filtered['strategy'].unique()
        colors = plt.cm.Set2(np.linspace(0, 1, len(strategies)))
        
        for strategy, color in zip(strategies, colors):
            strategy_data = df_filtered[df_filtered['strategy'] == strategy]
            ax.scatter(
                strategy_data['reduction_pct'],
                strategy_data['semantic_similarity'],
                label=strategy,
                alpha=0.7,
                s=100,
                color=color
            )
        
        ax.set_xlabel('Token Reduction (%)', fontsize=12)
        ax.set_ylabel('Semantic Similarity', fontsize=12)
        ax.set_title('Semantic Preservation vs Token Reduction Trade-off', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc='lower left', fontsize=10)
        ax.grid(alpha=0.3)
        
        # Add reference line at 0.85 similarity threshold
        ax.axhline(y=0.85, color='red', linestyle='--', alpha=0.5, 
                  label='Threshold (0.85)')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Similarity trade-off chart saved")
    
    def plot_processing_time(self, output_path: Path) -> None:
        """Plot average processing time by strategy."""
        strategy_time = self.df.groupby('strategy')['processing_time_ms'].mean().sort_values()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(strategy_time.index, strategy_time.values, color='coral')
        
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2,
                   f'{width:.1f}ms', ha='left', va='center', fontsize=10)
        
        ax.set_xlabel('Average Processing Time (ms)', fontsize=12)
        ax.set_ylabel('Strategy', fontsize=12)
        ax.set_title('Processing Time by Strategy', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Processing time chart saved")
    
    def plot_per_file_analysis(self, output_path: Path) -> None:
        """Plot token reduction for each file across strategies."""
        # Get unique files
        files = self.df['file'].unique()
        strategies = self.df['strategy'].unique()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(files))
        width = 0.15
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(strategies)))
        
        for i, (strategy, color) in enumerate(zip(strategies, colors)):
            strategy_data = self.df[self.df['strategy'] == strategy]
            reductions = [
                strategy_data[strategy_data['file'] == f]['reduction_pct'].values[0]
                if not strategy_data[strategy_data['file'] == f].empty else 0
                for f in files
            ]
            ax.bar(x + i * width, reductions, width, label=strategy, color=color)
        
        ax.set_xlabel('Test File', fontsize=12)
        ax.set_ylabel('Token Reduction (%)', fontsize=12)
        ax.set_title('Token Reduction by File and Strategy', fontsize=14, fontweight='bold')
        ax.set_xticks(x + width * (len(strategies) - 1) / 2)
        ax.set_xticklabels([f.replace('.md', '') for f in files], rotation=45, ha='right')
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Per-file analysis chart saved")
    
    def generate_summary_json(self, output_path: Path) -> None:
        """Generate summary statistics as JSON."""
        summary = {
            'total_files_tested': len(self.df['file'].unique()),
            'total_strategies_tested': len(self.df['strategy'].unique()),
            'strategies': {}
        }
        
        for strategy in self.df['strategy'].unique():
            strategy_data = self.df[self.df['strategy'] == strategy]
            
            strategy_summary = {
                'avg_token_reduction_pct': float(strategy_data['reduction_pct'].mean()),
                'min_token_reduction_pct': float(strategy_data['reduction_pct'].min()),
                'max_token_reduction_pct': float(strategy_data['reduction_pct'].max()),
                'avg_processing_time_ms': float(strategy_data['processing_time_ms'].mean()),
            }
            
            # Add semantic similarity if available
            if strategy_data['semantic_similarity'].notna().any():
                strategy_summary['avg_semantic_similarity'] = float(
                    strategy_data['semantic_similarity'].mean()
                )
                strategy_summary['min_semantic_similarity'] = float(
                    strategy_data['semantic_similarity'].min()
                )
            
            summary['strategies'][strategy] = strategy_summary
        
        # Find best strategy (highest reduction with acceptable similarity)
        best_strategy = None
        best_score = 0
        
        for strategy, data in summary['strategies'].items():
            if strategy == 'baseline':
                continue
            
            # Score = reduction * similarity (if available)
            similarity = data.get('avg_semantic_similarity', 1.0)
            reduction = data['avg_token_reduction_pct']
            score = reduction * similarity
            
            if score > best_score:
                best_score = score
                best_strategy = strategy
        
        summary['recommendation'] = {
            'best_strategy': best_strategy,
            'reason': 'Highest token reduction with acceptable semantic preservation'
        }
        
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"  ✓ Summary JSON saved")
        
        # Print summary to console
        print("\n" + "="*70)
        print("BENCHMARK SUMMARY")
        print("="*70)
        print(f"Files tested: {summary['total_files_tested']}")
        print(f"Strategies tested: {summary['total_strategies_tested']}")
        print(f"\nRecommended strategy: {best_strategy}")
        print("="*70 + "\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Visualize MiniMark token reduction benchmark results'
    )
    parser.add_argument(
        '--input',
        help='Input CSV file with benchmark results (auto-detects latest if omitted)'
    )
    parser.add_argument(
        '--output-dir',
        default='results/visualizations/token_reduction',
        help='Output directory for visualizations'
    )
    
    args = parser.parse_args()
    
    # Auto-detect latest token reduction benchmark if not specified
    if args.input:
        input_path = Path(args.input)
    else:
        results_dir = Path('results') / 'token_reduction'
        csv_files = list(results_dir.glob('run_*_results.csv'))
        if not csv_files:
            print("Error: No token reduction benchmark results found")
            print("Run benchmark first: python3 scripts/benchmark.py testdata/samples")
            return 1
        input_path = max(csv_files, key=lambda p: p.stem)
        print(f"Using latest result: {input_path.name}")
    
    output_dir = Path(args.output_dir)
    
    if not input_path.exists():
        print(f"Error: Results file '{args.input}' not found")
        print("Run benchmarks first: ./scripts/run_benchmarks.sh")
        return 1
    
    visualizer = BenchmarkVisualizer(input_path)
    visualizer.generate_all_visualizations(output_dir)
    
    return 0


if __name__ == '__main__':
    exit(main())
