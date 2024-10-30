from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class AgentPlanner:
    """
    Plans tasks by dividing them into subtasks and creating milestones.
    """
    def solve_task(self, task: str, **kwargs) -> Dict[str, List[str]]:
        """
        Solves the task by dividing it into subtasks and generating milestones.

        Args:
            task (str): The main task to be divided.

        Returns:
            Dict[str, List[str]]: Contains 'subtasks' and 'milestones'.
        """
        logger.info(f"Planning task: {task}")
        subtasks = self.divide_task(task)
        milestones = self.generate_milestones(subtasks)
        result = {
            'subtasks': subtasks,
            'milestones': milestones
        }
        logger.debug(f"Task planning result: {result}")
        return result
    
    def divide_task(self, task: str) -> List[str]:
        """
        Divides the main task into subtasks by splitting sentences.

        Args:
            task (str): The main task.

        Returns:
            List[str]: List of subtasks.
        """
        subtasks = [s.strip() for s in task.split('. ') if s.strip()]
        logger.debug(f"Divided task into subtasks: {subtasks}")
        return subtasks
    
    def generate_milestones(self, subtasks: List[str]) -> List[str]:
        """
        Generates milestones by marking every third subtask as a milestone.

        Args:
            subtasks (List[str]): List of subtasks.

        Returns:
            List[str]: List of milestones.
        """
        milestones = [subtasks[i] for i in range(len(subtasks)) if (i + 1) % 3 == 0]
        logger.debug(f"Generated milestones from subtasks: {milestones}")
        return milestones
