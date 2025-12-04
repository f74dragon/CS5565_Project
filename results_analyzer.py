"""
Results Analyzer for IPI Experiments
Analyzes experiment results and generates metrics/reports.
"""

import json
from typing import List, Dict, Any
from collections import defaultdict


# ============================================================================
# ANALYZER CLASS
# ============================================================================

class ResultsAnalyzer:
    """Analyzes IPI experiment results."""
    
    def __init__(self, results: List[Dict[str, Any]]):
        """
        Initialize analyzer with experiment results.
        
        Args:
            results: List of experiment result dictionaries
        """
        self.results = results
        self.metrics = {}
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """
        Calculate comprehensive metrics from results.
        
        Returns:
            Dictionary containing all metrics
        """
        # Separate baseline and attack results
        baseline_results = [r for r in self.results if r.get("is_baseline", False)]
        attack_results = [r for r in self.results if not r.get("is_baseline", False)]
        
        # Check if we have multi-model results
        models_in_results = set(r.get("model", "Unknown") for r in self.results)
        is_multi_model = len(models_in_results) > 1
        
        # Overall metrics
        total_experiments = len(self.results)
        total_attacks = len(attack_results)
        successful_injections = sum(1 for r in attack_results if r.get("injection_successful", False))
        
        # Calculate vulnerability rate
        vulnerability_rate = (successful_injections / total_attacks * 100) if total_attacks > 0 else 0
        
        # Metrics by attack category
        category_metrics = defaultdict(lambda: {"total": 0, "successful": 0})
        for result in attack_results:
            category = result.get("attack_category", "Unknown")
            category_metrics[category]["total"] += 1
            if result.get("injection_successful", False):
                category_metrics[category]["successful"] += 1
        
        # Calculate success rates by category
        category_success_rates = {}
        for category, data in category_metrics.items():
            rate = (data["successful"] / data["total"] * 100) if data["total"] > 0 else 0
            category_success_rates[category] = {
                "total_attacks": data["total"],
                "successful_attacks": data["successful"],
                "success_rate": round(rate, 2)
            }
        
        # Metrics by task type
        task_metrics = defaultdict(lambda: {"total": 0, "successful": 0})
        for result in attack_results:
            task_type = result.get("task_type", "Unknown")
            task_metrics[task_type]["total"] += 1
            if result.get("injection_successful", False):
                task_metrics[task_type]["successful"] += 1
        
        # Calculate success rates by task
        task_success_rates = {}
        for task_type, data in task_metrics.items():
            rate = (data["successful"] / data["total"] * 100) if data["total"] > 0 else 0
            task_success_rates[task_type] = {
                "total_attacks": data["total"],
                "successful_attacks": data["successful"],
                "success_rate": round(rate, 2)
            }
        
        # Baseline performance
        baseline_success_rate = 0
        if baseline_results:
            baseline_passed = sum(1 for r in baseline_results if r.get("task_utility_passed", False))
            baseline_success_rate = (baseline_passed / len(baseline_results) * 100)
        
        # Severity breakdown
        severity_counts = defaultdict(int)
        for result in attack_results:
            if result.get("injection_successful", False):
                severity = result.get("injection_severity", "unknown")
                severity_counts[severity] += 1
        
        # Most effective attacks
        successful_attacks = [r for r in attack_results if r.get("injection_successful", False)]
        attack_ranking = defaultdict(int)
        for result in successful_attacks:
            attack_name = result.get("attack_name", "Unknown")
            attack_ranking[attack_name] += 1
        
        # Sort by effectiveness
        most_effective = sorted(attack_ranking.items(), key=lambda x: x[1], reverse=True)
        
        # Model comparison (if multi-model)
        model_comparison = {}
        if is_multi_model:
            for model_name in models_in_results:
                model_attacks = [r for r in attack_results if r.get("model", "") == model_name]
                if model_attacks:
                    model_vulns = sum(1 for r in model_attacks if r.get("injection_successful", False))
                    model_comparison[model_name] = {
                        "total_attacks": len(model_attacks),
                        "successful_attacks": model_vulns,
                        "vulnerability_rate": round((model_vulns / len(model_attacks) * 100), 2) if model_attacks else 0
                    }
        
        # Compile all metrics
        self.metrics = {
            "summary": {
                "total_experiments": total_experiments,
                "baseline_tests": len(baseline_results),
                "attack_tests": total_attacks,
                "successful_injections": successful_injections,
                "overall_vulnerability_rate": round(vulnerability_rate, 2),
                "baseline_success_rate": round(baseline_success_rate, 2),
                "is_multi_model": is_multi_model,
                "models_tested": list(models_in_results) if is_multi_model else []
            },
            "by_category": category_success_rates,
            "by_task": task_success_rates,
            "severity_breakdown": dict(severity_counts),
            "most_effective_attacks": most_effective[:5],  # Top 5
            "model_comparison": model_comparison if is_multi_model else {},
            "detailed_results": {
                "baseline": baseline_results,
                "attacks": attack_results
            }
        }
        
        return self.metrics
    
    def print_summary(self):
        """Print a formatted summary of results."""
        if not self.metrics:
            self.calculate_metrics()
        
        print("\n" + "="*70)
        print("IPI VULNERABILITY ANALYSIS - RESULTS SUMMARY")
        print("="*70)
        
        # Overall Summary
        summary = self.metrics["summary"]
        print("\nOVERALL SUMMARY")
        print("-" * 70)
        print(f"Total Experiments:          {summary['total_experiments']}")
        print(f"  - Baseline Tests:         {summary['baseline_tests']}")
        print(f"  - Attack Tests:           {summary['attack_tests']}")
        print(f"\nSuccessful Injections:      {summary['successful_injections']}/{summary['attack_tests']}")
        print(f"Overall Vulnerability Rate: {summary['overall_vulnerability_rate']}%")
        print(f"Baseline Success Rate:      {summary['baseline_success_rate']}%")
        
        # By Category
        print("\nVULNERABILITY BY ATTACK CATEGORY")
        print("-" * 70)
        for category, data in self.metrics["by_category"].items():
            print(f"\n{category}:")
            print(f"  Success Rate:  {data['success_rate']}%")
            print(f"  Attacks:       {data['successful_attacks']}/{data['total_attacks']}")
        
        # By Task Type
        print("\nVULNERABILITY BY TASK TYPE")
        print("-" * 70)
        for task_type, data in self.metrics["by_task"].items():
            print(f"\n{task_type.capitalize()}:")
            print(f"  Success Rate:  {data['success_rate']}%")
            print(f"  Attacks:       {data['successful_attacks']}/{data['total_attacks']}")
        
        # Severity
        if self.metrics["severity_breakdown"]:
            print("\nSEVERITY BREAKDOWN")
            print("-" * 70)
            for severity, count in self.metrics["severity_breakdown"].items():
                print(f"  {severity.upper()}: {count}")
        
        # Most Effective Attacks
        print("\nMOST EFFECTIVE ATTACKS")
        print("-" * 70)
        for i, (attack_name, count) in enumerate(self.metrics["most_effective_attacks"], 1):
            print(f"  {i}. {attack_name} ({count} successful)")
        
        # Model Comparison (if multi-model)
        if self.metrics.get("model_comparison"):
            print("\nMODEL COMPARISON")
            print("-" * 70)
            for model_name, data in self.metrics["model_comparison"].items():
                print(f"\n{model_name}:")
                print(f"  Vulnerability Rate: {data['vulnerability_rate']}%")
                print(f"  Successful Attacks: {data['successful_attacks']}/{data['total_attacks']}")
        
        print("\n" + "="*70)
    
    def print_detailed_results(self):
        """Print detailed results for each experiment."""
        print("\n" + "="*70)
        print("DETAILED EXPERIMENT RESULTS")
        print("="*70)
        
        attack_results = self.metrics.get("detailed_results", {}).get("attacks", [])
        
        for i, result in enumerate(attack_results, 1):
            print(f"\n--- Experiment {i} ---")
            print(f"Task:        {result.get('task', 'Unknown')}")
            print(f"Attack:      {result.get('attack_name', 'Unknown')}")
            print(f"Category:    {result.get('attack_category', 'Unknown')}")
            print(f"Vulnerable:  {'YES - WARNING' if result.get('injection_successful') else 'NO - SAFE'}")
            
            if result.get("injection_successful"):
                print(f"Severity:    {result.get('injection_severity', 'unknown').upper()}")
                print(f"Indicators:  {', '.join(result.get('injection_indicators', []))}")
            
            print(f"Tool Calls:  {len(result.get('tool_calls', []))}")
            for tool_call in result.get('tool_calls', []):
                print(f"  - {tool_call.get('function')}({tool_call.get('args', {})})")
    
    def generate_paper_summary(self) -> str:
        """
        Generate a concise summary suitable for research paper.
        
        Returns:
            Formatted string with key findings
        """
        if not self.metrics:
            self.calculate_metrics()
        
        summary = self.metrics["summary"]
        
        paper_text = f"""
EXPERIMENTAL RESULTS SUMMARY
============================

We conducted {summary['total_experiments']} experiments testing GPT-4's vulnerability 
to Indirect Prompt Injection (IPI) attacks in a simulated banking environment.

Overall Findings:
- Vulnerability Rate: {summary['overall_vulnerability_rate']}% 
  ({summary['successful_injections']}/{summary['attack_tests']} attacks succeeded)
- Baseline Performance: {summary['baseline_success_rate']}% 
  (model correctly handled benign inputs)

Attack Effectiveness by Category:
"""
        
        for category, data in self.metrics["by_category"].items():
            paper_text += f"- {category}: {data['success_rate']}% success rate\n"
        
        paper_text += f"\nMost Effective Attack Techniques:\n"
        for i, (attack_name, count) in enumerate(self.metrics["most_effective_attacks"][:3], 1):
            paper_text += f"{i}. {attack_name}\n"
        
        return paper_text
    
    def save_report(self, filename: str = "analysis_report.txt"):
        """Save analysis report to file."""
        with open(filename, 'w') as f:
            # Write summary
            f.write("="*70 + "\n")
            f.write("IPI VULNERABILITY ANALYSIS - FULL REPORT\n")
            f.write("="*70 + "\n\n")
            
            # Write metrics as JSON
            f.write(json.dumps(self.metrics, indent=2))
            
            # Write paper summary
            f.write("\n\n")
            f.write(self.generate_paper_summary())
        
        print(f"Full report saved to: {filename}")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def analyze_results(results_file: str = "experiment_results.json"):
    """
    Load and analyze experiment results.
    
    Args:
        results_file: Path to JSON file with experiment results
    """
    print("\nLoading experiment results...")
    
    try:
        with open(results_file, 'r') as f:
            results = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Results file '{results_file}' not found.")
        print("   Run experiments first: python3 run_all_experiments.py")
        return
    
    print(f"Loaded {len(results)} experiment results\n")
    
    # Create analyzer
    analyzer = ResultsAnalyzer(results)
    
    # Calculate metrics
    analyzer.calculate_metrics()
    
    # Print summary
    analyzer.print_summary()
    
    # Save report
    analyzer.save_report()
    
    return analyzer


if __name__ == "__main__":
    analyze_results()
