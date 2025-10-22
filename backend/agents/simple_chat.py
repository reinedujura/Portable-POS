#!/usr/bin/env python3
"""
Simple working chat agent for testing
"""

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from pymongo import MongoClient

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"), 
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.2,
)

@tool
def post_data_from_db(query: str) -> str:
    """Fetch posts from MongoDB database when user asks about personal posts."""
    try:
        client = MongoClient(os.getenv("MONGODB_ATLAS_CLUSTER_URI"))
        db = client["example_db"]
        collection = db["posts"]
        posts = list(collection.find({}).limit(5))
        
        if posts:
            result = []
            for post in posts:
                post_info = f"Title: {post.get('title', 'N/A')}, Content: {post.get('content', 'N/A')}"
                result.append(post_info)
            return "\n".join(result)
        else:
            return "No posts found in the database."
    except Exception as e:
        return f"Error fetching data: {str(e)}"
    finally:
        client.close()

def simple_chat_agent(user_input: str) -> str:
    """Simple chat function that responds in Dr Seuss style"""
    
    # Check if user is asking about personal posts/database content
    if any(word in user_input.lower() for word in ['posts', 'database', 'personal', 'stored', 'my data']):
        # Use the database tool
        db_result = post_data_from_db.invoke({"query": user_input})
        
        # Create a Dr Seuss style response with the database info
        prompt = f"""You are Dr Seuss, a poetic AI assistant. The user asked: "{user_input}"
        
        Here's the information from the database: {db_result}
        
        Respond in Dr Seuss rhyming style, incorporating this database information."""
        
        response = llm.invoke(prompt)
        return response.content
    
    else:
        # Regular Dr Seuss response without tools
        prompt = f"""You are Dr Seuss, a poetic AI assistant that always responds in rhymes and whimsical style.
        
        The user said: "{user_input}"
        
        Respond in a fun, rhyming Dr Seuss style without using any tools or external data."""
        
        response = llm.invoke(prompt)
        return response.content

# Test function
if __name__ == "__main__":
    print("🎭 Dr Seuss AI Agent - Simple Test")
    print("=" * 40)
    
    # Test general question
    print("\n📝 Testing general question...")
    response1 = simple_chat_agent("What is the weather like today?")
    print(f"Response: {response1}")
    
    # Test database question  
    print("\n📝 Testing database question...")
    response2 = simple_chat_agent("Tell me about my personal posts")
    print(f"Response: {response2}")
    
    print("\n✅ Agent is working! You can now use the web interface.")