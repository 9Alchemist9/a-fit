document.addEventListener('DOMContentLoaded', () => {
    // Objeto com todos os preços extraídos da sua imagem
    const precos = {
        Online: { Mensal: 450, Trimestral: 400, Semestral: 300, Anual: 250 },
        Presencial: {
            Mensal: { 3: 1200, 4: 1520, 5: 1800, 6: 2040 },
            Trimestral: { 3: 1080, 4: 1360, 5: 1600, 6: 1800 },
            Semestral: { 3: 960, 4: 1200, 5: 1400, 6: 1560 },
            Anual: { 3: 840, 4: 1040, 5: 1200, 6: 1320 }
        },
        Híbrido: {
            Mensal: { 3: 1650, 4: 1970, 5: 2250, 6: 2490 },
            Trimestral: { 3: 1480, 4: 1760, 5: 2000, 6: 2200 },
            Semestral: { 3: 1260, 4: 1500, 5: 1700, 6: 1860 },
            Anual: { 3: 1090, 4: 1290, 5: 1450, 6: 1570 }
        }
    };

    // Estado da seleção do usuário
    let selecao = {
        modalidade: null,
        periodicidade: null,
        frequencia: null,
        planoFinal: null,
        valorFinal: 0
    };

    // Elementos do DOM
    const cardsModalidade = document.querySelectorAll('.card-modalidade');
    const seletoresDinamicos = document.getElementById('seletores-dinamicos');
    const passoPeriodicidade = document.getElementById('passo-periodicidade');
    const passoFrequencia = document.getElementById('passo-frequencia');
    const passoDadosCliente = document.getElementById('passo-dados-cliente');
    const resultadoPlano = document.getElementById('resultado-plano');
    const submitButton = document.getElementById('submit-button');

    const seletorPeriodicidade = document.getElementById('seletor-periodicidade');
    const seletorFrequencia = document.getElementById('seletor-frequencia');

    const resumoPlanoEl = document.getElementById('resumo-plano');
    const precoFinalEl = document.getElementById('preco-final');

    const form = document.getElementById('assessoria-form');
    const feedbackMessage = document.getElementById('feedback-message');

    // Funções de atualização da UI
    function atualizarUI() {
        seletoresDinamicos.classList.add('hidden');
        passoFrequencia.classList.add('hidden');
        resultadoPlano.classList.add('hidden');
        passoDadosCliente.classList.add('hidden');
        submitButton.classList.add('hidden');

        if (selecao.modalidade) {
            seletoresDinamicos.classList.remove('hidden');
            passoPeriodicidade.classList.remove('hidden');
        }
        if (selecao.periodicidade) {
            if (selecao.modalidade === 'Presencial' || selecao.modalidade === 'Híbrido') {
                passoFrequencia.classList.remove('hidden');
                seletorFrequencia.required = true; // TORNA OBRIGATÓRIO
            } else { // Caso Online
                passoFrequencia.classList.add('hidden'); // Garante que está escondido
                seletorFrequencia.required = false;    // DEIXA DE SER OBRIGATÓRIO
                calcularPrecoFinal();
            }
        }

        if (selecao.frequencia && (selecao.modalidade === 'Presencial' || selecao.modalidade === 'Híbrido')) {
            calcularPrecoFinal();
        }

        if (selecao.valorFinal > 0) {
            resultadoPlano.classList.remove('hidden');
            passoDadosCliente.classList.remove('hidden');
            submitButton.classList.remove('hidden');
        }
    }

    function calcularPrecoFinal() {
        const { modalidade, periodicidade, frequencia } = selecao;
        let valor = 0;
        let plano = `${modalidade} - ${periodicidade}`;

        if (modalidade === 'Online') {
            if (periodicidade) valor = precos[modalidade][periodicidade];
        } else if (modalidade && periodicidade && frequencia) {
            valor = precos[modalidade][periodicidade][frequencia];
            plano += ` (${frequencia}x/semana)`;
        }

        selecao.valorFinal = valor;
        selecao.planoFinal = plano;

        if (valor > 0) {
            resumoPlanoEl.textContent = plano;
            precoFinalEl.textContent = `R$ ${valor.toFixed(2).replace('.', ',')}/mês`;
        }
    }

    // Event Listeners para os BOTÕES
    const botoesModalidade = document.querySelectorAll('[data-modalidade-btn]');
    botoesModalidade.forEach(botao => {
        botao.addEventListener('click', (e) => {
            e.preventDefault();
            const modalidadeSelecionada = botao.dataset.modalidadeBtn;

            cardsModalidade.forEach(c => c.classList.remove('selected'));
            const cardPai = botao.closest('.card-modalidade');
            cardPai.classList.add('selected');

            selecao.modalidade = modalidadeSelecionada;
            selecao.periodicidade = null;
            selecao.frequencia = null;
            selecao.valorFinal = 0;
            seletorPeriodicidade.value = "";
            seletorFrequencia.value = "";

            atualizarUI();

            seletoresDinamicos.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
    });

    seletorPeriodicidade.addEventListener('change', (e) => {
        selecao.periodicidade = e.target.value;
        selecao.frequencia = null;
        seletorFrequencia.value = "";
        atualizarUI();
    });

    seletorFrequencia.addEventListener('change', (e) => {
        selecao.frequencia = e.target.value;
        atualizarUI();
    });

    // Lógica de envio do formulário
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        submitButton.setAttribute('aria-busy', 'true');
        submitButton.disabled = true;
        feedbackMessage.textContent = '';

        const dataToSend = {
            nome: document.getElementById('nome').value,
            email: document.getElementById('email').value,
            telefone: document.getElementById('telefone').value,
            servico: selecao.planoFinal,
            valor: selecao.valorFinal
        };

        try {
            const response = await fetch('/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dataToSend)
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.mensagem || 'Ocorreu um erro.');

            feedbackMessage.innerHTML = 'Inscrição realizada com sucesso! Entraremos em contato em breve.';
            feedbackMessage.className = 'success';

            // Limpa o formulário e reseta a UI
            document.getElementById('nome').value = '';
            document.getElementById('email').value = '';
            document.getElementById('telefone').value = '';
            selecao = { modalidade: null, periodicidade: null, frequencia: null, planoFinal: null, valorFinal: 0 };
            cardsModalidade.forEach(c => c.classList.remove('selected'));
            atualizarUI();

        } catch (error) {
            feedbackMessage.innerHTML = `Erro: ${error.message}`;
            feedbackMessage.className = 'error';
        } finally {
            submitButton.setAttribute('aria-busy', 'false');
            submitButton.disabled = false;
        }
    });

    // Aplica a máscara de telefone
    const telefoneInput = document.getElementById('telefone');
    const mascaraTelefone = {
        mask: [
            {
                mask: '+{55} (00) 0000-0000',
                lazy: false
            },
            {
                mask: '+{55} (00) 0 0000-0000',
                lazy: false
            }
        ]
    };
    const mascara = IMask(telefoneInput, mascaraTelefone);

    // Inicia a UI
    atualizarUI();
});
