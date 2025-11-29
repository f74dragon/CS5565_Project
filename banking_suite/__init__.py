"""
Banking MCP Testbed
A simple implementation for testing prompt injection vulnerabilities in MCP systems.
"""

from banking_suite.task_suite import (
    BankingEnvironment,
    BankAccount,
    UserAccount,
    Filesystem,
    Transaction,
    ScheduledTransaction,
    TOOLS,
    get_balance,
    send_money,
    get_transactions,
    schedule_transaction,
    get_scheduled_transactions,
    update_scheduled_transaction,
    read_file,
    get_user_info,
    update_user_info,
    update_password,
)

from banking_suite.user_tasks import (
    ALL_TASKS,
    run_task,
    UserTask1,
    UserTask2,
    UserTask3,
    UserTask4,
    UserTask5,
    UserTask6,
)

__version__ = "0.1.0"

__all__ = [
    # Environment classes
    "BankingEnvironment",
    "BankAccount",
    "UserAccount",
    "Filesystem",
    "Transaction",
    "ScheduledTransaction",
    
    # Tools
    "TOOLS",
    "get_balance",
    "send_money",
    "get_transactions",
    "schedule_transaction",
    "get_scheduled_transactions",
    "update_scheduled_transaction",
    "read_file",
    "get_user_info",
    "update_user_info",
    "update_password",
    
    # Tasks
    "ALL_TASKS",
    "run_task",
    "UserTask1",
    "UserTask2",
    "UserTask3",
    "UserTask4",
    "UserTask5",
    "UserTask6",
]
