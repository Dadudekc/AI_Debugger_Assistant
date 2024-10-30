# ------------------------
# AI Agent Class with Self-Improvement
# ------------------------

class AIAgentWithMemory:
    """
    AIAgentWithMemory Class

    Represents an AI agent that can interact with users, retain memory of past
    conversations, provide context-aware responses, and improve itself based on feedback.
    Integrates with the MemoryManager and PerformanceMonitor to handle memory and performance operations,
    respectively, and uses subprocess to communicate with the AI model (e.g., Mistral 7B via Ollama).
    """

    def __init__(self, name: str, project_name: str, memory_manager: MemoryManager, performance_monitor: 'PerformanceMonitor', dispatcher: AgentDispatcher):
        """
        Initialize the AI agent with a name, project name, a MemoryManager instance, 
        and a PerformanceMonitor instance.

        Args:
            name (str): Name of the AI agent.
            project_name (str): Name of the project/domain the agent is associated with.
            memory_manager (MemoryManager): Instance of MemoryManager for handling memory operations.
            performance_monitor (PerformanceMonitor): Instance of PerformanceMonitor for tracking performance.
            dispatcher (AgentDispatcher): Reference to the dispatcher for self-improvement actions.
        """
        self.name = name
        self.project_name = project_name
        self.memory_manager = memory_manager
        self.performance_monitor = performance_monitor
        self.dispatcher = dispatcher
        logger.info(f"Initialized AI Agent '{self.name}' for project '{self.project_name}'.")

    def run_query(self, prompt: str) -> str:
        """
        Run a query against Mistral 7B via Ollama and store the interaction in memory.

        Args:
            prompt (str): The user prompt to send to Mistral.

        Returns:
            str: The response from Mistral.
        """
        try:
            # Retrieve relevant memory context
            memory_context = self.memory_manager.retrieve_memory(self.project_name, limit=5)
            complete_prompt = f"{memory_context}User: {prompt}\nAI:"

            logger.debug(f"Complete prompt sent to AI:\n{complete_prompt}")

            # Run the Ollama command with the complete prompt
            result = subprocess.run(
                ["ollama", "run", "mistral", "--prompt", complete_prompt],
                capture_output=True,
                text=True,
                check=True
            )
            response = result.stdout.strip()
            logger.info(f"Received response from AI for prompt: '{prompt}'")

            # Save the interaction to memory
            self.memory_manager.save_memory(self.project_name, prompt, response)

            # Log performance as success
            self.performance_monitor.log_performance(self.name, prompt, True, response)

            return response
        except subprocess.CalledProcessError as e:
            error_message = f"An error occurred while communicating with Ollama: {e.stderr.strip()}"
            logger.error(error_message)

            # Log performance as failure
            self.performance_monitor.log_performance(self.name, prompt, False, error_message)

            return error_message
        except Exception as ex:
            error_message = f"An unexpected error occurred: {str(ex)}"
            logger.error(error_message)

            # Log performance as failure
            self.performance_monitor.log_performance(self.name, prompt, False, error_message)

            return error_message

    def chat(self, user_input: str) -> str:
        """
        Facilitate a chat interaction with the AI agent.

        Args:
            user_input (str): Input from the user.

        Returns:
            str: Response from the AI agent.
        """
        logger.info(f"User input received: '{user_input}'")
        response = self.run_query(user_input)
        logger.info(f"AI response: '{response}'")

        # Analyze performance after each interaction
        self.self_improve()

        return response

    def self_improve(self):
        """
        Analyze performance and adjust operations to improve future interactions.
        This method embodies the self-improvement capability of the AI agent.
        """
        analysis = self.performance_monitor.analyze_performance(self.name)
        if not analysis:
            logger.info("No performance data available for self-improvement.")
            return

        success_rate = analysis.get('success_rate', 0)
        failures = analysis.get('failures', 0)

        logger.debug(f"Self-improvement analysis: {analysis}")

        # Thresholds for triggering improvements
        SUCCESS_THRESHOLD = 80  # percent
        FAILURE_THRESHOLD = 20  # percent

        if success_rate < SUCCESS_THRESHOLD and failures > FAILURE_THRESHOLD:
            # Identify common failure reasons
            failure_reasons = analysis.get('failure_details', [])
            common_reasons = {}
            for reason in failure_reasons:
                common_reasons[reason] = common_reasons.get(reason, 0) + 1
            # Find the most common failure reason
            if common_reasons:
                most_common_reason = max(common_reasons, key=common_reasons.get)
                logger.warning(f"Most common failure reason: {most_common_reason}")
                # Take action based on failure reason
                self.take_action_based_on_failure(most_common_reason)
        elif success_rate >= SUCCESS_THRESHOLD:
            logger.info("Performance is satisfactory. No immediate improvements needed.")
        else:
            logger.info("Performance analysis does not require immediate action.")

    def take_action_based_on_failure(self, reason: str):
        """
        Takes specific actions based on the identified failure reason.

        Args:
            reason (str): The most common failure reason.
        """
        logger.info(f"Taking action based on failure reason: {reason}")
        # Example actions based on failure reasons
        if "communication" in reason.lower():
            # Maybe try to reset the AI model or check network
            suggestion = "I recommend checking the network connection or restarting the AI model service."
            logger.info(suggestion)
            # Optionally, communicate this suggestion to the user
            print(f"AI Suggestion: {suggestion}")
        elif "permission" in reason.lower():
            # Suggest checking file permissions
            suggestion = "It seems there are permission issues. Please verify the file permissions."
            logger.info(suggestion)
            print(f"AI Suggestion: {suggestion}")
        elif "docker" in reason.lower():
            # Suggest checking Docker setup
            suggestion = "Docker-related errors detected. Please ensure Docker is properly installed and configured."
            logger.info(suggestion)
            print(f"AI Suggestion: {suggestion}")
        else:
            # General suggestion
            suggestion = "I encountered an issue that needs attention. Please review the logs for more details."
            logger.info(suggestion)
            print(f"AI Suggestion: {suggestion}")

    def suggest_improvements(self):
        """
        Suggests improvements to its own operations based on performance data.
        """
        analysis = self.performance_monitor.analyze_performance(self.name)
        if not analysis:
            logger.info("No performance data available to suggest improvements.")
            return

        suggestions = []
        success_rate = analysis.get('success_rate', 0)
        failures = analysis.get('failures', 0)

        if success_rate < 90:
            suggestions.append("Consider refining task division strategies to better handle complex tasks.")
        if failures > 5:
            suggestions.append("Evaluate and possibly upgrade the tools in ToolServer to handle current task demands.")
        if len(suggestions) > 0:
            suggestion_message = "Here are some suggestions to improve my performance:\n" + "\n".join(suggestions)
            logger.info(suggestion_message)
            print(f"AI Suggestion: {suggestion_message}")
