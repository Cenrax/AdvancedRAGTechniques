# Diagram of Thought (DoT) Implementation

## Overview

This project implements the Diagram of Thought (DoT) framework, a novel approach to modeling iterative reasoning in large language models (LLMs). DoT organizes propositions, critiques, refinements, and verifications into a cohesive Directed Acyclic Graph (DAG) structure, allowing for complex reasoning pathways while maintaining logical consistency.

The implementation uses the OpenAI API to generate responses for different roles in the reasoning process and visualizes the reasoning chain using Graphviz.

## Features

- Iterative reasoning process with three distinct roles: Proposer, Critic, and Summarizer
- Integration with OpenAI's GPT models for generating responses
- Visualization of the reasoning process as a directed graph
- Error handling and retry mechanisms for robust operation

## Requirements

- Python 3.7+
- OpenAI API key
- Graphviz (for visualization)

## Installation



1. Install the required Python packages:
   ```
   pip install openai python-dotenv tenacity graphviz
   ```

2. Install Graphviz on your system:
   - On Ubuntu or Debian: `sudo apt-get install graphviz`
   - On macOS with Homebrew: `brew install graphviz`
   - On Windows: Download and install from [Graphviz's official website](https://graphviz.org/download/)

3. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Import the `DiagramOfThought` class from the main script:

   ```python
   from diagram_of_thought import DiagramOfThought
   ```

2. Create an instance of the `DiagramOfThought` class:

   ```python
   dot = DiagramOfThought()
   ```

3. Define your problem and run the reasoning process:

   ```python
   problem = "Your complex problem statement here"
   dot.run(problem)
   ```

4. Visualize the reasoning process:

   ```python
   dot.visualize()
   ```

## Example

```python
dot = DiagramOfThought()
problem = "Imagine a perfect cube of solid gold. If the cube's volume is 1,000 cubic centimeters, and the price of gold is $50 per gram, what is the approximate value of the cube in US dollars? (Assume the density of gold is 19.3 grams per cubic centimeter, and round your answer to the nearest million dollars.)"
dot.run(problem)
dot.visualize()
```

This will generate a PNG file named "diagram_of_thought.png" in your working directory, displaying the reasoning process as a directed graph.

## Customization

You can customize the behavior of the DoT implementation by modifying the following parameters in the `DiagramOfThought` class:

- `model`: Change the OpenAI model used (default is "gpt-3.5-turbo")
- `max_tokens`: Adjust the maximum number of tokens in the API responses

## Contributing

Contributions to improve the Diagram of Thought implementation are welcome. Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

