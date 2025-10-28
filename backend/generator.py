# import os
# import google.generativeai as genai
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # --- Configuration ---
# API_KEY = os.getenv("GOOGLE_API_KEY")
# if not API_KEY:
#     raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")

# genai.configure(api_key=API_KEY)
# model = genai.GenerativeModel('gemini-pro')

# # This is the core prompt for our RAG system
# PROMPT_TEMPLATE = """
# CONTEXT:
# {context}

# QUESTION:
# {question}

# Based on the context provided, answer the question. The answer should be concise and directly based on the information in the context.
# """

# def generate_answer(query: str, context_chunks: list):
#     """Synthesizes an answer using the retrieved context."""
    
#     # Combine the text from all context chunks
#     context_str = "\n---\n".join([chunk['text'] for chunk in context_chunks])
    
#     # Format the final prompt
#     prompt = PROMPT_TEMPLATE.format(context=context_str, question=query)
    
#     try:
#         response = model.generate_content(prompt)
#         return response.text
#     except Exception as e:
#         print(f"Error during generation: {e}")
#         return "Sorry, I was unable to generate an answer."

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")

genai.configure(api_key=API_KEY)

# --- Use a placeholder model for now ---
# We will replace this with a name from the list printed below.
MODEL_NAME_PLACEHOLDER = 'gemma-3-27b-it' # Keep this as a placeholder
model = genai.GenerativeModel(MODEL_NAME_PLACEHOLDER)

PROMPT_TEMPLATE = """
CONTEXT:
{context}

QUESTION:
{question}

Based on the context provided, answer the question. The answer should be concise and directly based on the information in the context.
"""

def generate_answer(query: str, context_chunks: list):
    """Synthesizes an answer using the retrieved context."""
    context_str = "\n---\n".join([chunk['text'] for chunk in context_chunks])
    prompt = PROMPT_TEMPLATE.format(context=context_str, question=query)
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error during generation: {e}")
        return "Sorry, I was unable to generate an answer."

# --- TEMPORARY DEBUGGING SECTION ---
# This code will run once when the application starts.
print("\n" + "="*50)
print("AVAILABLE GENERATIVE MODELS:")
try:
    for m in genai.list_models():
        # Check if the model supports the 'generateContent' method
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Could not list models. Error: {e}")
print("="*50 + "\n")
# --- END DEBUGGING SECTION ---