#!/bin/bash
# MiniMark Benchmark Runner
# Orchestrates the complete benchmarking pipeline

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TESTDATA_DIR="$PROJECT_ROOT/testdata/samples"
RESULTS_DIR="$PROJECT_ROOT/results"
BENCHMARK_SCRIPT="$SCRIPT_DIR/benchmark.py"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}MiniMark Benchmark Pipeline${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 not found${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv "$PROJECT_ROOT/venv"
    echo -e "${GREEN}Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$PROJECT_ROOT/venv/bin/activate"

# Install dependencies if needed
echo -e "${YELLOW}Checking dependencies...${NC}"
pip install -q -r "$PROJECT_ROOT/requirements.txt"
echo -e "${GREEN}Dependencies ready${NC}"
echo ""

# Check if test data exists
if [ ! -d "$TESTDATA_DIR" ] || [ -z "$(ls -A $TESTDATA_DIR/*.md 2>/dev/null)" ]; then
    echo -e "${RED}Error: No markdown test files found in $TESTDATA_DIR${NC}"
    exit 1
fi

FILE_COUNT=$(ls -1 "$TESTDATA_DIR"/*.md 2>/dev/null | wc -l)
echo -e "${GREEN}Found $FILE_COUNT test file(s)${NC}"
echo ""

# Parse command line arguments
SKIP_VALIDATION=false
OUTPUT_FILE="$RESULTS_DIR/benchmark_results.csv"

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-validation)
            SKIP_VALIDATION=true
            shift
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Run benchmark
echo -e "${YELLOW}Running benchmark...${NC}"
echo ""

if [ "$SKIP_VALIDATION" = true ]; then
    python3 "$BENCHMARK_SCRIPT" "$TESTDATA_DIR" --output "$OUTPUT_FILE" --no-validation
else
    python3 "$BENCHMARK_SCRIPT" "$TESTDATA_DIR" --output "$OUTPUT_FILE"
fi

BENCHMARK_STATUS=$?

echo ""
if [ $BENCHMARK_STATUS -eq 0 ]; then
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}Benchmark completed successfully!${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo -e "Results saved to: ${YELLOW}$OUTPUT_FILE${NC}"
    
    # Show quick summary
    if [ -f "$OUTPUT_FILE" ]; then
        echo ""
        echo -e "${GREEN}Quick Summary:${NC}"
        echo "Total benchmark runs: $(tail -n +2 "$OUTPUT_FILE" | wc -l)"
        echo ""
        
        # Calculate average reduction
        AVG_REDUCTION=$(tail -n +2 "$OUTPUT_FILE" | awk -F',' '{sum+=$5; count++} END {if(count>0) print sum/count; else print 0}')
        echo "Average token reduction: ${AVG_REDUCTION}%"
    fi
else
    echo -e "${RED}Benchmark failed with status $BENCHMARK_STATUS${NC}"
    exit $BENCHMARK_STATUS
fi

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review results: cat $OUTPUT_FILE"
echo "  2. Visualize data: python3 scripts/visualize.py"
echo "  3. Test individual files: python3 src/minimark.py <input> <output>"
echo ""

deactivate
