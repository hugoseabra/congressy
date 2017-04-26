Feature: Perfil de Usuário

  Scenario: Visualiza área restrita do organizador
    Visualiza área do organizador com os seguintes acessos
      - Barra superior:
        = título da plataforma
        = título da área: Área do Organizador
        = ícone de mensagens com submenu:
          > últimas 5 mensagens diferenciando-as entre lidas e não lidas
          > barra inferior com número de mensagens não lidas caso haja mais de 5 e botão "ver todas"
        = avatar e nome do usuário logado com possibilidade de submenu:
          > Percentual de completude de cadastro
          > Minha conta
          > Minhas organizações
          > Sair
        = ícone para mudança de área com submenu:
          > Acessar como participante
      - Menu Lateral:
        = Meus eventos
        = Meus locais
        = Ajuda
      - Área central:
        = Lista de eventos com filtros (ativos/inativos), realizados, não-realizados, Por dono (meus ou organização)


  Scenario: Editar os próprios dados e alterar senha
    Ao clicar em "Minha conta", o usúario poderá editar os próprios dados


  Scenario: Alterar senha
    Ao clicar em "Minha conta", o usúario poderá alterar a própria senha


  Scenario: Configurar Avatar
    Ao clicar em "Minha conta", o usúario poderá editar o avatar
