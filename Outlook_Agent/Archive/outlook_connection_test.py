import win32com.client

def test_outlook_connection(num_emails=5):
    print("Connecting to local Outlook instance...\n")
    
    try:
        # Connect to the Outlook application and get the MAPI namespace
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        
        # 6 is the internal Microsoft code for the default Inbox folder
        inbox = outlook.GetDefaultFolder(6) 
        messages = inbox.Items
        
        # Sort messages by received time, True means descending (newest first)
        messages.Sort("[ReceivedTime]", True) 
        
        print(f"Success! Found Inbox. Reading the last {num_emails} emails:\n")
        print("-" * 50)

        count = 0
        for message in messages:
            # message.Class == 43 ensures we only grab actual emails. 
            # If we don't do this, meeting invites (Class 26) can crash the script!
            if message.Class == 43:
                subject = getattr(message, 'Subject', 'No Subject')
                sender = getattr(message, 'SenderName', 'Unknown Sender')
                received = getattr(message, 'ReceivedTime', 'Unknown Time')
                
                # Grab the first 150 characters of the body to keep the terminal clean
                body = getattr(message, 'Body', '')
                preview = body.replace('\r', '').replace('\n', ' ')[:150]
                
                print(f"Subject:  {subject}")
                print(f"From:     {sender}")
                print(f"Received: {received}")
                print(f"Preview:  {preview}...")
                print("-" * 50)
                
                count += 1
                
            if count >= num_emails:
                break
                
    except Exception as e:
        print(f"Failed to connect or read emails. Error: {e}")
        print("Make sure you are on a Windows machine and Classic Outlook is open.")

if __name__ == "__main__":
    test_outlook_connection()
