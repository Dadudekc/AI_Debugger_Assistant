import logging
from typing import List, Optional, Dict, Any
import nltk
from transformers import pipeline
import networkx as nx
import asyncio

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logs
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Ensure NLTK data is downloaded
nltk.download('punkt')

class ChainOfThoughtReasoner:
    """
    Implements advanced chain-of-thought reasoning by decomposing tasks into semantic steps,
    supporting hierarchical reasoning, contextual memory, and dynamic step adjustment.
    """

    def __init__(self, agent_dispatcher, model_name: str = 'gpt-3.5-turbo'):
        """
        Initializes the ChainOfThoughtReasoner with an agent dispatcher and a semantic model.

        Args:
            agent_dispatcher: An instance responsible for dispatching tasks to agents.
            model_name (str): The name of the transformer model for semantic task decomposition.
        """
        self.agent_dispatcher = agent_dispatcher
        self.memory: Dict[str, Any] = {}  # Contextual memory
        self.decomposition_pipeline = pipeline("text2text-generation", model=model_name)
        self.reasoning_graph = nx.DiGraph()  # To manage hierarchical steps

    def solve_task_with_reasoning(self, task: str, agent_name: str) -> str:
        """
        Decomposes the task into semantic steps, iterates over each step with the specified agent,
        and manages hierarchical reasoning and memory.

        Args:
            task (str): The main task to solve with chain-of-thought reasoning.
            agent_name (str): The name of the agent to handle each reasoning step.

        Returns:
            str: The final result after completing all reasoning steps or an error message.
        """
        try:
            steps = self.decompose_task(task)
            final_result: Optional[str] = None

            # Build reasoning graph
            self.build_reasoning_graph(steps)

            # Execute steps based on dependencies
            execution_order = list(nx.topological_sort(self.reasoning_graph))
            logger.info(f"Execution order of steps: {execution_order}")

            for idx, step_id in enumerate(execution_order, start=1):
                step = self.reasoning_graph.nodes[step_id]['content']
                logger.info(f"Dispatching Step {idx}/{len(execution_order)}: {step}")

                # Incorporate contextual memory into the step
                enriched_step = self.enrich_step_with_memory(step)

                result = self.agent_dispatcher.dispatch_task(enriched_step, agent_name)

                if self._is_error(result):
                    error_message = f"Failed at step {idx}: '{step}'. Error: {result}"
                    logger.error(error_message)
                    return error_message

                # Update memory with the result
                self.update_memory(step_id, result)

                # Self-evaluation of the result
                if not self.self_evaluate(step, result):
                    retry_result = self.retry_step(step, agent_name)
                    if self._is_error(retry_result):
                        error_message = f"Retry failed at step {idx}: '{step}'. Error: {retry_result}"
                        logger.error(error_message)
                        return error_message
                    self.update_memory(step_id, retry_result)
                    result = retry_result

                final_result = result
                logger.debug(f"Completed Step {idx}: {step} with result: {result}")

            logger.info("All steps completed successfully.")
            return final_result if final_result is not None else "No result produced."

        except Exception as e:
            logger.exception(f"An unexpected error occurred while solving the task: {e}")
            return f"An unexpected error occurred: {str(e)}"

    def decompose_task(self, task: str) -> List[str]:
        """
        Breaks down the main task into semantically meaningful steps for advanced chain-of-thought processing.

        Args:
            task (str): The main task.

        Returns:
            List[str]: A list of semantically decomposed steps to achieve the task.
        """
        try:
            prompt = f"Decompose the following task into detailed, logical, and semantically meaningful steps:\n\nTask: {task}\n\nSteps:"
            decomposition = self.decomposition_pipeline(prompt, max_length=512, num_return_sequences=1)
            steps_text = decomposition[0]['generated_text']
            # Assume steps are numbered or bullet-pointed
            steps = self.parse_decomposition_output(steps_text)
            logger.debug(f"Task decomposed into steps: {steps}")
            return steps
        except Exception as e:
            logger.exception(f"Failed to decompose task: {e}")
            raise

    def parse_decomposition_output(self, text: str) -> List[str]:
        """
        Parses the output from the decomposition model into a list of steps.

        Args:
            text (str): The raw text output from the decomposition model.

        Returns:
            List[str]: A list of individual steps.
        """
        # Simple parsing logic; can be enhanced based on model's output format
        lines = text.split('\n')
        steps = []
        for line in lines:
            line = line.strip()
            if line:
                # Remove numbering or bullet points
                step = line.lstrip('0123456789.)-• ').strip()
                if step:
                    steps.append(step)
        return steps

    def build_reasoning_graph(self, steps: List[str]) -> None:
        """
        Builds a directed graph representing the dependencies between reasoning steps.

        Args:
            steps (List[str]): A list of steps to include in the reasoning graph.
        """
        self.reasoning_graph.clear()
        for idx, step in enumerate(steps, start=1):
            step_id = f"step_{idx}"
            self.reasoning_graph.add_node(step_id, content=step)
            if idx > 1:
                self.reasoning_graph.add_edge(f"step_{idx - 1}", step_id)
        logger.debug(f"Reasoning graph constructed with nodes: {self.reasoning_graph.nodes}")

    def enrich_step_with_memory(self, step: str) -> str:
        """
        Enhances the step with contextual memory for more informed processing.

        Args:
            step (str): The original step content.

        Returns:
            str: The enriched step content.
        """
        memory_content = "\n".join([f"{k}: {v}" for k, v in self.memory.items()])
        enriched_step = f"Contextual Memory:\n{memory_content}\n\nTask Step: {step}"
        return enriched_step

    def update_memory(self, step_id: str, result: str) -> None:
        """
        Updates the contextual memory with the result of a completed step.

        Args:
            step_id (str): The identifier of the completed step.
            result (str): The result produced by the step.
        """
        self.memory[step_id] = result
        logger.debug(f"Memory updated with {step_id}: {result}")

    def self_evaluate(self, step: str, result: str) -> bool:
        """
        Evaluates the quality of the step's result.

        Args:
            step (str): The step content.
            result (str): The result produced by the step.

        Returns:
            bool: True if the result is satisfactory, False otherwise.
        """
        # Placeholder for self-evaluation logic; can be enhanced with NLP models
        evaluation_prompt = f"Evaluate the following result for the step:\n\nStep: {step}\nResult: {result}\n\nIs the result correct and complete? (yes/no):"
        evaluation = self.decomposition_pipeline(evaluation_prompt, max_length=10, num_return_sequences=1)
        evaluation_text = evaluation[0]['generated_text'].strip().lower()
        is_valid = 'yes' in evaluation_text
        logger.debug(f"Self-evaluation of step '{step}': {'Passed' if is_valid else 'Failed'}")
        return is_valid

    def retry_step(self, step: str, agent_name: str) -> str:
        """
        Retries a failed step with possible refinements.

        Args:
            step (str): The step content.
            agent_name (str): The name of the agent to handle the retry.

        Returns:
            str: The result of the retried step.
        """
        retry_prompt = f"The previous attempt to complete the step failed. Please try again with more details.\n\nStep: {step}"
        logger.info(f"Retrying step: {step}")
        result = self.agent_dispatcher.dispatch_task(retry_prompt, agent_name)
        return result

    @staticmethod
    def _is_error(result: str) -> bool:
        """
        Determines if the result contains an error.

        Args:
            result (str): The result string to check.

        Returns:
            bool: True if an error is detected, False otherwise.
        """
        # Define a more robust error detection mechanism
        error_indicators = ["error", "failed", "exception", "invalid", "could not", "unable to"]
        return any(indicator in result.lower() for indicator in error_indicators)
