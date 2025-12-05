# PBJRAG Examples

This directory contains example codebases for testing PBJRAG's code quality assessment.

## 📁 Sample Project

The `sample_project/` directory contains a simple calculator application with varying code quality levels to demonstrate PBJRAG's blessing tier system.

### Files

- **calculator.py** - Well-documented Calculator class with proper type hints, logging, and error handling (expects high blessing tier)
- **utils.py** - Mixed quality utility functions demonstrating various quality levels
- **main.py** - Main application with decent structure but some areas for improvement

### Code Quality Highlights

The sample project intentionally includes:

✅ **Good Practices:**
- Type hints and documentation (calculator.py)
- Proper error handling with custom exceptions
- Logging and history tracking
- Clear function signatures

⚠️ **Areas for Improvement:**
- Missing type hints in some functions (utils.py, main.py)
- Incomplete documentation
- Unused functions (utils.old_function)
- Missing error handling (utils.quick_calc division by zero)

## 🧪 Testing PBJRAG

### Quick Test

```bash
# From the navi-pbjrag root directory
./quickstart.sh
```

Then in the WebUI:
1. Enter the path: `examples/sample_project`
2. Click "Analyze Codebase"
3. View the blessing tier results

### Expected Results

You should see different blessing tiers for each file:

- **calculator.py**: 🏆 Platinum or 🥇 Gold (high quality)
- **utils.py**: 🥈 Silver or 🥉 Bronze (mixed quality)
- **main.py**: 🥈 Silver (decent quality)

### Command Line Test

```bash
# Analyze the sample project
pbjrag examples/sample_project --output examples/analysis_output

# View the results
cat examples/analysis_output/summary.json
```

## 📊 Understanding Results

PBJRAG will generate:

1. **Blessing Tiers** - Quality grades from Platinum to Stone
2. **Quality Metrics** - Detailed scores for:
   - Documentation completeness
   - Type hint coverage
   - Complexity metrics
   - Error handling
   - Code organization

3. **Visualization** - Interactive charts showing:
   - Quality distribution across files
   - Module-level metrics
   - Improvement suggestions

## 🎯 Creating Your Own Examples

To create additional example projects:

1. Create a new directory under `examples/`
2. Add Python files with varying quality levels
3. Run PBJRAG to analyze
4. Compare results with expected quality

### Example Structure

```
examples/
  your_project/
    ├── module1.py      # High quality code
    ├── module2.py      # Medium quality code
    ├── legacy.py       # Low quality code
    └── README.md       # Project description
```

## 🔧 Customizing Analysis

You can customize PBJRAG analysis with configuration files:

```python
# examples/config.yaml
blessing_tiers:
  platinum: {min_score: 90}
  gold: {min_score: 80}
  silver: {min_score: 70}
  bronze: {min_score: 60}
```

## 📚 More Examples

For more examples and use cases, visit:
- Documentation: `docs/`
- Test fixtures: `tests/fixtures/`
- Real-world examples: [GitHub Wiki](https://github.com/yourusername/navi-pbjrag/wiki)

## 🤝 Contributing Examples

Have an interesting example to share? Contributions welcome!

1. Create your example project
2. Add a README explaining the quality patterns
3. Submit a pull request

Examples should demonstrate:
- Real-world code patterns
- Variety of quality levels
- Clear learning objectives
- Reproducible results
