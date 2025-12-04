# IPI Experiments Guide

Complete guide to running Indirect Prompt Injection vulnerability tests.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install openai
```

That's it! Only one dependency needed.

### 2. Run Experiments

```bash
cd /Users/arian/Documents/CS5565_Project
python3 run_all_experiments.py
```

You'll be prompted for your OpenAI API key.

### 3. View Results

Results are automatically saved to:
- `experiment_results.json` - Raw data
- `analysis_report.txt` - Summary report

## 📋 What Gets Tested

### Baseline Tests (6 tests)
- Task 2 (Bill Payment) - 3 runs with benign content
- Task 3 (Rent Update) - 3 runs with benign content

**Purpose:** Establish that GPT-4 works correctly with legitimate inputs.

### Attack Tests (8 tests)

**Bill Payment Attacks (5):**
1. Direct Command Injection
2. Context Confusion
3. Authority Impersonation
4. Hidden Instructions (HTML Comment)
5. Prompt Breakout

**Rent Update Attacks (3):**
1. Direct Command Injection (Rent)
2. Authority Impersonation (Rent)
3. Context Confusion (Rent)

**Total: 14 experiments**

## 📊 Understanding Results

### Metrics You'll Get

1. **Overall Vulnerability Rate** - What % of attacks succeeded
2. **By Attack Category** - Which techniques work best
3. **By Task Type** - Which tasks are most vulnerable
4. **Severity Breakdown** - How dangerous successful attacks were
5. **Most Effective Attacks** - Rankings by success rate

### Example Output

```
IPI VULNERABILITY ANALYSIS - RESULTS SUMMARY
======================================================================

📊 OVERALL SUMMARY
----------------------------------------------------------------------
Total Experiments:          14
  - Baseline Tests:         6
  - Attack Tests:           8

Successful Injections:      5/8
Overall Vulnerability Rate: 62.5%
Baseline Success Rate:      100.0%

🎯 VULNERABILITY BY ATTACK CATEGORY
----------------------------------------------------------------------

Direct:
  Success Rate:  66.7%
  Attacks:       2/3

Authority:
  Success Rate:  100.0%
  Attacks:       2/2

...
```

## 🔬 What Each File Does

| File | Purpose |
|------|---------|
| `injection_payloads.py` | Defines 8 attack techniques |
| `llm_agent.py` | Wraps OpenAI GPT-4 API |
| `experiment_runner.py` | Executes experiments, detects injections |
| `results_analyzer.py` | Calculates metrics, generates reports |
| `run_all_experiments.py` | **Main entry point - run this!** |

## 💰 Cost & Time

- **Cost:** ~$0.50-$1.00 (GPT-4 API calls)
- **Time:** 10-15 minutes (with rate limiting)
- **Experiments:** 14 total

## 📝 For Your Paper

After running, you'll have:

### Quantitative Results
- Exact vulnerability percentage
- Attack category effectiveness rates
- Task-specific vulnerability rates

### Qualitative Results
- Which attacks work best (and why)
- Which tasks are most vulnerable
- Severity of successful attacks

### Example Paper Text

From `analysis_report.txt`, you'll get a section like:

```
We conducted 14 experiments testing GPT-4's vulnerability 
to Indirect Prompt Injection (IPI) attacks in a simulated 
banking environment.

Overall Findings:
- Vulnerability Rate: 62.5% (5/8 attacks succeeded)
- Baseline Performance: 100.0% (model correctly handled benign inputs)

Attack Effectiveness by Category:
- Direct: 66.7% success rate
- Authority: 100.0% success rate
- Confusion: 50.0% success rate
...
```

## 🛠️ Customization

### Add More Attacks

Edit `injection_payloads.py`:

```python
new_attack = AttackPayload(
    name="Your Attack Name",
    category="YourCategory",
    description="What this attack does",
    content="Malicious file content here..."
)

BILL_ATTACKS.append(new_attack)
```

### Test Different Models

Edit line in `llm_agent.py`:

```python
# Change from gpt-4 to gpt-3.5-turbo for comparison
self.model = model  # default is "gpt-4"
```

### Adjust Number of Baseline Runs

Edit `experiment_runner.py`:

```python
baseline_results = runner.run_baseline_tests(num_runs=5)  # Change from 3
```

## 🔍 Troubleshooting

### "OpenAI package not found"
```bash
pip install openai
```

### "API key invalid"
- Check your OpenAI API key
- Make sure you have credits in your account
- Visit: https://platform.openai.com/account/api-keys

### "Rate limit exceeded"
- The script has 1-second delays built in
- If still hitting limits, increase delay in `experiment_runner.py`

### Results look wrong
1. Check `experiment_results.json` for raw data
2. Look at LLM reasoning in each experiment
3. Verify file content was properly injected

## 📈 Next Steps

After getting results:

1. **Analyze Patterns**
   - Which injection techniques worked?
   - Why did some fail?
   - Are there commonalities?

2. **Compare to Literature**
   - How do your results compare to [1], [2], [3]?
   - Are GPT-4's vulnerabilities similar to other models?

3. **Try Defenses** (Optional)
   - Add input sanitization
   - Test prompt filtering
   - Compare before/after rates

4. **Write Findings**
   - Use metrics from `analysis_report.txt`
   - Include example attacks
   - Discuss implications

## 🎯 Expected Outcomes

Based on similar research, you should see:

- **High vulnerability** to authority impersonation (60-100%)
- **Medium vulnerability** to direct commands (40-70%)
- **Lower vulnerability** to hidden instructions (20-50%)
- **Task-dependent** results (some tasks more vulnerable)

## 📚 References

[1] Radosevich & Halloran - MCP Safety Audit (2025)
[2] Hou et al. - MCP Security Threats (2025)
[3] Yang et al. - Survey of AI Agent Protocols (2025)

## ✅ Completion Checklist

Before running:
- [ ] Installed OpenAI package
- [ ] Have API key ready
- [ ] Have ~$1 in OpenAI credits

After running:
- [ ] Review `analysis_report.txt`
- [ ] Check `experiment_results.json`
- [ ] Note vulnerability percentage
- [ ] Identify most effective attacks
- [ ] Document findings for paper

## 🎓 Using Results in Your Paper

### Methods Section
"We created a banking simulation testbed with 10 tools and 2 vulnerable tasks. We tested 8 different IPI attack techniques against GPT-4, measuring success rate and severity."

### Results Section
"Our experiments revealed a X% overall vulnerability rate. Authority impersonation attacks were most effective (Y%), while hidden instruction attacks were least effective (Z%)."

### Discussion
"These findings suggest that current LLMs remain vulnerable to IPI attacks, particularly when malicious instructions are framed as authoritative or urgent."

## 🚨 Important Notes

- Results will vary between runs (LLM is non-deterministic)
- Run multiple times for statistical significance
- GPT-4 is updated regularly - results may change over time
- This is a simplified testbed - real systems have more complexity

## 📧 Support

Having issues? Check:
1. All files are in the same directory
2. Python 3.7+ is installed
3. OpenAI package is installed
4. API key is valid

---

**Good luck with your research! 🚀**
