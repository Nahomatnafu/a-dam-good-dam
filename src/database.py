import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime

class CatalogDatabase:
    def __init__(self, catalog_path: Path):
        self.catalog_path = catalog_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database connection and create tables"""
        self.catalog_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.catalog_path))
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()
        
        # Files table - main file information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT UNIQUE NOT NULL,
                filesize INTEGER,
                duration REAL,
                width INTEGER,
                height INTEGER,
                created_date TEXT,
                modified_date TEXT,
                analyzed_date TEXT,
                file_type TEXT,
                thumbnail_path TEXT
            )
        ''')
        
        # Keywords table - unique keywords
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT UNIQUE NOT NULL,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # File_keywords junction table - many-to-many relationship
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_keywords (
                file_id INTEGER,
                keyword_id INTEGER,
                confidence REAL DEFAULT 1.0,
                source TEXT DEFAULT 'manual',
                PRIMARY KEY (file_id, keyword_id),
                FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE,
                FOREIGN KEY (keyword_id) REFERENCES keywords (id) ON DELETE CASCADE
            )
        ''')
        
        # Metadata table - additional file metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                file_id INTEGER PRIMARY KEY,
                description TEXT,
                comment TEXT,
                faces_detected INTEGER DEFAULT 0,
                ai_analysis TEXT,  -- JSON string of full AI analysis
                custom_fields TEXT,  -- JSON string for extensibility
                FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_filepath ON files (filepath)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords (keyword)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_keywords_file ON file_keywords (file_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_keywords_keyword ON file_keywords (keyword_id)')
        
        self.conn.commit()
    
    def add_file(self, file_info: Dict) -> int:
        """Add a file to the catalog, or update it if it already exists.

        Uses an upsert pattern (INSERT … ON CONFLICT DO UPDATE) so that
        re-scanning a file never changes its primary key, which would
        cascade-delete all of its associated keywords and metadata.
        """
        cursor = self.conn.cursor()

        cursor.execute('''
            INSERT INTO files
                (filename, filepath, filesize, duration, width, height,
                 created_date, modified_date, file_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(filepath) DO UPDATE SET
                filename     = excluded.filename,
                filesize     = excluded.filesize,
                duration     = excluded.duration,
                width        = excluded.width,
                height       = excluded.height,
                created_date = excluded.created_date,
                modified_date= excluded.modified_date,
                file_type    = excluded.file_type
        ''', (
            file_info['filename'],
            file_info['filepath'],
            file_info.get('filesize'),
            file_info.get('duration'),
            file_info.get('width'),
            file_info.get('height'),
            file_info.get('created_date'),
            file_info.get('modified_date'),
            file_info.get('file_type')
        ))

        # lastrowid is 0 on an UPDATE path; fetch the real id.
        if cursor.lastrowid:
            file_id = cursor.lastrowid
        else:
            cursor.execute('SELECT id FROM files WHERE filepath = ?',
                           (file_info['filepath'],))
            file_id = cursor.fetchone()[0]

        self.conn.commit()
        return file_id
    
    def add_keywords_to_file(self, file_id: int, keywords: List[str], 
                           source: str = 'ai', confidence: float = 1.0):
        """Add keywords to a file"""
        cursor = self.conn.cursor()
        
        for keyword in keywords:
            # Insert keyword if it doesn't exist
            cursor.execute('''
                INSERT OR IGNORE INTO keywords (keyword) VALUES (?)
            ''', (keyword,))
            
            # Get keyword ID
            cursor.execute('SELECT id FROM keywords WHERE keyword = ?', (keyword,))
            keyword_id = cursor.fetchone()[0]
            
            # Link file to keyword
            cursor.execute('''
                INSERT OR REPLACE INTO file_keywords 
                (file_id, keyword_id, confidence, source)
                VALUES (?, ?, ?, ?)
            ''', (file_id, keyword_id, confidence, source))
        
        self.conn.commit()
    
    def search_files(self, query: str = "", keywords: List[str] = None) -> List[Dict]:
        """Search files by filename or keywords"""
        cursor = self.conn.cursor()
        
        base_query = '''
            SELECT DISTINCT f.*, 
                   GROUP_CONCAT(k.keyword, ', ') as keywords
            FROM files f
            LEFT JOIN file_keywords fk ON f.id = fk.file_id
            LEFT JOIN keywords k ON fk.keyword_id = k.id
        '''
        
        conditions = []
        params = []
        
        if query:
            conditions.append("f.filename LIKE ?")
            params.append(f"%{query}%")
        
        if keywords:
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append("k.keyword LIKE ?")
                params.append(f"%{keyword}%")
            conditions.append(f"({' OR '.join(keyword_conditions)})")
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        base_query += " GROUP BY f.id ORDER BY f.filename"
        
        cursor.execute(base_query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_keywords(self) -> List[Dict]:
        """Get all keywords with usage counts"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT k.keyword, COUNT(fk.file_id) as usage_count
            FROM keywords k
            LEFT JOIN file_keywords fk ON k.id = fk.keyword_id
            GROUP BY k.keyword
            ORDER BY usage_count DESC, k.keyword
        ''')
        return [dict(row) for row in cursor.fetchall()]
    
    def get_file_id(self, filepath: str) -> Optional[int]:
        """Get file ID by filepath"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM files WHERE filepath = ?', (filepath,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def clear_file_keywords(self, file_id: int):
        """Clear all keywords for a file"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM file_keywords WHERE file_id = ?', (file_id,))
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
