"""SQLite storage for tasks. Everything is saved locally on the device."""
import sqlite3
from contextlib import closing
from datetime import date

PRIORITIES = ('Low', 'Medium', 'High')


class TaskDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self._create_tables()

    # ---------- internal helpers ----------
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _run(self, sql, params=(), fetch=None):
        """Run one SQL statement, commit, and optionally return rows."""
        with closing(self._connect()) as conn:
            cur = conn.execute(sql, params)
            conn.commit()
            if fetch == 'all':
                return [dict(row) for row in cur.fetchall()]
            if fetch == 'one':
                row = cur.fetchone()
                return dict(row) if row else None
            return cur.lastrowid

    def _create_tables(self):
        self._run(
            """CREATE TABLE IF NOT EXISTS tasks (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   title TEXT NOT NULL,
                   description TEXT NOT NULL DEFAULT '',
                   due_date TEXT NOT NULL DEFAULT '',
                   priority TEXT NOT NULL DEFAULT 'Medium',
                   completed INTEGER NOT NULL DEFAULT 0,
                   created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                   completed_at TEXT
               )"""
        )

    @staticmethod
    def _clean(title, description, due_date, priority):
        title = (title or '').strip()
        if not title:
            raise ValueError('Title cannot be empty.')
        if priority not in PRIORITIES:
            priority = 'Medium'
        return title, (description or '').strip(), (due_date or '').strip(), priority

    # ---------- public API ----------
    def add_task(self, title, description='', due_date='', priority='Medium'):
        title, description, due_date, priority = self._clean(
            title, description, due_date, priority)
        return self._run(
            'INSERT INTO tasks (title, description, due_date, priority) VALUES (?, ?, ?, ?)',
            (title, description, due_date, priority))

    def update_task(self, task_id, title, description='', due_date='', priority='Medium'):
        title, description, due_date, priority = self._clean(
            title, description, due_date, priority)
        self._run(
            'UPDATE tasks SET title=?, description=?, due_date=?, priority=? WHERE id=?',
            (title, description, due_date, priority, task_id))

    def delete_task(self, task_id):
        self._run('DELETE FROM tasks WHERE id=?', (task_id,))

    def set_completed(self, task_id, completed):
        self._run(
            "UPDATE tasks SET completed=?, "
            "completed_at=CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE NULL END WHERE id=?",
            (1 if completed else 0, 1 if completed else 0, task_id))

    def get_tasks(self, completed=False, search=''):
        """Pending tasks: soonest due date first, then priority.
        Completed tasks: most recently completed first."""
        like = '%' + (search or '').strip() + '%'
        if completed:
            order = 'completed_at DESC, id DESC'
        else:
            order = ("CASE WHEN due_date = '' THEN 1 ELSE 0 END, due_date ASC, "
                     "CASE priority WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END, id DESC")
        return self._run(
            'SELECT * FROM tasks WHERE completed=? AND (title LIKE ? OR description LIKE ?) '
            'ORDER BY ' + order,
            (1 if completed else 0, like, like), fetch='all')

    def get_stats(self):
        row = self._run(
            "SELECT COUNT(*) AS total, "
            "COALESCE(SUM(completed), 0) AS completed, "
            "COALESCE(SUM(CASE WHEN completed=0 AND due_date != '' AND due_date < ? "
            "THEN 1 ELSE 0 END), 0) AS overdue FROM tasks",
            (date.today().isoformat(),), fetch='one')
        row['pending'] = row['total'] - row['completed']
        return row

    def delete_completed(self):
        self._run('DELETE FROM tasks WHERE completed=1')

    def delete_all(self):
        self._run('DELETE FROM tasks')
