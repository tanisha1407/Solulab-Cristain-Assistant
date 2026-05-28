# ==========================================
# SIMPLE IN-MEMORY CHAT STORAGE
# ==========================================

"""
This module handles conversation memory
for the Christian AI Assistant.

Using lightweight custom memory instead
of LangChain memory for better stability.
"""

# ==========================================
# GLOBAL CHAT HISTORY
# ==========================================

chat_history = []

# ==========================================
# SAVE CHAT
# ==========================================

def save_chat(user_input, assistant_response):
    """
    Save user + assistant messages
    into conversation history.
    """

    global chat_history

    chat_history.append({

        "user": user_input,

        "assistant": assistant_response
    })

# ==========================================
# GET CHAT HISTORY
# ==========================================

def get_chat_history():
    """
    Return full chat history.
    """

    global chat_history

    return chat_history

# ==========================================
# FORMAT HISTORY FOR PROMPTS
# ==========================================

def format_chat_history():
    """
    Convert chat history into
    prompt-friendly string.
    """

    global chat_history

    if not chat_history:

        return "No previous conversation."

    formatted = ""

    for message in chat_history:

        formatted += (
            f"User: {message['user']}\n"
        )

        formatted += (
            f"Assistant: "
            f"{message['assistant']}\n\n"
        )

    return formatted.strip()

# ==========================================
# CLEAR MEMORY
# ==========================================

def clear_memory():
    """
    Clear stored conversation memory.
    """

    global chat_history

    chat_history = []

# ==========================================
# GET LAST N MESSAGES
# ==========================================

def get_recent_messages(limit=5):
    """
    Retrieve recent conversation history.
    """

    global chat_history

    return chat_history[-limit:]

# ==========================================
# MEMORY SIZE
# ==========================================

def memory_size():
    """
    Return number of stored conversations.
    """

    global chat_history

    return len(chat_history)

# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":

    print("\n===== TEST MEMORY =====\n")

    save_chat(
        "What does Bible say about forgiveness?",
        "Matthew 6:14 teaches forgiveness."
    )

    save_chat(
        "What is prayer?",
        "Prayer is communication with God."
    )

    print("\n===== FULL HISTORY =====\n")

    print(
        get_chat_history()
    )

    print("\n===== FORMATTED =====\n")

    print(
        format_chat_history()
    )

    print("\n===== RECENT =====\n")

    print(
        get_recent_messages(1)
    )

    print("\n===== MEMORY SIZE =====\n")

    print(
        memory_size()
    )

    print("\n===== CLEAR =====\n")

    clear_memory()

    print(
        get_chat_history()
    )