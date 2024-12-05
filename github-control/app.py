from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import git
import os
from datetime import datetime
import pytz
import json
import psutil
import socket
import subprocess
import re
import glob
import time

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Arquivo para armazenar as configurações dos repositórios
CONFIG_FILE = 'repo_config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {'excluded_repos': [], 'remote_urls': {}}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def find_git_repos(start_path):
    git_repos = []
    config = load_config()
    excluded_repos = config.get('excluded_repos', [])
    
    for root, dirs, files in os.walk(start_path):
        if '.git' in dirs:
            # Ignora diretórios dentro de node_modules, venv e repositórios excluídos
            if ('node_modules' not in root and 
                'venv' not in root and 
                root not in excluded_repos):
                git_repos.append({
                    'path': root,
                    'name': os.path.basename(root)
                })
    return git_repos

def get_service_info(repo_path):
    services = []
    try:
        # Procura por arquivos de configuração comuns
        config_files = {
            'package.json': 'Node.js',
            'requirements.txt': 'Python',
            'pom.xml': 'Java',
            'build.gradle': 'Java',
            'Dockerfile': 'Docker'
        }
        
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file in config_files:
                    service_type = config_files[file]
                    service_path = os.path.join(root, file)
                    
                    # Procura por processos relacionados
                    for proc in psutil.process_iter(['pid', 'name', 'cwd', 'create_time']):
                        try:
                            if proc.cwd().startswith(os.path.dirname(service_path)):
                                # Obtém as portas em uso
                                ports = []
                                try:
                                    connections = proc.connections()
                                    for conn in connections:
                                        if conn.status == 'LISTEN':
                                            ports.append(conn.laddr.port)
                                except:
                                    pass
                                
                                # Calcula o uptime
                                uptime = datetime.now() - datetime.fromtimestamp(proc.create_time())
                                
                                services.append({
                                    'type': service_type,
                                    'name': os.path.basename(os.path.dirname(service_path)),
                                    'path': os.path.dirname(service_path),
                                    'pid': proc.pid,
                                    'ports': sorted(list(set(ports))),
                                    'status': 'Rodando' if ports else 'Em uso',
                                    'uptime': uptime
                                })
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                            continue
                            
                    # Se não encontrou processo rodando, adiciona como serviço parado
                    if not any(s['path'] == os.path.dirname(service_path) for s in services):
                        services.append({
                            'type': service_type,
                            'name': os.path.basename(os.path.dirname(service_path)),
                            'path': os.path.dirname(service_path),
                            'status': 'Parado'
                        })
    except Exception as e:
        app.logger.error(f"Erro ao obter informações dos serviços: {str(e)}")
    
    return services

def detect_service_type(service_path):
    """Detecta o tipo de serviço e retorna o comando para iniciá-lo"""
    if os.path.exists(os.path.join(service_path, 'package.json')):
        return 'Node.js', ['npm', 'start']
    elif os.path.exists(os.path.join(service_path, 'requirements.txt')):
        # Procura por um arquivo Python que possa ser o principal
        main_files = ['app.py', 'main.py', 'run.py', 'server.py']
        for file in main_files:
            if os.path.exists(os.path.join(service_path, file)):
                return 'Python', ['python3', file]
        return 'Python', None
    elif os.path.exists(os.path.join(service_path, 'pom.xml')):
        return 'Java', ['mvn', 'spring-boot:run']
    elif os.path.exists(os.path.join(service_path, 'build.gradle')):
        return 'Java', ['gradle', 'bootRun']
    elif os.path.exists(os.path.join(service_path, 'Dockerfile')):
        return 'Docker', ['docker-compose', 'up']
    return None, None

base_path = '/root'
repos_cache = {}

