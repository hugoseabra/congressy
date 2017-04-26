Feature: Gerenciamento de Eventos

  Scenario: Criar novo evento - Passo 1 - Informar Dados Básicos
    Campos:
      - Nome
      - Categoria
      - Proprietário
      - Data de hora inicial
      - Data e hora final
      - Descrição simples (para sites de busca)

  Scenario: Criar novo evento - Passo 2 - Configurar Público-alvo
    Configurar cadeias produtivas atendidas e assuntos abordados


  Scenario: Criar novo evento - Passo 2 - Configurar de publicação
    Configurar publicação do evento: se apenas on-line, se acontecerá alguml local e se deseja que o evento seja
    indexado em sites de busca e divugado para os membros da plataforma.


  Scenario: Criar novo evento - Passo 3 - Configurar inscrições
    Configurar se haverá inscrições on-line. Se sim, se haverá inscrições pagas. Se sim, configurar formas de
    recebimento, lotes, limites de público, valores e definições de transferências de taxas.

  Scenario: Criar novo evento - Passo 4 - Configurar site
    Ativar recursos do site: indexação em sites de busca, contador regressivo, redes sociais, emissão de certificado
    Ativar sessões: informações do evento, programação, assuntos, palestrantes, local do evento, sobre o organizador
    Enviar imagens:
      > banner do topo
      > banner de apresentação (pequeno)

  Scenario: Criar novo evento - Passo 5 - Ativar recursos
    Ativar recursos adicionais que podem gratuitos ou pagos que podem ser:
      - Financeiro
      - Plano de evento
      - Plano comercial
      - Pesquisa e Feedback
          = Viabilidade
          = Público-alvo
      - Página comercial
      - Comunicação:
          = convites
      - Secretaria (on-line):
          = emissão de etiquetas
          = credenciamento - novas inscrições
          = credenciamento (check-in) por leitor de código
          = credenciamento (check-in) por aplicativo
      - Atendimentos
          = pré-atendimento
          = atendimento
          = pós-atendimento
          = controle de filas
          = pré-atendimento
      - Sorteio
      - Serviços in-loco (Off-line):
          = Sorteio
          = Pesquisa e Feedback
              > Viabilidade
              > Público-alvo
          = Secretaria:
              > emissão de etiquetas
              > credenciamento - novas inscrições
              > credenciamento (check-in) por leitor de código
              > credenciamento (check-in) por aplicativo
          = Atendimentos:
              > pré-atendimento
              > atendimento
              > pós-atendimento
              > controle de filas
              > pré-atendimento


  Scenario: Editar Evento
    Edição de dados básicos do evento, lotes, configuração de público alvo e configuração de publicação


  Scenario: Desativar Evento
    Desativar mas não remover o evento.


  Scenario: Excluir Evento
    Exclusão do evento com os diálogos adequados.
