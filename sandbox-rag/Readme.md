

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


### Chunk Visualizer

It is a web-based application that allows you to visualize and analyze data stored in a Qdrant vector database. This tool is particularly useful for exploring embeddings, chunks, and associated metadata in your Qdrant collection.
#### Features

1. **Raw Data Display**: View the raw data fetched from your Qdrant collection, including vectors, chunks, and margins.

2. **Data Overview**: Displays a DataFrame with chunks and margins for a quick summary of your data.

3. **Embedding Visualization**: Creates a 2D scatter plot of your embeddings using t-SNE dimensionality reduction, allowing you to visualize the relationships between your vectors.

4. **Chunk and Margin Analysis**: 
   - Histogram of chunk lengths
   - Histogram of margin values

5. **Search Functionality**: Allows you to search for specific terms within the chunks.

6. **Vector Statistics**: Provides basic statistics about the vector lengths and their distribution.

7. **Similarity Search**: Performs a random similarity search to demonstrate how similar chunks can be found in your collection.

## Additional Information

- Make sure the Qdrant service is running before executing any scripts.
- All data will be stored in the `qdrant_storage` directory.
