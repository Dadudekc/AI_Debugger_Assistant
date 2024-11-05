# File Path: C:\Projects\AI_Debugger_Assistant\ai_agent_project\src\example_usage.py

import logging
import asyncio
from AgentDispatcher import AgentDispatcher

# Configure logging for the example
logger = logging.getLogger("ExampleUsage")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

async def main():
    # Initialize the AgentDispatcher with adjusted agent directory path
    dispatcher = AgentDispatcher(
        agents_directory=r"C:\Projects\AI_Debugger_Assistant\ai_agent_project\src\agents\core",
        model_name="mistral:latest",
        ollama_url="http://localhost:11434",
    )

    # Define a sample task
    sample_task = "Develop a machine learning pipeline for predicting housing prices."

    # Dispatch the task using chain-of-thought reasoning
    result = await dispatcher.dispatch_task(
        task=sample_task,
        agent_name="aiwithmemory",  # Ensure the agent name matches the loaded agents
        priority=1,
        use_chain_of_thought=True
    )

    if result:
        print("Final Result:", result)
    else:
        # Optionally, execute queued tasks
        await dispatcher.execute_tasks()
        print("Tasks have been dispatched to the queue.")

    # Shutdown the dispatcher gracefully
    dispatcher.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
