
from ai_engine.conversation import ConversationMemory

memory = ConversationMemory()

memory.add_message(
    "user",
    "Show top 10 cities by revenue"
)

memory.add_message(
    "assistant",
    "Here is the SQL result..."
)

memory.add_message(
    "user",
    "Now show only top 5"
)

print("Conversation history:")

for message in memory.get_history():
    print(message)

print("\nRecent context:")
print(memory.get_context(limit=2))
