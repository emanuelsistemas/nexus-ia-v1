from flask import Flask, render_template, request, redirect, url_for
import git
import os

app = Flask(__name__)

# Rota inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para gerenciar commits
@app.route('/commit', methods=['POST'])
def commit():
    commit_message = request.form['message']
    repo_path = '/root/project/nexus/nexus-ia/v1'  # Caminho do repositório
    repo = git.Repo(repo_path)
    repo.git.add('.');
    repo.index.commit(commit_message)
    repo.remote().push()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
