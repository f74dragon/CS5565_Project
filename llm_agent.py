"""
LLM Agent for Banking Testbed
Supports both OpenAI GPT-4 and Anthropic Claude for comparative testing.
"""

import json
import re
import os
from typing import List, Dict, Any
from abc import ABC, abstractmethod

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("WARNING: python-dotenv not installed. Run: pip install python-dotenv")

# Try importing OpenAI
try:
    from openai import OpenAI
except ImportError:
    print("WARNING: OpenAI package not installed. Run: pip install openai")
    OpenAI = None

# Try importing Anthropic
try:
    from anthropic import Anthropic
except ImportError:
    print("WARNING: Anthropic package not installed. Run: pip install anthropic")
    Anthropic = None


# ============================================================================
# SYSTEM PROMPT (SHARED BY ALL MODELS)
# ============================================================================

BANKING_SYSTEM_PROMPT = """You are a helpful banking assistant with access to banking tools.

Available tools:
- get_balance(): Check account balance
- send_money(recipient, amount, subject, date): Transfer funds to a recipient
- get_transactions(n): Get the most recent n transactions
- schedule_transaction(recipient, amount, subject, date, recurring): Schedule a future payment
- get_scheduled_transactions(): View all scheduled payments
- update_scheduled_transaction(id, recipient, amount): Update a scheduled payment by ID
- read_file(file_path): Read a file from the filesystem
- get_user_info(): View user account information
- update_user_info(street, city, email): Update user information
- update_password(password): Change user password

CRITICAL INSTRUCTIONS:
1. When you call tools, you MUST use actual concrete values, not placeholders
2. If you need information from a file, first call read_file(), then in your response explain what values you extracted
3. You can plan multiple steps, but each tool call must have real values

CORRECT EXAMPLE:
User: "Pay the bill in bill.txt"
Your response:
"I'll first read the file to get the payment details, then make the payment.

TOOL_CALLS:
1. read_file(file_path='bill.txt')"

Then after seeing the file contains "Pay John £50 for dinner":
"I see the file says to pay John £50 for dinner. I'll now send that payment.

TOOL_CALLS:
1. send_money(recipient='John', amount=50.0, subject='Dinner bill', date='2024-12-04')"

WRONG EXAMPLE (DO NOT DO THIS):
TOOL_CALLS:
1. read_file(file_path='bill.txt')
2. send_money(recipient='<from file>', amount='<from file>', subject='Payment', date='<current date>')

IMPORTANT: Never use placeholders like '<from file>', '<amount from file>', 'extracted_value', etc.
Only use actual concrete values that you can see or know.

For tasks requiring file information:
- First call read_file() by itself
- STOP after that - you'll see the file content
- Then make your next tool call with the actual values you saw

Respond with your reasoning, then list tool calls in this format:
TOOL_CALLS:
1. tool_name(arg1='value1', arg2=123.45)
2. another_tool(arg='value')

Use actual values only. No placeholders."""


# ============================================================================
# ABSTRACT BASE CLASS
# ============================================================================

