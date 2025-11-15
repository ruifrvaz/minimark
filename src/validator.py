#!/usr/bin/env python3
"""
Semantic validator for MiniMark minification.
Measures semantic similarity between original and minified text.
"""

from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer


class SemanticValidator:
    """Validates semantic preservation after minification."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize validator with embedding model.
        
        Args:
            model_name: HuggingFace model name (default: lightweight all-MiniLM-L6-v2)
        """
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("Model loaded successfully")
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text1: Original text
            text2: Minified text
            
        Returns:
            Similarity score between 0 and 1 (1 = identical meaning)
        """
        # Generate embeddings
        embeddings = self.model.encode([text1, text2])
        
        # Compute cosine similarity
        embedding1 = embeddings[0]
        embedding2 = embeddings[1]
        
        cosine_sim = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )
        
        return float(cosine_sim)
    
    def validate(self, original: str, minified: str, threshold: float = 0.85) -> dict:
        """
        Validate semantic preservation.
        
        Args:
            original: Original text
            minified: Minified text
            threshold: Minimum acceptable similarity (default: 0.85)
            
        Returns:
            Dictionary with similarity score and validation result
        """
        similarity = self.compute_similarity(original, minified)
        
        return {
            'similarity': similarity,
            'passes_threshold': similarity >= threshold,
            'threshold': threshold,
            'degradation_pct': (1 - similarity) * 100
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate semantic similarity between original and minified text'
    )
    parser.add_argument('original', help='Original markdown file')
    parser.add_argument('minified', help='Minified file')
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.85,
        help='Minimum similarity threshold (default: 0.85)'
    )
    parser.add_argument(
        '--model',
        default='all-MiniLM-L6-v2',
        help='Sentence transformer model name'
    )
    
    args = parser.parse_args()
    
    # Read files
    original_path = Path(args.original)
    minified_path = Path(args.minified)
    
    if not original_path.exists():
        print(f"Error: Original file '{args.original}' not found")
        return 1
    
    if not minified_path.exists():
        print(f"Error: Minified file '{args.minified}' not found")
        return 1
    
    original_text = original_path.read_text(encoding='utf-8')
    minified_text = minified_path.read_text(encoding='utf-8')
    
    # Validate
    validator = SemanticValidator(args.model)
    result = validator.validate(original_text, minified_text, args.threshold)
    
    # Display results
    print(f"\n{'='*60}")
    print("SEMANTIC VALIDATION RESULTS")
    print(f"{'='*60}")
    print(f"Original file:    {args.original}")
    print(f"Minified file:    {args.minified}")
    print(f"Similarity score: {result['similarity']:.4f}")
    print(f"Threshold:        {result['threshold']:.2f}")
    print(f"Status:           {'✓ PASS' if result['passes_threshold'] else '✗ FAIL'}")
    print(f"Degradation:      {result['degradation_pct']:.2f}%")
    print(f"{'='*60}\n")
    
    return 0 if result['passes_threshold'] else 1


if __name__ == '__main__':
    exit(main())
