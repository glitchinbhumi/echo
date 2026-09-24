import sqlite3


def initialize_database():
    connection = sqlite3.connect("echo.db")
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person TEXT NOT NULL,
        text TEXT NOT NULL,
        year INTEGER,
        place TEXT,
        importance REAL
    )
    """)

    connection.commit()
    connection.close()


def save_memory(memory):
    connection = sqlite3.connect("echo.db")
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO memories (person, text, year, place, importance)
    VALUES (?, ?, ?, ?, ?)
    """, (
        memory["person"],
        memory["text"],
        memory["year"],
        memory["place"],
        memory["importance"]
    ))

    connection.commit()
    connection.close()


def get_memories():
    connection = sqlite3.connect("echo.db")
    cursor = connection.cursor()

    cursor.execute("""
    SELECT id, person, text, year, place, importance
    FROM memories
    """)

    memories = cursor.fetchall()

    connection.close()

    return memories


def search_memories(keyword):

    connection = sqlite3.connect("echo.db")
    cursor = connection.cursor()

    cursor.execute("""
    SELECT id, person, text, year, place, importance
    FROM memories
    WHERE text LIKE ?
       OR person LIKE ?
       OR place LIKE ?
    """, (
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    memories = cursor.fetchall()

    connection.close()

    return memories


initialize_database()

print("ECHO memory database initialized.")

def get_memory_context(keyword):

    memories = search_memories(keyword)

    if not memories:
        return "No relevant memories were found."

    context = ""

    for memory in memories:

        context += f"""
Memory ID: {memory[0]}
Person: {memory[1]}
Memory: {memory[2]}
Year: {memory[3]}
Place: {memory[4]}
Importance: {memory[5]}
---
"""

    return context