@app.route('/')
def index():
    # Carrega repositórios e configurações
    repos = find_git_repos('/root')
    config = load_config()
    
    # Adiciona informações do remote e serviços para cada repositório
    for repo in repos:
        try:
            git_repo = git.Repo(repo['path'])
            if git_repo.remotes:
                repo['remote_url'] = git_repo.remotes.origin.url
            else:
                repo['remote_url'] = ''
        except:
            repo['remote_url'] = ''
            
        # Adiciona configuração salva
        if repo['path'] in config.get('remote_urls', {}):
            repo.update({'remote_url': config['remote_urls'][repo['path']]})
        
        # Adiciona informações dos serviços
        services_info = get_service_info(repo['path'])
        repo['services'] = services_info
        repo['detected_types'] = list(set(service['type'] for service in services_info))
    
    return render_template('index.html', repos=repos)

@app.route('/configure_repo', methods=['POST'])
def configure_repo():
    repo_path = request.form['repo_path']
    remote_url = request.form['remote_url']
    
    try:
        repo = git.Repo(repo_path)
        
        # Configura o remote
        if 'origin' in [remote.name for remote in repo.remotes]:
            repo.delete_remote('origin')
        repo.create_remote('origin', remote_url)
        
        # Salva configuração
        config = load_config()
        if 'remote_urls' not in config:
            config['remote_urls'] = {}
        config['remote_urls'][repo_path] = remote_url
        save_config(config)
        
        flash('Repositório configurado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao configurar repositório: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/confirm_remove/<path:repo_path>')
def confirm_remove(repo_path):
    # Decodifica o caminho do repositório
    repo_path = os.path.abspath(repo_path)
    return render_template('confirm_remove.html', repo_path=repo_path)

