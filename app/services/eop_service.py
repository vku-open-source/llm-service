from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from app.core.config import settings
from typing import Dict, Any


class EOPService:
    def __init__(self):
        self.llm = ChatOpenAI(
            # model_name="gpt-4o-mini-2024-07-18",
            model_name="gpt-4o",
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0.7,
        )

        self.eop_prompt_template = PromptTemplate(
            input_variables=["flood_data", "resource_data", "location"],
            template="""
You are an AI assistant tasked with generating a detailed Emergency Operations Plan (EOP) for a flood scenario. Your goal is to create a comprehensive and actionable plan based on the provided flood data and available resources. Follow these instructions carefully to generate an effective EOP.

### **Step 1: Review Flood Data:**

<flood_data>
{flood_data}
</flood_data>

### **Step 2: Review Resource Data:**

<resource_data>
{resource_data}
</resource_data>

### **Step 3: Location:**

<location>
{location}
</location>

Based on the location, remove the location which is not in the location.

### **Step 4: Analyze the Provided Data:**

- Water levels and their projected changes
- High-risk areas
- Available food and medical supplies
- Number and location of volunteers
- Other critical resources mentioned

Using this information, generate an Emergency Operations Plan (EOP) that addresses the following key areas:

---

### **EOP Outline**

1. **Situation Overview**
   - Summarize the current flood situation and potential risks.
   - Highlight key factors such as water levels, areas at risk, and ongoing impacts.

2. **Mission and Objectives**
   - Define the primary goals of the emergency response.
   - Ensure objectives focus on life-saving actions, resource management, and community safety.

3. **Resource Allocation**
   - Detail how available resources (e.g., medical supplies, food, volunteers) should be distributed and utilized.
   - Include logistics, priority areas, and the timing of resource deployment.

4. **Communication Plans**
   - Outline communication strategies and protocols, including:
     - How to communicate with affected communities
     - Internal communication within the response team
     - Coordination with local authorities, NGOs, and other stakeholders

5. **Evacuation Procedures**
   - Provide details on evacuation routes and shelters.
   - Include risk assessments for evacuation and priority groups (e.g., elderly, children).

6. **Medical Support and Safety**
   - Ensure medical facilities and supplies are effectively allocated to high-risk areas.
   - Detail medical evacuation procedures if necessary.

7. **Public Awareness and Information**
   - Create a strategy for disseminating critical information to the public, including warnings, safety instructions, and updates.
   - Use media channels and local community networks.

8. **Volunteer Management**
   - Plan for the mobilization, training, and coordination of volunteers.
   - Ensure the safety and effectiveness of volunteer operations.

9. **Transportation and Logistics**
   - Plan transportation routes and available vehicles for moving people, resources, and supplies.
   - Address any logistical challenges due to flooded infrastructure.

10. **Backup Plans and Contingencies**
    - Include contingency plans for any unforeseen complications, such as worsened weather conditions or infrastructure collapse.
    - Identify emergency supply reserves and alternative routes.

11. **Post-Flood Recovery and Assessment**
    - Plan for long-term recovery efforts, including damage assessment, rebuilding efforts, and psychological support for affected communities.
    - Address how resources will transition from emergency response to recovery.

---

### **Final EOP Format:**

<EOP>
# Emergency Operations Plan (EOP)

## Situation Overview
[Content here]

## Mission and Objectives
[Content here]

## Resource Allocation
[Content here]

## Communication Plans
[Content here]

## Evacuation Procedures
[Content here]

## Medical Support and Safety
[Content here]

## Public Awareness and Information
[Content here]

## Volunteer Management
[Content here]

## Transportation and Logistics
[Content here]

## Backup Plans and Contingencies
[Content here]

## Post-Flood Recovery and Assessment
[Content here]
</EOP>

Note: Respond in Vietnamese
            """,
        )

        self.eop_chain = LLMChain(llm=self.llm, prompt=self.eop_prompt_template)

    def post_processing_eop(self, eop_content: str) -> str:
        """
        Post-process the EOP content to ensure it is in the correct format.
        - Remove the <EOP> tags
        """

        # remove the <EOP> tags
        eop_content = eop_content.replace("<EOP>", "")
        eop_content = eop_content.replace("</EOP>", "")

        return eop_content

    async def generate_eop(
        self, flood_data: str, resource_data: str, location: str
    ) -> Dict[str, Any]:
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
            result = await self.eop_chain.ainvoke(
                {
                    "flood_data": flood_data,
                    "resource_data": resource_data,
                    "location": location,
                }
            )

            # Extract the EOP content from the response
            eop_content = result.get("text", "")

            # post-processing the eop content
            eop_content = self.post_processing_eop(eop_content)

            # Create a structured response
            report = {
                "status": "success",
                "eop_report": eop_content,
                "metadata": {
                    "location": location,
                    "generated_at": "2024-01-01T00:00:00Z",  # You might want to use actual timestamp
                    "model_used": "gpt-4o-mini-2024-07-18",
                },
            }

            return report

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to generate EOP: {str(e)}",
                "eop_report": None,
            }


# Create a singleton instance
eop_service = EOPService()
