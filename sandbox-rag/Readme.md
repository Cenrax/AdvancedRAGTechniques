

# Sandbox RAG System

This README provides step-by-step instructions to set up and run a Qdrant-based Retrieval Augmented Generation (RAG) system.

## Prerequisites

1. **Docker:** Ensure Docker is installed and running on your system. You can download Docker from [here](https://www.docker.com/products/docker-desktop).
2. **Python Environment:** Make sure you have Python installed along with `pip`.

## Setup

### 1. Pull the Qdrant Docker Image

To get started, you need to pull the Qdrant Docker image from Docker Hub:

```bash
docker pull qdrant/qdrant
```

### 2. Run the Qdrant Docker Container

Run the following command to start the Qdrant service in a Docker container:

```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

This command will:
- Expose Qdrant on ports `6333` (for HTTP) and `6334` (for gRPC).
- Mount a local directory (`qdrant_storage`) to persist data.

### 3. Install Python Dependencies

Ensure you have all required Python packages by installing them via `pip`:

```bash
pip install -r requirements.txt
```

## Running the System

### 1. Run the Chunking Script

Before running the main RAG system, execute the `chunking.py` script to preprocess data:

```bash
python chunking.py
```

### 2. Run the RAG System

After chunking is complete, run the `rag-system.py` script to interact with the RAG system and ask questions:

```bash
python rag-system.py
```

## Usage

- Start by running the `chunking.py` script to prepare the data.
- Then, use the `rag-system.py` script to perform queries and retrieve augmented results.

## Additional Information

- Make sure the Qdrant service is running before executing any scripts.
- All data will be stored in the `qdrant_storage` directory.
