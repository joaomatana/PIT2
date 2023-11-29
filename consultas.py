import sqlite3

conn = sqlite3.connect('cupcakes.db')
cursor = conn.cursor()

# Executar uma consulta SELECT
cursor.execute('SELECT * FROM users')

# Obter todos os registros
rows = cursor.fetchall()

# Exibir os registros
for row in rows:
    print(row)

conn.close()
