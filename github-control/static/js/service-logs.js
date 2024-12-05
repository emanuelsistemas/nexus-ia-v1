// Mapa para armazenar o estado de auto-scroll de cada serviço
const autoScrollEnabled = new Map();

// Mapa para armazenar os intervalos de monitoramento
const monitoringIntervals = new Map();

// Função para gerenciar o toggle dos logs
function handleLogToggle(pid) {
    const logsElement = document.getElementById(`logs-${pid}`);
    
    // Observa mudanças no estado do collapse
    logsElement.addEventListener('shown.bs.collapse', function () {
        console.log('Iniciando monitoramento de logs para PID:', pid);
        startLogMonitoring(pid);
        toggleAutoScroll(pid, true);
    });
    
    logsElement.addEventListener('hidden.bs.collapse', function () {
        console.log('Parando monitoramento de logs para PID:', pid);
        stopLogMonitoring(pid);
    });
}

// Função para limpar os logs
function clearLogs(pid) {
    const logsContent = document.getElementById(`logs-content-${pid}`);
    logsContent.innerHTML = '';
}

// Função para copiar os logs
function copyLogs(pid) {
    const logsContent = document.getElementById(`logs-content-${pid}`);
    navigator.clipboard.writeText(logsContent.textContent)
        .then(() => showToast('Logs copiados!', 'success'))
        .catch(() => showToast('Erro ao copiar logs', 'error'));
}

// Função para alternar o auto-scroll
function toggleAutoScroll(pid, forceEnable = null) {
    const button = document.getElementById(`autoscroll-${pid}`);
    const newState = forceEnable !== null ? forceEnable : !autoScrollEnabled.get(pid);
    
    autoScrollEnabled.set(pid, newState);
    button.classList.toggle('active', newState);
    
    if (newState) {
        scrollToBottom(pid);
    }
}

// Função para rolar para o final dos logs
function scrollToBottom(pid) {
    const container = document.getElementById(`logs-container-${pid}`);
    container.scrollTop = container.scrollHeight;
}

// Função para iniciar o monitoramento dos logs
function startLogMonitoring(pid) {
    if (monitoringIntervals.has(pid)) {
        return;
    }
    
    // Faz a primeira requisição imediatamente
    fetchLogs(pid);
    
    // Configura o intervalo para atualizações
    const interval = setInterval(() => fetchLogs(pid), 2000); // Atualiza a cada 2 segundos
    monitoringIntervals.set(pid, interval);
}

// Função para parar o monitoramento dos logs
function stopLogMonitoring(pid) {
    const interval = monitoringIntervals.get(pid);
    if (interval) {
        clearInterval(interval);
        monitoringIntervals.delete(pid);
    }
}

// Função para buscar os logs do serviço
function fetchLogs(pid) {
    fetch(`/service/logs/${pid}`)
        .then(response => response.json())
        .then(data => {
            console.log('Resposta do servidor:', data); // Debug
            if (data.success) {
                updateLogs(pid, data.logs);
            } else {
                console.error('Erro ao buscar logs:', data.error);
                const logsContent = document.getElementById(`logs-content-${pid}`);
                logsContent.innerHTML = `<div class="log-line log-error">Erro: ${data.error}</div>`;
            }
        })
        .catch(error => {
            console.error('Erro ao buscar logs:', error);
            const logsContent = document.getElementById(`logs-content-${pid}`);
            logsContent.innerHTML = `<div class="log-line log-error">Erro ao buscar logs: ${error.message}</div>`;
        });
}

// Cache para armazenar os últimos logs mostrados
const logsCache = new Map();

// Função para atualizar os logs na interface
function updateLogs(pid, logs) {
    const logsContent = document.getElementById(`logs-content-${pid}`);
    const lastLogs = logsCache.get(pid) || [];
    
    // Se não houver novos logs, não faz nada
    if (logs.length === 0 && lastLogs.length === 0) {
        if (!logsContent.innerHTML) {
            logsContent.innerHTML = '<div class="log-line text-muted">Nenhum log disponível</div>';
        }
        return;
    }
    
    // Verifica se há novos logs
    if (JSON.stringify(logs) === JSON.stringify(lastLogs)) {
        return; // Nenhuma mudança nos logs
    }
    
    // Limpa o conteúdo atual
    logsContent.innerHTML = '';
    
    // Adiciona as novas linhas
    logs.forEach(log => {
        const lineElement = document.createElement('div');
        lineElement.className = `log-line ${getLogLevel(log)}`;
        lineElement.textContent = log;
        logsContent.appendChild(lineElement);
    });
    
    // Atualiza o cache
    logsCache.set(pid, logs);
    
    // Rola para o final se o auto-scroll estiver ativado
    if (autoScrollEnabled.get(pid)) {
        scrollToBottom(pid);
    }
}

// Função para determinar o nível do log
function getLogLevel(log) {
    const lowerLog = log.toLowerCase();
    if (lowerLog.includes('error') || lowerLog.includes('erro') || lowerLog.includes('exception')) {
        return 'log-error';
    } else if (lowerLog.includes('warn') || lowerLog.includes('aviso')) {
        return 'log-warning';
    } else if (lowerLog.includes('info') || lowerLog.includes('informação')) {
        return 'log-info';
    } else if (lowerLog.includes('debug')) {
        return 'log-debug';
    }
    return 'log-default';
}

// Função para copiar o caminho do serviço
function copyPath(path) {
    navigator.clipboard.writeText(path)
        .then(() => showToast('Caminho copiado!', 'success'))
        .catch(() => showToast('Erro ao copiar caminho', 'error'));
}

// Limpa os intervalos quando a página é fechada
window.addEventListener('beforeunload', () => {
    monitoringIntervals.forEach((interval, pid) => {
        clearInterval(interval);
    });
});
