from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from app.core.config import settings
from typing import Dict, Any, List
import json
import re

class TaskService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name='gpt-4o-mini-2024-07-18',
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0.7
        )

        self.task_prompt_template = PromptTemplate(
            input_variables=["emergency_operations_plan", "flood_data", "resource_data"],
            template="""
You are an AI assistant tasked with generating a volunteer task list based on an Emergency Operations Plan (EOP) and current situational data. Your goal is to create a prioritized list of tasks that volunteers can undertake to assist in flood response efforts.

First, review the Emergency Operations Plan:

<emergency_operations_plan>
{emergency_operations_plan}
</emergency_operations_plan>

Now, consider the current flood situation:

<flood_data>
{flood_data}
</flood_data>

Take into account the available resources:

<resource_data>
{resource_data}
</resource_data>

Analyze the Emergency Operations Plan, flood data, and resource data to identify key areas where volunteer assistance is needed. Consider the following factors:
1. Immediate life-saving actions
2. Property protection measures
3. Support for vulnerable populations
4. Logistics and supply chain management
5. Community outreach and communication

Based on your analysis, generate a prioritized task list for volunteers. Each task should:
1. Be specific and actionable
2. Align with the Emergency Operations Plan
3. Address current flood conditions
4. Consider available resources
5. Be suitable for untrained volunteers (avoid tasks requiring specialized skills unless specified in the resource data)

Present your task list in the following format:

<task_list>
<task>
<priority>[High/Medium/Low]</priority>
<description>[Clear, concise task description]</description>
<location>[General location or area for the task]</location>
<resources_needed>[List of resources required, if any]</resources_needed>
</task>
[Repeat for each task, with a minimum of 5 and a maximum of 10 tasks]
</task_list>

Remember to focus on tasks that are safe and appropriate for volunteers, considering the severity of the flood situation and the guidelines in the Emergency Operations Plan.
Just respond tasks list

Note: Respond in Vietnamese
"""
        )

        self.task_chain = LLMChain(
            llm=self.llm,
            prompt=self.task_prompt_template
        )

    def _parse_task_list(self, response_text: str) -> List[Dict[str, str]]:
        """
        Parse the task list from the LLM response and convert to structured format.

        Args:
            response_text: Raw response from LLM

        Returns:
            List of task dictionaries
        """
        tasks = []

        # Extract content between <task_list> tags
        task_list_match = re.search(r'<task_list>(.*?)</task_list>', response_text, re.DOTALL)
        if not task_list_match:
            return tasks

        task_list_content = task_list_match.group(1)

        # Find all individual tasks
        task_matches = re.findall(r'<task>(.*?)</task>', task_list_content, re.DOTALL)

        for task_match in task_matches:
            # Extract task components
            priority_match = re.search(r'<priority>(.*?)</priority>', task_match, re.DOTALL)
            description_match = re.search(r'<description>(.*?)</description>', task_match, re.DOTALL)
            location_match = re.search(r'<location>(.*?)</location>', task_match, re.DOTALL)
            resources_match = re.search(r'<resources_needed>(.*?)</resources_needed>', task_match, re.DOTALL)

            if priority_match and description_match and location_match:
                task = {
                    "priority": priority_match.group(1).strip(),
                    "description": description_match.group(1).strip(),
                    "location": location_match.group(1).strip(),
                    "resource_needed": resources_match.group(1).strip() if resources_match else ""
                }
                tasks.append(task)

        return tasks

    async def generate_tasks(self, emergency_operations_plan: str, flood_data: str, resource_data: str) -> Dict[str, Any]:
        """
        Generate volunteer tasks based on EOP report and current situation data.

        Args:
            emergency_operations_plan: The EOP report content
            flood_data: Current flood situation data
            resource_data: Available resources information

        Returns:
            Dictionary containing the generated task list
        """
        try:
            # Execute the LangChain workflow
            result = await self.task_chain.ainvoke({
                "emergency_operations_plan": emergency_operations_plan,
                "flood_data": flood_data,
                "resource_data": resource_data
            })

            # Extract the task list content from the response
            task_list_content = result.get('text', '')

            # Parse the task list into structured format
            tasks = self._parse_task_list(task_list_content)

            # Create a structured response
            response = {
                "status": "success",
                "tasks": tasks,
                "total_tasks": len(tasks),

            }

            return response

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to generate tasks: {str(e)}",
                "tasks": []
            }

# Create a singleton instance
task_service = TaskService()