from flask import Flask, render_template, request, redirect, session, flash, url_for, send_from_directory

from models import Jogo, Usuario
from flask_mysqldb import MySQL
from dao import JogoDao, UsuarioDao
import os
import time

app = Flask(__name__)
app.secret_key = 'alura'

app.config['MYSQL_HOST'] = "0.0.0.0"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "jogoteca"
app.config['MYSQL_PORT'] = 3306
app.config['UPLOAD_PATH'] = os.path.dirname(os.path.abspath(__file__)) + '/upload'

db = MySQL(app)

jogo_dao = JogoDao(db)

usuario_dao = UsuarioDao(db)

@app.route('/')
def index():
    lista = jogo_dao.listar()
    return render_template('lista.html', titulo='Jogos', jogos=lista)

@app.route('/novo')
def novo():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    return render_template('novo.html', titulo='Novo jogo')

@app.route('/criar', methods=['POST',])
def criar():
    nome = request.form['nome']
    categoria = request.form['categoria']
    console = request.form['console']
    jogo = Jogo(nome, categoria, console)
    jogo = jogo_dao.salvar(jogo)

    arquivo = request.files['arquivo']
    upload_path = app.config['UPLOAD_PATH']

    timestamp = time.time()

    arquivo.save('{0}{1}{2}{3}{4}{5}'.format(upload_path, '/capa_', jogo.id, '-', timestamp, '.jpg'))

    return redirect(url_for('index'))

@app.route('/editar/<int:id>')
def editar(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('editar')))

    jogo = jogo_dao.busca_por_id(id)
    nome_imagem = recupera_imagem(id)
    capa_jogo='{0}{1}{2}'.format('capa_', id, '.jpg')
    return render_template('editar.html', titulo='Editando jogo', jogo=jogo, capa_jogo=nome_imagem)

@app.route('/deletar/<int:id>')
def deletar(id):
    jogo_dao.deletar(id)
    deleta_arquivo(id)
    flash('O jogo foi removido com sucesso!')
    return redirect(url_for('index'))

@app.route('/atualizar', methods=['POST',])
def atualizar():
    nome = request.form['nome']
    categoria = request.form['categoria']
    console = request.form['console']
    jogo = Jogo(nome, categoria, console, id=request.form['id'])
    jogo_dao.salvar(jogo)

    arquivo = request.files['arquivo']
    upload_path = app.config['UPLOAD_PATH']
    timestamp = time.time()
    deleta_arquivo(jogo.id)
    arquivo.save('{0}{1}{2}{3}{4}{5}'.format(upload_path, '/capa_', jogo.id, '-', timestamp, '.jpg'))
    return redirect(url_for('index'))

@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)

@app.route('/autenticar', methods=['POST',])
def autenticar():
    usuario = usuario_dao.buscar_por_id(request.form['usuario'])
    if usuario:
        if usuario.senha == request.form['senha']:
            session['usuario_logado'] = usuario.id
            flash(usuario.nome + ' logou com sucesso!')
            proxima_pagina = request.form['proxima']
            return redirect(proxima_pagina)
    else:
        flash('Username or password invalid !')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Nenhum usuário logado!')
    return redirect(url_for('index'))


@app.route('/upload/<nome_arquivo>')
def imagem(nome_arquivo):
    return send_from_directory('upload', nome_arquivo)


def recupera_imagem(id):
    for nome_arquivo in os.listdir(app.config['UPLOAD_PATH']):
        if '{0}{1}'.format('capa_', id) in nome_arquivo:
            return nome_arquivo

def deleta_arquivo(id):
    arquivo = recupera_imagem(id)
    os.remove(os.path.join(app.config['UPLOAD_PATH'], arquivo))


if __name__ == '__main__':
    app.run(debug=True)

