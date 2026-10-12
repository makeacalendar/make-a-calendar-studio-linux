"""Small local SQLite store. Project data never leaves the device."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class ProjectStore:
    def __init__(self, database: str | Path):
        self.path = Path(database)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.path))
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                payload TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                event_date TEXT NOT NULL,
                title TEXT NOT NULL,
                layer TEXT NOT NULL DEFAULT 'personal',
                notes TEXT NOT NULL DEFAULT ''
            );
            CREATE INDEX IF NOT EXISTS events_date_idx ON events(project_id, event_date);
        """)
        self.connection.commit()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    def create_project(self, name: str, payload: Optional[Dict[str, Any]] = None) -> str:
        name = name.strip()
        if not name:
            raise ValueError("project name cannot be empty")
        project_id, now = str(uuid.uuid4()), self._now()
        self.connection.execute("INSERT INTO projects(id,name,payload,created_at,updated_at) VALUES(?,?,?,?,?)",
                                (project_id, name, json.dumps(payload or {}, ensure_ascii=False), now, now))
        self.connection.commit()
        return project_id

    def list_projects(self) -> List[Dict[str, Any]]:
        rows = self.connection.execute("SELECT * FROM projects ORDER BY updated_at DESC, name COLLATE NOCASE").fetchall()
        return [{"id": row["id"], "name": row["name"], "payload": json.loads(row["payload"]),
                 "created_at": row["created_at"], "updated_at": row["updated_at"]} for row in rows]

    def get_project(self, project_id: str) -> Dict[str, Any]:
        row = self.connection.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
        if row is None:
            raise KeyError(project_id)
        events = self.connection.execute("SELECT * FROM events WHERE project_id=? ORDER BY event_date,id", (project_id,)).fetchall()
        return {"id": row["id"], "name": row["name"], "payload": json.loads(row["payload"]),
                "events": [dict(event) for event in events], "created_at": row["created_at"], "updated_at": row["updated_at"]}

    def list_events(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT e.*, p.name AS project_name FROM events e JOIN projects p ON p.id=e.project_id"
        clauses=[]; args=[]
        if start_date is not None:
            clauses.append("e.event_date >= ?"); args.append(start_date)
        if end_date is not None:
            clauses.append("e.event_date <= ?"); args.append(end_date)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY e.event_date, e.title COLLATE NOCASE"
        return [dict(row) for row in self.connection.execute(query,args).fetchall()]

    def update_project(self, project_id: str, *, name: Optional[str] = None, payload: Optional[Dict[str, Any]] = None) -> None:
        current = self.get_project(project_id)
        next_name = (name.strip() if name is not None else current["name"])
        if not next_name:
            raise ValueError("project name cannot be empty")
        next_payload = payload if payload is not None else current["payload"]
        self.connection.execute("UPDATE projects SET name=?,payload=?,updated_at=? WHERE id=?",
                                (next_name, json.dumps(next_payload, ensure_ascii=False), self._now(), project_id))
        self.connection.commit()

    def add_event(self, project_id: str, event_date: str, title: str, *, layer: str = "personal", notes: str = "") -> str:
        from datetime import date
        date.fromisoformat(event_date)
        if not title.strip():
            raise ValueError("event title cannot be empty")
        event_id = str(uuid.uuid4())
        self.connection.execute("INSERT INTO events(id,project_id,event_date,title,layer,notes) VALUES(?,?,?,?,?,?)",
                                (event_id, project_id, event_date, title.strip(), layer, notes))
        self.connection.execute("UPDATE projects SET updated_at=? WHERE id=?", (self._now(), project_id))
        self.connection.commit()
        return event_id

    def delete_event(self, event_id: str) -> None:
        self.connection.execute("DELETE FROM events WHERE id=?", (event_id,))
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()
