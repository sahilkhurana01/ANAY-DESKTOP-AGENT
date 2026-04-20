import sqlite3
import json
import os
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "anay_brain.db")

def init_db():
    """Initialize SQLite tables for user facts, chat history, memories, and contacts."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # User facts table — naam, age, preferences etc
        c.execute("""CREATE TABLE IF NOT EXISTS user_facts (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TEXT
        )""")
        # Conversation history — last 100 messages
        c.execute("""CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            timestamp TEXT
        )""")
        # Long term memories — important things user said
        c.execute("""CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory TEXT,
            timestamp TEXT
        )""")
        
        # COLUMN MIGRATION: Add 'kind' to memories if missing
        try:
            c.execute("ALTER TABLE memories ADD COLUMN kind TEXT DEFAULT 'note'")
        except sqlite3.OperationalError:
            pass # Already exists

        # Contacts table — specifically for phone numbers
        c.execute("""CREATE TABLE IF NOT EXISTS contacts (
            name TEXT PRIMARY KEY,
            phone TEXT,
            updated_at TEXT
        )""")
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {DB_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

# --- Contact Management ---

def save_contact(name: str, phone: str):
    """Save or update a contact's phone number"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT OR REPLACE INTO contacts VALUES (?,?,?)",
                     (name.lower().strip(), phone.strip(), datetime.now().isoformat()))
        conn.commit()
        conn.close()
        logger.info(f"Saved contact: {name} -> {phone}")
    except Exception as e:
        logger.error(f"Error saving contact: {e}")

def get_contact_number(name: str) -> str:
    """Retrieve a contact's phone number by name"""
    try:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute("SELECT phone FROM contacts WHERE name=?",
                           (name.lower().strip(),)).fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        logger.error(f"Error getting contact: {e}")
        return None

# --- Fact Management ---

def save_fact(key: str, value: str):
    """Save user fact like name, age, preferences"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT OR REPLACE INTO user_facts VALUES (?,?,?)",
                     (key.lower().strip(), str(value), datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error saving fact: {e}")

def get_fact(key: str) -> str:
    """Retrieve a specific user fact."""
    try:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute("SELECT value FROM user_facts WHERE key=?",
                           (key.lower().strip(),)).fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        logger.error(f"Error getting fact: {e}")
        return None

def get_all_facts() -> dict:
    """Retrieve all stored user facts."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("SELECT key, value FROM user_facts").fetchall()
        conn.close()
        return {r[0]: r[1] for r in rows}
    except Exception as e:
        logger.error(f"Error getting all facts: {e}")
        return {}

# --- Memory Management ---

def save_memory(memory: str, kind: str = "note"):
    """Save an important long-term memory."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO memories (id, memory, kind, timestamp) VALUES (NULL,?,?,?)",
                     (memory, kind, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error saving memory: {e}")

def get_recent_memories(limit=10) -> list:
    """Retrieve recent long-term memories."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("SELECT memory FROM memories ORDER BY id DESC LIMIT ?",
                            (limit,)).fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception as e:
        logger.error(f"Error getting memories: {e}")
        return []

# --- History Management ---

def save_message(role: str, content: str):
    """Persist a chat message to history."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO chat_history (id, role, content, timestamp) VALUES (NULL,?,?,?)",
                     (role, content, datetime.now().isoformat()))
        # Keep only last 100 messages
        conn.execute("""DELETE FROM chat_history WHERE id NOT IN
                        (SELECT id FROM chat_history ORDER BY id DESC LIMIT 100)""")
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error saving message: {e}")

def get_recent_history(limit=15) -> list:
    """Retrieve the recent chat history for LLM context."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT role, content FROM chat_history ORDER BY id DESC LIMIT ?",
            (limit,)).fetchall()
        conn.close()
        # Return in chronological order
        return [{"role": r[0], "content": r[1]} for r in reversed(rows)]
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return []

# --- Context Builder ---

