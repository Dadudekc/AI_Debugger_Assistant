# example_usage.py

import time
from utilities.agent_base import RobustAgent  # Adjust the import path as necessary

# Assuming MemoryManager and PerformanceMonitor are defined elsewhere
class MemoryManager:
    def retrieve_memory(self, project_name: str, limit: int = 5) -> str:
        # Placeholder implementation
        return "Previous interactions context. "

    def save_memory(self, project_name: str, prompt: str, response: str):
        # Placeholder implementation
        pass

class PerformanceMonitor:
    def log_performance(self, agent_name: str, prompt: str, success: bool, response: str):
        # Placeholder implementation
        pass

    def analyze_performance(self, agent_name: str) -> Dict[str, Any]:
        # Placeholder implementation
        return {
            'success_rate': 85,
            'failures': 15,
            'failure_details': ['network', 'timeout']
        }

# Define a SampleAgent subclass
class SampleAgent(RobustAgent):
    def solve_task(self, task_data: dict) -> str:
        """
        Implements the abstract solve_task method. Processes the task_data
        and returns a result. Can be extended to handle various task types.
        """
        task_type = task_data.get("type")
        self.log(f"Processing task of type: {task_type}")

        if task_type == "simple_task":
            return "Simple task completed successfully."
        elif task_type == "trigger_error":
            raise ValueError("Simulated task error for demonstration.")
        elif task_type == "plugin_task":
            plugin_name = task_data.get("plugin_name")
            plugin_data = task_data.get("plugin_data", {})
            return self.execute_plugin_task(plugin_name, plugin_data)
        else:
            self.log("Unknown task type provided.", level=logging.WARNING)
            return "Unknown task type."

# Main script to initialize and test SampleAgent
if __name__ == "__main__":
    # Initialize the SampleAgent with MemoryManager and PerformanceMonitor
    memory_manager = MemoryManager()
    performance_monitor = PerformanceMonitor()

    agent = SampleAgent(
        name="SampleAgent",
        description="A test agent with plugin support, memory management, and AI self-healing capabilities.",
        project_name="AI_Debugger_Assistant",
        plugin_dir="plugins",  # Ensure this directory exists with plugins
        memory_manager=memory_manager,
        performance_monitor=performance_monitor,
        log_to_file=True
    )

    # Introduction and capability description
    print(agent.introduce())
    print(agent.describe_capabilities())

    # Execute a simple task
    simple_task_data = {"type": "simple_task"}
    print(agent.solve_task(simple_task_data))

    # Execute a task that triggers an error to test AI-based resolution and user prompts
    error_task_data = {"type": "trigger_error"}
    print(agent.handle_task_with_error_handling(error_task_data))

    # Execute a plugin-based task (ensure 'example_plugin.py' exists in the plugins directory)
    plugin_task_data = {
        "type": "plugin_task",
        "plugin_name": "example_plugin",  # Name of the plugin without .py extension
        "plugin_data": {"input": "Test input for plugin"}
    }
    print(agent.solve_task(plugin_task_data))

    # Schedule a recurring task with fallback handling
    # This example schedules the 'handle_task_with_error_handling' method to run every minute
    scheduled_task_id = "recurring_error_task"
    agent.schedule_task(
        cron_expression="*/1 * * * *",  # Every minute
        task_callable=agent.handle_task_with_error_handling,
        task_data=error_task_data,
        task_id=scheduled_task_id
    )

    # Keep the script running to allow scheduled tasks to execute
    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        agent.shutdown()  # Gracefully shutdown the agent when exiting