class AIAgentWithMemory:
    """
    AIAgentWithMemory Class

    Represents an AI agent that can interact with users, retain memory of past
    conversations, provide context-aware responses, and improve itself based on feedback.
    Integrates with the MemoryManager and PerformanceMonitor to handle memory and performance operations,
    respectively, and uses subprocess to communicate with the AI model (e.g., Mistral 7B via Ollama).
    """

    def __init__(self, name: str, project_name: str, memory_manager: MemoryManager, performance_monitor: 'PerformanceMonitor', dispatcher: AgentDispatcher):
        """
            Initialize the AI agent with a name, project name, a MemoryManager instance, 
            and a PerformanceMonitor instance.

            Args:
                name (str): Name of the AI agent.
                project_name (str): Name of the project/domain the agent is associated with.
                memory_manager (MemoryManager): Instance of MemoryManager for handling memory operations.
                performance_monitor (PerformanceMonitor): Instance of PerformanceMonitor for tracking performance.
                dispatcher (AgentDispatcher): Reference to the dispatcher for self-improvement actions.
        """
        self.name = name
        self.project_name = project_name
        self.memory_manager = memory_manager
        self.performance_monitor = performance_monitor
        self.dispatcher = dispatcher
        logger.info(f"Initialized AI Agent '{self.name}' for project '{self.project_name}'.")

    def run_query(self, prompt: str) -> str:
        """
        Run a query against Mistral 7B via Ollama and store the interaction in memory.

        Args:
            prompt (str): The user prompt to send to Mistral.

        Returns:
            str: The response from Mistral.
        """
        try:
            # Retrieve relevant memory context
            memory_context = self.memory_manager.retrieve_memory(self.project_name, limit=5)
            complete_prompt = f"{memory_context}User: {prompt}\nAI:"

            logger.debug(f"Complete prompt sent to AI:\n{complete_prompt}")

            # Run the Ollama command with the complete prompt
            result = subprocess.run(
                ["ollama", "run", "mistral", "--prompt", complete_prompt],
                capture_output=True,
                text=True,
                check=True
            )
            response = result.stdout.strip()
            logger.info(f"Received response from AI for prompt: '{prompt}'")

            # Save the interaction to memory
            self.memory_manager.save_memory(self.project_name, prompt, response)

            # Log performance as success
            self.performance_monitor.log_performance(self.name, prompt, True, response)

            return response
        except subprocess.CalledProcessError as e:
            error_message = f"An error occurred while communicating with Ollama: {e.stderr.strip()}"
            logger.error(error_message)

            # Log performance as failure
            self.performance_monitor.log_performance(self.name, prompt, False, error_message)

            return error_message
        except Exception as ex:
            error_message = f"An unexpected error occurred: {str(ex)}"
            logger.error(error_message)

            # Log performance as failure
            self.performance_monitor.log_performance(self.name, prompt, False, error_message)

            return error_message

    def chat(self, user_input: str) -> str:
        """
        Facilitate a chat interaction with the AI agent.

        Args:
            user_input (str): Input from the user.

        Returns:
            str: Response from the AI agent.
        """
        logger.info(f"User input received: '{user_input}'")
        response = self.run_query(user_input)
        logger.info(f"AI response: '{response}'")

        # Analyze performance after each interaction
        self.self_improve()

        return response

    def self_improve(self):
        """
        Analyze performance and adjust operations to improve future interactions.
        This method embodies the self-improvement capability of the AI agent.
        """
        analysis = self.performance_monitor.analyze_performance(self.name)
        if not analysis:
            logger.info("No performance data available for self-improvement.")
            return

        success_rate = analysis.get('success_rate', 0)
        failures = analysis.get('failures', 0)

        logger.debug(f"Self-improvement analysis: {analysis}")

        # Thresholds for triggering improvements
        SUCCESS_THRESHOLD = 80  # percent
        FAILURE_THRESHOLD = 20  # percent

        if success_rate < SUCCESS_THRESHOLD and failures > FAILURE_THRESHOLD:
            # Identify common failure reasons
            failure_reasons = analysis.get('failure_details', [])
            common_reasons = {}
            for reason in failure_reasons:
                common_reasons[reason] = common_reasons.get(reason, 0) + 1
            # Find the most common failure reason
            if common_reasons:
                most_common_reason = max(common_reasons, key=common_reasons.get)
                logger.warning(f"Most common failure reason: {most_common_reason}")
                # Take action based on failure reason
                self.take_action_based_on_failure(most_common_reason)
        elif success_rate >= SUCCESS_THRESHOLD:
            logger.info("Performance is satisfactory. No immediate improvements needed.")
        else:
            logger.info("Performance analysis does not require immediate action.")

    def take_action_based_on_failure(self, reason: str):
        """
        Takes specific actions based on the identified failure reason.

        Args:
            reason (str): The most common failure reason.
        """
        logger.info(f"Taking action based on failure reason: {reason}")
        # Example actions based on failure reasons
        if "communication" in reason.lower():
            # Maybe try to reset the AI model or check network
            suggestion = "I recommend checking the network connection or restarting the AI model service."
            logger.info(suggestion)
            # Optionally, communicate this suggestion to the user
            print(f"AI Suggestion: {suggestion}")
        elif "permission" in reason.lower():
            # Suggest checking file permissions
            suggestion = "It seems there are permission issues. Please verify the file permissions."
            logger.info(suggestion)
            print(f"AI Suggestion: {suggestion}")
        elif "docker" in reason.lower():
            # Suggest checking Docker setup
            suggestion = "Docker-related errors detected. Please ensure Docker is properly installed and configured."
            logger.info(suggestion)
            print(f"AI Suggestion: {suggestion}")
        else:
            # General suggestion
            suggestion = "I encountered an issue that needs attention. Please review the logs for more details."
            logger.info(suggestion)
            print(f"AI Suggestion: {suggestion}")
    
    def suggest_improvements(self):
        """
        Suggests improvements to its own operations based on performance data.
        """
        analysis = self.performance_monitor.analyze_performance(self.name)
        if not analysis:
            logger.info("No performance data available to suggest improvements.")
            return

        suggestions = []
        success_rate = analysis.get('success_rate', 0)
        failures = analysis.get('failures', 0)

        if success_rate < 90:
            suggestions.append("Consider refining task division strategies to better handle complex tasks.")
        if failures > 5:
            suggestions.append("Evaluate and possibly upgrade the tools in ToolServer to handle current task demands.")
        if len(suggestions) > 0:
            suggestion_message = "Here are some suggestions to improve my performance:\n" + "\n".join(suggestions)
            logger.info(suggestion_message)
            print(f"AI Suggestion: {suggestion_message}")