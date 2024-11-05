from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class AgentPlanner:
    """
    Plans tasks by dividing them into subtasks, assigning priorities, and creating customizable milestones.
    """
    def solve_task(self, task: str, priority: Optional[str] = None, milestone_criteria: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Solves the task by dividing it into subtasks, assigning priorities, and generating milestones based on criteria.

        Args:
            task (str): The main task to be divided.
            priority (Optional[str]): Priority level for subtasks (e.g., 'High', 'Medium', 'Low').
            milestone_criteria (Optional[str]): Keyword to mark specific subtasks as milestones.

        Returns:
            Dict[str, List[str]]: Contains 'subtasks' and 'milestones' along with their priorities.
        """
        logger.info(f"Planning task: {task} with priority: {priority}")
        subtasks = self.divide_task(task, priority)
        milestones = self.generate_milestones(subtasks, milestone_criteria)
        result = {
            'subtasks': subtasks,
            'milestones': milestones
        }
        logger.debug(f"Task planning result: {result}")
        return result

    def divide_task(self, task: str, priority: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Divides the main task into subtasks, optionally assigning a priority to each.

        Args:
            task (str): The main task.
            priority (Optional[str]): Priority level for subtasks.

        Returns:
            List[Dict[str, str]]: List of subtasks with their priorities.
        """
        subtasks = [{'task': s.strip(), 'priority': priority if priority else 'Medium'} 
                    for s in task.split('. ') if s.strip()]
        logger.debug(f"Divided task into subtasks with priorities: {subtasks}")
        return subtasks

    def generate_milestones(self, subtasks: List[Dict[str, str]], milestone_criteria: Optional[str] = None) -> List[str]:
        """
        Generates milestones by identifying subtasks that meet the criteria or fall at set intervals.

        Args:
            subtasks (List[Dict[str, str]]): List of subtasks.
            milestone_criteria (Optional[str]): Keyword to mark specific subtasks as milestones.

        Returns:
            List[str]: List of milestones.
        """
        if milestone_criteria:
            milestones = [subtask['task'] for subtask in subtasks if milestone_criteria in subtask['task']]
        else:
            # Default milestone criteria: every third task as milestone
            milestones = [subtask['task'] for i, subtask in enumerate(subtasks) if (i + 1) % 3 == 0]
        
        logger.debug(f"Generated milestones from subtasks with criteria '{milestone_criteria}': {milestones}")
        return milestones

if __name__ == "__main__":
    planner = AgentPlanner()
    task_description = "Initialize the project environment. Set up the database. Develop the API. Integrate frontend and backend. Run initial tests. Deploy to staging."
    result = planner.solve_task(task_description, priority="High", milestone_criteria="Deploy")
    print("Subtasks and milestones:", result)
