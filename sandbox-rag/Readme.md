## Prerequisites

`
docker pull qdrant/qdrant
`
`
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
`

pip install -r requirements.txt

1. First run chunking.py
2. Run rag-system.py to ask question
