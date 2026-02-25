graph TD
    %% Define Styles
    classDef host fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#01579b;
    classDef docker fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#2e7d32;
    classDef venv fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#e65100;
    classDef cloud fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,stroke-dasharray: 5 5,color:#4a148c;
    classDef database fill:#fff9c4,stroke:#fbc02d,stroke-width:2px,color:#fbc02d;
    classDef note fill:#fff,stroke:#d32f2f,stroke-width:2px,color:#d32f2f,stroke-dasharray: 2 2;

    subgraph Cloud_Services ["☁️ External Cloud Services"]
        SlackAPI[Slack Cloud Platform]
        OpenAI[OpenAI API\n(GPT-4o & Embeddings)]
        JiraCloud[Atlassian Jira Cloud]
    end

    subgraph Host_Machine ["🖥️ Host Machine (Oracle Linux 9 / WSL)"]
        
        subgraph Shared_Storage ["📂 Shared Host Volumes"]
            PDF_Source[/"Let's drop PDFs here"\n./data/pdfs/]
            ChromaDB_Vol[/"Persistent Vector DB"\n./data/chroma_db/]
        end

        subgraph Infrastructure_Layer ["🏗️ Infrastructure Layer (The Kitchen - Docker)"]
            airflow_db[(Postgres DB)]
            
            subgraph Airflow_Containers ["Apache Airflow (Docker Compose)"]
                Scheduler[Airflow Scheduler]
                Webserver[Airflow Webserver UI]
                
                subgraph DAG_Process ["Daily RAG Ingestion DAG (Python)"]
                    Task1[1. PyPDFLoader\n(Read PDFs from Volume)]
                    Task2[2. Text Splitter\n(Chunking)]
                    Task3[3. OpenAIEmbeddings\n(Vectorize & Upsert)]
                end
            end
        end

        subgraph Application_Layer ["🤖 Application Layer (The Waiter - Local Venv)"]
            
            subgraph OS_Fix ["🔧 The 'Final Boss' Fix"]
                SQLite_Compiled["Custom Compiled SQLite 3.45\n(/usr/local/lib)"]
                PySQLite_Bridge["pysqlite3 workaround\n(in app.py)"]
            end

            subgraph Bot_Process ["Python Bot Process (app.py)"]
                SocketMode[Slack Socket Mode Handler]
                
                subgraph LangChain_Agent ["🧠 LangChain V1.0 Agent"]
                    Router[LLM Router/ReAct Loop\n(System Prompt)]
                    
                    subgraph Tools ["Agent Tools"]
                        RAG_Tool[RAG Tool\n(Multi-Query Retriever)]
                        Action_Tool[Action Tool\n(Jira API Client)]
                    end
                end
            end
        end
    end

    %% Connections - Infrastructure Flow
    PDF_Source -->|Read Access| Task1
    Scheduler -->|Triggers @daily| DAG_Process
    Task1 --> Task2 --> Task3
    Task3 -.->|Generate Vectors| OpenAI
    Task3 -->|WRITE Vectors| ChromaDB_Vol
    airflow_db --- Scheduler & Webserver

    %% Connections - Application Flow
    User((Slack User)) <-->|Messages| SlackAPI
    SlackAPI <-->|Real-time Events| SocketMode
    SocketMode <--> Router
    Router <-->|Reasoning & Generation| OpenAI
    
    Router -- "Need Info?" --> RAG_Tool
    RAG_Tool -.->|Generate Query Variations| OpenAI
    RAG_Tool -->|READ Vectors| ChromaDB_Vol
    
    Router -- "Create Ticket?" --> Action_Tool
    Action_Tool -->|REST API| JiraCloud

    %% Connection - OS Fix
    SQLite_Compiled -.-> PySQLite_Bridge
    PySQLite_Bridge -.->|Used by| RAG_Tool
    
    %% Styling Application
    class Cloud_Services,SlackAPI,OpenAI,JiraCloud cloud;
    class Host_Machine,Shared_Storage host;
    class Infrastructure_Layer,Airflow_Containers,Scheduler,Webserver,DAG_Process,Task1,Task2,Task3 docker;
    class Application_Layer,Bot_Process,SocketMode,LangChain_Agent,Router,Tools,RAG_Tool,Action_Tool venv;
    class ChromaDB_Vol,airflow_db database;
    class OS_Fix,SQLite_Compiled,PySQLite_Bridge note;