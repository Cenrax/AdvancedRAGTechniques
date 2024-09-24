import json
import re
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
import os
from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential
import streamlit as st
import json


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    return client.chat.completions.create(**kwargs)

@dataclass
class UserGoal:
    primary_goal: str
    requirements: List[str]
    preferences: Dict[str, Any]
    cot_strategy: str

class RequirementAgent:
    def gather_requirements(self, user_input: str) -> UserGoal:
        print(f"RequirementAgent: Gathering requirements for input: {user_input}")
        prompt = f"""
        Based on the following user input, extract the primary goal, list of requirements, 
        user preferences, and suggest a chain-of-thought strategy.
        User input: {user_input}
        
        Respond in JSON format with the following structure:
        {{
            "primary_goal": "string",
            "requirements": ["string", "string", ...],
            "preferences": {{"key": "value", ...}},
            "cot_strategy": "string"
        }}
        """
        
        try:
            response = completion_with_backoff(
                model="gpt-4o",
                messages=[{"role": "system", "content": "You are a requirement gathering assistant."},
                          {"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            response_content = response.choices[0].message.content.strip()
            print(f"RequirementAgent: Raw API response: {response_content}")
            
            extracted_info = json.loads(response_content)
            print(f"RequirementAgent: Parsed response: {extracted_info}")
            return UserGoal(**extracted_info)
        except Exception as e:
            print(f"RequirementAgent: Error occurred: {str(e)}")
            raise

class PlannerAgent:
    def create_plan(self, user_goal: UserGoal) -> List[Dict[str, Any]]:
        print(f"PlannerAgent: Creating plan for user goal: {asdict(user_goal)}")
        prompt = f"""
        Given the following user goal, create a detailed plan for implementing an AI pipeline flow.
        User Goal: {json.dumps(asdict(user_goal))}
        
        Respond with a list of tasks in JSON format, where each task has a 'task_type' and 'details':
        [
            {{"task_type": "string", "details": {{"key": "value", ...}}}},
            ...
        ]
        Ensure that your response is a valid JSON array with the exact structure shown above.
        """
        
        try:
            response = completion_with_backoff(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a planner for AI pipeline flows. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            response_content = response.choices[0].message.content.strip()
            print(f"PlannerAgent: Raw API response: {response_content}")
            
            try:
                plan = json.loads(response_content)
                print(f"PlannerAgent: Parsed plan: {plan}")
                return plan
            except json.JSONDecodeError:
                print("PlannerAgent: JSON decoding failed, attempting to extract JSON from response")
                json_match = re.search(r'\[.*\]', response_content, re.DOTALL)
                if json_match:
                    plan = json.loads(json_match.group())
                    print(f"PlannerAgent: Extracted plan: {plan}")
                    return plan
                else:
                    print("PlannerAgent: No valid JSON found in response")
                    raise ValueError("Unable to extract valid JSON from the response")
        
        except Exception as e:
            print(f"PlannerAgent: Error occurred: {str(e)}")
            raise

class TaskAgent:
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        print(f"TaskAgent: Executing task: {task}")
        prompt = f"""
        Execute the following task for an AI pipeline flow:
        {json.dumps(task)}
        
        Respond with the result in JSON format:
        {{
            "node_type": "string",
            "node_data": {{
                "key1": "value1",
                "key2": "value2",
                ...
            }}
        }}
        Ensure that your response is a valid JSON object with the exact structure shown above.
        """
        
        try:
            response = completion_with_backoff(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a task execution agent for AI pipelines. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            response_content = response.choices[0].message.content.strip()
            print(f"TaskAgent: Raw API response: {response_content}")
            
            try:
                result = json.loads(response_content)
                print(f"TaskAgent: Parsed result: {result}")
                return result
            except json.JSONDecodeError:
                print("TaskAgent: JSON decoding failed, attempting to extract JSON from response")
                json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    print(f"TaskAgent: Extracted result: {result}")
                    return result
                else:
                    print("TaskAgent: No valid JSON found in response")
                    raise ValueError("Unable to extract valid JSON from the response")
        
        except Exception as e:
            print(f"TaskAgent: Error occurred: {str(e)}")
            raise

class ConnectionAgent:
    def connect_nodes(self, nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        print(f"ConnectionAgent: Connecting nodes: {nodes}")
        prompt = f"""
        Given the following nodes, create edge specifications to connect them and provide 
        starter x-y positions for each node:
        {json.dumps(nodes)}
        
        Respond with the updated nodes and edges in JSON format:
        {{
            "nodes": [
                {{"id": "string", "type": "string", "data": {{}}, "position": {{"x": 0, "y": 0}}}},
                ...
            ],
            "edges": [
                {{"source": "string", "target": "string", "id": "string"}},
                ...
            ]
        }}
        """
        
        try:
            response = completion_with_backoff(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a connection agent for AI pipeline flows. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            response_content = response.choices[0].message.content.strip()
            print(f"ConnectionAgent: Raw API response: {response_content}")
            
            try:
                result = json.loads(response_content)
                print(f"ConnectionAgent: Parsed result: {result}")
                return result
            except json.JSONDecodeError:
                print("ConnectionAgent: JSON decoding failed, attempting to extract JSON from response")
                json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    print(f"ConnectionAgent: Extracted result: {result}")
                    return result
                else:
                    print("ConnectionAgent: No valid JSON found in response")
                    raise ValueError("Unable to extract valid JSON from the response")
        
        except Exception as e:
            print(f"ConnectionAgent: Error occurred: {str(e)}")
            raise

class ReviewerAgent:
    def review_flow(self, flow: Dict[str, Any], user_goal: UserGoal) -> Dict[str, Any]:
        print(f"ReviewerAgent: Reviewing flow: {flow}")
        prompt = f"""
        Review the following AI pipeline flow against the initial user criteria:
        Flow: {json.dumps(flow)}
        User Goal: {json.dumps(asdict(user_goal))}
        
        Provide feedback and suggestions for improvement in JSON format:
        {{
            "meets_criteria": true/false,
            "feedback": "string",
            "suggestions": ["string", ...]
        }}
        """
        
        try:
            response = completion_with_backoff(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a reviewer agent for AI pipeline flows. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            response_content = response.choices[0].message.content.strip()
            print(f"ReviewerAgent: Raw API response: {response_content}")
            
            try:
                result = json.loads(response_content)
                print(f"ReviewerAgent: Parsed result: {result}")
                return result
            except json.JSONDecodeError:
                print("ReviewerAgent: JSON decoding failed, attempting to extract JSON from response")
                json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    print(f"ReviewerAgent: Extracted result: {result}")
                    return result
                else:
                    print("ReviewerAgent: No valid JSON found in response")
                    raise ValueError("Unable to extract valid JSON from the response")
        
        except Exception as e:
            print(f"ReviewerAgent: Error occurred: {str(e)}")
            raise

class NexusFlow:
    def __init__(self):
        self.requirement_agent = RequirementAgent()
        self.planner_agent = PlannerAgent()
        self.task_agent = TaskAgent()
        self.connection_agent = ConnectionAgent()
        self.reviewer_agent = ReviewerAgent()

    def generate_flow(self, user_input: str) -> Dict[str, Any]:
        try:
            print(f"NexusFlow: Starting flow generation for input: {user_input}")
            
            # Step 1: Gather requirements
            print("NexusFlow: Step 1 - Gathering requirements")
            user_goal = self.requirement_agent.gather_requirements(user_input)
            print(f"NexusFlow: User goal created: {asdict(user_goal)}")
            
            # Step 2: Create a plan
            print("NexusFlow: Step 2 - Creating plan")
            tasks = self.planner_agent.create_plan(user_goal)
            print(f"NexusFlow: Plan created with {len(tasks)} tasks")
            
            # Step 3: Execute tasks
            print("NexusFlow: Step 3 - Executing tasks")
            nodes = []
            for i, task in enumerate(tasks):
                print(f"NexusFlow: Executing task {i+1}/{len(tasks)}")
                node = self.task_agent.execute_task(task)
                nodes.append(node)
            print(f"NexusFlow: {len(nodes)} nodes created")
            
            # Step 4: Connect nodes
            print("NexusFlow: Step 4 - Connecting nodes")
            flow = self.connection_agent.connect_nodes(nodes)
            print("NexusFlow: Nodes connected")
            
            # Step 5: Review the flow
            print("NexusFlow: Step 5 - Reviewing the flow")
            review = self.reviewer_agent.review_flow(flow, user_goal)
            print("NexusFlow: Flow reviewed")
            
            print("NexusFlow: Flow generation completed successfully")
            return {
                "user_goal": asdict(user_goal),
                "flow": flow,
                "review": review
            }
           
        except Exception as e:
            print(f"ChainBuddy: Error in generate_flow: {str(e)}")
            return {
                "error": str(e),
                "user_goal": asdict(user_goal) if 'user_goal' in locals() else None,
                "flow": None,
                "review": None
            }


def main():
    st.title("NexusFlow: AI Pipeline Generator")
    
    st.write("Welcome to NexusFlow! Describe the AI pipeline you want to create, and I'll generate a flow for you.")
    
    user_input = st.text_area("Describe your desired AI pipeline:", height=150)
    
    if st.button("Generate Flow"):
        if user_input:
            with st.spinner("Generating your AI pipeline flow..."):
                nexus_flow = NexusFlow()
                result = nexus_flow.generate_flow(user_input)
                
                if "error" in result:
                    st.error(f"An error occurred: {result['error']}")
                else:
                    st.success("Flow generated successfully!")
                    
                    # Display User Goal
                    if result.get("user_goal"):
                        st.subheader("User Goal")
                        st.json(result["user_goal"])
                    
                    # Display Flow
                    if result.get("flow"):
                        st.subheader("Generated Flow")
                        st.json(result["flow"])
                    
                    # Display Review
                    if result.get("review"):
                        st.subheader("Flow Review")
                        st.json(result["review"])
                    
                    # Offer download of the full JSON
                    st.download_button(
                        label="Download Full JSON",
                        data=json.dumps(result, indent=2),
                        file_name="nexusflow_pipeline.json",
                        mime="application/json"
                    )
        else:
            st.warning("Please enter a description of your desired AI pipeline.")

if __name__ == "__main__":
    main()
