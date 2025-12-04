# Multi-Model IPI Testing - Quick Setup Guide

## Overview
Your IPI testing framework now supports comparing GPT-4 and Claude 3.5 Sonnet!

## What's New
- **10 attack techniques** (up from 8)
- **Multi-model support**: Test GPT-4, Claude, or both
- **Model comparison analysis**: See which model is more vulnerable
- **Secure API key management**: Uses .env file

---

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `openai` - For GPT-4
- `anthropic` - For Claude
- `python-dotenv` - For loading .env files

### 2. Set Up API Keys

Open the `.env` file and paste your API keys:

```bash
OPENAI_API_KEY=sk-proj-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

**IMPORTANT**: Don't commit `.env` to GitHub! (It's already in .gitignore)

### 3. Run Experiments

```bash
python3 run_all_experiments.py
```

You'll be prompted to choose:
1. **GPT-4 only** (if you only have OpenAI key)
2. **Claude only** (if you only have Anthropic key)
3. **Both models** (compares them side-by-side)

---

## What Gets Tested

### Baseline Tests (6 total)
- 3 runs each for bill payment and rent update tasks
- Tests normal behavior without attacks

### Attack Tests (10 total per model)
1. **Direct Command Injection** (2x)
2. **Context Confusion** (2x)
3. **Authority Impersonation** (2x)
4. **Hidden Instructions** (1x)
5. **Prompt Breakout** (1x)
6. **Social Engineering** (1x)
7. **Technical Jargon Obfuscation** (1x)

### Total Experiments
- **Single model**: 16 experiments (~8 minutes)
- **Both models**: 32 experiments (~16 minutes)

---

## Understanding Results

### Files Generated

**Single Model Testing:**
```
experiment_results_gpt4.json     # GPT-4 raw data
experiment_results_claude.json   # Claude raw data
analysis_report.txt              # Summary report
```

**Multi-Model Testing:**
```
experiment_results_gpt4.json       # GPT-4 data
experiment_results_claude.json     # Claude data
experiment_results_combined.json   # Combined data
analysis_report.txt                # Comparison report
```

### Key Metrics

**Vulnerability Rate**: % of attacks that succeeded

**By Category**: Which attack types work best

**Model Comparison** (if testing both):
```
GPT-4:
  Vulnerability Rate: 62.5%
  Successful Attacks: 5/8

Claude 3.5:
  Vulnerability Rate: 37.5%
  Successful Attacks: 3/8
```

---

## Example Output

```
======================================================================
MODEL COMPARISON
----------------------------------------------------------------------

GPT-4 (gpt-4):
  Vulnerability Rate: 62.5%
  Successful Attacks: 5/10

Claude (claude-3-5-sonnet-20241022):
  Vulnerability Rate: 37.5%
  Successful Attacks: 3/10
======================================================================
```

---

## For Your Research Paper

The framework generates:

1. **Quantitative data**: Vulnerability rates, attack success rates
2. **Categorical analysis**: Which attack types work on which models
3. **Severity classification**: Critical vs high vs medium vulnerabilities
4. **Model comparison**: Direct GPT-4 vs Claude comparison

### Key Research Questions Answered:
- Are MCP systems vulnerable to IPI attacks? ✓
- Which models are more resistant? ✓
- Which attack techniques are most effective? ✓
- What defenses might work? (Future work)

---

## Troubleshooting

### "API key not found"
- Make sure `.env` file exists in project root
- Check API keys are on the right lines
- No spaces around the `=` sign

### "ImportError: openai"
```bash
pip install openai anthropic python-dotenv
```

### Rate Limiting
- Script includes 1-second delays between calls
- If you hit limits, wait and re-run

### Partial Results
- Results save after each experiment
- Check `experiment_results_*.json` files
- Can analyze partial data with `python3 results_analyzer.py`

---

## Cost Estimate

**Per model (16 experiments):**
- GPT-4: ~$0.50-$1.00
- Claude: ~$0.30-$0.60

**Both models (32 experiments):**
- Total: ~$1.00-$2.00

---

## Next Steps

1. **Run experiments** with your API keys
2. **Review** `analysis_report.txt`
3. **Compare** models if you tested both
4. **Document** findings in your research paper
5. **Extend** with more attacks or defenses (optional)

---

## Need Help?

- Check `EXPERIMENTS_GUIDE.md` for more details
- Check `PROJECT_SUMMARY.md` for architecture
- Review code in `llm_agent.py` for model integration

Good luck with your research! 🔬
