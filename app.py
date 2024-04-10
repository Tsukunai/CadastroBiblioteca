import os
from flask import Flask, render_template, request, Response
import sqlite3
import csv
from io import StringIO  # Adicionando a importação do módulo io
import codecs
from datetime import datetime
from tempfile import NamedTemporaryFile

app = Flask(__name__)

def conectar_bd():
    return sqlite3.connect('pesquisas.db')

def criar_bd():
    if not os.path.exists('pesquisas.db'):
        conn = conectar_bd()
        conn.execute('''CREATE TABLE pesquisas
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      isbn TEXT,
                      titulo TEXT,
                      autor_principal TEXT,
                      autor_secundario TEXT,
                      edicao TEXT,
                      ano TEXT,
                      editora TEXT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.close()

criar_bd()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inserir_pesquisa', methods=['POST'])
def inserir_pesquisa():
    isbn = request.form['isbn']
    titulo = request.form['titulo']
    autor_principal = request.form['autorPrincipal']
    autor_secundario = request.form['autorSecundario']
    edicao = request.form['edicao']
    ano = request.form['ano']
    editora = request.form['editora']

    conn = conectar_bd()
    conn.execute("INSERT INTO pesquisas (isbn, titulo, autor_principal, autor_secundario, edicao, ano, editora) VALUES (?, ?, ?, ?, ?, ?, ?)",
                 (isbn, titulo, autor_principal, autor_secundario, edicao, ano, editora))
    conn.commit()
    conn.close()
    return 'Dados da pesquisa inseridos com sucesso!'

@app.route('/pesquisas')
def listar_pesquisas():
    conn = conectar_bd()
    cursor = conn.execute("SELECT * FROM pesquisas ORDER BY timestamp DESC")
    pesquisas = cursor.fetchall()
    conn.close()
    return render_template('pesquisas.html', pesquisas=pesquisas)

@app.route('/download_pesquisas')
def download_pesquisas():
    conn = conectar_bd()
    cursor = conn.execute("SELECT * FROM pesquisas ORDER BY timestamp DESC")
    pesquisas = cursor.fetchall()
    conn.close()

    # Escrever o conteúdo dos dados em um arquivo temporário com codificação UTF-8
    with NamedTemporaryFile('w', delete=False, encoding='utf-8') as temp_file:
        for pesquisa in pesquisas:
            temp_file.write(f'ISBN: {pesquisa[1]}\n')
            temp_file.write(f'Título: {pesquisa[2]}\n')
            temp_file.write(f'Autor Principal: {pesquisa[3]}\n')
            temp_file.write(f'Autor Secundário: {pesquisa[4]}\n')
            temp_file.write(f'Edição: {pesquisa[5]}\n')
            temp_file.write(f'Ano: {pesquisa[6]}\n')
            temp_file.write(f'Editora: {pesquisa[7]}\n')
            temp_file.write(f'Data: {pesquisa[8]}\n\n')

    # Ler o conteúdo do arquivo temporário e enviar como resposta HTTP
    with codecs.open(temp_file.name, 'r', 'utf-8') as file:
        txt_content = file.read()

    # Remover o arquivo temporário após sua leitura
    os.unlink(temp_file.name)

    # Criar a resposta HTTP a partir do conteúdo do arquivo de texto
    return Response(txt_content, mimetype="text/plain", headers={"Content-Disposition": "attachment;filename=pesquisas.txt"})


@app.route('/pesquisar_por_isbn/<isbn>')
def pesquisar_por_isbn(isbn):
    conn = conectar_bd()
    cursor = conn.execute("SELECT * FROM pesquisas WHERE isbn=?", (isbn,))
    pesquisa = cursor.fetchone()
    conn.close()

    if pesquisa:
        # Formatar os dados da pesquisa para exibição
        resultado = f'ISBN: {pesquisa[1]}<br>'
        resultado += f'Título: {pesquisa[2]}<br>'
        resultado += f'Autor Principal: {pesquisa[3]}<br>'
        resultado += f'Autor Secundário: {pesquisa[4]}<br>'
        resultado += f'Edição: {pesquisa[5]}<br>'
        resultado += f'Ano: {pesquisa[6]}<br>'
        resultado += f'Editora: {pesquisa[7]}<br>'
        resultado += f'Data: {pesquisa[8]}<br>'
    else:
        resultado = 'Nenhuma pesquisa encontrada para o ISBN fornecido.'

    return resultado

@app.route('/adicionar_isbn', methods=['POST'])
def adicionar_isbn():
    isbn = request.json.get('isbn')
    conn = conectar_bd()
    conn.execute("INSERT INTO pesquisas (isbn) VALUES (?)", (isbn,))
    conn.commit()
    conn.close()
    return 'ISBN adicionado à base de dados com sucesso!'


if __name__ == '__main__':
    app.run(debug=True)


