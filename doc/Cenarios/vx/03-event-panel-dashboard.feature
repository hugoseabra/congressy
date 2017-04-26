Feature: Painel de Evento - Dashboard

  Scenario: Visualiza o dashboard do evento
    Visualiza área do organizador com os seguintes acessos
      - Barra superior conforme área restrita do cenário "Perfil do usuário::Visualiza área restrita do organizador"
      - Menu Lateral:
        = Ícone com Avatar do proprietário do evento (Pessoa ou organização) com possibilidade de submenu:
          > Gerenciar colaboradores
          > Convidar colaboradores
        = Certificado  (padrão)
        = Página do evento  (padrão)

        = Inscrições (ativado)
        = Secretaria (ativado)
        = Convites (ativado)
        = Financeiro (ativado)
        = Projeto de evento (ativado)
        = Plano comercial (ativado)
        = Página comercial (ativado)
        = Sorteio (ativado)
        = Atendimentos (ativado)
        = Sincronização (ativado)

        = Gerenciar Recursos (padrão)
        = Estatísticas (padrão)
        = Ajuda (padrão)

      - Área central:
        = Informações do evento: ícone da categoria, banner de apresentação (pequeno), nome, período e botão de editar,
          status (se não realizados, informar quantos dias faltam)
        = Ícones de acessos rápidos (de acordo com recursos ativados): Credenciamento,
        = Estatísticas (quantitativas) de incrição (se ativo). Se inativo, apresentar a mensagem (desativado). Infos:
          > Total de inscritos
          > Total de credenciados
          > Lotes limitados (se houver): preenchidos
          > PNEs
        = Estatísticas (gráficos) de incrição (se ativo). Se inativo, apresentar a mensagem (desativado). Info:
          > Inscrições por dia
          > Reincidências (participantes de eventos anteriores) em comparação a novos
          > Novatos (novos cadastrados na plataforma) em comparação a usuários da plataforma
        = Vagas do evento (se inscrições ativadas). Se inativado, não exibir. Se ativado e for simples, apresentar um
          gráfico simples de vagas preenchidas. Se por lotes, apresentar o mesmo gráfico com o botão "Detalhar"






