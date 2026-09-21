import sqlite3
import os


# ============================================================
# SPIDEY PERSISTENT MEMORY
# ============================================================

# Always keep the database beside memory.py.
# This means SPIDEY uses the SAME memory database regardless
# of where main.py is launched from.
BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "spidey_memory.db"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

connection = sqlite3.connect(
    DATABASE_PATH,
    check_same_thread=False
)

cursor = connection.cursor()


# ============================================================
# CREATE MEMORY TABLE
# ============================================================

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        information TEXT NOT NULL
    )
    """
)

connection.commit()


# ============================================================
# SAVE MEMORY
# ============================================================

def save_memory(information):

    if not information:
        return False

    information = str(
        information
    ).strip()

    if not information:
        return False

    try:

        cursor.execute(
            """
            INSERT INTO memories
            (information)
            VALUES (?)
            """,
            (information,)
        )

        connection.commit()

        print(
            "MEMORY SAVED:",
            information
        )

        return True

    except Exception as e:

        print(
            "Memory save error:",
            e
        )

        return False


# ============================================================
# GET ALL MEMORIES
# ============================================================

def get_memories():

    try:

        cursor.execute(
            """
            SELECT information
            FROM memories
            ORDER BY id ASC
            """
        )

        memories = cursor.fetchall()

        print(
            "MEMORY LOADED:",
            len(memories),
            "memories"
        )

        return memories

    except Exception as e:

        print(
            "Memory loading error:",
            e
        )

        return []


# ============================================================
# CLOSE DATABASE
# ============================================================

def close_memory():

    try:

        connection.commit()
        connection.close()

        print(
            "MEMORY DATABASE CLOSED."
        )

    except Exception as e:

        print(
            "Memory close error:",
            e
        )