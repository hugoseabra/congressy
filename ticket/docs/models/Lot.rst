=====================================
Lot
=====================================


Campos
-----------------

- ticket
   - Tipo: *Chave Estrangeira*
   - Obrigatorio: Sim
   - Ao deletar: *PROTECT*

- name
   - Tipo: *Char*
   - Tamanho máximo: 80
   - Obrigatorio: Sim

- date_start
   - Tipo: *Dia/Hora*
   - Obrigatorio: Sim

- date_end
   - Tipo: *Dia/Hora*
   - Obrigatorio: Sim

- price
   - Tipo: *Decimal*
   - Casas Decimais: 2 digitos
   - Tamanho máximo: 8 digitos
   - Padrão: 0.00
   - Obrigatorio: Não

- limit
   - Tipo: *Inteiro Positivo*
   - Obrigatorio: Não

- num_subs
   - Tipo: *Inteiro Positivo*
   - Obrigatorio: Não
   - Padrão: 0
   - Editavel: Não

- created
   - Tipo: *Dia/Hora*
   - Padrão: Agora(auto_now_add)
   - Editavel: Não

- last
   - Tipo: *Booleano*
   - Obrigatorio: Não
   - Editavel: Não

- modified
   - Tipo: *Dia/Hora*
   - Padrão: Agora(auto_now)
   - Editavel: Não