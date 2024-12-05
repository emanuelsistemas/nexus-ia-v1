#!/bin/bash

# Obtém o caminho absoluto do diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Cria o arquivo de aliases se não existir
ALIAS_FILE="$HOME/.bash_aliases"
touch "$ALIAS_FILE"

# Adiciona ou atualiza os aliases
echo "# Nexus IA V1 Aliases - Adicionado em $(date '+%d/%m/%Y %H:%M:%S')" >> "$ALIAS_FILE"
echo "alias ac='$PROJECT_DIR/scripts/automation/auto_commit.sh'" >> "$ALIAS_FILE"
echo "alias rolllist='$PROJECT_DIR/scripts/automation/roll_list.sh'" >> "$ALIAS_FILE"
echo "alias monitor='$PROJECT_DIR/scripts/automation/monitor.sh'" >> "$ALIAS_FILE"

# Função para adicionar o alias de rollback
function add_rollback_alias() {
    echo "function rollback-() { $PROJECT_DIR/scripts/automation/roll_back.sh \"\${1}\"; }" >> "$ALIAS_FILE"
}

add_rollback_alias

# Torna os scripts executáveis
chmod +x "$PROJECT_DIR/scripts/automation/"*.sh

echo "Aliases instalados com sucesso!"
echo "Para começar a usar, execute:"
echo "source ~/.bash_aliases"
echo ""
echo "Comandos disponíveis:"
echo "ac          - Commit e push automático com data/hora"
echo "rolllist    - Lista commits disponíveis para rollback"
echo "rollback-0  - Volta para o último commit"
echo "rollback-[hash] - Volta para um commit específico"
echo "monitor     - Monitora alterações continuamente"
