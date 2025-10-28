import streamlit as st
import requests
import pandas as pd

# --- IMPORTANT CONFIGURATION ---
# Replace this with the public IP address or domain name of your remote server.
# Do NOT use localhost or 127.0.0.1 if your browser is on a different machine.
SERVER_IP_ADDRESS = "10.10.3.141" 
API_URL = f"http://{SERVER_IP_ADDRESS}:8000/query"

# --- Page Setup ---
st.set_page_config(layout="wide")
st.title("🧠 PromptCache: A Harry Potter RAG System")
st.write("Ask a question about the Harry Potter books and see the semantic cache in action.")

# --- Session State Initialization ---
# This is to keep track of metrics across multiple queries.
if 'cache_hits' not in st.session_state:
    st.session_state.cache_hits = 0
if 'total_queries' not in st.session_state:
    st.session_state.total_queries = 0
if 'latencies' not in st.session_state:
    st.session_state.latencies = []

# --- Main Application ---
with st.form("query_form"):
    prompt = st.text_input("Enter your question:", "Who tried to steal the Sorcerer's Stone?")
    submitted = st.form_submit_button("Submit Query")

if submitted and prompt:
    with st.spinner("Searching the Hogwarts Library..."):
        payload = {"prompt": prompt}
        try:
            response = requests.post(API_URL, json=payload)
            st.session_state.total_queries += 1
            
            if response.status_code == 200:
                data = response.json()
                
                # Update metrics based on the response
                if data['source'] == 'cache':
                    st.session_state.cache_hits += 1
                st.session_state.latencies.append(float(data['latency_ms']))
                
                # Display results
                st.success(f"Query completed in **{data['latency_ms']} ms**. Data sourced from **{data['source'].upper()}**.")
                st.subheader("Generated Answer:")
                st.markdown(data['generated_answer'])

                st.subheader("Retrieved Sources:") # Renamed for clarity
                for i, res in enumerate(data['results']):
                    with st.expander(f"Source {i+1}: {res['source']}"):
                        st.markdown(f"*{res['text']}*")
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            st.error(f"Connection Error: Could not connect to the backend at {API_URL}. Is the backend server running?")

# --- Sidebar for Metrics ---
st.sidebar.header("📊 System Metrics")
if st.session_state.latencies:
    hit_rate = (st.session_state.cache_hits / st.session_state.total_queries) * 100
    avg_latency = sum(st.session_state.latencies) / len(st.session_state.latencies)
    
    st.sidebar.write(f"**Total Queries:** {st.session_state.total_queries}")
    st.sidebar.write(f"**Cache Hits:** {st.session_state.cache_hits}")
    st.sidebar.metric(label="Cache Hit Rate", value=f"{hit_rate:.2f}%")
    st.sidebar.metric(label="Average Latency", value=f"{avg_latency:.2f} ms")

    st.sidebar.subheader("Latency Over Time (ms)")
    latency_df = pd.DataFrame(st.session_state.latencies, columns=['Latency (ms)'])
    st.sidebar.line_chart(latency_df)
else:
    st.sidebar.write("No queries made yet.")