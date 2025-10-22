import os
from langchain_core.tools import tool
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

@tool
def post_data_from_db(query: str) -> str:
    """
    Fetch posts from MongoDB database.

    ONLY use this tool when the user explicitly asks about:
    - Your personal posts
    - Posts from the database
    - Content you have written or saved
    - Blog posts or articles in your collection

    DO NOT use this tool for:
    - General knowledge questions
    - Greetings or casual conversation
    - Questions about topics not related to stored posts

    Args:
        query: The user's question about posts

    Returns:
        A formatted string of posts from the database or an error message.
    """
    try:
        client = MongoClient(os.getenv("MONGODB_ATLAS_CLUSTER_URI"))
        db = client["example_db"]
        collection = db["posts"]

        # Fetch all posts (you can modify this to search by title, content, etc.)
        posts = list(collection.find({}).limit(5))  # Limit to 5 posts for brevity

        if posts:
            # Format the posts nicely
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


tools = [post_data_from_db]