# Glossario


# Objetivo
Interface para interagir com parceiros comerciais. 

# Intenção

Oferecer uma maneira de incentivar parceiros  nas promoções de eventos por meio 
de rateamento ou compartilhamento de um percentual em cima do percentual que 
a Congressy ganha das transações financeiras referentes a um evento. 

Parceiros serão vinculados ao evento por meio de um *Contrato* em que um 
evento pode ter varios contratos e um parceiro também pode ter varios 
contratos de eventos. 

Esses Contratos deveram ser feitos e vinculadas aos parceiros pela Congressy 
pela interface de Administração da plataforma.


# Premissas

 1. Parceiros devem ser pessoas que se cadastram voluntariamente pelo site.
 2. Um parceiro para ser ativo deve ser aprovado pelo comercial.
 3. O parceiro deve possuir uma maneira de comprovar sua aprovação. ie.: seu 
    email de aprovação. 

# Restrições
1. A soma dos percentuais dados aos parceiros de um evento nunca 
    devem ultrapassar uma quantidade minima padrão de 20% do valor total 
    recebido pela Congressy.
2. Um parceiro só deve ter um contrato por evento. 
3. Um contrato só deve conter um parceiro e um evento.
4. Não podem ser feitos novos contratos após o inicio de evento.

# Regras de Negócio

1. Parceiros devem se cadastrar através de uma interface publica.
2. Parceiros receberão um percentual financeiro em cima do percentual da 
    Congressy
3. A soma de todos parceiros de determinado evento não deve ultrapassar a
    20% do montante da Congressy
4. Deve ser enviado um email para o parceiro após seu cadastro. 
5. Deve ser enviado um email para o comercial da Congressy após o cadastro
    de um novo parceiro. 
    
# Domínio

1. Parceiro:
    1. id
    2. id_pessoa
2. Plano de Parceiro:
    1. id
    2. nome
    3. percentual 
3. Contrato de Parceiro
    1. id
    2. id_evento
    3. id_parceiro
    



