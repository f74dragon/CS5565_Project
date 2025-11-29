from banking_suite import BankingEnvironment, ALL_TASKS, TOOLS


def simulate_tool_execution(env: BankingEnvironment, tool_name: str, **kwargs):
    """
    Simulate calling a tool from the TOOLS list.
    
    Args:
        env: The banking environment
        tool_name: Name of the tool to call
        **kwargs: Arguments to pass to the tool
    
    Returns:
        Tool output as string
    """
    # Find the tool function
    tool_func = None
    for tool in TOOLS:
        if tool.__name__ == tool_name:
            tool_func = tool
            break
    
    if not tool_func:
        return f"Error: Tool '{tool_name}' not found"
    
    # Call the tool with environment and arguments
    try:
        result = tool_func(env, **kwargs)
        return result
    except TypeError as e:
        return f"Error calling {tool_name}: {e}"


def test_task_1():
    """Test Task 1: Check account balance."""
    print("\n" + "="*60)
    print("Testing Task 1: Check Account Balance")
    print("="*60)
    
    env = BankingEnvironment()
    task = ALL_TASKS[0]  # UserTask1
    
    print(f"Prompt: {task.PROMPT}")
    print(f"Expected calls: {task.ground_truth_calls()}")
    
    # Simulate what the LLM should do
    result = simulate_tool_execution(env, "get_balance")
    print(f"\nTool Output: {result}")
    
    # Check if task passes
    success = task.utility(result, BankingEnvironment(), env)
    print(f"Task Success: {success}")
    
    return success


def test_task_2():
    """Test Task 2: Pay a bill from file."""
    print("\n" + "="*60)
    print("Testing Task 2: Pay Bill from File")
    print("="*60)
    
    env = BankingEnvironment()
    task = ALL_TASKS[1]  # UserTask2
    
    print(f"Prompt: {task.PROMPT}")
    print(f"Expected calls: {task.ground_truth_calls()}")
    
    # Simulate what the LLM should do
    print("\nStep 1: Read the bill file")
    file_content = simulate_tool_execution(env, "read_file", file_path="bill-december-2023.txt")
    print(f"File Content: {file_content}")
    
    print("\nStep 2: Send payment")
    payment_result = simulate_tool_execution(
        env, 
        "send_money",
        recipient="Car Rental Company",
        amount=98.70,
        subject="Car Rental Payment",
        date="2023-12-15"
    )
    print(f"Payment Result: {payment_result}")
    
    # Check if task passes
    model_output = f"{file_content}\n{payment_result}"
    success = task.utility(model_output, BankingEnvironment(), env)
    print(f"\nTask Success: {success}")
    
    return success


def test_task_3():
    """Test Task 3: Update rent based on landlord notice."""
    print("\n" + "="*60)
    print("Testing Task 3: Update Rent Payment")
    print("="*60)
    
    env = BankingEnvironment()
    task = ALL_TASKS[2]  # UserTask3
    
    print(f"Prompt: {task.PROMPT}")
    print(f"Expected calls: {task.ground_truth_calls()}")
    
    # Simulate what the LLM should do
    print("\nStep 1: Read landlord notice")
    notice = simulate_tool_execution(env, "read_file", file_path="landlord-notices.txt")
    print(f"Notice: {notice}")
    
    print("\nStep 2: Check scheduled transactions")
    scheduled = simulate_tool_execution(env, "get_scheduled_transactions")
    print(f"Scheduled: {scheduled}")
    
    print("\nStep 3: Update rent to £1200")
    update_result = simulate_tool_execution(
        env,
        "update_scheduled_transaction",
        id=7,
        amount=1200.00
    )
    print(f"Update Result: {update_result}")
    
    # Check if task passes
    model_output = f"{notice}\n{scheduled}\n{update_result}"
    success = task.utility(model_output, BankingEnvironment(), env)
    print(f"\nTask Success: {success}")
    
    return success


def main():
    """Run all test examples."""
    print("="*60)
    print("Banking MCP Testbed - Example Tests")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Task 1", test_task_1()))
    results.append(("Task 2", test_task_2()))
    results.append(("Task 3", test_task_3()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for task_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{task_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    print(f"\nTotal: {passed}/{total} tests passed")


if __name__ == "__main__":
    main()
