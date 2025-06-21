from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from app.core.config import settings
from typing import Dict, Any

class EOPService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name='gpt-4o-mini-2024-07-18',
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0.7
        )

        self.eop_prompt_template = PromptTemplate(
            input_variables=["flood_data", "resource_data", "location"],
            template="""
You are an AI assistant tasked with generating an Emergency Operations Plan (EOP) for a flood scenario. Your goal is to create a comprehensive plan based on the provided flood data and available resources. Follow these instructions carefully to produce an effective EOP.

First, review the flood data:
<flood_data>
{flood_data}
</flood_data>

Next, examine the resource data:
<resource_data>
{resource_data}
</resource_data>

<location>
{location}
</location>

Analyze the provided data, paying close attention to:
- Water levels and their projected changes
- Areas at highest risk
- Available food and medical supplies
- Number and location of volunteers
- Other critical resources mentioned

Using this information, generate an Emergency Operations Plan (EOP) that addresses the following key areas:
1. Situation Overview: Summarize the current flood situation and potential risks.
2. Mission and Objectives: Define the primary goals of the emergency response.
3. Resource Allocation: Detail how available resources should be distributed and utilized.
4. Communication Plans: Outline communication strategies and protocols.

When creating the EOP, ensure that each section is concise, clear, and actionable. Use bullet points where appropriate for easy readability. Tailor the plan to the specific flood scenario and available resources described in the input data.

Present your final Emergency Operations Plan within <EOP> tags, using appropriate subsection tags for each major component of the plan. For example:

<EOP>
# Tổng quan tình hình
[Nội dung ở đây]

# Sứ mệnh và mục tiêu
[Nội dung ở đây]

# Phân bổ nguồn lực
[Nội dung ở đây]

# Kế hoạch truyền thông
[Nội dung ở đây]
</EOP>

Remember to base all aspects of the EOP on the provided flood and resource data. Do not include any information or assumptions that are not supported by the given data.

Note: Respond in Vietnamese
"""
        )

        self.eop_chain = LLMChain(
            llm=self.llm,
            prompt=self.eop_prompt_template
        )

    def post_processing_eop(self, eop_content: str) -> str:
        """
        Post-process the EOP content to ensure it is in the correct format.
        - Remove the <EOP> tags
        """

        # remove the <EOP> tags
        eop_content = eop_content.replace('<EOP>', '')
        eop_content = eop_content.replace('</EOP>', '')

        return eop_content

    async def generate_eop(self, flood_data: str, resource_data: str, location: str) -> Dict[str, Any]:
        """
        Generate an Emergency Operations Plan (EOP) based on flood and resource data.

        Args:
            flood_data: Information about the flood situation
            resource_data: Information about available resources
            location: Location information

        Returns:
            Dictionary containing the generated EOP report
        """
        try:
            # Execute the LangChain workflow
            result = await self.eop_chain.ainvoke({
                "flood_data": flood_data,
                "resource_data": resource_data,
                "location": location
            })

            # Extract the EOP content from the response
            eop_content = result.get('text', '')

            # post-processing the eop content
            eop_content = self.post_processing_eop(eop_content)

            # Create a structured response
            report = {
                "status": "success",
                "eop_report": eop_content,
                "metadata": {
                    "location": location,
                    "generated_at": "2024-01-01T00:00:00Z",  # You might want to use actual timestamp
                    "model_used": "gpt-4o-mini-2024-07-18"
                }
            }

            return report

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to generate EOP: {str(e)}",
                "eop_report": None
            }

# Create a singleton instance
eop_service = EOPService()