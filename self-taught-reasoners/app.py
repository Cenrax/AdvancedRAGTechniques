import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    return client.chat.completions.create(**kwargs)

class DirectResponse:
   
    def __init__(self, model="gpt-4o-mini", temperature=0.7):
        self.model = model
        self.temperature = temperature

    def call_openai(self, prompt):
        response = completion_with_backoff(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )
        return response.choices[0].message.content
    
class SelfTaught:
    def __init__(self, model="gpt-4o-mini", temperature=0.7):
        self.model = model
        self.temperature = temperature

    def call_openai(self, prompt):
        response = completion_with_backoff(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )
        return response.choices[0].message.content

    def identify_information(self, problem):
        prompt = f"""[QUESTION]
                {problem}

            List the necessary information that one must know for solving the above question. Your response should be in an abstractive manner."""
        print("Problem",problem)
        return self.call_openai(prompt)

    def generate_pseudo_problem(self, problem, information):
        prompt = f"""[QUESTION]
                    {problem}

                    [INFORMATION]
                    {information}

                    Based on the above information, generate a new question that addresses similar information/knowledge with higher relevance and no ambiguity."""
        return self.call_openai(prompt)

    def generate_pseudo_solution(self, pseudo_problem):
        prompt = f"""[QUESTION]
            {pseudo_problem}

        Solve this question step by step. At the end, provide your confidence level (0-100) for your answer."""
        solution = self.call_openai(prompt)

        # Use regex to find the confidence score
        match = re.search(r"confidence level.*?(\d+)", solution, re.IGNORECASE)
        if match:
            confidence = int(match.group(1))
        else:
            # If no confidence score is found, assume a low score
            confidence = 0

        return solution, confidence

    def solve_problem(self, problem, demonstrations):
        prompt = f"""[QUESTION]
        {problem}

        Here are some relevant examples:

        {demonstrations}

        Now, solve the original question step by step."""
        return self.call_openai(prompt)

    def run(
        self, problem, num_demonstrations=3, confidence_threshold=90, max_attempts=5
    ):
        information = self.identify_information(problem)
        demonstrations = []

        for index in range(num_demonstrations):
            pseudo_problem = self.generate_pseudo_problem(problem, information)

            print("Index of Psuedo Problem",index)
            print("Pseudo Problem", pseudo_problem)
            for _ in range(max_attempts):
                pseudo_solution, confidence = self.generate_pseudo_solution(
                    pseudo_problem
                )
                
                print("Solution", pseudo_solution)
                
                print("Confidence",confidence)
                if confidence >= confidence_threshold:
                    demonstrations.append(
                        f"Problem: {pseudo_problem}\nSolution: {pseudo_solution}\n"
                    )
                    break

            if len(demonstrations) < _ + 1:
                demonstrations.append(
                    f"Problem: {pseudo_problem}\nSolution: {pseudo_solution}\n"
                )

        return self.solve_problem(problem, "\n".join(demonstrations))

# Example usage
if __name__ == "__main__":
    problem = """You bought a limousine for $98,000 and are planning to rent it for weddings, ceremonies 
and parties at $245 per hour. If you estimate the car will be hired for 2 hours a day on 
average, with daily costs at about $50, what is the estimated yearly yield on your investment 
if you work all year round, i.e. every day of the year, including any festivities and 
weekends? A) 164% (B) 1.64% (C) 0.45% (D) 183% """
    self_taught = SelfTaught()
    solution = self_taught.run(problem)
    
    direct_response = DirectResponse()
    print("Solution", direct_response.call_openai(problem))
    # print(f"Problem: {problem}")
    print(f"Solution: {solution}")
