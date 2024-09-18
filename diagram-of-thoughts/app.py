import os
from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential
import json
import graphviz

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    return client.chat.completions.create(**kwargs)

class DiagramOfThought:
    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        self.conversation_history = []
        self.roles = ["proposer", "critic", "summarizer"]
        self.graph = graphviz.Digraph(comment='Diagram of Thought')
        self.graph.attr(rankdir='TB', size='8,8')
        self.node_count = 0

    def generate_response(self, role, prompt):
        messages = self.conversation_history + [
            {"role": "system", "content": f"You are now acting as the {role} in the Diagram of Thought process. Always enclose your response in <{role}> tags."},
            {"role": "user", "content": prompt}
        ]
        
        response = completion_with_backoff(
            model=self.model,
            messages=messages,
            max_tokens=300
        )
        
        content = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": content})
        return content

    def extract_role_content(self, response, role):
        start_tag = f"<{role}>"
        end_tag = f"</{role}>"
        start = response.find(start_tag)
        end = response.find(end_tag)
        if start != -1 and end != -1:
            return response[start + len(start_tag):end].strip()
        print(f"Warning: Could not extract {role} content. Using full response.")
        return response

    def add_node(self, role, content):
        self.node_count += 1
        node_id = f"{role}_{self.node_count}"
        label = f"{role.capitalize()}:\n{content[:50]}..."  # Truncate long content for readability
        color = {"proposer": "lightblue", "critic": "lightcoral", "summarizer": "lightgreen"}[role]
        self.graph.node(node_id, label, style="filled", fillcolor=color)
        return node_id

    def add_edge(self, from_node, to_node):
        self.graph.edge(from_node, to_node)

    def run(self, problem):
        print(f"Problem: {problem}\n")
        self.graph.attr(label=f'Problem: {problem}')
        iteration = 1
        prev_node = None
        while True:
            print(f"Iteration {iteration}")
            
            # Proposer
            proposer_prompt = f"Based on the current state of reasoning, propose the next step(s) to solve the problem: {problem}"
            proposer_response = self.generate_response("proposer", proposer_prompt)
            proposition = self.extract_role_content(proposer_response, "proposer")
            print(f"Proposer: {proposition}\n")
            proposer_node = self.add_node("proposer", proposition)
            if prev_node:
                self.add_edge(prev_node, proposer_node)
            
            # Critic
            critic_prompt = f"Critically evaluate the following proposition: {proposition}"
            critic_response = self.generate_response("critic", critic_prompt)
            critique = self.extract_role_content(critic_response, "critic")
            print(f"Critic: {critique}\n")
            critic_node = self.add_node("critic", critique)
            self.add_edge(proposer_node, critic_node)
            
            # Summarizer
            summarizer_prompt = "Review the current state of reasoning. Synthesize the validated propositions and determine if a final answer can be reached. If not, indicate what aspects still need to be addressed."
            summarizer_response = self.generate_response("summarizer", summarizer_prompt)
            summary = self.extract_role_content(summarizer_response, "summarizer")
            print(f"Summarizer: {summary}\n")
            summarizer_node = self.add_node("summarizer", summary)
            self.add_edge(critic_node, summarizer_node)
            
            if "final answer" in summary.lower():
                print("Final Answer:", summary)
                break
            
            iteration += 1
            prev_node = summarizer_node

if __name__ == "__main__":
    dot = DiagramOfThought()
    problem = "Imagine a perfect cube of solid gold. If the cube's volume is 1,000 cubic centimeters, and the price of gold is $50 per gram, what is the approximate value of the cube in US dollars? (Assume the density of gold is 19.3 grams per cubic centimeter, and round your answer to the nearest million dollars.)"
    dot.run(problem)
