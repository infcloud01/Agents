import os
import sys
import win32com.client
from dotenv import load_dotenv
from langchain_oci import ChatOCIGenAI
from langchain_core.messages import HumanMessage, SystemMessage
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()
load_dotenv()

# ==========================================
# CUSTOMIZE YOUR SIGNATURE HERE
# ==========================================
MY_SIGNATURE = """

Conrad
"""

def summarize_email(full_email_text):
    with console.status("[bold green]🧠 Oracle GenAI is summarizing the thread...", spinner="dots"):
        try:
            compartment_id = os.getenv("OCI_COMPARTMENT_ID")
            service_endpoint = os.getenv("OCI_SERVICE_ENDPOINT")
            model_id = os.getenv("OCI_MODEL_ID")
            
            if not compartment_id or not service_endpoint:
                return "[bold red]Configuration Error: Missing OCI variables![/bold red]"

            oci_llm = ChatOCIGenAI(
                model_id=model_id, 
                service_endpoint=service_endpoint, 
                compartment_id=compartment_id,
                model_kwargs={"max_tokens": 512} 
            )
            
            system_prompt = (
                "You are a highly efficient executive assistant. Provide a concise, bulleted summary "
                "of the following email thread. Highlight the main points, any deadlines, and any action items "
                "required from the user. Keep it brief and highly readable."
            )
            human_prompt = f"Email Thread:\n{full_email_text}"

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = oci_llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            return f"[Oracle GenAI Error: {e}]"

def generate_llm_reply(full_email_text, user_instructions=None):
    with console.status("[bold cyan]🧠 Oracle GenAI is drafting your response...", spinner="dots"):
        try:
            compartment_id = os.getenv("OCI_COMPARTMENT_ID")
            service_endpoint = os.getenv("OCI_SERVICE_ENDPOINT")
            model_id = os.getenv("OCI_MODEL_ID")
            
            if not compartment_id or not service_endpoint:
                return "[bold red]Configuration Error: Missing OCI variables![/bold red]"

            oci_llm = ChatOCIGenAI(
                model_id=model_id, 
                service_endpoint=service_endpoint, 
                compartment_id=compartment_id,
                model_kwargs={"max_tokens": 1024} 
            )
            
            if user_instructions:
                system_prompt = (
                    "You are drafting an email on behalf of the user. Draft a polite, warm, and informal email reply "
                    "based on the user's instructions and the original email context. The tone should be conversational "
                    "and friendly. "
                    "CRITICAL RULE: Output ONLY the core paragraph(s) of the email body. DO NOT include any greeting "
                    "(like 'Hi' or 'Dear'), sign-off, closing, or signature (like 'Best' or 'Thanks'). "
                    "Stop generating immediately after your final sentence."
                )
                human_prompt = f"Original Email:\n{full_email_text}\n\nUser Instructions: {user_instructions}"
            else:
                system_prompt = (
                    "You are drafting an email on behalf of the user. Read the following email and draft a polite, "
                    "warm, and informal reply based purely on the context. The tone should be conversational and friendly. "
                    "If they ask a question, provide a gentle, polite holding response. "
                    "CRITICAL RULE: Output ONLY the core paragraph(s) of the email body. DO NOT include any greeting "
                    "(like 'Hi' or 'Dear'), sign-off, closing, or signature (like 'Best' or 'Thanks'). "
                    "Stop generating immediately after your final sentence."
                )
                human_prompt = f"Original Email:\n{full_email_text}"

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            
            response = oci_llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            return f"[Oracle GenAI Error: {e}]"

def run_terminal_inbox(num_emails=20):
    console.rule("[bold magenta]🚀 STARTING AI TERMINAL INBOX")
    
    try:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        inbox = outlook.GetDefaultFolder(6) 
        messages = inbox.Items
        messages.Sort("[ReceivedTime]", True) 
    except Exception as e:
        console.print(f"[bold red]Failed to connect to Outlook: {e}[/bold red]")
        return

    console.print(f"[green]✔ Connection successful. Fetching your last {num_emails} emails...[/green]\n")

    count = 0
    for message in messages:
        if message.Class == 43: 
            count += 1
            
            subject = getattr(message, 'Subject', 'No Subject')
            sender = getattr(message, 'SenderName', 'Unknown Sender')
            full_body = getattr(message, 'Body', '')
            preview = full_body.replace('\r', '').replace('\n', ' ')[:300]
            
            email_content = f"[bold]From:[/bold] {sender}\n[bold]Subject:[/bold] {subject}\n\n[dim]{preview}...[/dim]"
            console.print(Panel(email_content, title=f"[bold blue]📧 EMAIL {count} OF {num_emails}[/bold blue]", border_style="blue"))
            
            while True:
                action = Prompt.ask(
                    "[bold yellow]Main Menu?[/bold yellow] Auto-draft | Custom | Summarize | Ignore | Quit", 
                    choices=["a", "c", "s", "i", "q"], 
                    default="i"
                )
                
                if action == 'q':
                    console.print("[bold red]Exiting Terminal Inbox. Goodbye![/bold red]")
                    sys.exit()
                    
                elif action == 'i':
                    console.print("[dim]Skipping to next email...[/dim]\n")
                    break 
                    
                elif action == 's':
                    summary_text = summarize_email(full_body)
                    console.print("\n")
                    console.print(Panel(summary_text, title="[bold green]📝 THREAD SUMMARY[/bold green]", border_style="green"))
                    console.print("[dim]Returning to Main Menu for this email...[/dim]\n")
                    
                elif action in ['a', 'c']:
                    instructions = None
                    if action == 'c':
                        instructions = Prompt.ask("\n[bold green]What is the gist of your custom reply?[/bold green]")
                    
                    saved_draft = False
                    
                    while True:
                        drafted_text = generate_llm_reply(full_body, instructions)
                        
                        console.print("\n")
                        console.print(Panel(drafted_text, title="[bold cyan]✨ DRAFT PREVIEW[/bold cyan]", border_style="cyan"))
                        
                        draft_action = Prompt.ask(
                            "[bold magenta]Draft Options:[/bold magenta] Save | Regenerate | Discard", 
                            choices=["s", "r", "d"], 
                            default="s"
                        )
                        
                        if draft_action == 's':
                            console.print("[dim]💾 Saving to Outlook Drafts...[/dim]")
                            reply_email = message.Reply() 
                            
                            formatted_body = drafted_text + MY_SIGNATURE + "\n\n--- Original Message ---\n" + reply_email.Body
                            reply_email.Body = formatted_body
                            
                            reply_email.Save() 
                            console.print("[bold green]✅ Draft saved with signature![/bold green]")
                            
                            # ==========================================
                            # NEW: MARK ORIGINAL AS READ
                            # ==========================================
                            if message.UnRead:
                                message.UnRead = False
                                message.Save() # We have to save the original message to commit the read state
                                console.print("[dim]📬 Original email marked as read.[/dim]\n")
                            else:
                                console.print("\n") # Just add spacing if it was already read
                                
                            saved_draft = True
                            break 
                            
                        elif draft_action == 'r':
                            console.print("[dim]🔄 Rolling the dice again...[/dim]")
                            
                        elif draft_action == 'd':
                            console.print("[yellow]🗑️ Draft discarded. Returning to Main Menu...[/yellow]\n")
                            break 
                    
                    if saved_draft:
                        break
            
        if count >= num_emails:
            break

    console.rule(f"[bold magenta]Finished reviewing the last {num_emails} emails!")

if __name__ == "__main__":
    run_terminal_inbox()