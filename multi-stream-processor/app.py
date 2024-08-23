import os
from openai import OpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_random_exponential
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import csv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    return client.chat.completions.create(**kwargs)

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def embedding_with_backoff(**kwargs):
    return client.embeddings.create(**kwargs)

def get_embedding(text):
    print(text)
    result = embedding_with_backoff(model="text-embedding-ada-002", input=text)
    return result.data[0].embedding

def generate_code(prompt):
    response = completion_with_backoff(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Generate Python code for: {prompt}"}]
    )
    return response.choices[0].message.content

def cosine_sim(a, b):
    return cosine_similarity([a], [b])[0][0]

def multi_stream_code_search(query, functions, classes):
    augmented_query = f"Python code for: {query}"
    query_embedding = get_embedding(augmented_query)
    function_embeddings = [get_embedding(func) for func in functions]
    class_embeddings = [get_embedding(cls) for cls in classes]
    
    # Stream 1
    stream1_results = sorted(range(len(function_embeddings)), 
                             key=lambda i: cosine_sim(query_embedding, function_embeddings[i]), 
                             reverse=True)[:3]
    
    # Stream 2
    generated_code = generate_code(augmented_query)
    code_embedding = get_embedding(generated_code)
    stream2_func_results = sorted(range(len(function_embeddings)), 
                                  key=lambda i: cosine_sim(code_embedding, function_embeddings[i]), 
                                  reverse=True)[:3]
    stream2_class_results = sorted(range(len(class_embeddings)), 
                                   key=lambda i: cosine_sim(code_embedding, class_embeddings[i]), 
                                   reverse=True)[:3]
    
    # Stream 3 (simplified)
    component_embeddings = [get_embedding(generated_code)]
    stream3_results = [max(range(len(function_embeddings)), 
                           key=lambda i: cosine_sim(comp_emb, function_embeddings[i])) 
                       for comp_emb in component_embeddings]
    
    final_set = set(stream1_results + stream2_func_results + [i + len(functions) for i in stream2_class_results] + stream3_results)
    return list(final_set)

def direct_embedding_search(query, functions, classes):
    query_embedding = get_embedding(query)
    all_code = functions + classes
    all_embeddings = [get_embedding(code) for code in all_code]
    
    similarities = [cosine_sim(query_embedding, emb) for emb in all_embeddings]
    top_5 = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:5]
    return top_5

# Complex, real-life code snippets
functions = [
    """
    def quick_sort(arr):
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return quick_sort(left) + middle + quick_sort(right)
    """,
    """
    def fibonacci(n, memo={}):
        if n in memo:
            return memo[n]
        if n <= 2:
            return 1
        memo[n] = fibonacci(n-1, memo) + fibonacci(n-2, memo)
        return memo[n]
    """,
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    
    def analyze_stock_data(file_path):
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        
        # Calculate moving averages
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()
        
        # Plot the data
        plt.figure(figsize=(12,6))
        plt.plot(df.index, df['Close'], label='Close Price')
        plt.plot(df.index, df['MA50'], label='50-day MA')
        plt.plot(df.index, df['MA200'], label='200-day MA')
        plt.title('Stock Price Analysis')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.show()
        
        return df
    """,
    """
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, classification_report
    
    def train_random_forest(X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_classifier.fit(X_train, y_train)
        
        y_pred = rf_classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred)
        
        return rf_classifier, accuracy, report
    """,
    """
    import requests
    from bs4 import BeautifulSoup
    
    def scrape_news_headlines(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.find_all('h2', class_='headline')
        return [headline.text.strip() for headline in headlines]
    """
]

classes = [
    """
    class BinarySearchTree:
        def __init__(self, value):
            self.value = value
            self.left = None
            self.right = None

        def insert(self, value):
            if value < self.value:
                if self.left is None:
                    self.left = BinarySearchTree(value)
                else:
                    self.left.insert(value)
            else:
                if self.right is None:
                    self.right = BinarySearchTree(value)
                else:
                    self.right.insert(value)

        def search(self, value):
            if value == self.value:
                return True
            elif value < self.value and self.left:
                return self.left.search(value)
            elif value > self.value and self.right:
                return self.right.search(value)
            return False
    """,
    """
    import threading
    
    class ThreadSafeCounter:
        def __init__(self):
            self._value = 0
            self._lock = threading.Lock()

        def increment(self):
            with self._lock:
                self._value += 1

        def decrement(self):
            with self._lock:
                self._value -= 1

        @property
        def value(self):
            with self._lock:
                return self._value
    """
]

# Evaluation
queries = [
    "implement quicksort algorithm",
    "create a function for fibonacci sequence with memoization",
    "analyze stock market data using pandas and matplotlib",
    "train a random forest classifier",
    "web scraping to get news headlines",
    "implement a binary search tree",
    "create a thread-safe counter class"
]

# Function to get snippet names
def get_snippet_names(indices, functions, classes):
    all_snippets = functions + classes
    return [all_snippets[i].split('\n')[1].strip() for i in indices]

# CSV generation
with open('code_search_comparison.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Query", "Multi-Stream Architecture Results", "Direct Embedding Results"])

    for query in queries:
        multi_stream_results = multi_stream_code_search(query, functions, classes)
        direct_results = direct_embedding_search(query, functions, classes)

        multi_stream_names = get_snippet_names(multi_stream_results, functions, classes)
        direct_names = get_snippet_names(direct_results, functions, classes)

        writer.writerow([query, ", ".join(multi_stream_names[:2]), ", ".join(direct_names[:2])])

print("CSV file 'code_search_comparison.csv' has been created with the comparison results.")

# Print results
print("\nMulti-Stream Architecture Results:")
for query in queries:
    results = multi_stream_code_search(query, functions, classes)
    print(f"\nQuery: {query}")
    print(f"Relevant snippet indices: {results}")
    print(f"Snippet names: {get_snippet_names(results, functions, classes)}")

print("\nDirect Embedding Approach Results:")
for query in queries:
    results = direct_embedding_search(query, functions, classes)
    print(f"\nQuery: {query}")
    print(f"Relevant snippet indices: {results}")
    print(f"Snippet names: {get_snippet_names(results, functions, classes)}")