@app.route('/remove_repo', methods=['POST'])
def remove_repo():
    try:
        repo_path = request.form.get('repo_path')
        remove_option = request.form.get('remove_option')
        
        if not repo_path or not remove_option:
            flash('Parâmetros inválidos', 'error')
            return redirect(url_for('index'))
        
        # Carrega a configuração atual
        config = load_config()
        
        # Para qualquer opção, primeiro para os serviços em execução
        services = get_service_info(repo_path)
        if services:
            for service in services:
                if service.get('pid'):
                    try:
                        process = psutil.Process(service['pid'])
                        process.terminate()
                        process.wait(timeout=5)  # Espera até 5 segundos pelo término
                    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                        pass  # Processo já não existe ou não terminou a tempo
        
        # Remove arquivos Git se necessário
        if remove_option in ['git_only', 'completely']:
            try:
                import shutil
                git_dir = os.path.join(repo_path, '.git')
                if os.path.exists(git_dir):
                    shutil.rmtree(git_dir)
                
                # Remove arquivos de configuração do Git
                git_files = ['.gitignore', '.gitmodules', '.gitattributes']
                for git_file in git_files:
                    git_file_path = os.path.join(repo_path, git_file)
                    if os.path.exists(git_file_path):
                        os.remove(git_file_path)
                
            except Exception as e:
                flash(f'Erro ao excluir arquivos do Git: {str(e)}', 'error')
                return redirect(url_for('index'))
        
        # Remove da lista de configuração se necessário
        if remove_option in ['list_only', 'completely']:
            if 'excluded_repos' not in config:
                config['excluded_repos'] = []
            
            if repo_path not in config['excluded_repos']:
                config['excluded_repos'].append(repo_path)
            
            # Remove a URL remota se existir
            if 'remote_urls' in config and repo_path in config['remote_urls']:
                del config['remote_urls'][repo_path]
            
            save_config(config)
        
        flash('Repositório removido com sucesso', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Erro ao processar solicitação: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/commit', methods=['POST'])
def commit():
    try:
        app.logger.info("Iniciando processo de commit...")
        repo_path = request.form.get('repo_path')
        commit_message = request.form.get('message')
        
        if not repo_path or not commit_message:
            app.logger.error("Parâmetros inválidos: repo_path ou message não fornecidos")
            return jsonify({
                'success': False,
                'error': 'Parâmetros inválidos'
            }), 400
        
        app.logger.info(f"Abrindo repositório: {repo_path}")
        repo = git.Repo(repo_path)
        
        # Verifica se há alterações para commitar
        app.logger.info("Verificando alterações...")
        if not repo.is_dirty(untracked_files=True):
            app.logger.info("Nenhuma alteração encontrada para commit")
            return jsonify({
                'success': False,
                'error': 'Não há alterações para commitar'
            }), 400
        
        # Adiciona todas as alterações
        app.logger.info("Adicionando alterações ao stage...")
        repo.git.add('.')
        
        # Cria o commit com a mensagem
        app.logger.info("Criando commit...")
        date_br = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%d/%m/%Y %H:%M:%S")
        full_message = f"{commit_message} - {date_br}"
        repo.index.commit(full_message)
        
        # Verifica se tem remote configurado
        if not repo.remotes:
            app.logger.error("Nenhum remote configurado")
            return jsonify({
                'success': False,
                'error': 'Nenhum remote configurado. Configure um remote primeiro.'
            }), 400
        
        try:
            app.logger.info("Tentando push...")
            # Tenta fazer push
            repo.remote().push()
            app.logger.info("Push realizado com sucesso!")
        except git.exc.GitCommandError as e:
            app.logger.warning(f"Erro no push inicial: {str(e)}")
            if "no upstream branch" in str(e):
                # Se não houver upstream branch, configura e tenta novamente
                app.logger.info("Configurando upstream branch...")
                current = repo.active_branch
                repo.git.branch('--set-upstream-to', f'origin/{current.name}', current.name)
                app.logger.info("Tentando push novamente...")
                repo.remote().push()
                app.logger.info("Push realizado com sucesso após configurar upstream!")
            else:
                raise e
        
        return jsonify({
            'success': True,
            'message': 'Commit e push realizados com sucesso!'
        })
        
    except Exception as e:
        error_message = str(e)
        app.logger.error(f"Erro durante commit/push: {error_message}")
        return jsonify({
            'success': False,
            'error': f'Erro ao realizar commit/push: {error_message}'
        }), 500

@app.route('/get_changes', methods=['GET', 'POST'])
def get_changes():
    repo_path = request.args.get('repo_path')
    if not repo_path and request.is_json:
        repo_path = request.json.get('repo_path')
    
    if not repo_path:
        return jsonify({'success': False, 'error': 'Caminho do repositório não fornecido'}), 400
        
    try:
        repo = git.Repo(repo_path)
        changes = []
        
        try:
            # Verifica arquivos modificados (incluindo staged)
            for item in repo.index.diff(None):
                if item.new_file:
                    changes.append(f"A {item.a_path}")
                elif item.deleted_file:
                    changes.append(f"D {item.a_path}")
                else:
                    changes.append(f"M {item.a_path}")
            
            # Verifica arquivos staged
            for item in repo.index.diff('HEAD'):
                status = "S"  # S para staged
                path = item.a_path
                if not any(c.endswith(path) for c in changes):  # Evita duplicatas
                    changes.append(f"{status} {path}")
            
            # Verifica arquivos não rastreados
            for item in repo.untracked_files:
                changes.append(f"? {item}")
                
            return jsonify({
                'success': True,
                'changes': changes,
                'branch': repo.active_branch.name
            })
        except git.exc.GitCommandError as e:
            # Se houver erro no git, tenta recuperar manualmente
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                 cwd=repo_path, 
                                 capture_output=True, 
                                 text=True)
            if result.returncode == 0:
                changes = [line.strip() for line in result.stdout.splitlines()]
                return jsonify({
                    'success': True,
                    'changes': changes,
                    'branch': 'unknown'  # Não podemos determinar o branch neste caso
                })
            else:
                raise Exception(f"Erro ao executar git status: {result.stderr}")
                
    except Exception as e:
        app.logger.error(f"Erro ao obter alterações: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/refresh_repos', methods=['POST'])
def refresh_repos():
    try:
        # Atualiza o cache de informações dos repositórios
        global repos_cache
        repos_cache = {}
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Erro ao atualizar repositórios: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/service/logs/<int:pid>')
def get_service_logs(pid):
    try:
        # Verifica se o processo existe
        process = psutil.Process(pid)
        
        # Obtém o caminho do executável e o diretório de trabalho
        exe = process.exe()
        cwd = process.cwd()
        
        logs = []
        
        # Primeiro tenta ler a saída direta do processo
        try:
            # No Linux, podemos tentar ler /proc/{pid}/fd/1 e /proc/{pid}/fd/2
            try:
                with open(f'/proc/{pid}/fd/1', 'r') as stdout:
                    logs.extend(stdout.readlines()[-50:])  # Últimas 50 linhas
            except:
                pass
                
            try:
                with open(f'/proc/{pid}/fd/2', 'r') as stderr:
                    logs.extend(stderr.readlines()[-50:])  # Últimas 50 linhas
            except:
                pass
        except:
            pass
            
        # Se não conseguiu ler a saída direta, procura por arquivos de log
        if not logs:
            log_files = []
            common_log_files = ['*.log', 'logs/*.log', 'log/*.log', 'var/log/*.log']
            for pattern in common_log_files:
                found_files = glob.glob(os.path.join(cwd, pattern))
                if found_files:
                    log_files.extend(found_files)
            
            # Se encontrou arquivos de log, lê o conteúdo do mais recente
            if log_files:
                latest_log = max(log_files, key=os.path.getmtime)
                try:
                    with open(latest_log, 'r') as f:
                        logs = f.readlines()[-50:]  # Últimas 50 linhas
                except:
                    pass
        
        # Se ainda não tem logs, tenta usar o comando ps
        if not logs:
            try:
                ps_output = subprocess.check_output(['ps', '-p', str(pid), '-o', 'cmd='])
                logs = [f"Comando em execução: {ps_output.decode().strip()}"]
            except:
                pass
        
        # Limpa as linhas e remove linhas vazias
        logs = [line.strip() for line in logs if line.strip()]
        
        return jsonify({
            'success': True,
            'logs': logs
        })
        
    except psutil.NoSuchProcess:
        return jsonify({
            'success': False,
            'error': f'Processo {pid} não encontrado'
        })
    except Exception as e:
        app.logger.error(f"Erro ao obter logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Erro ao obter logs: {str(e)}'
        })

