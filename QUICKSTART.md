# MiniMark Quick Start Guide

## Installation & Setup

1. **Install dependencies**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Download NLTK data** (automatic on first run):
The minifier will automatically download required NLTK corpora (stopwords, punkt, wordnet) on first execution.

## Quick Commands

### Test Basic Minification
```bash
# Minify with all strategies (output saved to output/output.mm)
python3 src/minimark.py testdata/samples/technical_doc.md output.mm --strategy all

# Minify with specific strategies
python3 src/minimark.py testdata/samples/readme_example.md output.mm --strategy syntax stopwords

# No minification (baseline)
python3 src/minimark.py README.md baseline.mm --strategy none
```

### Validate Semantic Preservation
```bash
python3 src/validator.py testdata/samples/technical_doc.md output/output.mm
```

### Run Complete Benchmark
```bash
# Full benchmark with semantic validation
./scripts/run_benchmarks.sh

# Fast benchmark without validation
./scripts/run_benchmarks.sh --no-validation
```

### Generate Visualizations
```bash
python3 scripts/visualize.py
# View results in results/ directory
```

### Test LLM Comprehension (Optional - Requires OpenAI API)
```bash
# Setup (one time): Copy .env.example to .env and add your API key
# Edit .env and add: OPENAI_API_KEY=sk-your-key-here

# Run comprehension test (key loaded automatically from .env)
python3 scripts/llm_benchmark.py testdata/samples

# See docs/LLM_BENCHMARK.md for details
```

## Understanding Output

### Minifier Output
```
Minified technical_doc.md -> output/output.mm
Strategies: syntax, stopwords, simplify, synonyms
Original size: 1250 chars
Minified size: 890 chars
Reduction: 28.8%
```

### Validator Output
```
SEMANTIC VALIDATION RESULTS
Original file:    technical_doc.md
Minified file:    output.mm
Similarity score: 0.9124
Threshold:        0.85
Status:           ✓ PASS
Degradation:      8.76%
```

### Benchmark Results
CSV columns:
- `file`: Test file name
- `strategy`: Minification strategy used
- `original_tokens`: Token count before minification
- `minified_tokens`: Token count after minification
- `reduction_pct`: Percentage of tokens saved
- `semantic_similarity`: Embedding similarity score (0-1)
- `processing_time_ms`: Time taken in milliseconds

## Troubleshooting

### Import Errors
If you see `Import "nltk" could not be resolved`, activate the virtual environment:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### First Run Downloads
NLTK will download required data on first run. This is normal and happens once.

### Semantic Validation Slow
The sentence-transformer model (~80MB) downloads on first use. Subsequent runs are fast. Use `--no-validation` flag to skip.

### OpenAI API Key
For LLM comprehension benchmarking, you need an OpenAI API key. Without it, the benchmark runs in mock mode (no actual testing).

## Next Steps

1. Add your own test documents to `testdata/samples/`
2. Run benchmarks to compare strategies
3. Review visualizations in `results/`
4. Choose optimal strategy based on your use case
5. (Optional) Run LLM comprehension tests with API key
6. Integrate into your workflow

## Strategy Selection Guide

| Use Case | Recommended Strategy | Why |
|----------|---------------------|-----|
| Technical docs | `syntax stopwords` | Preserves terminology, removes formatting |
| General content | `all_strategies` | Maximum compression |
| Code documentation | `syntax_only` | Keeps technical terms intact |
| LLM prompts | `syntax stopwords simplify` | Balance of compression & clarity |

Experiment with different strategies and measure results!

## Benchmark Types

### 1. Token Reduction Benchmark
Measures how much minification reduces token count:
```bash
./scripts/run_benchmarks.sh
```

### 2. Semantic Similarity Benchmark  
Validates that meaning is preserved using embeddings:
```bash
python3 scripts/benchmark.py testdata/samples
```

### 3. LLM Comprehension Benchmark
Tests if LLMs understand minified content (requires API):
```bash
export OPENAI_API_KEY='your-key'
python3 scripts/llm_benchmark.py testdata/samples
```

Each benchmark serves a different validation purpose!
