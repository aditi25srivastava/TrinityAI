import subprocess
from langchain_core.tools import tool

@tool
def open_application(app_name: str) -> str:
    """
    Opens an application on the macOS system.
    Args:
        app_name: The name of the application to open (e.g., "Safari", "Calculator", "Notes").
    """
    print(f"Executing REAL action: Opening {app_name}")
    try:
        # Use macOS 'open -a' command
        subprocess.run(["open", "-a", app_name], check=True)
        return f"Successfully opened {app_name} on your Mac."
    except subprocess.CalledProcessError as e:
        return f"Failed to open {app_name}. Are you sure it's installed? Error: {e}"
    except Exception as e:
        return f"An error occurred while trying to open {app_name}: {e}"

@tool
def schedule_meeting(title: str, time: str, attendees: list[str]) -> str:
    """
    Schedules a meeting in the calendar.
    Args:
        title: The title or subject of the meeting.
        time: The time of the meeting (e.g., "Tomorrow at 2pm").
        attendees: A list of email addresses or names of attendees.
    """
    print(f"Executing MOCK action: Scheduling meeting '{title}' at {time} with {attendees}")
    return f"Successfully scheduled meeting '{title}' for {time} with {len(attendees)} attendees."

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """
    Sends an email.
    Args:
        to: The recipient's email address or name.
        subject: The subject of the email.
        body: The content of the email.
    """
    print(f"Executing MOCK action: Sending email to {to} about '{subject}'")
    return f"Successfully sent email to {to}."

@tool
def search_knowledge_base(query: str) -> str:
    """
    Searches the internal knowledge base (PDFs, notes, documents) for information.
    Args:
        query: The search query to look for.
    """
    print(f"Executing REAL action: Searching knowledge base for '{query}'")
    from app.agents.rag import knowledge_base
    return knowledge_base.search(query)

@tool
def generate_report(topic: str) -> str:
    """
    Generates a PDF or text report on a specific topic.
    Args:
        topic: The topic to generate a report about.
    """
    print(f"Executing MOCK action: Generating report on '{topic}'")
    return f"Successfully generated a 5-page report on '{topic}' and saved it to the desktop."

# Export a list of all tools
ALL_TOOLS = [open_application, schedule_meeting, send_email, search_knowledge_base, generate_report]
