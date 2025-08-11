import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any

class DatabaseHandler:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User tickets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discord_user_id TEXT NOT NULL,
                    mantis_ticket_id TEXT NOT NULL,
                    ticket_summary TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'open'
                )
            ''')
            
            # User sessions table for conversation context
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    discord_user_id TEXT PRIMARY KEY,
                    conversation_history TEXT,
                    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def create_ticket_record(self, discord_user_id: str, mantis_ticket_id: str, summary: str) -> int:
        """Create a new ticket record"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_tickets (discord_user_id, mantis_ticket_id, ticket_summary)
                VALUES (?, ?, ?)
            ''', (discord_user_id, mantis_ticket_id, summary))
            conn.commit()
            return cursor.lastrowid
    
    def get_user_tickets(self, discord_user_id: str) -> list:
        """Get all tickets for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT mantis_ticket_id, ticket_summary, created_at, status
                FROM user_tickets
                WHERE discord_user_id = ?
                ORDER BY created_at DESC
            ''', (discord_user_id,))
            return cursor.fetchall()
    
    def update_session(self, discord_user_id: str, conversation_history: dict):
        """Update user conversation session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO user_sessions (discord_user_id, conversation_history, last_interaction)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (discord_user_id, json.dumps(conversation_history)))
            conn.commit()
    
    def get_session(self, discord_user_id: str) -> Optional[dict]:
        """Get user conversation session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT conversation_history FROM user_sessions
                WHERE discord_user_id = ?
            ''', (discord_user_id,))
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None
