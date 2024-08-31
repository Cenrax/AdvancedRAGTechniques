import os
from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential
from docx import Document
import nltk
from nltk.tokenize import sent_tokenize
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
import uuid

nltk.download('punkt_tab')
# Download necessary NLTK data
#nltk.download('punkt',download_dir="C:\\UsersSubham\\Desktop\\amentities\\code\\asyncCalls\\venv\\nltk_data")

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

def read_docx(file_path):
    """
    Read content from a docx file.
    """
    doc = Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def chunk_text(text, max_chunk_size=4000):
    """
    Split the text into chunks of approximately max_chunk_size tokens.
    """
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        sentence_size = len(sentence.split())
        if current_size + sentence_size > max_chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_size = sentence_size
        else:
            current_chunk.append(sentence)
            current_size += sentence_size
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def generate_margin(chunk):
    """
    Generate a margin (summary) for a given chunk of text.
    """
    response = completion_with_backoff(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": f"Summarize the following text in 2-3 sentences, focusing on key information:\n\n{chunk}"}
        ]
    )
    return response.choices[0].message.content

def get_embedding(text):
    """
    Get the embedding for a given text.
    """
    response = embedding_with_backoff(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def store_in_qdrant(chunk, margin, embedding):
    """
    Store the chunk, margin, and embedding in Qdrant.
    """
    qdrant_client.upsert(
        collection_name="situational_awareness",
        points=[
            {
                "id": str(uuid.uuid4()),
                "vector": embedding,
                "payload": {
                    "chunk": chunk,
                    "margin": margin
                }
            }
        ]
    )

def process_book(file_path):
    """
    Process the book: read, chunk, generate margins, create embeddings, and store in Qdrant.
    """
    # Read the document
    print("Reading the document...")
    text = read_docx(file_path)
    
    # Create Qdrant collection if it doesn't exist
    collections = qdrant_client.get_collections().collections
    if not any(collection.name == "situational_awareness" for collection in collections):
        qdrant_client.create_collection(
            collection_name="situational_awareness",
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )
        print("Created 'situational_awareness' collection in Qdrant.")
    
    # Process the text
    chunks = chunk_text(text)
    print(f"Document split into {len(chunks)} chunks.")
    
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        
        # Generate margin
        margin = generate_margin(chunk)
        
        # Generate embedding for the chunk
        embedding = get_embedding(chunk)
        
        # Store in Qdrant
        store_in_qdrant(chunk, margin, embedding)
        
        if i+1 == 50:
            break
        
    print("Processing complete. All chunks stored in Qdrant.")

# Main execution
if __name__ == "__main__":
    book_path = "assets/situationalawareness.docx"
    process_book(book_path)
