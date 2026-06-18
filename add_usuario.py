import sqlite3

conn = sqlite3.connect("banco.db")
cur = conn.cursor()

usuarios = [
    ("admin", "123", 1),
    ("Jullia", "123", 0),
    ("Matheus", "123", 0),
    ("Atila", "123", 0),
    ("Rovilson", "123", 0)
]

cur.executemany("""
INSERT INTO usuarios (usuario, senha, admin)
VALUES (?, ?, ?)
""", usuarios)

conn.commit()
conn.close()

print("Usuários criados com sucesso!")
