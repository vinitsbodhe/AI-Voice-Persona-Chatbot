from backend import config

class ConversationMemory:
    def __init__(self, window_size: int = config.MEMORY_WINDOW_SIZE):
        """
        Manages conversation history mapped by session ID.
        Window size defines the maximum number of conversation turns (user/assistant pairs) to retain.
        """
        self.window_size = window_size
        # Dictionary of session_id -> list of message dicts: {"role": str, "content": str}
        self.sessions = {}

    def get_history(self, session_id: str) -> list:
        """
        Retrieves the conversation history for a given session.
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return self.sessions[session_id]

    def add_message(self, session_id: str, role: str, content: str):
        """
        Adds a message (user or assistant) to the history. Truncates history if it exceeds the window size.
        Note: One turn consists of one user message and one assistant response (2 messages).
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            
        self.sessions[session_id].append({"role": role, "content": content})
        
        # Max messages = window_size * 2
        max_messages = self.window_size * 2
        if len(self.sessions[session_id]) > max_messages:
            # We slice from the beginning but keep the structure aligned (remove the oldest turn)
            self.sessions[session_id] = self.sessions[session_id][-max_messages:]

    def clear_history(self, session_id: str):
        """
        Clears the conversation history for a given session.
        """
        self.sessions[session_id] = []
