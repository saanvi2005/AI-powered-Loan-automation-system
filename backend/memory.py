class ConversationMemory:
    def __init__(self):
        self.sessions = {}

    def get(self, session_id):
        print(f"MEMORY GET: {session_id} -> {self.sessions.get(session_id, {})}")  # Debug
        return self.sessions.get(session_id, {})

    def update(self, session_id, data):
        print(f"MEMORY UPDATE: {session_id} with {data}")  # Debug
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        self.sessions[session_id].update(data)
        print(f"MEMORY AFTER UPDATE: {session_id} -> {self.sessions[session_id]}")  # Debug

    def clear(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]
            print(f"MEMORY CLEARED: {session_id}")  # Debug

memory = ConversationMemory()