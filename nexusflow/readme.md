# NexusFlow: AI Pipeline Generator

## Overview

NexusFlow is an intelligent assistant designed to help users create AI pipelines using natural language descriptions. It leverages the power of large language models (LLMs) to interpret user requirements, plan tasks, and generate a complete workflow for AI-driven data processing and analysis.

## Architecture Diagram
```
graph TD
    A[User] -->|Input| B[Streamlit Interface]
    B -->|User Query| C[NexusFlow]
    C -->|Extract Requirements| D[RequirementAgent]
    D -->|User Goal| E[PlannerAgent]
    E -->|Task List| F[TaskAgent]
    F -->|Nodes| G[ConnectionAgent]
    G -->|Connected Flow| H[ReviewerAgent]
    H -->|Review| C
    C -->|Generated Flow| B
    B -->|Display Results| A

    subgraph "OpenAI API"
        I[GPT-4o]
        J[GPT-4o-mini]
    end

    D -.->|API Call| I
    E -.->|API Call| I
    F -.->|API Call| J
    G -.->|API Call| J
    H -.->|API Call| I

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
    style E fill:#fbb,stroke:#333,stroke-width:2px
    style F fill:#fbb,stroke:#333,stroke-width:2px
    style G fill:#fbb,stroke:#333,stroke-width:2px
    style H fill:#fbb,stroke:#333,stroke-width:2px
    style I fill:#ff9,stroke:#333,stroke-width:2px
    style J fill:#ff9,stroke:#333,stroke-width:2px
```
## Features

- **Natural Language Interface**: Describe your AI pipeline needs in plain English.
- **Automated Pipeline Generation**: Converts user requirements into a structured flow.
- **Modular Architecture**: Utilizes specialized agents for each step of the pipeline creation process.
- **Extensible Design**: Easy to add new capabilities or modify existing ones.
- **Interactive Web Interface**: Built with Streamlit for easy use and visualization.

## Use Cases

NexusFlow can be used in various scenarios, including:

1. **Rapid Prototyping**: Quickly generate initial AI pipeline designs for proof-of-concept projects.
2. **Educational Tool**: Help students and beginners understand AI pipeline construction.
3. **Workflow Optimization**: Suggest improvements or alternatives to existing AI pipelines.
4. **Cross-domain Application**: Assist domain experts in creating AI pipelines without deep technical knowledge.

## Components

NexusFlow consists of several key components:

1. **RequirementAgent**: Interprets user input and extracts key requirements.
2. **PlannerAgent**: Creates a detailed plan based on the extracted requirements.
3. **TaskAgent**: Executes individual tasks in the plan, generating pipeline nodes.
4. **ConnectionAgent**: Connects the nodes to form a coherent flow.
5. **ReviewerAgent**: Evaluates the generated pipeline against the original requirements.
6. **NexusFlow**: The main class that orchestrates the entire process.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/nexusflow.git
   cd nexusflow
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key in a `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

Run the Streamlit app:

```
streamlit run nexusflow_app.py
```

Then, follow these steps:

1. Enter a description of your desired AI pipeline in the text area.
2. Click the "Generate Flow" button.
3. Wait for NexusFlow to process your request (this may take a few moments).
4. Review the generated pipeline, including the interpreted user goal, the flow structure, and the review feedback.
5. Download the generated JSON file for use with your preferred pipeline execution environment or for further modification.

## Limitations and Future Work

- Currently relies on the OpenAI API, which may have usage costs.
- The generated pipelines may require further refinement by domain experts.
- Future versions could include more specialized agents for specific AI tasks or domains.
- Integration with actual execution environments for the generated pipelines is a potential next step.

## Contributing

Contributions to NexusFlow are welcome! Please feel free to submit pull requests, create issues, or suggest new features.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

