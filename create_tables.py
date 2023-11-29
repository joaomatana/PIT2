import sqlite3

conn = sqlite3.connect('cupcakes.db')
cursor = conn.cursor()

# Tabela de Usuários
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        nome TEXT,
        email TEXT
        endereco TEXT
    )
''')

# Tabela de Produtos (Cupcakes)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY,
        nome TEXT UNIQUE NOT NULL,
        descricao TEXT,
        preco REAL NOT NULL
    )
''')

# Tabela de Carrinho de Compras
cursor.execute('''
    CREATE TABLE IF NOT EXISTS carrinho (
        id INTEGER PRIMARY KEY,
        usuario_id INTEGER,
        produto_id INTEGER,
        quantidade INTEGER NOT NULL,
        finalizado INTEGER DEFAULT 0,
        FOREIGN KEY (usuario_id) REFERENCES users(id),
        FOREIGN KEY (produto_id) REFERENCES produtos(id)
    )
''')

# Tabela de Pedidos
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY,
        usuario_id INTEGER,
        data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES users(id)
    )
''')

conn.commit()
conn.close()