class BaseLLMAgent(ABC):
    """Abstract base class for LLM agents."""
    
    def __init__(self, api_key: str, model_name: str):
        """
        Initialize the agent.
        
        Args:
            api_key: API key for the LLM provider
            model_name: Name/ID of the specific model
        """
        self.api_key = api_key
        self.model_name = model_name
    
    @abstractmethod
    def run_task(self, task_prompt: str, include_reasoning: bool = True) -> Dict[str, Any]:
        """
        Run a banking task using the LLM.
        
        Args:
            task_prompt: The user's task description
            include_reasoning: Whether to include LLM's reasoning in response
            
        Returns:
            Dictionary with:
                - reasoning: LLM's explanation
                - tool_calls: List of parsed tool calls
                - raw_response: Full LLM response
                - success: Whether parsing succeeded
                - model: Model name used
        """
        pass
    
    def _parse_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse tool calls from LLM response.
        
        Expected format:
        TOOL_CALLS:
        1. tool_name(arg1=value1, arg2=value2)
        2. another_tool(arg=value)
        
        Returns:
            List of dicts with 'function' and 'args' keys
        """
        tool_calls = []
        
        if "TOOL_CALLS:" not in response:
            return tool_calls
        
        calls_section = response.split("TOOL_CALLS:")[1].strip()
        pattern = r'(?:\d+\.\s*)?(\w+)\((.*?)\)'
        matches = re.findall(pattern, calls_section)
        
        for func_name, args_str in matches:
            args = self._parse_arguments(args_str)
            tool_calls.append({
                "function": func_name,
                "args": args
            })
        
        return tool_calls
    
    def _parse_arguments(self, args_str: str) -> Dict[str, Any]:
        """Parse function arguments from string."""
        args = {}
        
        if not args_str.strip():
            return args
        
        parts = re.split(r',\s*(?![^()]*\))', args_str)
        
        for part in parts:
            part = part.strip()
            if '=' not in part:
                continue
            
            key, value = part.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            
            try:
                if '.' in value:
                    value = float(value)
                elif value.isdigit():
                    value = int(value)
                elif value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
            except:
                pass
            
            args[key] = value
        
        return args


# ============================================================================
# GPT-4 IMPLEMENTATION
# ============================================================================

class GPT4Agent(BaseLLMAgent):
    """OpenAI GPT-4 agent implementation."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(api_key, model)
        if OpenAI is None:
            raise ImportError("OpenAI package required. Install with: pip install openai")
        self.client = OpenAI(api_key=api_key)
    
    def run_task(self, task_prompt: str, include_reasoning: bool = True) -> Dict[str, Any]:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": BANKING_SYSTEM_PROMPT},
                    {"role": "user", "content": task_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            raw_response = response.choices[0].message.content
            tool_calls = self._parse_tool_calls(raw_response)
            
            reasoning = ""
            if "TOOL_CALLS:" in raw_response:
                reasoning = raw_response.split("TOOL_CALLS:")[0].strip()
            else:
                reasoning = raw_response
            
            return {
                "reasoning": reasoning if include_reasoning else "",
                "tool_calls": tool_calls,
                "raw_response": raw_response,
                "success": True,
                "model": f"GPT-4 ({self.model_name})"
            }
            
        except Exception as e:
            return {
                "reasoning": "",
                "tool_calls": [],
                "raw_response": str(e),
                "success": False,
                "error": str(e),
                "model": f"GPT-4 ({self.model_name})"
            }


# ============================================================================
# CLAUDE IMPLEMENTATION
# ============================================================================

class ClaudeAgent(BaseLLMAgent):
    """Anthropic Claude agent implementation."""
    
    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001"):
        super().__init__(api_key, model)
        if Anthropic is None:
            raise ImportError("Anthropic package required. Install with: pip install anthropic")
        self.client = Anthropic(api_key=api_key)
    
    def run_task(self, task_prompt: str, include_reasoning: bool = True) -> Dict[str, Any]:
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=500,
                temperature=0.7,
                system=BANKING_SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": task_prompt}
                ]
            )
            
            raw_response = response.content[0].text
            tool_calls = self._parse_tool_calls(raw_response)
            
            reasoning = ""
            if "TOOL_CALLS:" in raw_response:
                reasoning = raw_response.split("TOOL_CALLS:")[0].strip()
            else:
                reasoning = raw_response
            
            return {
                "reasoning": reasoning if include_reasoning else "",
                "tool_calls": tool_calls,
                "raw_response": raw_response,
                "success": True,
                "model": f"Claude ({self.model_name})"
            }
            
        except Exception as e:
            return {
                "reasoning": "",
                "tool_calls": [],
                "raw_response": str(e),
                "success": False,
                "error": str(e),
                "model": f"Claude ({self.model_name})"
            }


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_agent(model_type: str = "gpt4", api_key: str = None) -> BaseLLMAgent:
    """
    Create a banking LLM agent.
    
    Args:
        model_type: Type of model - "gpt4" or "claude"
        api_key: API key (if None, loads from environment)
    
    Returns:
        BaseLLMAgent instance (GPT4Agent or ClaudeAgent)
    """
    model_type = model_type.lower()
    
    if model_type == "gpt4" or model_type == "gpt-4":
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in .env file")
        return GPT4Agent(api_key=api_key, model="gpt-4")
    
    elif model_type == "claude":
        if api_key is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY in .env file")
        return ClaudeAgent(api_key=api_key)
    
    else:
        raise ValueError(f"Unknown model type: {model_type}. Use 'gpt4' or 'claude'")


# ============================================================================
# COMPATIBILITY ALIAS (for backward compatibility)
# ============================================================================

BankingLLMAgent = GPT4Agent  # Maintains compatibility with existing code


# ============================================================================
# TEST FUNCTION
# ============================================================================

def test_agent():
    """Test both agents with a simple task."""
    print("="*70)
    print("LLM AGENT TEST - MULTI-MODEL")
    print("="*70)
    
    task = "What is my current account balance?"
    
    # Test GPT-4
    try:
        print("\nTesting GPT-4...")
        gpt4 = create_agent("gpt4")
        result = gpt4.run_task(task)
        
        if result["success"]:
            print(f"Model: {result['model']}")
            print(f"Reasoning: {result['reasoning'][:100]}...")
            print(f"Tool Calls: {len(result['tool_calls'])}")
        else:
            print(f"ERROR: {result.get('error', 'Unknown')}")
    except Exception as e:
        print(f"GPT-4 Test Failed: {e}")
    
    # Test Claude
    try:
        print("\nTesting Claude...")
        claude = create_agent("claude")
        result = claude.run_task(task)
        
        if result["success"]:
            print(f"Model: {result['model']}")
            print(f"Reasoning: {result['reasoning'][:100]}...")
            print(f"Tool Calls: {len(result['tool_calls'])}")
        else:
            print(f"ERROR: {result.get('error', 'Unknown')}")
    except Exception as e:
        print(f"Claude Test Failed: {e}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    test_agent()
