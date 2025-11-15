#!/usr/bin/env python3
"""
MiniMark - Markdown Minifier for LLM Contexts
Rule-based strategies for optimizing markdown documents.
"""

import re
import argparse
from pathlib import Path
from typing import Set
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize, sent_tokenize

# Download required NLTK data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)


class MiniMarkMinifier:
    """MiniMark minification engine with multiple strategies."""
    
    def __init__(self):
        self.stopwords = set(stopwords.words('english'))
        # Add common filler words for LLM contexts
        self.stopwords.update([
            'please', 'thank', 'thanks', 'kindly', 'could', 'would',
            'maybe', 'perhaps', 'possibly', 'probably'
        ])
        
        # Filler phrases to remove
        self.filler_patterns = [
            r'\b(in order to|in my opinion|I think|I believe|it seems|as you know)\b',
            r'\b(basically|actually|literally|honestly|frankly)\b',
            r'\b(very|really|quite|rather|somewhat|fairly)\b',
        ]
        
        # Technical terms to preserve (never replace with synonyms)
        self.preserve_terms = {
            'api', 'cli', 'json', 'xml', 'html', 'css', 'sql', 'http', 'https',
            'git', 'github', 'docker', 'kubernetes', 'python', 'javascript',
            'markdown', 'minimark', 'function', 'class', 'method', 'variable'
        }
    
    def strip_markdown_syntax(self, text: str) -> str:
        """Remove markdown formatting characters while preserving content."""
        # Remove bold/italic markers
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold**
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic*
        text = re.sub(r'__([^_]+)__', r'\1', text)      # __bold__
        text = re.sub(r'_([^_]+)_', r'\1', text)        # _italic_
        
        # Remove headers but keep text
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Remove code block markers but keep code
        text = re.sub(r'```[\w]*\n', '', text)
        text = re.sub(r'```', '', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Remove links but keep text [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove list markers
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Remove horizontal rules
        text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)
        
        # Clean up extra whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def remove_stopwords(self, text: str) -> str:
        """Remove stopwords while preserving sentence structure."""
        sentences = sent_tokenize(text)
        cleaned_sentences = []
        
        for sentence in sentences:
            words = word_tokenize(sentence)
            # Keep first word even if stopword (maintains sentence structure)
            filtered_words = [words[0]] if words else []
            
            for word in words[1:]:
                if word.lower() not in self.stopwords or word.isalnum() is False:
                    filtered_words.append(word)
            
            if filtered_words:
                cleaned_sentences.append(' '.join(filtered_words))
        
        return ' '.join(cleaned_sentences)
    
    def simplify_sentences(self, text: str) -> str:
        """Remove filler phrases and unnecessary adverbs."""
        for pattern in self.filler_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove multiple spaces created by removals
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([.,!?])', r'\1', text)
        
        return text.strip()
    
    def replace_synonyms(self, text: str) -> str:
        """Replace longer words with shorter synonyms where appropriate."""
        words = word_tokenize(text)
        replaced_words = []
        
        for word in words:
            # Skip if word should be preserved or is short enough
            if word.lower() in self.preserve_terms or len(word) <= 4:
                replaced_words.append(word)
                continue
            
            # Try to find shorter synonym
            synsets = wordnet.synsets(word)
            if synsets:
                # Get all lemmas from first synset
                lemmas = synsets[0].lemmas()
                # Find shortest synonym that's not the same word
                synonyms = [l.name().replace('_', ' ') for l in lemmas 
                           if l.name().lower() != word.lower()]
                if synonyms:
                    shortest = min(synonyms, key=len)
                    if len(shortest) < len(word):
                        replaced_words.append(shortest)
                        continue
            
            replaced_words.append(word)
        
        return ' '.join(replaced_words)
    
    def minify(self, text: str, strategies: list[str]) -> str:
        """Apply selected minification strategies in order."""
        result = text
        
        if 'syntax' in strategies:
            result = self.strip_markdown_syntax(result)
        
        if 'stopwords' in strategies:
            result = self.remove_stopwords(result)
        
        if 'simplify' in strategies:
            result = self.simplify_sentences(result)
        
        if 'synonyms' in strategies:
            result = self.replace_synonyms(result)
        
        return result


def main():
    parser = argparse.ArgumentParser(
        description='MiniMark - Minify markdown for optimal LLM context usage'
    )
    parser.add_argument('input', help='Input markdown file path')
    parser.add_argument('output', help='Output minimark file path')
    parser.add_argument(
        '--strategy',
        choices=['none', 'syntax', 'stopwords', 'simplify', 'synonyms', 'all'],
        nargs='+',
        default=['all'],
        help='Minification strategies to apply'
    )
    
    args = parser.parse_args()
    
    # Read input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found")
        return 1
    
    text = input_path.read_text(encoding='utf-8')
    
    # Determine strategies
    strategies = args.strategy
    if 'all' in strategies:
        strategies = ['syntax', 'stopwords', 'simplify', 'synonyms']
    elif 'none' in strategies:
        strategies = []
    
    # Apply minification
    minifier = MiniMarkMinifier()
    minified = minifier.minify(text, strategies)
    
    # Write output
    output_path = Path(args.output)
    # If output path is relative, place it in output/minified/ directory
    if not output_path.is_absolute():
        output_dir = Path(__file__).parent.parent / 'output' / 'minified'
        output_path = output_dir / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(minified, encoding='utf-8')
    
    print(f"Minified {input_path} -> {output_path}")
    print(f"Strategies: {', '.join(strategies) if strategies else 'none'}")
    print(f"Original size: {len(text)} chars")
    print(f"Minified size: {len(minified)} chars")
    print(f"Reduction: {((len(text) - len(minified)) / len(text) * 100):.1f}%")
    
    return 0


if __name__ == '__main__':
    exit(main())
