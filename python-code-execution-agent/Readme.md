# AgentPro

AgentPro is an intelligent Python code generator and execution system that leverages OpenAI's GPT models to create and run Python scripts based on user prompts.

## Table of Contents
1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Usage](#usage)
5. [How It Works](#how-it-works)
6. [Configuration](#configuration)
7. [Error Handling](#error-handling)


## Features

- Generate Python code from natural language prompts
- Automatically install required libraries
- Execute generated code in a safe environment
- Handle errors and retry code generation
- Logging for debugging and monitoring

## Requirements

- Python 3.6+
- OpenAI API key

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/agentpro.git
   cd agentpro
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key:
   Create a `.env` file in the project root and add your API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

Run the main script:

```
python app.py
```

Follow the prompts to enter your code generation requests. Type 'exit' to quit the program.

## How It Works

1. The user provides a prompt describing the desired Python code.
2. AgentPro uses OpenAI's GPT model to generate Python code based on the prompt.
3. The system analyzes the generated code to identify required libraries.
4. Required libraries are automatically installed using pip.
5. The code is executed in a temporary file within the current working directory.
6. Output and errors are captured and displayed to the user.
7. If errors occur, the system can retry code generation with error information.

## Configuration

- Modify the `OpenAI` client initialization in the `AgentPro` class to change the API key source or other settings.
- Adjust the `max_retries` parameter in the `run` method to change the number of retry attempts for code generation.

## Error Handling

AgentPro implements robust error handling:
- Retries API calls with exponential backoff
- Catches and logs exceptions during code generation and execution
- Provides informative error messages to the user

