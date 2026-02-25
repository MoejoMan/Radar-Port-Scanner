import sqlite3
from typing import List, Dict, Optional
from pathlib import Path

# Get the directory where this script is located
APP_DIR = Path(__file__).resolve().parent

Scan_Profiles = "CREATE TABLE IF NOT EXISTS profiles ( Scan_Profile_ID INTEGER PRIMARY KEY AUTOINCREMENT, Profile_Name TEXT UNIQUE, TargetIP TEXT, Port_Selection TEXT, Timeout REAL, Threads INTEGER, Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP )"

class Profile_Manager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(APP_DIR / "data.db")
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute(Scan_Profiles)
            self.conn.commit()
        except Exception as e:
            print(f"Database connection error: {e}")
            raise

    def save_profile(self, name, target, ports, timeout, threads):
        """Save a scan profile"""
        try:
            ports_list = ",".join(map(str, ports))
            self.cursor.execute(
                "INSERT INTO profiles (Profile_Name, TargetIP, Port_Selection, Timeout, Threads) VALUES (?, ?, ?, ?, ?)",
                (name, target, ports_list, timeout, threads)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Profile '{name}' already exists")
        except Exception as e:
            raise Exception(f"Error saving profile: {e}")

    def load_profile(self, name):
        """Load a saved profile by name"""
        try:
            self.cursor.execute("SELECT * FROM profiles WHERE Profile_Name = ?", (name,))
            fetchone = self.cursor.fetchone()
            if fetchone:
                profile = {
                    "Profile_Name": fetchone[1],
                    "TargetIP": fetchone[2],
                    "Port_Selection": list(map(int, fetchone[3].split(","))),
                    "Timeout": fetchone[4],
                    "Threads": fetchone[5],
                    "Created_At": fetchone[6]
                }
                return profile
            return None
        except Exception as e:
            print(f"Error loading profile: {e}")
            return None

    def list_profiles(self):
        self.cursor.execute("SELECT Profile_Name FROM profiles")
        fetchall = self.cursor.fetchall()
        return [name[0] for name in fetchall]
        #return a list of names

    def delete_profile(self, name):
        """Delete a saved profile"""
        try:
            self.cursor.execute("DELETE FROM profiles WHERE Profile_Name = ?", (name,))
            self.conn.commit()
        except Exception as e:
            print(f"Error deleting profile: {e}")
    
    def close(self):
        """Close database connection"""
        try:
            if self.conn:
                self.conn.close()
        except Exception as e:
            print(f"Error closing database: {e}")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()
