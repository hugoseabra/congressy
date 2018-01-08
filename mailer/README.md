# Congressy Mailer

Módulo para envio de e-mail da Congressy.

## Configuração

Este módulo utiliza os seguintes recursos:

* Redis para envio assíncrono e controle de fila;
* Celery para controlar as **Queues** (filas): _workers_ e _jobs_;
* Configurações de **settings** no django:
    
```python
# INSTALLED_APPS -> adicionar:

'django.contrib.humanize',
 

# Configura o Celery para usar o servidor Redis (como Broker)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
 
# Configuração da SparkPost
EMAIL_HOST = 'smtp.sparkpostmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'SMTP_Injection'
EMAIL_HOST_PASSWORD = '<SPARKHOST KEY>'
EMAIL_USE_TLS = True
CONGRESSY_EMAIL_SENDER = 'mail@congressy.net'
CONGRESSY_REPLY_TO = 'congressy@congressy.com'
```

**Ref:** https://www.sparkpost.com/docs/integrations/django/

## Ambiente de Desenvolvimeto

Configura o django para enviar e-mail via console (no arquivo _settings.py_):
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

## Ambiente de Produção

Configura o django para enviar e-mail via console (no arquivo _settings.py_):
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

## Sobre o Celery

No site do [**Celery**]("https://redis.io") descreve que a solução é:

```text
Celery is an asynchronous task queue/job queue based on distributed message 
passing.	It is focused on real-time operation, but supports scheduling as
well.
 
The execution units, called tasks, are executed concurrently on a single or 
more worker servers using multiprocessing, Eventlet, or gevent. Tasks can
execute asynchronously (in the background) or synchronously (wait until 
ready).
```

Esta solução é utilizada para gerenciar as filas de envio de e-mail e cuida
das **retentativas** de processamentos dos *jobs*. Neste módulo utilizamos
o **Redis** para persistência.



## Sobre o Redis

No site do [**Redis**]("https://redis.io") descreve que a solução é:

```text
Redis is an open source (BSD licensed), in-memory data structure store, used
as a database, cache and message broker. It supports data structures such 
as strings, hashes, lists, sets, sorted sets with range queries, bitmaps, 
hyperloglogs and geospatial indexes with radius queries. Redis has built-in
replication, Lua scripting, LRU eviction, transactions and different levels
of on-disk persistence, and provides high availability via Redis Sentinel 
and automatic partitioning with Redis Cluster.
 

You can run atomic operations on these types, like appending to a string; 
incrementing the value in a hash; pushing an element to a list; computing  
set intersection, union and difference; or getting the member with highest  
ranking in a sorted set.  In order to achieve its outstanding performance,  
Redis works with an in-memory dataset. Depending on your use case, you can  
persist it either by dumping the dataset to disk every once in a while, or 
by appending each command to a log. Persistence can be optionally disabled, 
if you just need a feature-rich, networked, in-memory cache.
 
Redis also supports trivial-to-setup master-slave asynchronous replication,
with very fast non-blocking first synchronization, auto-reconnection with  
partial resynchronization on net split.
``` 

Ele será utlizado principalmente por causa da necessidade de **retentivas**
de envio de e-mail que podem ser perdidos durante o envio de um grande número
de destinatários.

### Gerenciando o Redis

Utilizamos o [**Redsmin**]("https://app.redsmin.com") de onde podemos obter
métricas de desempenho, gerenciar alocação de recursos, dentre muitas ouras
coisas.