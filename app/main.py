"""
AI EMAIL AGENT ARCHITECTURE (DEMO)
----------------------------------
Author: AdrianL-Automations
Status: Showcase Version (Logic Redacted)

DESCRIPTION:
This is the architectural skeleton of a self-hosted AI Agent using:
- Local LLM (Llama 3.2 via Ollama) for privacy.
- LangGraph for state management.
- FastAPI for the interface.

NOTE: 
This code demonstrates the *infrastructure*. The production version 
includes proprietary prompt engineering, error recovery, and 
advanced guardrails not shown here.
"""

import os
from typing import TypedDict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# --- LANGGRAPH IMPORTS ---
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama 

app = FastAPI()

# ========================================
# CONFIGURATION
# ========================================
# We use 'host.docker.internal' so Docker can talk to the host machine
llm = ChatOllama(
    model="llama3.2", 
    base_url="http://host.docker.internal:11434", 
    temperature=0
)

CALENDLY_LINK = "https://cal.com/demo-link" 

# ========================================
# STATE DEFINITION
# ========================================
class AgentState(TypedDict):
    email_content: str
    history: str          # Context window for conversation continuity
    category: str
    generated_reply: str

# ========================================
# HELPER FUNCTIONS
# ========================================
def clean_reply(text: str) -> str:
    """
    Sanitizes AI output to ensure enterprise-grade formatting.
    Removes hallucinations, checks for 'Subject:' lines, and enforces signatures.
    """
    # =================================================================
    # [LOGIC REDACTED FOR DEMO]
    # The production system enforces:
    # 1. Removal of AI-generated subject lines.
    # 2. Placeholder verification (e.g., removing '[Insert Name]').
    # 3. Tone consistency checks.
    # =================================================================
    
    # Simple pass-through for architectural demo
    return text.strip()

# ========================================
# GRAPH NODES
# ========================================
def analyze_email(state: AgentState):
    """
    Node 1: Categorize the email based on content + conversation history.
    """
    print("--- ANALYZING EMAIL ---")
    
    email_text = state['email_content']
    history_text = state.get('history', 'No previous history.')
    
    # =================================================================
    # PROPRIETARY PROMPT LOGIC (REDACTED FOR DEMO)
    # =================================================================
    # The production system uses a 4-stage Chain-of-Thought prompt to:
    # 1. Analyze sentiment and urgency.
    # 2. Check conversation history for conflict.
    # 3. Apply agency-specific tone guidelines.
    # =================================================================
    prompt = f"""
    You are an AI assistant.
    Analyze the following email conversation:
    
    HISTORY: "{history_text}"
    CURRENT EMAIL: "{email_text}"
    
    Categorize into one of: URGENT, LEAD, SPAM, OTHER.
    Return ONLY the category name.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        # Simple normalization for demo
        category = response.content.strip().upper()
        
        # Basic validation
        valid = ["URGENT", "LEAD", "SPAM", "OTHER"]
        if not any(v in category for v in valid):
            category = "OTHER"
            
        print(f"Normalized category: {category}")
        return {"category": category}
        
    except Exception as e:
        print(f"Error in analyze_email: {str(e)}")
        return {"category": "OTHER"}


def draft_reply(state: AgentState):
    """
    Node 2: Draft a contextual reply based on category and conversation history.
    """
    print(f"--- DRAFTING REPLY (Category: {state['category']}) ---")
    
    category = state['category']
    email_text = state['email_content']
    history_text = state.get('history', 'No previous history.')
    
    if "SPAM" in category:
        return {"generated_reply": "IGNORE"}
    
    # =================================================================
    # PROPRIETARY PROMPT LOGIC (REDACTED FOR DEMO)
    # =================================================================
    # Production prompts include specific handling for:
    # - Negotiation tactics for LEADS.
    # - De-escalation scripts for URGENT issues.
    # - Calendar conflict resolution.
    # =================================================================
    prompt = f"""
    You are a helpful AI assistant.
    Reply to the email based on category: {category}
    
    HISTORY: "{history_text}"
    EMAIL: "{email_text}"
    
    Link to include: {CALENDLY_LINK}
    Keep it professional and short.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw_reply = response.content
        
        # Post-process
        cleaned_reply = clean_reply(raw_reply)
        
        return {"generated_reply": cleaned_reply}
        
    except Exception as e:
        return {
            "generated_reply": "Thank you for your email. We will respond shortly."
        }

# ========================================
# BUILD THE GRAPH
# ========================================
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("categorizer", analyze_email)
workflow.add_node("writer", draft_reply)

# Define flow
workflow.set_entry_point("categorizer")
workflow.add_edge("categorizer", "writer")
workflow.add_edge("writer", END)

# Compile
app_agent = workflow.compile()

# ========================================
# API ENDPOINTS
# ========================================
class RequestData(BaseModel):
    input: str
    history: str = "" 

@app.post("/agent/run")
def run_agent(q: RequestData):
    """
    Main endpoint to process emails.
    """
    try:
        print(f"Processing email: {q.input[:50]}...")
        
        initial_state = {
            "email_content": q.input,
            "history": q.history,
            "category": "",
            "generated_reply": ""
        }
        
        result = app_agent.invoke(initial_state)
        
        return {
            "status": "success",
            "category": result["category"],
            "reply": result["generated_reply"]
        }
        
    except Exception as e:
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("Starting AI Agent Architecture (...")
    uvicorn.run(app, host="0.0.0.0", port=8000)