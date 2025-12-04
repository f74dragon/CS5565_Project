#!/usr/bin/env python3
"""
Main Entry Point for IPI Vulnerability Testing
Run this script to execute all experiments and generate results.
Supports multi-model testing (GPT-4 and Claude).
"""

import sys
import os
import json
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("WARNING: python-dotenv not installed. Make sure .env file is loaded.")

from experiment_runner import ExperimentRunner
from llm_agent import create_agent
from results_analyzer import analyze_results


def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("IPI VULNERABILITY TESTING FRAMEWORK - MULTI-MODEL EDITION")
    print("Security Analysis of Model Context Protocol Systems")
    print("="*70)
    
    # Check for required packages
    missing_packages = []
    try:
        import openai
    except ImportError:
        missing_packages.append("openai")
    
    try:
        import anthropic
    except ImportError:
        missing_packages.append("anthropic")
    
    if missing_packages:
        print("\nWARNING: Some packages are missing:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\nInstall with: pip install openai anthropic python-dotenv")
        print("You can still proceed if you have API keys in .env file")
    
    # Check for API keys in environment
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    print("\n" + "="*70)
    print("API KEY STATUS")
    print("="*70)
    print(f"OpenAI API Key:    {'Found in .env' if openai_key else 'NOT FOUND'}")
    print(f"Anthropic API Key: {'Found in .env' if anthropic_key else 'NOT FOUND'}")
    
    if not openai_key and not anthropic_key:
        print("\nERROR: No API keys found!")
        print("\n   1. Create a .env file in this directory")
        print("   2. Add your API keys:")
        print("      OPENAI_API_KEY=your-key-here")
        print("      ANTHROPIC_API_KEY=your-key-here")
        print("   3. Run this script again")
        return
    
    # Model selection
    print("\n" + "="*70)
    print("MODEL SELECTION")
    print("="*70)
    print("\nWhich model(s) would you like to test?")
    
    available_models = []
    if openai_key:
        print("   1. GPT-4 (OpenAI)")
        available_models.append(("gpt4", "GPT-4"))
    if anthropic_key:
        print(f"   2. Claude 3.5 Sonnet (Anthropic)")
        available_models.append(("claude", "Claude 3.5"))
    if openai_key and anthropic_key:
        print("   3. Both (Comparison)")
    
    print("\nEnter choice (1, 2, or 3): ", end="")
    choice = input().strip()
    
    models_to_test = []
    if choice == "1" and openai_key:
        models_to_test = [("gpt4", "GPT-4")]
    elif choice == "2" and anthropic_key:
        models_to_test = [("claude", "Claude 3.5")]
    elif choice == "3" and openai_key and anthropic_key:
        models_to_test = [("gpt4", "GPT-4"), ("claude", "Claude 3.5")]
    else:
        print("\nInvalid choice or API key not available.")
        return
    
    # Confirm start
    num_experiments = 16  # 6 baseline (3 per task x 2 tasks) + 10 attacks
    total_experiments = num_experiments * len(models_to_test)
    
    print("\n" + "="*70)
    print("EXPERIMENT DETAILS")
    print("="*70)
    print(f"Models to test:      {len(models_to_test)}")
    for model_id, model_name in models_to_test:
        print(f"   - {model_name}")
    print(f"Experiments per model: {num_experiments}")
    print(f"Total experiments:     {total_experiments}")
    print(f"Estimated time:        {total_experiments * 30 // 60} minutes")
    
    if len(models_to_test) > 1:
        print("\nNOTE: Running multiple models will generate comparison analysis!")
    
    print("\n   Continue? (y/n): ", end="")
    confirm = input().strip().lower()
    if confirm not in ['y', 'yes']:
        print("\nCancelled by user.")
        return
    
    # Run experiments for each model
    all_results = []
    
    for model_id, model_name in models_to_test:
        print("\n" + "="*70)
        print(f"TESTING {model_name.upper()}")
        print("="*70)
        
        try:
            # Create agent for this model
            print(f"\nInitializing {model_name} agent...")
            agent = create_agent(model_id)
            
            # Create runner
            runner = ExperimentRunner(agent)
            
            # Run baseline tests
            baseline_results = runner.run_baseline_tests(num_runs=3)
            runner.results.extend(baseline_results)
            
            # Run attack tests
            attack_results = runner.run_attack_tests()
            runner.results.extend(attack_results)
            
            # Save model-specific results
            model_filename = f"experiment_results_{model_id}.json"
            runner.save_results(filename=model_filename)
            
            # Add to combined results
            all_results.extend(runner.results)
            
        except Exception as e:
            print(f"\nERROR testing {model_name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Save combined results
    if len(models_to_test) > 1:
        print("\n" + "="*70)
        print("SAVING COMBINED RESULTS")
        print("="*70)
        
        combined_filename = "experiment_results_combined.json"
        with open(combined_filename, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"Combined results saved to: {combined_filename}")
    
    # Analyze results
    print("\n" + "="*70)
    print("ANALYZING RESULTS")
    print("="*70)
    
    try:
        if len(models_to_test) > 1:
            # Analyze combined results for comparison
            analyzer = analyze_results("experiment_results_combined.json")
        else:
            # Analyze single model results
            model_id, model_name = models_to_test[0]
            analyzer = analyze_results(f"experiment_results_{model_id}.json")
        
        print("\n" + "="*70)
        print("ALL EXPERIMENTS COMPLETE!")
        print("="*70)
        
        print("\nFiles generated:")
        if len(models_to_test) == 1:
            model_id, model_name = models_to_test[0]
            print(f"   - experiment_results_{model_id}.json  (raw data)")
        else:
            for model_id, model_name in models_to_test:
                print(f"   - experiment_results_{model_id}.json ({model_name} data)")
            print(f"   - experiment_results_combined.json (all models)")
        print("   - analysis_report.txt (summary report)")
        
        print("\nNext steps:")
        print("   1. Review analysis_report.txt for key findings")
        if len(models_to_test) > 1:
            print("   2. Compare vulnerability rates between models")
            print("   3. Identify which attacks work on which models")
        print("   4. Use findings in your research paper")
        
    except Exception as e:
        print(f"\nERROR during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nWARNING: Interrupted by user. Partial results may be saved.")
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
