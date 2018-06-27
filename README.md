# PERMISSÕES DE MEMBROS DE ORGANIZAÇÃO #

ALGUMAS AÇÕES DENTRO DA PLATAFORMA SERÃO DE ACORDO COM A ORGANIZAÇÃO E GRUPO DO MEMBRO DENTRO DELA.

## Grupos de memberos: ##
1. ADMIN - Administrador
2. HELPER - Auxiliar

## Ações possíveis: ##

### Organização:###
1. Retirar-se de organização - ADMIN | HELPER
2. Editar organização - ADMIN
3. Excluir organização - ADMIN
4. Transferir eventos - ADMIN

### Evento:###
1. Criar evento - ADMIN
2. Editar evento - ADMIN | HELPER
3. Excluir evento - ADMIN
4. Publicar/Despublicar site evento  - ADMIN
5. Ativar/Desativar/Alterar tipo inscrições - ADMIN
6. Exportar dados - ADMIN

### Lote:###
1. Criar lotes - ADMIN | HELPER
2. editar lotes - ADMIN  | HELPER
3. excluir lotes - ADMIN | HELPER

### Inscrição:###

#### Formulário:####
1. Editar formulário - ADMIN | HELPER

#### Pré-inscrição (antes da inicial do evento):####
1. Cadastrar inscrição - ADMIN | HELPER
2. Editar inscrição - ADMIN | HELPER
3. Excluir inscrição - ADMIN | HELPER

#### Credenciamento (depois da inicial do evento):####
1. Cadastrar inscrição - ADMIN | HELPER
2. Editar inscrição - ADMIN | HELPER
3. Excluir inscrição - ADMIN | HELPER
4. Confirmar presença (check-in) - ADMIN | HELPER

# Verificação Pylint #
  
Esta seção é para documentar a configuração feita em ```.pylintrc```

-- ---

Referência de códigos: http://pylint-messages.wikidot.com/all-codes

-- ---

Disabilitar as seguintes verificações:
 
### Warnings: ###

#### W0212 - Access to a protected member %s of a client class ####

As vezes é necessário acessar variáveis protegidas. Esta decisão fica por conta
do desenvolvedor.

#### W0221 - Arguments number differs from %s method ####

O uso **kwargs as vezes simplifica o desenvolvimento, por isso, o uso dele fica
sob decisão do desenvolvedor.

#### W0232 - Class has no __init__ method ####

Modelos e algumas classes não necessitam de `__init__()`.


#### W0512 - Cannot decode using encoding "ascii" ####

Comentários em português causam este erro.


### Crash: ###

#### C0103 - Invalid %s name "%s" ####

Invalid %s name "%s"

Invalid constant name "newline"
Invalid variable name "MyVar"
Invalid class name "myClass"

Verifica nomes normalizados de constantes, variáveis e classes.

### Refactoring help: ###
 
#### R0903 - Too few public methods (%s/%s) ####  
 
Classes de verificações simples. A decisão em refatorar classes assim fica a
cargo do desenvolvedor.
  
#### R0201 - Method could be a function ####

Usado para verificar métodos que poderiam ser estáticos.
  
### Error detection: ###

#### E1101 - Class Event has no objects member ####
 
As vezes o pylint não consegue encontrar @classonly objects.
