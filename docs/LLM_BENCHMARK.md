# LLM Comprehension Benchmark

This benchmark tests whether LLMs can understand and extract the same information from minified MiniMark content as they can from original markdown.

## How It Works

1. **Question Generation**: Creates comprehension questions based on document content
2. **Dual Testing**: Asks the same questions with both original and minified content
3. **Answer Comparison**: Uses LLM to judge if answers convey equivalent information
4. **Metrics**: Tracks comprehension preservation, similarity scores, and token savings

## Setup

### Install OpenAI Package

```bash
pip install openai
```

### Set API Key (Recommended: Use .env file)

**Option 1: Using .env file (secure)**
```bash
# Copy example file
cp .env.example .env

# Edit and add your key
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env

# Key is automatically loaded!
```

**Option 2: Environment variable**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

Or pass directly:
```bash
python3 scripts/llm_benchmark.py testdata/samples --api-key your-key
```

## Usage

### Basic Comprehension Test

```bash
python3 scripts/llm_benchmark.py testdata/samples
```

### With Custom Strategy

```bash
python3 scripts/llm_benchmark.py testdata/samples \
  --strategy syntax stopwords simplify \
  --model gpt-4 \
  --output results/comprehension_test.json
```

### Test Different Models

```bash
# GPT-4 (most accurate)
python3 scripts/llm_benchmark.py testdata/samples --model gpt-4

# GPT-3.5-turbo (faster, cheaper)
python3 scripts/llm_benchmark.py testdata/samples --model gpt-3.5-turbo

# GPT-4-turbo
python3 scripts/llm_benchmark.py testdata/samples --model gpt-4-turbo-preview
```

## Output Format

The benchmark generates a JSON file with detailed results:

```json
{
  "file": "technical_doc.md",
  "strategies": ["syntax", "stopwords", "simplify"],
  "comprehension_preserved": 0.95,
  "avg_similarity": 0.92,
  "total_token_savings": 245,
  "questions": [
    {
      "question": "What is the main topic?",
      "type": "comprehension",
      "original_answer": "...",
      "minified_answer": "...",
      "equivalent": true,
      "similarity_score": 0.94,
      "token_savings": 42
    }
  ]
}
```

## Metrics Explained

- **comprehension_preserved**: Percentage of questions where answers are equivalent (0-1)
- **avg_similarity**: Average semantic similarity of answer pairs (0-1)
- **token_savings**: Total input tokens saved by using minified content
- **equivalent**: Boolean - do the answers convey the same core information?

## Success Criteria

- **Comprehension Preserved ≥ 85%**: Minified content maintains understanding
- **Avg Similarity ≥ 0.80**: Answers are semantically similar
- **Token Savings > 0**: Minification actually reduces token usage

## Question Types

The benchmark tests different aspects of comprehension:

1. **Comprehension**: Main topic/purpose understanding
2. **Recall**: Ability to list key points
3. **Technical**: Understanding of code examples
4. **Procedural**: Following instructions/steps

## Cost Estimates

Approximate costs per test file (with GPT-4):

- Questions per file: 4
- Queries per file: 8 (original + minified × 4 questions)
- Comparison calls: 4
- Total API calls: 12 per file
- Estimated cost: $0.10-0.30 per file

For 4 test files: ~$0.40-1.20 per full benchmark run

Use `gpt-3.5-turbo` for cheaper testing (~10x less expensive).

## Example Results

```
==================================================================
LLM COMPREHENSION BENCHMARK
==================================================================
Model: gpt-4
Files: 4
Strategies: syntax, stopwords, simplify
==================================================================

Benchmarking: technical_doc.md
Strategies: syntax, stopwords, simplify
Testing 4 questions...
  Question 1/4: comprehension
    Equivalent: True, Similarity: 0.94
  Question 2/4: recall
    Equivalent: True, Similarity: 0.89
  Question 3/4: technical
    Equivalent: True, Similarity: 0.96
  Question 4/4: procedural
    Equivalent: False, Similarity: 0.78

Results saved to results/llm_comprehension_benchmark.json

==================================================================
COMPREHENSION BENCHMARK SUMMARY
==================================================================

Files tested: 4
Average comprehension preserved: 92.5%
Average answer similarity: 0.895
Total token savings: 890
Average compression ratio: 0.682

Status (threshold=0.85): ✓ PASS
==================================================================
```

## Integration with Pipeline

Add to your benchmark workflow:

```bash
# Run token benchmark
./scripts/run_benchmarks.sh

# Run comprehension benchmark
python3 scripts/llm_benchmark.py testdata/samples

# Visualize all results
python3 scripts/visualize.py
```

## Limitations

1. **API Dependent**: Requires OpenAI API access and credits
2. **Question Quality**: Auto-generated questions may not cover all aspects
3. **Subjective Equivalence**: LLM judges answer similarity (not perfect)
4. **Cost**: Each benchmark run costs money
5. **Latency**: Takes time due to multiple API calls

## Future Enhancements

- [ ] Support for other LLM providers (Anthropic, local models)
- [ ] Human-validated question sets per document type
- [ ] Multi-model comparison (test across different LLMs)
- [ ] Caching to reduce repeat API calls
- [ ] Batch processing for cost optimization
