import logging
from ai_agent_utils import PerformanceMonitor, MemoryManager, ToolServer, Shell, PythonNotebook
from agent_actor import AgentActor
from AgentDispatcher import AgentDispatcher

logger = logging.getLogger(__name__)

def main():
    # Setup logging configuration
    logging.basicConfig(level=logging.DEBUG)
    logger.info("Starting the AI Agent System...")

    try:
        # Initialize PerformanceMonitor and MemoryManager
        performance_monitor = PerformanceMonitor()
        memory_manager = MemoryManager()

        # Initialize ToolServer with default tools, assuming Shell and PythonNotebook are defined in ai_agent_utils
        tool_server = ToolServer(shell=Shell(), python_notebook=PythonNotebook())

        # Initialize AgentActor with required arguments
        agent_actor = AgentActor(tool_server=tool_server, memory_manager=memory_manager, performance_monitor=performance_monitor)
        logger.debug(f"Initialized AgentActor with ToolServer={tool_server}, MemoryManager={memory_manager}, PerformanceMonitor={performance_monitor}")

        # Initialize AgentDispatcher and add agents
        dispatcher = AgentDispatcher()
        dispatcher.add_agent('actor', agent_actor)

        # Dispatch an example shell task to the 'actor' agent
        task = "echo Hello, Jarvis!"
        result = dispatcher.dispatch_task(task, 'actor', priority=1)
        print(f"Result of task '{task}': {result}")

        # Dispatch a Python code task to the 'actor' agent
        python_task = "python: print('Hello from Python code!')"
        python_result = dispatcher.dispatch_task(python_task, 'actor', priority=2)
        print(f"Result of task '{python_task}': {python_result}")

        # Dispatch a trading functionality task to the 'actor' agent
        trading_task = """
from trading_robot import TradingRobot  # Adjust import based on your module structure
robot = TradingRobot()
robot.load_data('path_to_data.csv')  # Replace with actual data path
analysis_result = robot.run_analysis()
print('Trading Analysis Result:', analysis_result)
"""
        trading_result = dispatcher.dispatch_task(f"python: {trading_task}", 'actor', priority=3)
        print(f"Result of trading task: {trading_result}")

        # Execute all queued tasks in the dispatcher (if implementing queue processing)
        dispatcher.execute_tasks()

    except Exception as e:
        logger.error(f"An error occurred in the main process: {str(e)}")

if __name__ == "__main__":
    main()
