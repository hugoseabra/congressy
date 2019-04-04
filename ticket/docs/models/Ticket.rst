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