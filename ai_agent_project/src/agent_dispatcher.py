import logging

logger = logging.getLogger(__name__)

class AgentDispatcher:
    """
    Dispatches tasks to various agents. This acts as an interface for handling
    task processing, managing the flow between the GUI and the ChainOfThoughtReasoner.
    """

    def dispatch_task(self, task: str, agent_name: str) -> str:
        """
        Processes the given task with the specified agent.
        
        Args:
            task (str): Task to be processed.
            agent_name (str): Name of the agent to use.

        Returns:
            str: Processed result or error message.
        """
        # Example implementation
        try:
            # Simulate processing task by returning task + agent name
            logger.info(f"Agent '{agent_name}' processing task: {task}")
            result = f"[{agent_name}]: Processed task - {task}"
            return result
        except Exception as e:
            logger.error(f"Error processing task: {e}")
            return f"Error: {str(e)}"
