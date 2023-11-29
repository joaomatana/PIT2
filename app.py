from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

# Função auxiliar para obter o cursor e a conexão
def get_cursor_and_conn():
    conn = sqlite3.connect('cupcakes.db', check_same_thread=False)
    cursor = conn.cursor()
    return cursor, conn

# Rota para a página de login
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('cupcake_list'))
    return render_template('login.html')

# Rota para processar o login
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Conectar ao banco de dados
    conn = sqlite3.connect('cupcakes.db')
    cursor = conn.cursor()

    # Consulta para encontrar o usuário
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()

    if user:
        session['username'] = username
        conn.close()
        return redirect(url_for('cupcake_list'))
    else:
        conn.close()
        return render_template('login.html', error="Usuário ou senha inválidos")

# Rota para a página de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_name = request.form.get('new_name')
        new_username = request.form.get('new_username')
        new_password = request.form.get('new_password')
        email = request.form.get('email')
        endereco = request.form.get('endereco')

        # Conectar ao banco de dados
        conn = sqlite3.connect('cupcakes.db')
        cursor = conn.cursor()

        # Verificar se o usuário já existe
        cursor.execute('SELECT * FROM users WHERE username=?', (new_username,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return "Usuário já existe. Escolha um nome de usuário diferente."

        # Inserir novo usuário no banco de dados
        cursor.execute('INSERT INTO users (nome, username, password, email, endereco) VALUES (?, ?, ?, ?, ?)',
                       (new_name, new_username, new_password, email, endereco))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('register.html')

# Função para obter o ID do usuário
def obter_usuario_id(username):
    conn = sqlite3.connect('cupcakes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username=?', (username,))
    user_id = cursor.fetchone()
    conn.close()
    return user_id[0] if user_id else None

# Rota para a página de listagem de cupcakes
@app.route('/cupcakes')
def cupcake_list():
    # Verifica se o usuário está autenticado
    if 'username' in session:
        # Conectar ao banco de dados
        conn = sqlite3.connect('cupcakes.db')
        cursor = conn.cursor()

        # Executar uma consulta SELECT para obter todos os cupcakes
        cursor.execute('SELECT * FROM produtos')

        # Obter todos os cupcakes da consulta
        cupcakes = cursor.fetchall()

        # Fechar a conexão
        conn.close()

        # Renderizar a página HTML e passar a lista de cupcakes
        return render_template('cupcake_list.html', cupcakes=cupcakes)

    # Redirecionar para a página de login se o usuário não estiver autenticado
    return redirect(url_for('index'))

# Função para obter o ID do carrinho do usuário
def obter_carrinho_id_do_usuario(username):
    conn = sqlite3.connect('cupcakes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM carrinho WHERE usuario_id=?', (obter_usuario_id(username),))
    carrinho_id = cursor.fetchone()
    if carrinho_id:
        carrinho_id = carrinho_id[0]
    else:
        # Se o usuário não tiver um carrinho ativo, cria um novo
        cursor.execute('INSERT INTO carrinho (usuario_id, quantidade) VALUES (?, ?)', (obter_usuario_id(username), 0))
        conn.commit()

        # Obtém o ID do carrinho recém-criado
        cursor.execute('SELECT id FROM carrinho WHERE usuario_id=?', (obter_usuario_id(username),))
        carrinho_id = cursor.fetchone()
        if carrinho_id:
            carrinho_id = carrinho_id[0]

    conn.close()
    return carrinho_id

# Rota para a página do carrinho
@app.route('/shopping-cart')
def shopping_cart():
    if 'username' in session:
        user_id = obter_usuario_id(session['username'])

        if user_id:
            # Conectar ao banco de dados
            conn = sqlite3.connect('cupcakes.db')
            cursor = conn.cursor()

            # Obter o ID do carrinho do usuário que ainda não foi finalizado
            carrinho_id = obter_carrinho_id_do_usuario(session['username'])

            if carrinho_id:
                # Obter informações dos produtos no carrinho
                cursor.execute('''
                    SELECT produtos.nome, produtos.descricao, produtos.preco
                    FROM carrinho
                    JOIN produtos ON carrinho.produto_id = produtos.id
                    WHERE carrinho.usuario_id = ?
                ''', (user_id,))

                cupcakes_no_carrinho = cursor.fetchall()

                # Fechar a conexão
                conn.close()

                # Renderizar a página HTML e passar a lista de produtos no carrinho
                return render_template('shopping_cart.html', cupcakes_no_carrinho=cupcakes_no_carrinho)

    # Redirecionar para a página de login se o usuário não estiver autenticado ou não tiver um carrinho ativo
    return redirect(url_for('index'))

# Rota para adicionar itens ao carrinho
@app.route('/adicionar-ao-carrinho', methods=['POST'])
def adicionar_ao_carrinho():
    if 'username' not in session:
        return redirect(url_for('index'))

    cupcake_id = request.form.get('cupcake_id')

    # Lógica para adicionar ao carrinho
    cursor, conn = get_cursor_and_conn()

    # Adiciona o ID do cupcake ao carrinho
    cursor.execute('INSERT INTO carrinho (usuario_id, produto_id, quantidade) VALUES (?, ?, ?)',
                   (obter_usuario_id(session['username']), cupcake_id, 1))

    conn.commit()
    conn.close()

    # Informa ao Flask que a sessão foi modificada
    session.modified = True

    return redirect(url_for('cupcake_list'))

# Rota para excluir item do carrinho
@app.route('/excluir-do-carrinho', methods=['POST'])
def excluir_do_carrinho():
    if 'username' not in session:
        return redirect(url_for('index'))

    cupcake_id = request.form.get('cupcake_id')
    user_id = obter_usuario_id(session['username'])

    if user_id:
        # Conectar ao banco de dados
        conn = sqlite3.connect('cupcakes.db')
        cursor = conn.cursor()

        # Lógica para excluir do carrinho
        cursor.execute('DELETE FROM carrinho WHERE usuario_id=? AND produto_id=?', (user_id, cupcake_id))
        conn.commit()

        # Fechar a conexão
        conn.close()

        # Informa ao Flask que a sessão foi modificada
        session.modified = True

    return redirect(url_for('shopping_cart'))

# Rota para o checkout
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'username' not in session:
        return redirect(url_for('index'))

    user_id = obter_usuario_id(session['username'])

    if user_id:
        # Conectar ao banco de dados
        conn = sqlite3.connect('cupcakes.db')
        cursor = conn.cursor()

        # Obter o ID do carrinho do usuário que ainda não foi finalizado
        carrinho_id = obter_carrinho_id_do_usuario(session['username'])

        if carrinho_id:
            # Obter informações dos produtos no carrinho
            cursor.execute('''
                SELECT produtos.nome, produtos.descricao, produtos.preco
                FROM carrinho
                JOIN produtos ON carrinho.produto_id = produtos.id
                WHERE carrinho.usuario_id = ?
            ''', (user_id,))

            cupcakes_no_carrinho = cursor.fetchall()

            # Calcular o total da compra
            total = sum(cupcake[2] for cupcake in cupcakes_no_carrinho)

            # Renderizar a página HTML e passar a lista de produtos no carrinho e o total
            return render_template('checkout.html', cupcakes_no_carrinho=cupcakes_no_carrinho, total=total)

    # Redirecionar para a página de login se o usuário não estiver autenticado ou não tiver um carrinho ativo
    return redirect(url_for('index'))

# Rota para finalizar o pedido
@app.route('/finalizar-pedido', methods=['POST'])
def finalizar_pedido():
    if 'username' not in session:
        return redirect(url_for('index'))

    user_id = obter_usuario_id(session['username'])

    if user_id:
        # Conectar ao banco de dados
        conn = sqlite3.connect('cupcakes.db')
        cursor = conn.cursor()

        # Obter o ID do carrinho do usuário que ainda não foi finalizado
        carrinho_id = obter_carrinho_id_do_usuario(session['username'])

        if carrinho_id:
            # Marcar o carrinho como finalizado
            cursor.execute('UPDATE carrinho SET finalizado=1 WHERE id=?', (carrinho_id,))
            conn.commit()

            # Criar um novo pedido
            cursor.execute('INSERT INTO pedidos (usuario_id) VALUES (?)', (user_id,))
            conn.commit()

            # Excluir os itens do carrinho
            cursor.execute('DELETE FROM carrinho WHERE usuario_id=?', (user_id,))
            conn.commit()

            # Fechar a conexão
            conn.close()

            return render_template('pedido_finalizado.html')
                

    # Redirecionar para a página de login se o usuário não estiver autenticado ou não tiver um carrinho ativo
    return redirect(url_for('index'))

# Rota para a página de perfil do usuário
@app.route('/user-profile')
def user_profile():
    if 'username' in session:
        conn = sqlite3.connect('cupcakes.db')
        cursor = conn.cursor()

        # Obter dados do usuário
        cursor.execute('SELECT * FROM users WHERE username=?', (session['username'],))
        user_data = cursor.fetchone()

        conn.close()

        if user_data:
            user = {
                'username': user_data[1],
                'password': user_data[2],
                'nome': user_data[3],
                'email': user_data[4],
                'endereco': user_data[5]
            }
            return render_template('user_profile.html', user=user)
    
    return redirect(url_for('index'))

# Rota para a página de edição do perfil
@app.route('/editar-perfil', methods=['GET', 'POST'])
def editar_perfil():
    if 'username' in session:
        conn = sqlite3.connect('cupcakes.db')
        cursor = conn.cursor()

        if request.method == 'POST':
            novo_email = request.form.get('novo_email')
            novo_endereco = request.form.get('novo_endereco')

            # Atualizar dados do usuário
            cursor.execute('UPDATE users SET email=?, endereco=? WHERE username=?',
                           (novo_email, novo_endereco, session['username']))
            conn.commit()

            conn.close()

            return redirect(url_for('user_profile'))

        # Obter dados atuais do usuário
        cursor.execute('SELECT * FROM users WHERE username=?', (session['username'],))
        user_data = cursor.fetchone()

        conn.close()

        if user_data:
            user = {
                'username': user_data[1],
                'password': user_data[2],
                'nome': user_data[3],
                'email': user_data[4],
                'endereco': user_data[5]
            }
            return render_template('editar_perfil.html', user=user)
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
