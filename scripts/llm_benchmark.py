#!/usr/bin/env python3
"""
LLM Comprehension Benchmark for MiniMark.
Tests whether LLMs can understand minified content as well as original markdown.
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from minimark import MiniMarkMinifier

# Load environment variables from .env file if present
try:
    import env_loader
except ImportError:
    pass  # env_loader is optional


class LLMComprehensionBenchmark:
    """
    Benchmark LLM comprehension of original vs minified content.
    Tests understanding through question-answering tasks.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize comprehension benchmark.
        
        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: Model to test (default: gpt-4)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.minifier = MiniMarkMinifier()
        
        # Check if OpenAI is available
        try:
            from openai import OpenAI
            if self.api_key:
                self.client = OpenAI(api_key=self.api_key)
            else:
                self.client = None
        except ImportError:
            print("Warning: openai package not installed. Install with: pip install openai")
            self.client = None
    
    def create_test_questions(self, content: str) -> List[Dict]:
        """
        Generate test questions based on content.
        These should test factual recall and comprehension.
        
        Args:
            content: Original markdown content
            
        Returns:
            List of test questions with expected answer patterns
        """
        # This is a placeholder - in real implementation, questions would be
        # generated automatically or loaded from a test suite
        return [
            {
                "question": "What is the main topic or purpose described in this document?",
                "type": "comprehension"
            },
            {
                "question": "List the key features or main points mentioned.",
                "type": "recall"
            },
            {
                "question": "If there are code examples, what do they demonstrate?",
                "type": "technical"
            },
            {
                "question": "What instructions or steps are provided to the reader?",
                "type": "procedural"
            },
            {
                "question": "What are the key takeaways or conclusions from this document?",
                "type": "synthesis"
            }
        ]
    
    def query_llm(self, context: str, question: str) -> Dict:
        """
        Query LLM with context and question.
        
        Args:
            context: Document content (original or minified)
            question: Question to ask
            
        Returns:
            Dict with answer, tokens used, and response time
        """
        if not self.client:
            # Return mock data for testing without API
            return {
                "answer": "[API not configured - mock response]",
                "tokens_used": 0,
                "response_time_ms": 0,
                "error": "No API key configured"
            }
        
        prompt = f"""Based on the following document, answer the question.

Document:
{context}

Question: {question}

Answer:"""
        
        try:
            start_time = time.perf_counter()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided documents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent answers
                max_tokens=500
            )
            
            response_time = (time.perf_counter() - start_time) * 1000
            
            return {
                "answer": response.choices[0].message.content.strip(),
                "tokens_used": response.usage.total_tokens,
                "response_time_ms": response_time,
                "error": None
            }
            
        except Exception as e:
            return {
                "answer": "",
                "tokens_used": 0,
                "response_time_ms": 0,
                "error": str(e)
            }
    
    def compare_answers(self, answer1: str, answer2: str) -> Dict:
        """
        Compare two answers for similarity.
        Uses LLM to judge if answers convey the same information.
        
        Args:
            answer1: Answer from original content
            answer2: Answer from minified content
            
        Returns:
            Dict with similarity score and analysis
        """
        if not self.client:
            return {
                "similarity_score": 0.0,
                "equivalent": False,
                "analysis": "API not configured"
            }
        
        comparison_prompt = f"""Compare these two answers to the same question. 
Do they convey the same core information and meaning?

Answer 1: {answer1}

Answer 2: {answer2}

Respond in JSON format:
{{
    "equivalent": true/false,
    "similarity_score": 0.0-1.0,
    "analysis": "brief explanation"
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at comparing text for semantic equivalence. Always respond with valid JSON only, no other text."},
                    {"role": "user", "content": comparison_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
                return result
            else:
                return {
                    "similarity_score": 0.0,
                    "equivalent": False,
                    "analysis": "Empty response"
                }
            
        except Exception as e:
            return {
                "similarity_score": 0.0,
                "equivalent": False,
                "analysis": f"Error: {str(e)}"
            }
    
    def benchmark_file(self, file_path: Path, strategies: List[str]) -> Dict:
        """
        Benchmark comprehension on a single file.
        
        Args:
            file_path: Path to markdown file
            strategies: Minification strategies to test
            
        Returns:
            Benchmark results
        """
        print(f"\nBenchmarking: {file_path.name}")
        print(f"Strategies: {', '.join(strategies)}")
        
        # Read and minify content
        original_content = file_path.read_text(encoding='utf-8')
        minified_content = self.minifier.minify(original_content, strategies)
        
        # Generate test questions
        questions = self.create_test_questions(original_content)
        
        results = {
            "file": file_path.name,
            "strategies": strategies,
            "original_length": len(original_content),
            "minified_length": len(minified_content),
            "compression_ratio": len(minified_content) / len(original_content),
            "questions": []
        }
        
        print(f"Testing {len(questions)} questions...")
        
        for i, q in enumerate(questions, 1):
            print(f"  Question {i}/{len(questions)}: {q['type']}")
            
            # Query with original content
            original_response = self.query_llm(original_content, q['question'])
            
            # Query with minified content
            minified_response = self.query_llm(minified_content, q['question'])
            
            # Compare answers
            comparison = self.compare_answers(
                original_response['answer'],
                minified_response['answer']
            )
            
            question_result = {
                "question": q['question'],
                "type": q['type'],
                "original_answer": original_response['answer'],
                "minified_answer": minified_response['answer'],
                "original_tokens": original_response['tokens_used'],
                "minified_tokens": minified_response['tokens_used'],
                "token_savings": original_response['tokens_used'] - minified_response['tokens_used'],
                "equivalent": comparison.get('equivalent', False),
                "similarity_score": comparison.get('similarity_score', 0.0),
                "analysis": comparison.get('analysis', ''),
                "error": original_response.get('error') or minified_response.get('error')
            }
            
            results['questions'].append(question_result)
            
            print(f"    Equivalent: {question_result['equivalent']}, "
                  f"Similarity: {question_result['similarity_score']:.2f}")
        
        # Calculate overall metrics
        valid_questions = [q for q in results['questions'] if not q['error']]
        if valid_questions:
            results['comprehension_preserved'] = sum(q['equivalent'] for q in valid_questions) / len(valid_questions)
            results['avg_similarity'] = sum(q['similarity_score'] for q in valid_questions) / len(valid_questions)
            results['total_token_savings'] = sum(q['token_savings'] for q in valid_questions)
        else:
            results['comprehension_preserved'] = 0.0
            results['avg_similarity'] = 0.0
            results['total_token_savings'] = 0
        
        return results
    
    def benchmark_directory(
        self, 
        directory: Path,
        strategies: List[str],
        output_json: Optional[Path] = None
    ) -> None:
        """
        Benchmark all markdown files in directory.
        
        Args:
            directory: Directory with test files
            strategies: Minification strategies to test
            output_json: Path to output JSON results (auto-generated if None)
        """
        md_files = list(directory.glob('*.md'))
        
        if not md_files:
            print(f"No markdown files found in {directory}")
            return
        
        # Auto-generate output path if not provided
        if output_json is None:
            project_root = Path(__file__).parent.parent
            results_base = project_root / 'results' / 'llm_comprehension'
            results_base.mkdir(parents=True, exist_ok=True)
            
            # Get next run number
            existing_runs = [f for f in results_base.glob('run_*.json')]
            if existing_runs:
                run_numbers = [int(f.stem.split('_')[1]) for f in existing_runs]
                next_run = max(run_numbers) + 1
            else:
                next_run = 1
            
            model_name = self.model.replace('.', '').replace('-', '')
            output_json = results_base / f'run_{next_run:03d}_{model_name}.json'
        
        print(f"="*70)
        print("LLM COMPREHENSION BENCHMARK")
        print(f"="*70)
        print(f"Model: {self.model}")
        print(f"Files: {len(md_files)}")
        print(f"Strategies: {', '.join(strategies)}")
        print(f"="*70)
        
        all_results = []
        
        for file_path in md_files:
            try:
                result = self.benchmark_file(file_path, strategies)
                all_results.append(result)
            except Exception as e:
                print(f"Error benchmarking {file_path.name}: {e}")
                continue
        
        # Save results
        output_json.parent.mkdir(parents=True, exist_ok=True)
        with open(output_json, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\nResults saved to {output_json}")
        
        # Print summary
        self._print_summary(all_results)
    
    def _print_summary(self, results: List[Dict]) -> None:
        """Print summary of comprehension benchmark."""
        print("\n" + "="*70)
        print("COMPREHENSION BENCHMARK SUMMARY")
        print("="*70)
        
        if not results:
            print("No results to summarize")
            return
        
        valid_results = [r for r in results if 'comprehension_preserved' in r]
        
        if not valid_results:
            print("No valid results (API may not be configured)")
            return
        
        avg_comprehension = sum(r['comprehension_preserved'] for r in valid_results) / len(valid_results)
        avg_similarity = sum(r['avg_similarity'] for r in valid_results) / len(valid_results)
        total_token_savings = sum(r['total_token_savings'] for r in valid_results)
        avg_compression = sum(r['compression_ratio'] for r in valid_results) / len(valid_results)
        
        print(f"\nFiles tested: {len(valid_results)}")
        print(f"Average comprehension preserved: {avg_comprehension*100:.1f}%")
        print(f"Average answer similarity: {avg_similarity:.3f}")
        print(f"Total token savings: {total_token_savings}")
        print(f"Average compression ratio: {avg_compression:.3f}")
        
        # Pass/Fail threshold
        threshold = 0.85
        status = "✓ PASS" if avg_comprehension >= threshold else "✗ FAIL"
        print(f"\nStatus (threshold={threshold}): {status}")
        print("="*70 + "\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Benchmark LLM comprehension of minified markdown'
    )
    parser.add_argument(
        'input_dir',
        help='Directory containing test markdown files'
    )
    parser.add_argument(
        '--output',
        default='results/llm_comprehension_benchmark.json',
        help='Output JSON file path'
    )
    parser.add_argument(
        '--strategy',
        nargs='+',
        choices=['syntax', 'stopwords', 'simplify', 'synonyms'],
        default=['syntax', 'stopwords', 'simplify'],
        help='Minification strategies to test (default: syntax stopwords simplify)'
    )
    parser.add_argument(
        '--model',
        default='gpt-4',
        help='OpenAI model to use (default: gpt-4)'
    )
    parser.add_argument(
        '--api-key',
        help='OpenAI API key (or set OPENAI_API_KEY env var)'
    )
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_path = Path(args.output)
    
    if not input_dir.exists():
        print(f"Error: Input directory '{args.input_dir}' not found")
        return 1
    
    # Check for API key
    api_key = args.api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Warning: No OpenAI API key found. Set OPENAI_API_KEY environment variable")
        print("or use --api-key flag. Running in mock mode.")
        print()
    
    # Run benchmark
    benchmark = LLMComprehensionBenchmark(api_key=api_key, model=args.model)
    benchmark.benchmark_directory(input_dir, args.strategy, output_path)
    
    return 0


if __name__ == '__main__':
    exit(main())
