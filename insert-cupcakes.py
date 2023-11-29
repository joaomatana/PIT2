import sqlite3

conn = sqlite3.connect('cupcakes.db')
cursor = conn.cursor()

# Dados de exemplo para os cupcakes
cupcakes = [
    ('Cupcake de Chocolate', 'Delicioso cupcake de chocolate', 5.99),
    ('Cupcake de Baunilha', 'Saboroso cupcake de baunilha', 4.99),
    ('Cupcake de Morango', 'Irresistível cupcake de morango', 6.49),
    ('Cupcake de Limão', 'Refrescante cupcake de limão', 3.99),
    ('Cupcake de Cenoura', 'Cupcake de cenoura com cobertura de chocolate', 7.99),
]

# Inserir dados na tabela produtos
cursor.executemany('INSERT INTO produtos (nome, descricao, preco) VALUES (?, ?, ?)', cupcakes)

# Commit para salvar as alterações
conn.commit()

# Fechar a conexão
conn.close()
