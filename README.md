# MiniMark - Markdown Minifier for LLM Contexts

MiniMark is a Python-based markdown minification tool designed to optimize documents for LLM context windows by reducing token count while preserving semantic meaning. It is 

## Features

- **Multiple Minification Strategies**: Syntax stripping, stopword removal, sentence simplification, and synonym replacement
- **Token-Based Benchmarking**: Measures token reduction using tiktoken (OpenAI tokenizer)
- **Semantic Validation**: Uses sentence transformers to ensure meaning preservation
- **Comprehensive Analytics**: Visualizations and statistics for strategy comparison

## Project Structure

```
minimark/
│
├── README.md                          # Original project manifesto
├── README_IMPLEMENTATION.md           # Full implementation documentation
├── QUICKSTART.md                      # Quick start guide
├── IMPLEMENTATION_COMPLETE.md         # Phase 1 completion summary
├── requirements.txt                   # Python dependencies
├── .gitignore                        # Git ignore rules
│
├── src/                              # Source code
│   ├── minimark.py                   # Core minifier (4 strategies)
│   └── validator.py                  # Semantic similarity validator
│
├── scripts/                          # Automation scripts
│   ├── benchmark.py                  # Benchmark engine
│   ├── run_benchmarks.sh            # Orchestration script (executable)
│   ├── llm_benchmark.py              # LLM comprehension testing
│   └── visualize.py                  # Results visualization
│
├── testdata/                         # Test corpus
│   └── samples/                      # Sample markdown files
│       ├── technical_doc.md          # Technical documentation
│       ├── api_documentation.md      # API reference
│       ├── readme_example.md         # README sample
│       └── llm_prompt_guide.md       # Prompt engineering guide
│
├── docs/                             # Additional documentation
│   └── LLM_BENCHMARK.md              # LLM comprehension testing guide
│
├── results/                          # Benchmark outputs (generated)
│   ├── benchmark_results.csv         # Raw benchmark data
│   ├── token_reduction.png           # Strategy comparison chart
│   ├── similarity_tradeoff.png       # Semantic vs reduction analysis
│   ├── processing_time.png           # Performance comparison
│   ├── per_file_analysis.png         # Per-document breakdown
│   └── summary.json                  # Statistical summary
│
├── output/                           # Minified files (generated, gitignored)
│   └── *.mm                          # MiniMark output files
│
└── venv/                             # Python virtual environment (gitignored)
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd minimark
```

2. Create virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Basic Minification

Minify a single markdown file:

```bash
python3 src/minimark.py input.md output.mm --strategy all
# Output will be saved to output/output.mm
```

Strategy options:
- `none` - No minification (baseline)
- `syntax` - Strip markdown formatting only
- `stopwords` - Remove common stopwords
- `simplify` - Remove filler phrases
- `synonyms` - Replace with shorter synonyms
- `all` - Apply all strategies (default)

### Semantic Validation

Check semantic similarity between original and minified:

```bash
python3 src/validator.py original.md minified.mm --threshold 0.85
```

### Run Full Benchmark Suite

Test all strategies on all sample files:

```bash
./scripts/run_benchmarks.sh
```

Options:
- `--no-validation` - Skip semantic similarity computation (faster)
- `--output <path>` - Custom output CSV path

### Visualize Results

Generate charts and summary statistics:

```bash
python3 scripts/visualize.py
```

Outputs:
- `results/token_reduction.png` - Token reduction by strategy
- `results/similarity_tradeoff.png` - Semantic preservation vs reduction
- `results/processing_time.png` - Performance comparison
- `results/per_file_analysis.png` - Per-file breakdown
- `results/summary.json` - Statistical summary

## Minification Strategies

### 1. Syntax Stripping
Removes markdown formatting characters while preserving content:
- Bold: `**text**` → `text`
- Headers: `## Header` → `Header`
- Code blocks: ` ```code``` ` → `code`
- Links: `[text](url)` → `text`

### 2. Stopword Removal
Eliminates common words with minimal semantic value:
- Articles: the, a, an
- Common verbs: is, are, was, were
- LLM-specific: please, thank you, kindly

### 3. Sentence Simplification
Removes filler phrases and unnecessary modifiers:
- Filler phrases: "in my opinion", "I think", "basically"
- Adverbs: very, really, quite, honestly

### 4. Synonym Replacement
Replaces longer words with shorter alternatives using WordNet:
- Preserves technical terms and code references
- Only replaces when synonym is meaningfully shorter

## Benchmark Metrics

The benchmark suite measures:

- **Token Count**: Using tiktoken with cl100k_base encoding (GPT-4/GPT-3.5)
- **Reduction Percentage**: Token savings compared to original
- **Semantic Similarity**: Cosine similarity of sentence embeddings (0-1 scale)
- **Processing Time**: Milliseconds per minification operation
- **Character Count**: For additional context on size reduction
- **LLM Comprehension**: Whether LLMs understand minified content equivalently (requires OpenAI API)

## Phase 1 Goals

This implementation represents Phase 1 - rule-based minification with validation:

✅ Deterministic, fast minification strategies  
✅ Comprehensive token-based benchmarking  
✅ Embedding-based semantic validation  
✅ Multi-strategy comparison framework  
✅ Test corpus with diverse document types  

## Phase 2 Roadmap

Future enhancements to explore:

- **Model-Based Minification**: LLM-powered compression (GPT-4, Claude, Llama)
- **Go Implementation**: Portable single-binary executable
- **Custom Tokenizers**: Support for different model families
- **Bidirectional Conversion**: Expand .mm back to readable markdown
- **Configuration Profiles**: Preset optimization levels for different use cases

## Contributing

This is an experimental research project. Contributions welcome!

## License

MIT License - See LICENSE file for details

## Acknowledgments

Built with:
- [NLTK](https://www.nltk.org/) - Natural language processing
- [sentence-transformers](https://www.sbert.net/) - Semantic embeddings
- [tiktoken](https://github.com/openai/tiktoken) - OpenAI tokenizer
- [matplotlib](https://matplotlib.org/) - Visualization
