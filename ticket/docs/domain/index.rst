=====================================
Domínios
=====================================

.. toctree::
   :maxdepth: 2

Temos dois modelos de dados, *ingresso* e *lote*. A função destes modelos é organizar a venda de inscrições.


Qual a intenção destes modelos?
-------------------------------------

**Ingresso**

Esse modelo age como uma categoria para os lotes, exemplo de ingressos seria *Estudantes*, *Médicos*, *Pre-Venda*.
Seria uma forma cobrir um determinado número de lotes com algumas caracteristicas especificas gerais, como:

- Formulário Personalizado
- Ativo ou inativo (Se aparece ou não para participantes)
- Quantidade de parcelas sem juros
- Limite
- Privacidade


**Lote**

Nada mais é do que um forma de aplicar algumas regras do *ingresso* a qual ela pertence, além de suas proprias regras
com mais granularidade como, limite de tempo com data de inicio e fim. Cada ingresso pode ter apenas um lote vigiante
no momento. Dentro desse prazo caso ocorra de lotar o limite, acontecerá o que chamamos de :ref:`Virada de Lote`, que nada
mais é que o ato de fechar o lote vigente e antecipar o próximo lote caso exista. Essa *virada* também irá ocorrer ao atingir a data de fim do lote.

Regras de Integridade
-------------------------------------

Nenhuma.


Regras de Negócio
-------------------------------------
- Ingresso:
    - Não é possivel absorver mais de 10 parcelas.
    - Uma vez criado, o evento do ticket é imutavel.

- Lote:
    - Não pode haver conflito de data com lotes.
    - Ao criar e houver limite de vaga, verificar se o limite, somado aos outros lotes, ultrapassa o limite define na categoria.
    - Se há inscrições confirmadas não permitir mudar preço.
    - Uma vez criado, o ticket do lote é imutavel.


Permissões de acesso
-------------------------------------
- Ingresso:
   - Criação    - Apenas organizadores do evento a qual a entidade pertence e a qualquer momento.
   - Leitura    - Apenas organizadores do evento a qual a entidade pertence e a qualquer momento.
   - Edição     - Apenas organizadores do evento a qual a entidade pertence e a qualquer momento.
   - Deletação  - Apenas organizadores do evento a qual a entidade pertence e apenas se não possuirem inscritos.


- Lote:
   - Criação    - Apenas organizadores do evento a qual a entidade pertence e a qualquer momento.
   - Leitura    - Apenas organizadores do evento a qual a entidade pertence e a qualquer momento.
   - Edição     - Apenas organizadores do evento a qual a entidade pertence e a qualquer momento.
   - Deletação  - Apenas organizadores do evento a qual a entidade pertence e apenas se não possuirem inscritos.


