import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class RecursiveQASystem:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def generate_subquestions(self, main_question: str, num_subquestions: int = 5) -> List[str]:
        """Generate subquestions for the main question."""
        prompt = f"""Given the main question: "{main_question}"
        Generate {num_subquestions} relevant sub questions that would help answer the main question.
        Return only the numbered list of sub questions."""

        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates relevant sub questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=1,
        )

        subquestions = completion.choices[0].message.content.strip().split('\n')
        print("Sub Questions", subquestions)
        return [q.split('. ', 1)[1] if '. ' in q else q for q in subquestions]

    def answer_question(self, question: str, context: Optional[str] = None, qa_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Generate an answer for a given question, considering context and Q&A history."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant that provides concise and accurate answers based on given information."},
            {"role": "user", "content": f"Question: {question}"}
        ]
        
        if context:
            messages.append({"role": "user", "content": f"Context: {context}"})
        
        if qa_history:
            qa_history_content = "Previous Q&A:\n" + "\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in qa_history])
            messages.append({"role": "user", "content": qa_history_content})
        
        messages.append({"role": "user", "content": "Please provide a concise and accurate answer based on the given information."})

        completion = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.5,
        )

        return completion.choices[0].message.content.strip()

    def recursive_qa(self, main_question: str) -> str:
        """Perform recursive Q&A to answer the main question."""
        subquestions = self.generate_subquestions(main_question)
        qa_history = []

        for subq in subquestions:
            answer = self.answer_question(subq, qa_history=qa_history)
            qa_history.append({"question": subq, "answer": answer})

        final_answer = self.answer_question(main_question, qa_history=qa_history)
        return final_answer

def main():
    # Example usage
    qa_system = RecursiveQASystem()
    main_question = "How ethics is important for society"
    
    print(f"Main Question: {main_question}")
    print("\nGenerating answer using recursive Q&A technique...")
    
    final_answer = qa_system.recursive_qa(main_question)
    
    print("\nFinal Answer:")
    print(final_answer)

if __name__ == "__main__":
    main()
