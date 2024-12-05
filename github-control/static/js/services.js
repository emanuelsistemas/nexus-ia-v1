// Função para copiar o caminho do serviço
async function copyPath(path) {
    try {
        await navigator.clipboard.writeText(path);
        const btn = event.currentTarget;
        btn.classList.add('copied');
        btn.querySelector('i').classList.remove('fa-copy');
        btn.querySelector('i').classList.add('fa-check');
        
        setTimeout(() => {
            btn.classList.remove('copied');
            btn.querySelector('i').classList.remove('fa-check');
            btn.querySelector('i').classList.add('fa-copy');
        }, 2000);
        
        showToast('Caminho copiado!', 'success');
    } catch (err) {
        console.error('Erro ao copiar:', err);
        showToast('Erro ao copiar caminho', 'error');
    }
}

// Função para atualizar informações de todos os repositórios
function refreshAllRepos() {
    const refreshButtons = document.querySelectorAll('.fa-sync-alt');
    refreshButtons.forEach(btn => btn.classList.add('spinning'));

    fetch('/refresh_repos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            showToast('Erro ao atualizar repositórios', 'error');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao atualizar repositórios', 'error');
    })
    .finally(() => {
        refreshButtons.forEach(btn => btn.classList.remove('spinning'));
    });
}

// Função para mostrar toast de notificação
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type} show`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
