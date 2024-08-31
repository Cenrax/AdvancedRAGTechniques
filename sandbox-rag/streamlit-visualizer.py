import streamlit as st
import numpy as np
import pandas as pd
from qdrant_client import QdrantClient
from sklearn.manifold import TSNE
import plotly.express as px

# Initialize Qdrant client
@st.cache_resource
def init_qdrant_client():
    return QdrantClient("localhost", port=6333)

qdrant_client = init_qdrant_client()

st.title("Qdrant Data Visualizer")

# Fetch data from Qdrant
@st.cache_data
def fetch_qdrant_data(limit=1000):
    response = qdrant_client.scroll(
        collection_name="situational_awareness",
        limit=limit,
        with_vectors=True,
        with_payload=True
    )
    points = response[0]
    if not points:
        st.warning("No data found in the Qdrant collection.")
        return np.array([]), [], []
    vectors = np.array([point.vector for point in points])
    chunks = [point.payload['chunk'] for point in points]
    margins = [point.payload['margin'] for point in points]
    return vectors, chunks, margins

# Load data
vectors, chunks, margins = fetch_qdrant_data()

if len(vectors) == 0:
    st.warning("No data available. Please check your Qdrant collection.")
    st.stop()

# Display raw data
st.subheader("Raw Data")
if st.checkbox("Show raw data"):
    raw_data = [{"vector": v.tolist(), "chunk": c, "margin": m} for v, c, m in zip(vectors, chunks, margins)]
    st.write(raw_data)

# Create a DataFrame
df = pd.DataFrame({
    'chunk': chunks,
    'margin': margins
})

# Display DataFrame
st.subheader("Data Overview")
st.dataframe(df)

# Visualize embeddings
st.subheader("Embedding Visualization")

# Dimensionality reduction
@st.cache_data
def reduce_dimensions(vectors):
    n_samples = vectors.shape[0]
    perplexity = min(30, n_samples - 1)  # Ensure perplexity is valid
    if n_samples >= 5:  # t-SNE requires at least 5 samples
        tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity)
        return tsne.fit_transform(vectors)
    else:
        st.warning("Not enough data points for t-SNE. Displaying raw 2D projection.")
        return vectors[:, :2]  # Just take the first two dimensions

if vectors.shape[0] > 1:  # Check if we have more than one vector
    vectors_2d = reduce_dimensions(vectors)

    # Create a DataFrame for plotting
    plot_df = pd.DataFrame({
        'x': vectors_2d[:, 0],
        'y': vectors_2d[:, 1],
        'chunk': chunks,
        'margin': margins
    })

    # Create an interactive scatter plot
    fig = px.scatter(
        plot_df, 
        x='x', 
        y='y', 
        hover_data=['chunk', 'margin'],
        title='2D Visualization of Embeddings'
    )
    st.plotly_chart(fig)
else:
    st.warning("Not enough data points to create a meaningful visualization.")

# Chunk and Margin Analysis
st.subheader("Chunk and Margin Analysis")

if len(chunks) > 0:
    # Chunk length distribution
    st.write("Chunk Length Distribution")
    chunk_lengths = [len(chunk) for chunk in chunks]
    fig_chunk_len = px.histogram(chunk_lengths, nbins=20, title="Chunk Length Distribution")
    st.plotly_chart(fig_chunk_len)

    # Margin distribution
    st.write("Margin Distribution")
    fig_margin = px.histogram(margins, nbins=20, title="Margin Distribution")
    st.plotly_chart(fig_margin)
else:
    st.warning("Not enough data for chunk and margin analysis.")

# Search functionality
st.subheader("Search Chunks")
search_query = st.text_input("Enter a search term")
if search_query:
    filtered_df = df[df['chunk'].str.contains(search_query, case=False)]
    st.write(f"Found {len(filtered_df)} matches:")
    st.dataframe(filtered_df)

# Vector statistics
st.subheader("Vector Statistics")
if len(vectors) > 0:
    vector_lengths = np.linalg.norm(vectors, axis=1)
    st.write(f"Average vector length: {np.mean(vector_lengths):.2f}")
    st.write(f"Min vector length: {np.min(vector_lengths):.2f}")
    st.write(f"Max vector length: {np.max(vector_lengths):.2f}")

    fig_vector_len = px.histogram(vector_lengths, nbins=20, title="Vector Length Distribution")
    st.plotly_chart(fig_vector_len)
else:
    st.warning("Not enough data for vector statistics.")

# Similarity Search
st.subheader("Similarity Search")
if len(vectors) > 0:
    if st.button("Perform Random Similarity Search"):
        # Select a random vector
        random_index = np.random.randint(0, len(vectors))
        query_vector = vectors[random_index]
        
        # Perform similarity search
        search_results = qdrant_client.search(
            collection_name="situational_awareness",
            query_vector=query_vector.tolist(),
            limit=min(5, len(vectors))
        )
        
        st.write("Query chunk:")
        st.write(chunks[random_index])
        
        st.write("Similar chunks:")
        for result in search_results:
            st.write(f"Chunk: {result.payload['chunk']}")
            st.write(f"Similarity: {result.score:.4f}")
            st.write("---")
else:
    st.warning("Not enough data for similarity search.")
