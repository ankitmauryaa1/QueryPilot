
class ConversationMemory:

    def __init__(self):
        self.history = []

    def add_message(self, role, content):

        self.history.append({
            "role": role,
            "content": content
        })

    def get_history(self):
        return self.history

    def clear_history(self):
        self.history = []

    def get_context(self, limit=10):

        return self.history[-limit:]
