import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import git
import os
from datetime import datetime
import pytz

class GitManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da janela
        self.title("Nexus Git Manager")
        self.geometry("1000x600")
        
        # Tema escuro por padrão
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Variáveis
        self.current_repo = None
        self.projects = {}
        self.selected_project = tk.StringVar()

        # Layout
        self.create_widgets()
        self.load_projects()

    def create_widgets(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame superior para seleção de projeto
        top_frame = ctk.CTkFrame(main_frame)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        # Combobox para seleção de projeto
        ctk.CTkLabel(top_frame, text="Projeto:").pack(side=tk.LEFT, padx=5)
        self.project_combo = ctk.CTkComboBox(
            top_frame,
            variable=self.selected_project,
            command=self.on_project_select,
            width=300
        )
        self.project_combo.pack(side=tk.LEFT, padx=5)

        # Botão para adicionar novo projeto
        ctk.CTkButton(
            top_frame,
            text="Adicionar Projeto",
            command=self.add_project
        ).pack(side=tk.LEFT, padx=5)

        # Frame para alterações
        changes_frame = ctk.CTkFrame(main_frame)
        changes_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Lista de alterações
        self.changes_list = ttk.Treeview(
            changes_frame,
            columns=("Status", "File"),
            show="headings"
        )
        self.changes_list.heading("Status", text="Status")
        self.changes_list.heading("File", text="Arquivo")
        self.changes_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame inferior para ações
        bottom_frame = ctk.CTkFrame(main_frame)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)

        # Campo de mensagem do commit
        self.commit_msg = ctk.CTkEntry(
            bottom_frame,
            placeholder_text="Mensagem do commit",
            width=400
        )
        self.commit_msg.pack(side=tk.LEFT, padx=5)

        # Botões de ação
        ctk.CTkButton(
            bottom_frame,
            text="Commit & Push",
            command=self.commit_and_push
        ).pack(side=tk.LEFT, padx=5)

        ctk.CTkButton(
            bottom_frame,
            text="Atualizar",
            command=self.refresh_changes
        ).pack(side=tk.LEFT, padx=5)

        # Frame para histórico
        history_frame = ctk.CTkFrame(main_frame)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Lista de commits
        self.history_list = ttk.Treeview(
            history_frame,
            columns=("Hash", "Date", "Message"),
            show="headings"
        )
        self.history_list.heading("Hash", text="Hash")
        self.history_list.heading("Date", text="Data")
        self.history_list.heading("Message", text="Mensagem")
        self.history_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_projects(self):
        # Carrega projetos Git existentes
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for root, dirs, files in os.walk(base_path):
            if '.git' in dirs:
                project_name = os.path.basename(root)
                self.projects[project_name] = root

        # Atualiza combobox
        self.project_combo.configure(values=list(self.projects.keys()))
        if self.projects:
            self.project_combo.set(list(self.projects.keys())[0])
            self.on_project_select(list(self.projects.keys())[0])

    def on_project_select(self, project_name):
        if project_name in self.projects:
            self.current_repo = git.Repo(self.projects[project_name])
            self.refresh_changes()
            self.refresh_history()

    def refresh_changes(self):
        if not self.current_repo:
            return

        # Limpa a lista
        for item in self.changes_list.get_children():
            self.changes_list.delete(item)

        # Adiciona alterações não commitadas
        for item in self.current_repo.index.diff(None):
            status = "Modificado"
            if item.new_file:
                status = "Novo"
            elif item.deleted_file:
                status = "Deletado"
            self.changes_list.insert("", tk.END, values=(status, item.a_path))

        # Adiciona arquivos não rastreados
        for item in self.current_repo.untracked_files:
            self.changes_list.insert("", tk.END, values=("Não rastreado", item))

    def refresh_history(self):
        if not self.current_repo:
            return

        # Limpa a lista
        for item in self.history_list.get_children():
            self.history_list.delete(item)

        # Adiciona commits
        for commit in self.current_repo.iter_commits():
            date = datetime.fromtimestamp(commit.committed_date)
            date_br = date.astimezone(pytz.timezone('America/Sao_Paulo'))
            self.history_list.insert("", tk.END, values=(
                commit.hexsha[:7],
                date_br.strftime("%d/%m/%Y %H:%M:%S"),
                commit.message
            ))

    def commit_and_push(self):
        if not self.current_repo:
            messagebox.showerror("Erro", "Nenhum projeto selecionado!")
            return

        if not self.commit_msg.get():
            messagebox.showerror("Erro", "Por favor, insira uma mensagem de commit!")
            return

        try:
            # Adiciona todas as alterações
            self.current_repo.git.add('.')

            # Realiza o commit
            date_br = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%d/%m/%Y %H:%M:%S")
            commit_message = f"{self.commit_msg.get()} - {date_br}"
            self.current_repo.index.commit(commit_message)

            # Push
            origin = self.current_repo.remote(name='origin')
            origin.push()

            messagebox.showinfo("Sucesso", "Commit e push realizados com sucesso!")
            self.refresh_changes()
            self.refresh_history()
            self.commit_msg.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao realizar commit/push: {str(e)}")

    def add_project(self):
        # TODO: Implementar adição de novos projetos
        messagebox.showinfo("Info", "Funcionalidade em desenvolvimento!")

if __name__ == "__main__":
    app = GitManager()
    app.mainloop()
