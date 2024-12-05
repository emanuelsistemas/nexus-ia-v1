import os
import json
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel

class LogLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"

class LogEntry(BaseModel):
    """Estrutura de um log"""
    timestamp: datetime
    level: LogLevel
    project_id: str
    backup_id: Optional[str]
    action: str
    status: str
    message: str
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BackupLogger:
    """Sistema de logs para backup"""

    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    def _write_log(self, entry: LogEntry):
        """Escreve um log no arquivo"""
        # Nome do arquivo: project_YYYY-MM-DD.log
        date_str = entry.timestamp.strftime("%Y-%m-%d")
        log_file = os.path.join(self.log_dir, f"{entry.project_id}_{date_str}.log")
        
        # Formata a mensagem
        log_line = (
            f"[{entry.timestamp.isoformat()}] "
            f"[{entry.level.value}] "
            f"[{entry.action}] "
            f"[{entry.status}] "
            f"{entry.message}\n"
        )

        if entry.details:
            log_line += f"Details: {json.dumps(entry.details, indent=2)}\n"

        if entry.error:
            log_line += f"Error: {entry.error}\n"

        # Escreve no arquivo
        with open(log_file, "a") as f:
            f.write(log_line)
            f.write("-" * 80 + "\n")

    def log(self, 
            level: LogLevel,
            project_id: str,
            action: str,
            status: str,
            message: str,
            backup_id: Optional[str] = None,
            details: Optional[Dict[str, Any]] = None,
            error: Optional[str] = None):
        """Registra um log"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            project_id=project_id,
            backup_id=backup_id,
            action=action,
            status=status,
            message=message,
            details=details,
            error=error
        )
        self._write_log(entry)

    def get_logs(self,
                project_id: str,
                start_date: Optional[datetime] = None,
                end_date: Optional[datetime] = None,
                level: Optional[LogLevel] = None,
                backup_id: Optional[str] = None) -> list[LogEntry]:
        """Recupera logs com filtros"""
        logs = []
        
        # Define período
        if not start_date:
            start_date = datetime.min
        if not end_date:
            end_date = datetime.max

        # Lista arquivos de log do projeto
        for filename in os.listdir(self.log_dir):
            if not filename.startswith(f"{project_id}_"):
                continue

            with open(os.path.join(self.log_dir, filename), "r") as f:
                content = f.read()

            # Processa cada entrada
            for entry_str in content.split("-" * 80):
                if not entry_str.strip():
                    continue

                try:
                    # Parse da entrada
                    entry = LogEntry.parse_raw(entry_str)

                    # Aplica filtros
                    if entry.timestamp < start_date or entry.timestamp > end_date:
                        continue
                    if level and entry.level != level:
                        continue
                    if backup_id and entry.backup_id != backup_id:
                        continue

                    logs.append(entry)

                except Exception as e:
                    print(f"Erro ao processar log: {e}")

        return sorted(logs, key=lambda x: x.timestamp, reverse=True)

