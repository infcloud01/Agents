# --- SQLITE WORKAROUND FOR CHROMADB ON LINUX ---
#__import__('pysqlite3')
#import sys
#sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# -----------------------------------------------

# --- SQLITE WORKAROUND FOR OLDER LINUX HOSTS ---
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    # If we are inside Docker, it will fail to import this, which is fine 
    # because Docker's native SQLite is already up to date!
    pass
    # -----------------------------------------------
import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from jira import JIRA

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_classic.retrievers.multi_query import MultiQueryRetriever
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Load environment variables (.env)
load_dotenv()

# ==========================================
# 1. DEFINE AGENT TOOLS
# ==========================================

@tool
def search_knowledge_base(query: str) -> str:
    """Use this tool to search company documentation to answer customer questions."""
    print(f"--> [ROUTING] RAG Tool triggered for query: {query}")
    
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    query_generator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    try:
        # Point to the database folder created by your Airflow DAG
        DB_PATH = "./data/chroma_db" 
        vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
        
        base_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        advanced_retriever = MultiQueryRetriever.from_llm(
            retriever=base_retriever,
            llm=query_generator_llm
        )
        
        print("--> [RETRIEVAL] Generating query variations and searching...")
        docs = advanced_retriever.invoke(query)
        
        if not docs:
            return "I couldn't find any relevant information in the documentation."
            
        context = "\n\n".join([doc.page_content for doc in docs])
        print(f"--> [RETRIEVAL] Success! Handing {len(docs)} unique chunks back to the agent.")
        return f"Here is the exact documentation retrieved:\n{context}"
        
    except Exception as e:
        print(f"Database Error: {e}")
        return "The knowledge base is currently unavailable."


@tool
def create_support_ticket(summary: str, description: str) -> str:
    """
    Use this tool to create a Jira support ticket when a user reports a bug, 
    requests a feature, or needs human help.
    You must extract a brief 'summary' and a detailed 'description' from the user's request.
    """
    print(f"--> [ROUTING] Action Tool triggered to create Jira ticket: {summary}")
    
    try:
        jira_options = {'server': os.environ.get("JIRA_SERVER_URL")}
        jira = JIRA(
            options=jira_options,
            basic_auth=(os.environ.get("JIRA_USER_EMAIL"), os.environ.get("JIRA_API_TOKEN"))
        )
        
        issue_dict = {
            'project': {'key': os.environ.get("JIRA_PROJECT_KEY")},
            'summary': summary,
            'description': description,
            'issuetype': {'name': 'Task'},
        }
        
        new_issue = jira.create_issue(fields=issue_dict)
        print(f"--> [ACTION] Successfully created Jira ticket: {new_issue.key}")
        return f"Success! I have created Jira ticket {new_issue.key}. You can view it here: {os.environ.get('JIRA_SERVER_URL')}/browse/{new_issue.key}"
        
    except Exception as e:
        print(f"Jira API Error: {e}")
        return "I tried to create a ticket, but my connection to Jira failed. Please ensure credentials are correct."

# ==========================================
# 2. INITIALIZE AGENT & MEMORY
# ==========================================

# Define the System Prompt
system_prompt = """
You are the manager of the Image Development team. You provide knowledgable answers to your consumers based on the knowledge_base.
When a user asks a question, you MUST use the search_knowledge_base tool to find the answer.
You must base your final answer STRICTLY on the text retrieved by the tool.
If the tool does not provide the answer, do not guess. Simply state: "I'm sorry, I don't have that information in my current documentation."
"""

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Initialize the Checkpointer (Memory)
memory = MemorySaver()

# Bundle the tools and create the LangGraph Agent
tools = [search_knowledge_base, create_support_ticket]
agent = create_react_agent(
    model=llm,
    tools=tools,
    checkpointer=memory,
    prompt=system_prompt  # <-- This injects your system prompt!
)

# ==========================================
# 3. CONFIGURE SLACK BOT
# ==========================================

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.event("app_mention")
def handle_mentions(body, say):
    event = body.get("event", {})
    user_text = event.get("text")
    
    # Grab the Slack Thread ID to use as our memory compartment key
    thread_id = event.get("thread_ts", event.get("ts"))
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"\n--> [SLACK] Received message in thread: {thread_id}")
    
    try:
        # Invoke the LangGraph agent
        result = agent.invoke({"messages": [("user", user_text)]}, config=config)
        
        # Extract the final answer
        bot_reply = result["messages"][-1].content
        
        # Reply in the exact same thread
        say(text=bot_reply, thread_ts=thread_id)
        
    except Exception as e:
        print(f"Agent Error: {e}")
        say(text="I'm sorry, I encountered an internal error while processing that request.", thread_ts=thread_id)

# ==========================================
# 4. START THE SERVER
# ==========================================

if __name__ == "__main__":
    print("⚡️ Starting Agentic RAG Slackbot with LangGraph Memory...")
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()