@app.route('/control_service', methods=['POST'])
def control_service():
    service_path = request.form.get('service_path')
    action = request.form.get('action')
    
    if not service_path or not action:
        flash('Parâmetros inválidos', 'error')
        return redirect(url_for('index'))
    
    try:
        # Obtém informações do serviço atual
        services = get_service_info(service_path)
        current_service = next((s for s in services if s.get('path') == service_path), None)
        
        if action == 'stop' and current_service and current_service.get('pid'):
            # Para o serviço
            try:
                process = psutil.Process(current_service['pid'])
                process.terminate()
                process.wait(timeout=5)
                flash('Serviço parado com sucesso', 'success')
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                flash('Erro ao parar o serviço', 'error')
        
        elif action in ['start', 'restart']:
            # Se for restart, primeiro para o serviço atual
            if action == 'restart' and current_service and current_service.get('pid'):
                try:
                    process = psutil.Process(current_service['pid'])
                    process.terminate()
                    process.wait(timeout=5)
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    pass
            
            # Detecta o tipo de serviço e obtém o comando para iniciá-lo
            service_type, start_command = detect_service_type(service_path)
            
            if not start_command:
                flash(f'Não foi possível determinar como iniciar o serviço do tipo {service_type}', 'error')
                return redirect(url_for('index'))
            
            try:
                # Inicia o serviço
                process = subprocess.Popen(
                    start_command,
                    cwd=service_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # Aguarda um pouco para ver se o processo inicia corretamente
                time.sleep(2)
                if process.poll() is None:  # Se ainda está rodando
                    flash(f'Serviço {"reiniciado" if action == "restart" else "iniciado"} com sucesso', 'success')
                else:
                    stdout, stderr = process.communicate()
                    error_msg = stderr.strip() or stdout.strip()
                    flash(f'Erro ao iniciar serviço: {error_msg}', 'error')
            
            except Exception as e:
                flash(f'Erro ao iniciar serviço: {str(e)}', 'error')
    
    except Exception as e:
        flash(f'Erro ao controlar serviço: {str(e)}', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
