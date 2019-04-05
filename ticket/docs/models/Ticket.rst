=====================================
Ticket
=====================================


Campos
-----------------

- event
   - Tipo: *Chave Estrangeira*
   - Obrigatorio: Sim
   - Ao deletar: *CASCADE*

- event_survey
   - Tipo: *Chave Estrangeira*
   - Obrigatorio: Não
   - Ao deletar: *SET_NULL*

- name
   - Tipo: *Char*
   - Tamanho máximo: 255
   - Obrigatorio: Sim

- description
   - Tipo: *Text*
   - Obrigatorio: Não

- paid
   - Tipo: *Booleano*
   - Padrão: Falso
   - Obrigatorio: Não

- transfer_tax
   - Tipo: *Booleano*
   - Padrão: Verdadeiro
   - Obrigatorio: Sim

- free_installments
   - Tipo: *Inteiro*
   - Padrão: 0
   - Obrigatorio: Não

- active
   - Tipo: *Booleano*
   - Padrão: Verdadeiro
   - Obrigatorio: Sim

- limit
   - Tipo: *Inteiro Positivo*
   - Obrigatorio: Não

- num_subs
   - Tipo: *Inteiro Positivo*
   - Editavel: Não
   - Padrão: 0
   - Obrigatorio: Não

- private
   - Tipo: *Booleano*
   - Padrão: Falso
   - Obrigatorio: Sim

- created
   - Tipo: *Dia/Hora*
   - Padrão: Agora(auto_now_add)
   - Editavel: Não

- modified
   - Tipo: *Dia/Hora*
   - Padrão: Agora(auto_now)
   - Editavel: Não


Propriedades - Atributos Dinâmicos
-----------------------------------

- current_lot - Resgatar o lote vigente no ingresso, caso possua
- display_name - Centralizar a junção do nome do ingresso, com o nome do lote atualmente vigente, caso possua

Métodos
-----------------
- anticipate_lots - Em caso de virada por lotação vagas, colocar o lote seguinte no ar
- update_num_subs - Atualizar número de inscrições em num_subs