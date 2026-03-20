import os
from dotenv import load_dotenv
from langchain_oci import ChatOCIGenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# 1. The Stable OCI Brain
oci_llm = ChatOCIGenAI(
    model_id=os.getenv("OCI_MODEL_ID"),
    service_endpoint=os.getenv("OCI_SERVICE_ENDPOINT"),
    compartment_id=os.getenv("OCI_COMPARTMENT_ID"),
    model_kwargs={"max_tokens": 1024}
)

# 2. The "Agent" Logic (The Prompt)
# This replaces the "Backstory" and "Goal" of CrewAI
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a professional Executive Assistant. 
    Your context includes:
    - TODO LIST: {todo_context}
    - JIRA TICKETS: {jira_context}
    
    Task: Summarize the email from {sender} and draft a warm, informal reply.
    If the email conflicts with the Todo List or relates to a Jira ticket, mention it."""),
    ("user", "Subject: {subject}\n\n{body}")
])

# 3. The "Chain" (This replaces the Crew)
# This is a modern LangChain 'Pipe' - extremely stable and production-ready.
agent_chain = prompt | oci_llm | StrOutputParser()

def run_agent(email_data, jira_data, todo_data):
    try:
        response = agent_chain.invoke({
            "sender": email_data['sender'],
            "subject": email_data['subject'],
            "body": email_data['body'],
            "jira_context": jira_data,
            "todo_context": todo_data
        })
        return response
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    # Test Data
    test_email = {
        "sender": "John Doe",
        "subject": "Project Meeting",
        "body": "Can we meet at 3 PM to discuss the API?"
    }
    
    # Simulating your tools
    test_jira = "PROJ-123 is Open."
    test_todo = "- 3 PM: Focused deep work (No meetings)."

    print("\n🚀 Running Stable OCI Agent...")
    result = run_agent(test_email, test_jira, test_todo)
    print(f"\nFINAL OUTPUT:\n{result}")
