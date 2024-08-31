import os
from openai import OpenAI
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from tenacity import retry, stop_after_attempt, wait_random_exponential

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Qdrant client
qdrant_client = QdrantClient("localhost", port=6333)

# Retry decorators
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    return client.chat.completions.create(**kwargs)

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def embedding_with_backoff(**kwargs):
    return client.embeddings.create(**kwargs)

def get_embedding(text):
    """
    Get the embedding for a given text.
    """
    response = embedding_with_backoff(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def search_similar_chunks(query, top_k=5):
    """
    Search for similar chunks in the Qdrant database.
    """
    query_vector = get_embedding(query)
    search_result = qdrant_client.search(
        collection_name="situational_awareness",
        query_vector=query_vector,
        limit=top_k
    )
    return search_result

def format_context(similar_chunks):
    """
    Format the similar chunks and their margins into a context string.
    """
    context = ""
    for i, chunk in enumerate(similar_chunks):
        context += f"Chunk {i+1}:\n"
        context += f"Content: {chunk.payload['chunk']}\n"
        context += f"Summary: {chunk.payload['margin']}\n\n"
    return context

def generate_answer(query, context):
    """
    Generate an answer using the GPT model with the given context.
    """
    response = completion_with_backoff(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context. If the answer cannot be found in the context, say so."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"}
        ]
    )
    return response.choices[0].message.content

def rag_query(query):
    """
    Perform a RAG query: retrieve similar chunks, format context, and generate an answer.
    """
    print(f"Query: {query}")
    print("Searching for relevant chunks...")
    similar_chunks = search_similar_chunks(query)
    
    print("Formatting context...")
    context = format_context(similar_chunks)
    
    print("Generating answer...")
    answer = generate_answer(query, context)
    
    return answer

def interactive_rag():
    """
    Run an interactive RAG session.
    """
    print("Welcome to the Situational Awareness RAG system!")
    print("You can ask questions about the book, or type 'quit' to exit.")
    
    while True:
        query = input("\nEnter your question: ")
        if query.lower() == 'quit':
            print("Thank you for using the RAG system. Goodbye!")
            break
        
        answer = rag_query(query)
        print("\nAnswer:", answer)

if __name__ == "__main__":
    interactive_rag()
