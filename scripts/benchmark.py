#!/usr/bin/env python3
"""
Benchmark engine for MiniMark strategies.
Tests all minification approaches and measures token reduction.
"""

import sys
import time
import csv
from pathlib import Path
from typing import Dict, List
import tiktoken

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from minimark import MiniMarkMinifier
from validator import SemanticValidator


class MiniMarkBenchmark:
    """Benchmark different minification strategies."""
    
    # Define strategy combinations to test
    STRATEGY_CONFIGS = {
        'baseline': [],
        'syntax_only': ['syntax'],
        'syntax_stopwords': ['syntax', 'stopwords'],
        'syntax_stopwords_simplify': ['syntax', 'stopwords', 'simplify'],
        'all_strategies': ['syntax', 'stopwords', 'simplify', 'synonyms'],
    }
    
    def __init__(self, tokenizer_encoding: str = 'cl100k_base'):
        """
        Initialize benchmark engine.
        
        Args:
            tokenizer_encoding: tiktoken encoding (cl100k_base for GPT-4/GPT-3.5-turbo)
        """
        self.minifier = MiniMarkMinifier()
        self.validator = None  # Lazy load (heavy model)
        self.tokenizer = tiktoken.get_encoding(tokenizer_encoding)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken."""
        return len(self.tokenizer.encode(text))
    
    def benchmark_file(
        self, 
        file_path: Path, 
        validate_semantics: bool = True
    ) -> List[Dict]:
        """
        Benchmark all strategies on a single file.
        
        Args:
            file_path: Path to markdown file
            validate_semantics: Whether to compute semantic similarity
            
        Returns:
            List of result dictionaries
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        original_text = file_path.read_text(encoding='utf-8')
        original_tokens = self.count_tokens(original_text)
        
        # Lazy load validator only if needed
        if validate_semantics and self.validator is None:
            self.validator = SemanticValidator()
        
        results = []
        
        for strategy_name, strategies in self.STRATEGY_CONFIGS.items():
            # Time the minification
            start_time = time.perf_counter()
            minified_text = self.minifier.minify(original_text, strategies)
            processing_time_ms = (time.perf_counter() - start_time) * 1000
            
            # Count tokens
            minified_tokens = self.count_tokens(minified_text)
            reduction_pct = ((original_tokens - minified_tokens) / original_tokens * 100) \
                if original_tokens > 0 else 0
            
            # Semantic validation
            similarity = None
            if validate_semantics and strategy_name != 'baseline':
                similarity = self.validator.compute_similarity(
                    original_text, minified_text
                )
            
            results.append({
                'file': file_path.name,
                'strategy': strategy_name,
                'original_tokens': original_tokens,
                'minified_tokens': minified_tokens,
                'reduction_pct': reduction_pct,
                'semantic_similarity': similarity,
                'processing_time_ms': processing_time_ms,
                'original_chars': len(original_text),
                'minified_chars': len(minified_text)
            })
        
        return results
    
    def benchmark_directory(
        self, 
        directory: Path, 
        output_csv: Path,
        validate_semantics: bool = True
    ) -> None:
        """
        Benchmark all markdown files in a directory.
        
        Args:
            directory: Directory containing test markdown files
            output_csv: Path to output CSV file
            validate_semantics: Whether to compute semantic similarity
        """
        md_files = list(directory.glob('*.md'))
        
        if not md_files:
            print(f"No markdown files found in {directory}")
            return
        
        print(f"Found {len(md_files)} markdown files to benchmark")
        print(f"Testing {len(self.STRATEGY_CONFIGS)} strategy configurations")
        print(f"Semantic validation: {'enabled' if validate_semantics else 'disabled'}")
        print()
        
        all_results = []
        
        for i, file_path in enumerate(md_files, 1):
            print(f"[{i}/{len(md_files)}] Benchmarking {file_path.name}...")
            try:
                results = self.benchmark_file(file_path, validate_semantics)
                all_results.extend(results)
            except Exception as e:
                print(f"  Error: {e}")
                continue
        
        # Write results to CSV
        if all_results:
            output_csv.parent.mkdir(parents=True, exist_ok=True)
            
            fieldnames = [
                'file', 'strategy', 'original_tokens', 'minified_tokens',
                'reduction_pct', 'semantic_similarity', 'processing_time_ms',
                'original_chars', 'minified_chars'
            ]
            
            with open(output_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_results)
            
            print(f"\nResults saved to {output_csv}")
            
            # Print summary
            self._print_summary(all_results)
    
    def _print_summary(self, results: List[Dict]) -> None:
        """Print benchmark summary statistics."""
        print("\n" + "="*70)
        print("BENCHMARK SUMMARY")
        print("="*70)
        
        # Group by strategy
        strategies = {}
        for result in results:
            strategy = result['strategy']
            if strategy not in strategies:
                strategies[strategy] = []
            strategies[strategy].append(result)
        
        for strategy_name, strategy_results in strategies.items():
            avg_reduction = sum(r['reduction_pct'] for r in strategy_results) / len(strategy_results)
            avg_similarity = None
            if strategy_results[0]['semantic_similarity'] is not None:
                similarities = [r['semantic_similarity'] for r in strategy_results 
                              if r['semantic_similarity'] is not None]
                if similarities:
                    avg_similarity = sum(similarities) / len(similarities)
            
            print(f"\n{strategy_name}:")
            print(f"  Avg token reduction: {avg_reduction:.1f}%")
            if avg_similarity is not None:
                print(f"  Avg semantic similarity: {avg_similarity:.4f}")
        
        print("\n" + "="*70 + "\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Benchmark MiniMark minification strategies'
    )
    parser.add_argument(
        'input_dir',
        help='Directory containing markdown test files'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='Output CSV file path (default: auto-generated in results/token_reduction/)'
    )
    parser.add_argument(
        '--no-validation',
        action='store_true',
        help='Skip semantic similarity validation (faster)'
    )
    parser.add_argument(
        '--encoding',
        default='cl100k_base',
        help='Tiktoken encoding (default: cl100k_base for GPT-4)'
    )
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    
    # Auto-generate output path if not provided
    if args.output is None:
        results_base = Path('results') / 'token_reduction'
        results_base.mkdir(parents=True, exist_ok=True)
        
        # Get next run number
        existing_runs = [f for f in results_base.glob('run_*')]
        if existing_runs:
            run_numbers = [int(f.stem.split('_')[1]) for f in existing_runs if f.stem.startswith('run_')]
            next_run = max(run_numbers) + 1 if run_numbers else 1
        else:
            next_run = 1
        
        output_path = results_base / f'run_{next_run:03d}_results.csv'
    else:
        output_path = Path(args.output)
    
    if not input_dir.exists():
        print(f"Error: Input directory '{args.input_dir}' not found")
        return 1
    
    if not input_dir.is_dir():
        print(f"Error: '{args.input_dir}' is not a directory")
        return 1
    
    # Run benchmark
    benchmark = MiniMarkBenchmark(tokenizer_encoding=args.encoding)
    benchmark.benchmark_directory(
        input_dir, 
        output_path,
        validate_semantics=not args.no_validation
    )
    
    return 0


if __name__ == '__main__':
    exit(main())
