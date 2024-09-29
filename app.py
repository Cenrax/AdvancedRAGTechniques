import os
import platform
from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential
import subprocess
import tempfile
import re
import importlib
import sys
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AgentPro:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not self.client.api_key:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def completion_with_backoff(self, **kwargs):
        return self.client.chat.completions.create(**kwargs)

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def embedding_with_backoff(self, **kwargs):
        return self.client.embeddings.create(**kwargs)

    def generate_code(self, prompt, error_info=None):
        try:
            messages = [
                {"role": "system", "content": "You are a Python code generator. Respond only with executable Python code, no explanations or comments except for required pip installations at the top."},
                {"role": "user", "content": f"Generate Python code to {prompt}. If you need to use any external libraries, include a comment at the top of the code listing the required pip installations."}
            ]
            
            if error_info:
                messages.append({"role": "user", "content": f"The previous code generated an error. Please fix the following error and regenerate the code: {error_info}"})

            response = self.completion_with_backoff(
                model="gpt-4o",
                messages=messages,
                max_tokens=4000,
                temperature=0.7,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            code = response.choices[0].message.content.strip()
            code = re.sub(r'^```python\n|^```\n|```$', '', code, flags=re.MULTILINE)
            code_lines = code.split('\n')
            while code_lines and not (code_lines[0].startswith('import') or code_lines[0].startswith('from') or code_lines[0].startswith('#')):
                code_lines.pop(0)
            return '\n'.join(code_lines)
        except Exception as e:
            logging.error(f"Error generating code: {str(e)}")
            raise

    def get_required_libraries(self, code):
        # Improved regex pattern to handle multiple libraries in a single line
        libraries = re.findall(r'#\s*(?:Required pip installations:|pip install)\s*((?:[\w-]+(?:\s*,\s*)?)+)', code)
        if libraries:
            # Flatten the list and split by commas if present
            libraries = [lib.strip() for sublist in libraries for lib in sublist.split(',')]
        
        if not libraries:
            # If regex fails, use LLM to extract libraries
            response = self.completion_with_backoff(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that identifies required Python libraries from code."},
                    {"role": "user", "content": f"Please list all the external libraries that need to be installed for this code to run. Respond with only the library names, separated by commas:\n\n{code}"}
                ],
                max_tokens=100,
                temperature=0.3
            )
            libraries = [lib.strip() for lib in response.choices[0].message.content.split(',')]
        logging.info("Libraries",libraries)
        return libraries

    def install_libraries(self, code):
        libraries = self.get_required_libraries(code)
        if libraries:
            logging.info("Installing required libraries...")
            for lib in libraries:
                try:
                    importlib.import_module(lib.replace('-', '_'))
                    logging.info(f"{lib} is already installed.")
                except ImportError:
                    logging.info(f"Installing {lib}...")
                    try:
                        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
                    except subprocess.CalledProcessError as e:
                        logging.error(f"Failed to install {lib}: {str(e)}")
                        raise
            logging.info("Libraries installed successfully.")

    def execute_code(self, code):
        current_dir = os.getcwd()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=current_dir, delete=False, encoding='utf-8') as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        try:
            if platform.system() == "Windows":
                activate_cmd = r"venv\Scripts\activate.bat"
            else:
                activate_cmd = "source venv/bin/activate"

            run_script = f"python {os.path.basename(temp_file_path)}"
            full_command = f"{activate_cmd} && {run_script}"
            
            if platform.system() == "Windows":
                result = subprocess.run(full_command, 
                                        shell=True,
                                        cwd=current_dir,
                                        capture_output=True, 
                                        text=True, 
                                        timeout=30)
            else:
                result = subprocess.run(['/bin/bash', '-c', full_command],
                                        cwd=current_dir,
                                        capture_output=True, 
                                        text=True, 
                                        timeout=30)
            
            output = result.stdout
            error = result.stderr
        except subprocess.TimeoutExpired:
            output = ""
            error = "Execution timed out after 30 seconds."
        except Exception as e:
            output = ""
            error = f"An error occurred during execution: {str(e)}"
        finally:
            os.unlink(temp_file_path)

        return output, error

    def run(self, prompt, max_retries=3):
        for attempt in range(max_retries):
            try:
                logging.info(f"Generating code for: {prompt}")
                code = self.generate_code(prompt)
                logging.info("Generated code:\n%s", code)

                self.install_libraries(code)

                logging.info("Executing code...")
                output, error = self.execute_code(code)

                if output:
                    logging.info("Output:\n%s", output)
                if error:
                    logging.error("Error:\n%s", error)
                    if attempt < max_retries - 1:
                        logging.info(f"Retrying... (Attempt {attempt + 2}/{max_retries})")
                        continue
                
                return output, error
            except Exception as e:
                logging.error(f"An error occurred during execution: {str(e)}")
                if attempt < max_retries - 1:
                    logging.info(f"Retrying... (Attempt {attempt + 2}/{max_retries})")
                    continue
                raise
        
        return None, f"Failed to generate valid code after {max_retries} attempts."

def main():
    agent = AgentPro()
    
    print("Welcome to AgentPro!")
    print("Enter your prompt below. Type 'exit' to quit.")
    
    while True:
        prompt = input("\nEnter your prompt: ")
        
        if prompt.lower() == 'exit':
            print("Thank you for using AgentPro. Goodbye!")
            break
        
        output, error = agent.run(prompt)
        
        print("\nOutput:")
        print(output)
        
        if error:
            print("\nError:")
            print(error)

if __name__ == "__main__":
    main()
