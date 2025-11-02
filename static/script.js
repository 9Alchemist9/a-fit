// Aguarda o conteúdo da página carregar completamente
document.addEventListener('DOMContentLoaded', () => {
    
    // Seleciona os elementos do formulário no HTML
    const form = document.getElementById('assessoria-form');
    const submitButton = document.getElementById('submit-button');
    const feedbackMessage = document.getElementById('feedback-message');

    // Adiciona um "ouvinte" para o evento de envio do formulário
    form.addEventListener('submit', async (event) => {
        // Previne o comportamento padrão do formulário (que é recarregar a página)
        event.preventDefault();

        // Desabilita o botão para evitar múltiplos envios
        submitButton.setAttribute('aria-busy', 'true');
        submitButton.disabled = true;
        feedbackMessage.textContent = '';
        feedbackMessage.className = '';

        // Coleta os dados do formulário
        const formData = new FormData(form);
        const nome = formData.get('nome');
        const email = formData.get('email');
        const telefone = formData.get('telefone');
        
        // Pega o serviço e o valor do radio button selecionado
        const servicoRadio = document.querySelector('input[name="servico"]:checked');
        const servico = servicoRadio.value;
        const valor = servicoRadio.dataset.valor;

        // Monta o objeto de dados para enviar ao backend
        const dataToSend = {
            nome,
            email,
            telefone,
            servico,
            valor
        };

        try {
            // Faz a requisição para a nossa API Flask
            const response = await fetch('/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dataToSend)
            });

            // Pega a resposta do backend
            const result = await response.json();

            if (response.ok) {
                // Se a resposta foi bem-sucedida (status 2xx)
                feedbackMessage.textContent = 'Inscrição realizada com sucesso! Entraremos em contato em breve.';
                feedbackMessage.className = 'success';
                form.reset(); // Limpa o formulário
            } else {
                // Se o backend retornou um erro
                throw new Error(result.mensagem || 'Ocorreu um erro ao enviar seus dados.');
            }
        } catch (error) {
            // Se ocorreu um erro de rede ou outro problema
            feedbackMessage.textContent = `Erro: ${error.message}`;
            feedbackMessage.className = 'error';
        } finally {
            // Reabilita o botão, independentemente do resultado
            submitButton.setAttribute('aria-busy', 'false');
            submitButton.disabled = false;
        }
    });
});
