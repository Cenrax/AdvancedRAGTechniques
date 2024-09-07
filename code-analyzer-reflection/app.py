import os
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Retry decorators for API calls
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    return client.chat.completions.create(**kwargs)

REFLECTION_PROMPT_TEMPLATE = """
You are an AI assistant specialized in code analysis. Your task is to analyze the given code for potential bugs, inefficiencies, and suggest improvements. Follow this exact format:

<thinking>
Begin by outlining your approach to analyzing the code. Break down your process into steps.
</thinking>

<reflection>
If you need to clarify or correct any part of your initial thinking, do so here. This step is optional if no correction is needed.
</reflection>

<thinking>
Continue your analysis, incorporating any reflections or corrections. Identify potential issues and areas for improvement.
</thinking>

<output>
Provide your final analysis, including:
1. Identified bugs or potential issues
2. Suggestions for improvements
3. A brief explanation of the changes and their benefits
</output>

Now, please analyze the following code:
{code_snippet}

Remember to use the exact format with <thinking>, <reflection> (if needed), and <output> tags as shown above.
"""

VALIDATOR_PROMPT = """
You are a validator AI specialized in code review. Your job is to check if the given code analysis is thorough, accurate, and helpful. Provide a confidence score between 0 and 100.

Original code snippet:
{code_snippet}

Generated analysis:
{generated_analysis}

Please evaluate the analysis and provide:
1. A brief explanation of whether the analysis is thorough, accurate, and helpful.
2. A confidence score between 0 and 100.

Your response should be in the format:
<explanation>
Your explanation here
</explanation>
<confidence_score>
Your confidence score here (just the number)
</confidence_score>
"""

CORRECTOR_PROMPT = """
You are a corrector AI specialized in improving code analysis. Your job is to enhance the given analysis to ensure it's thorough, accurate, and helpful.

Original code snippet:
{code_snippet}

Generated analysis:
{generated_analysis}

Validator's explanation:
{validator_explanation}

Please provide an improved analysis that addresses any issues mentioned by the validator. Your goal is to achieve a confidence score above 90%.

Use the same format as the original analysis, with <thinking>, <reflection>, and <output> tags.
"""

def get_reflection_response(code_snippet):
    try:
        response = completion_with_backoff(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": REFLECTION_PROMPT_TEMPLATE},
                {"role": "user", "content": code_snippet}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def validate_response(code_snippet, generated_analysis):
    try:
        response = completion_with_backoff(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": VALIDATOR_PROMPT.format(
                    code_snippet=code_snippet, 
                    generated_analysis=generated_analysis
                )},
            ],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred during validation: {e}")
        return None

def correct_response(code_snippet, generated_analysis, validator_explanation):
    try:
        response = completion_with_backoff(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": CORRECTOR_PROMPT.format(
                    code_snippet=code_snippet,
                    generated_analysis=generated_analysis,
                    validator_explanation=validator_explanation
                )},
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred during correction: {e}")
        return None

def extract_confidence_score(validator_response):
    start = validator_response.find("<confidence_score>") + len("<confidence_score>")
    end = validator_response.find("</confidence_score>")
    return float(validator_response[start:end].strip())

def main(code_snippet):
    # Get initial response
    initial_response = get_reflection_response(code_snippet)
    if not initial_response:
        return "Failed to generate initial analysis."

    # Validate the response
    validation_result = validate_response(code_snippet, initial_response)
    if not validation_result:
        return "Failed to validate the analysis."

    confidence_score = extract_confidence_score(validation_result)

    if confidence_score >= 90:
        return f"Final analysis (confidence: {confidence_score}%):\n\n{initial_response}"
    else:
        # Extract explanation from validator's response
        start = validation_result.find("<explanation>") + len("<explanation>")
        end = validation_result.find("</explanation>")
        validator_explanation = validation_result[start:end].strip()

        # Correct the response
        corrected_response = correct_response(code_snippet, initial_response, validator_explanation)
        if not corrected_response:
            return "Failed to correct the analysis."

        # Validate the corrected response
        final_validation = validate_response(code_snippet, corrected_response)
        if not final_validation:
            return "Failed to validate the corrected analysis."

        final_confidence_score = extract_confidence_score(final_validation)

        return f"Final analysis (confidence: {final_confidence_score}%):\n\n{corrected_response}"

# Example usage
if __name__ == "__main__":
    code_snippet = """
    def factorial(n):
        if n == 0:
            return 1
        else:
            return n * factorial(n-1)

    def main():
        num = input("Enter a number: ")
        result = factorial(num)
        print(f"The factorial of {num} is {result}")

    if __name__ == "__main__":
        main()
    """
    result = main(code_snippet)
    print(result)