def build_memory_context() -> str:
    """Build a rich context string for the AI system prompt."""
    facts = get_all_facts()
    memories = get_recent_memories(10)
    
    # Also fetch contacts for the prompt so the AI knows who the user knows
    try:
        conn = sqlite3.connect(DB_PATH)
        contacts = conn.execute("SELECT name, phone FROM contacts").fetchall()
        conn.close()
    except:
        contacts = []
    
    context = ""
    if facts:
        context += "USER KE BAARE MEIN PATA HAI (Facts):\n"
        for k, v in facts.items():
            context += f"  - {k}: {v}\n"
    
    if contacts:
        context += "\nSAVED CONTACTS (WhatsApp Numbers):\n"
        for name, phone in contacts:
            context += f"  - {name.capitalize()}: {phone}\n"
            
    if memories:
        context += "\nIMPORTANT BAATEIN JO YAAD RAKHNI HAIN:\n"
        for m in memories:
            context += f"  - {m}\n"
    
    return context.strip()

# --- Extraction Logic ---

def extract_and_save_facts(user_message: str, assistant_reply: str):
    """Auto-detect facts and contacts from natural language."""
    msg = user_message.lower()
    
    # 1. Name detection (Mera naam Sahil hai, I am Sahil, etc.)
    name_patterns = [
        r"(?:mera naam|my name is|main hoon|i am|naam hai mera)\s+([a-zA-Z]+)",
        r"(?:call me|mujhe)\s+([a-zA-Z]+)\s+(?:bolna|bula)"
    ]
    for pattern in name_patterns:
        match = re.search(pattern, msg)
        if match:
            name = match.group(1).capitalize()
            save_fact("naam", name)
            save_memory(f"User ka naam {name} hai.")
            logger.info(f"Auto-extracted name: {name}")

    # 2. Contact detection (Vansh ka number 9876543210 hai)
    contact_patterns = [
        r"([a-zA-Z]+)\s+(?:ka|da)?\s*(?:number|contact|phone|mobile|whatsapp)\s+(?:hai\s+)?(\d{10,12})",
        r"save\s+([a-zA-Z]+)(?:'s)?\s+(?:number|contact)\s+as\s+(\d{10,12})",
        r"(\d{10,12})\s+(?:hai\s+)?([a-zA-Z]+)\s+(?:ka|da)?\s*(?:number|contact)"
    ]
    for pattern in contact_patterns:
        match = re.search(pattern, msg)
        if match:
            # Handle different match group orders
            if match.group(1).isalpha():
                name, num = match.group(1), match.group(2) if len(match.groups()) > 1 else None
                if not num and len(match.groups()) > 2: num = match.group(3)
            else:
                num, name = match.group(1), match.group(2)
            
            if name and num:
                save_contact(name, num)
                save_memory(f"{name.capitalize()} ka contact number {num} save kar liya hai.")
                logger.info(f"Auto-extracted contact: {name} -> {num}")

    # 3. Explicit "Remember" triggers
    remember_triggers = ["yaad rakh", "remember", "note kar", "save kar", "likh le", "write down"]
    for trigger in remember_triggers:
        if trigger in msg:
            content = user_message.split(trigger, 1)[-1].strip()
            if content and len(content) > 3:
                save_memory(content)
                logger.info(f"Auto-extracted memory from trigger '{trigger}': {content}")

# --- Compatibility Class for main.py ---

class MemoryStore:
    """Unified DB-backed memory store for API endpoints."""
    def list_tasks(self, limit=10): return [] # Placeholder for agent tasks
    def forget(self, id): return False # Should implement DB delete
    
    def list_memories(self, limit=30):
        try:
            conn = sqlite3.connect(DB_PATH)
            rows = conn.execute("SELECT id, memory, kind, timestamp FROM memories ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
            conn.close()
            return [{"id": r[0], "content": r[1], "kind": r[2], "updated_at": r[3]} for r in rows]
        except: return []

    def list_reminders(self, limit=10):
        # Placeholder for reminders (handled by scheduler.py normally)
        return []

    def remember(self, content, kind="note", metadata=None):
        save_memory(content, kind)
        # Return a dict instead of a dynamic object to avoid serialization issues
        return {
            "id": "db",
            "content": content,
            "kind": kind,
            "updated_at": datetime.now().isoformat()
        }

    def save_reminder(self, task, time):
        # This is used by pc_control.py
        pass

memory_store = MemoryStore()

# Ensure tables exist on startup
init_db()
