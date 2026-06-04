import sqlite3

conn = sqlite3.connect("data/sample.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees(
    id INTEGER PRIMARY KEY,
    name TEXT,
    department TEXT,
    salary INTEGER
)
""")

employees = [
    ("John", "IT", 60000),
    ("Alice", "HR", 50000),
    ("Bob", "IT", 70000),
    ("Emma", "Finance", 65000),
    ("David", "HR", 55000)
]

cursor.executemany(
    "INSERT INTO employees(name, department, salary) VALUES (?, ?, ?)",
    employees
)

conn.commit()
conn.close()

print("Database created successfully!")