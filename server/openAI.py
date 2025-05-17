# .env
import os
from dotenv import find_dotenv, load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


envPath = find_dotenv()
load_dotenv(envPath)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



# GOTO - ChatBot Init/Deactivation

# PLANNED
# Function | ChatBot initializer
def initChat (systemPrompt: str):
    """_summary_
    """
    
    try:
        gpt = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name="gpt-4.1-mini",
            temperature=1.2,
            max_tokens = 2048,
            timeout=None,
            max_retries=1        
            )
    
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant."),
                ("human", "{input}")            
            ]
            )
    
        chain = prompt | gpt
    
        return gpt, chain
    
    except Exception as e:
        return e.message

# PLANNED
# Function | Deactivate ChatBot Functionality
def deactivate():
    """_summary_
    """
    try:
        
        return None
    
    except Exception as e:
        return e.message



# GOTO - ChatBot Requests

# PLANNED
# Function | Single User Request
def singleUserRequest (userInput: str, chatHistory):
    """_summary_

    Args:
        uri (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        
        return None
    
    except Exception as e:
        return e.message

# PLANNED
# Function | Community Request    
def communityRequest (userInput, username, chatHistory):
    """_summary_

    Args:
        userInput (_type_): _description_
        username (_type_): _description_
        chatHistory (_type_): _description_
    """
    try:
        
        return None
    
    except Exception as e:
        return e.message