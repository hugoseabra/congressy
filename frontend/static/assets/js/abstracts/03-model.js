/**
 * @module
 * @name Congressy Abstracts - Model
 * @namespace window.cgsy.abstracts.domain
 * @description Modelos de domínio e todas as suas interações.
 * @depends
 *  - jQuery
 *  - window.cgsy.AjaxSender
 *  - window.cgsy.abstracts.error
 *  - window.cgsy.abstracts.http
 */
window.cgsy = window.cgsy || {};
window.cgsy.abstracts = window.cgsy.abstracts || {};

(function (abstracts, moment) {
    'use strict';

    abstracts.domain = {};

    /**
     * Campo de modelo de domínio.
     * @param {string} name
     * @param {string} label
     * @param {string} type
     * @param {boolean} required
     * @constructor
     */
    abstracts.domain.Field = function (name, label, type, required) {
        var self = this;

        /**
         * Nome do campo.
         * @type {string}
         */
        this.name = name;

        /**
         * Rótulo do campo.
         * @type {string}
         */
        this.label = label;

        /**
         * Tipo do campo:
         *  - integer
         *  - float
         *  - boolean
         *  - list
         *  - date
         *  - datetime
         *  - string
         * @type {string}
         */
        this.type = type;

        /**
         * Campo obrigatório.
         * @type {boolean}
         */
        this.required = required === true;

        /**
         * Se pode ser aceito mesmo sem valor.
         * @type {boolean}
         */
        this.blank = false;

        /**
         * Se possui erro.
         * @type {boolean}
         */
        this.has_error = false;

        /**
         * Se campo será utilizado na requisição REST.
         * @type {boolean}
         */
        this.submittable = true;

        /**
         * Menesagem de erro.
         * @type {string}
         * @private
         */
        var _message = 'message not set for "' + label + '"';

        /**
         * Valor do campo.
         */
        var _value;

        /**
         * Seta mensagem de erro.
         * @param {string} message
         */
        this.setMessage = function (message) {
            _message = message;
        };

        /**
         * Resgata mensagem de erro.
         * @returns {string}
         */
        this.getMessage = function () {
            return _message;
        };

        /**
         * Resgata valor de formulário.
         * @returns {*}
         */
        this.getValue = function () {
            return _value;
        };

        /**
         * Seta valor do campo.
         * @param {integer|float|boolean|Array|string} v
         */
        this.setValue = function (v) {
            _value = _processValue(v);
        };

        /**
         * Processa e valida valor informado.
         * @param {integer|float|boolean|Array|string} v
         * @returns {*}
         * @private
         */
        var _processValue = function (v) {
            var value;

            var is_null = typeof v === 'undefined' || v === null;
            var is_number = typeof v === 'number';
            var is_float = is_number && v % 1 !== 0;
            var is_boolean = typeof v === 'boolean';
            var is_string = typeof v === 'string';
            var is_list = v instanceof Array;
            var is_date = v instanceof Date;
            var is_required = self.required === true;

            self.has_error = false;

            switch (type.toLowerCase()) {
                case 'integer':
                case 'number':
                    if ((is_required && !is_number) || !is_null && !is_number) {
                        self.has_error = true;
                        value = undefined;
                    } else if (v) {
                        value = (is_float) ? parseFloat(v) : parseInt(v);
                    }
                    break;
                case 'float':
                    if ((is_required && !is_number) || !is_null && !is_number) {
                        self.has_error = true;
                        value = undefined;
                    } else {
                        value = (!v) ? v : parseFloat(v);
                    }
                    break;
                case 'boolean':
                    if (is_required && !is_boolean && !is_string) {
                        self.has_error = true;
                        value = undefined;
                    } else {
                        value = v === true || v === 'true' || v === 'on';
                    }
                    break;
                case 'list':
                    if (is_required && !is_list || is_list && v.length === 0 || !is_null && !is_list) {
                        self.has_error = true;
                        value = undefined;
                    } else {
                        value = v;
                    }
                    break;
                case 'date':
                    if ((is_required && !is_string && !is_date) || (!is_string && !is_date) || !moment(v, 'YYYY-MM-DD', true).isValid()) {
                        self.has_error = true;
                        value = undefined;
                    } else {
                        if (!v) {
                            value = v;
                        } else if (is_date) {
                            value = moment(v);
                        } else {
                            value = (!v) ? v : moment(v, 'YYYY-MM-DD');
                        }
                    }
                    break;
                case 'datetime':
                    if ((is_required && !is_string && !is_date) || (!is_string && !is_date) || !moment(v, 'YYYY-MM-DD HH:mm:ss', true).isValid()) {
                        self.has_error = true;
                        value = undefined;
                    } else {
                        if (!v) {
                            value = v;
                        } else if (is_date) {
                            value = moment(v);
                        } else {
                            value = (!v) ? v : moment(v, 'YYYY-MM-DD HH:mm:ss');
                        }
                    }
                    break;
                case 'string':
                    var not_str = is_boolean || is_list || is_number;
                    if ((is_required && not_str) || !is_null && not_str) {
                        self.has_error = true;
                        value = undefined;
                    } else {
                        value = v;
                    }
                    break;
                default:
                    value = v;
            }

            if (self.has_error) {
                var msg = self.getMessage() || self.label + ': ';
                console.warn(msg + ' Valor informado: ' + v + ' (' + typeof v + ').');
            }

            return value;
        };
    };

    /**
     * Erro de modelo de domínio.
     * @param {abstracts.domain.Model} model_instance
     * @constructor
     */
     abstracts.domain.ModelError = function (model_instance) {
        abstracts.error.Error.call(this);
        var self = this;

        /**
         * Modelo de domínio.
         * @type {abstracts.domain.Model}
         */
        this.model_instance = model_instance;

        /**
         * Verifica se model é válido para buscar dados via REST.
         * @returns {boolean}
         */
        this.isValidForFetch = function () {
            var valid = model_instance.hasOwnProperty('pk') && model_instance.pk;

            if (!valid) {
                self.setKeyError('pk', 'Entidade não possui ID.');
            }

            return valid && self.non_key_errors.length === 0;
        };

        /**
         * Verifica se model é válido para criar registro via REST.
         * @returns {boolean}
         */
        this.isValidForCreate = function () {
            this.key_errors = {};

            var valid = true;

            if (model_instance.pk) {
                self.setKeyError('pk', 'Entidade já existe.');
                valid = false;
            }

            valid = valid === true && _hasValidFields();
            return valid && self.non_key_errors.length === 0;
        };

        /**
         * Verifica se model é válido para atualizar registro via REST.
         * @returns {boolean}
         */
        this.isValidForUpdate = function () {
            this.key_errors = {};

            var valid = true;

            if (!model_instance.hasOwnProperty('pk') || !model_instance.pk) {
                self.setKeyError('pk', 'Entidade não possui ID.');
                valid = false;
            }
            valid = valid === true && _hasValidFields();
            return valid && self.non_key_errors.length === 0;
        };

        /**
         * Verifica se model é válido para ser deletado via REST.
         * @returns {boolean}
         */
        this.isValidForDelete = this.isValidForUpdate;

        /**
         * Verifica se todos os campos do modelo de domínio são válidos.
         * @returns {boolean}
         * @private
         */
        var _hasValidFields = function () {
            var valid = true;

            model_instance.getFieldNames().forEach(function (name) {
                var field = model_instance.getField(name);

                // ID não é verificado aqui.
                if (field.name === 'pk') {
                    return;
                }

                if (field.required === false) {
                    return;
                }

                var value = field.getValue();
                var empty = value === null || typeof value === 'undefined';

                if (empty && model_instance.isBlank(field.name) === false) {
                    valid = false;
                    self.setKeyError(field.name, field.getMessage());
                }
            });

            return valid;
        };
    };
    abstracts.domain.ModelError.prototype = Object.create(abstracts.error.Error.prototype);
    abstracts.domain.ModelError.prototype.constructor = abstracts.domain.ModelError;

    /**
     * Modelo de domínio
     * @param {string|integer} pk
     * @constructor
     */
    abstracts.domain.Model = function (pk) {
        var self = this;

        /**
         * @type {string|integer|null}
         */
        this.pk = pk;

        /**
         * Tipo de valor para ID da instância do modelo de domínio.
         * @type {string}
         */
        this.pk_type = 'integer';

        /**
         * Schema de configuração de campos.
         * @type {Array}
         */
        this.fields = [];

        /**
         * Nome de alto nível do modelo no singular.
         * @type {string}
         */
        this.verbose_name = '';

        /**
         * Nome de alto nível do modelo no plural.
         * @type {string}
         */
        this.verbose_name_plural = '';

        /**
         * Gerenciador de URI
         * @type {abstracts.uri.URIManager}
         */
        this.uri_manager = null;

        /**
         * URI de criação de registro de modelo do domínio.
         * @type {string}
         */
        this.creation_uri = '';

        /**
         * URI de atualização e remoção do modelo de domínio.
         * @type {null}
         */
        this.uri = null;

        /**
         * Gerenciador de erros.
         * @type {abstracts.domain.ModelError}
         */
        this.error_handler = new abstracts.domain.ModelError(this);

        /**
         * Cliente HTTP REST.
         * @type {abstracts.http.Client}
         */
        this.client = new abstracts.http.Client(self.error_handler);

        /**
         * Instâncias de window.cgsy.abstracts.domain.Field
         *  - nome do campo -> instância de Field.
         * @type {Object}
         * @private
         */
        var _fields = {};

        /**
         * Lista de nomes de campos.
         * @type {Array}
         * @private
         */
        var _field_names = [];

        /**
         * Lista de campos obrigatórios.
         * @type {Array}
         * @private
         */
        var _required_field_names = [];

        /**
         * Lista de campos booleanos.
         * @type {Array}
         * @private
         */
        var _boolean_field_names = [];

        /**
         * Lista de campos inteiros.
         * @type {Array}
         * @private
         */
        var _integer_field_names = [];

        /**
         * Lista de campos que podem ficar em branco.
         * @type {Array}
         * @private
         */
        var _blank_field_names = [];

        /**
         * Lista de campos que serão submetidos para o servidor via REST.
         * @type {Array}
         * @private
         */
        var _submittable_field_names = [];

        /**
         * Se iniciado e todos os campos devidamente mapeados.
         * @type {boolean}
         * @private
         */
        var _initialized = false;

        /**
         * Se populado.
         * @type {boolean}
         * @private
         */
        var _populated = false;

        /**
         * Resgata URI de criação de modelo de domínio.
         * @returns {string}
         */
        this.getCreationUri = function () {
            if (!self.uri_manager) {
                console.error('<model>.uri_manager not configured.');
                return '';
            }

            var uri = self.creation_uri;
            if (!uri) {
                console.error('<model>.creation_uri not configured.');
                return '';
            }

            var has_error = false;
            self.getFieldNames().forEach(function(name) {
                var criteria = '{{' + name + '}}';
                if (uri.includes(criteria)) {
                    var field = self.getField(name);
                    var value = field.getValue();
                    if (value) {
                        uri = uri.replace(criteria, value);
                    } else {
                        has_error = true;
                        console.error('Valor inexistente para critério "'+criteria+'"');
                    }
                }
            });

            if (has_error) {
                self.error_handler.setNonKeyError('URI inválida.');
                return '';
            }

            return self.uri_manager.getUri(uri);
        };

        /**
         * Resgata URI de modelo de domínio.
         * @returns {string}
         */
        this.getUri = function () {
            var uri_manager = self.getUriManager();

            if (!uri_manager) {
                return '';
            }

            var uri = this.uri || '';
            if (!uri) {
                console.error('<model>.uri not configured.');
                return '';
            }

            var has_error = false;
            self.getFieldNames().forEach(function(name) {
                var criteria = '{{' + name + '}}';
                if (uri.includes(criteria)) {
                    var field = self.getField(name);
                    var value = field.getValue();
                    if (value) {
                        uri = uri.replace(criteria, value);
                    } else {
                        has_error = true;
                        console.error('Valor inexistente para critério "'+criteria+'".');
                    }
                }
            });

            if (has_error) {
                self.error_handler.setNonKeyError('URI inválida.');
                return '';
            }
            return uri_manager.getUri(uri);
        };

        /**
         * Resgata instância de URIManager.
         * @returns {abstracts.uri.URIManager}
         */
        this.getUriManager = function () {
            var uri_manager = self.uri_manager;
            if (!uri_manager) {
                console.error('<model>.uri_manager not configured.');
            }
            return uri_manager;
        };

        /**
         * Se campo com o nome informado existe.
         * @param {string} field_name
         * @returns {boolean}
         */
        this.hasField = function (field_name) {
            init();
            return _field_names.includes(field_name);
        };

        /**
         * Se campo com o nome informado é booleano.
         * @param {string} field_name
         * @returns {boolean}
         */
        this.isBoolean = function (field_name) {
            init();
            return _boolean_field_names.includes(field_name);
        };

        /**
         * Se campo com o nome informado é inteiro.
         * @param {string} field_name
         * @returns {boolean}
         */
        this.isInteger = function (field_name) {
            init();
            return _integer_field_names.includes(field_name);
        };

        /**
         * Se campo com o nome informado é obrigatório.
         * @param {string} field_name
         * @returns {boolean}
         */
        this.isRequired = function (field_name) {
            init();
            return _required_field_names.includes(field_name);
        };

        /**
         * Se campo com o nome informado é passível de ser enviado para o servidor
         * via REST.
         * @param {string} field_name
         * @returns {boolean}
         */
        this.isSubmittable = function (field_name) {
            init();
            return _submittable_field_names.includes(field_name);
        };

        /**
         * Se campo com o nome informado pode ficar em branco.
         * @param {string} field_name
         * @returns {boolean}
         */
        this.isBlank = function (field_name) {
            init();
            return _blank_field_names.includes(field_name);
        };

        /**
         * Se model é novo.
         * @returns {boolean}
         */
        this.isNew = function () {
            return !self.pk;
        };

        /**
         * Se modelo é válido.
         * @returns {boolean}
         */
        this.isValid = function () {
            init();

            if (self.pk && !self.get('pk')) {
                self.set('pk', self.pk);
            }

            var has_key_errors = Object.keys(self.error_handler.key_errors).length > 0;
            var has_errors = self.error_handler.non_key_errors.length > 0;
            valid = valid && has_errors === false && has_key_errors === false;

            if (valid === false) {
                return false;
            }

            var valid = (self.isNew())
                ? self.error_handler.isValidForCreate()
                : self.error_handler.isValidForUpdate();

            has_key_errors = Object.keys(self.error_handler.key_errors).length > 0;
            has_errors = self.error_handler.non_key_errors.length > 0;
            valid = valid && has_errors === false && has_key_errors === false;

            return valid === true;
        };

        /**
         * Se modelo possui suporta a buscar seus dados no servidor.
         * @returns {boolean}
         */
        this.isFetchable = function () {
            return self.error_handler.isValidForFetch();
        };

        /**
         * Resgata nomes de campos do modelo.
         * @returns {Array}
         */
        this.getFieldNames = function () {
            init();
            return _field_names;
        };

        /**
         * Resgata lista de instâncias de Field.
         * @returns {Object}
         */
        this.getFields = function () {
            init();
            return _fields;
        };

        /**
         * Resgata instância de Field de acordo o nome do campo informado.
         * @param {string} field_name
         * @returns {abstracts.domain.Field}
         */
        this.getField = function (field_name) {
            init();
            if (!self.hasField(field_name)) {
                console.warn('Campo "' + field_name + '" não existe no model.');
                return undefined;
            }
            return _fields[field_name];
        };

        /**
         * Seta valor de campo.
         * @param {string} field_name
         * @param {*} value
         * @returns {abstracts.domain.Model}
         */
        this.set = function (field_name, value) {
            init();
            if (!self.hasField(field_name)) {
                console.warn('Campo "' + field_name + '" não existe no model.');
                return self;
            }

            var field = _fields[field_name];
            field.setValue(value);

            var pk_possibles = ['pk', 'id', 'uuid'];
            pk_possibles.forEach(function (pk) {
                if (field_name === pk) {
                    if (self.pk_type === 'integer') {
                        value = parseInt(value);
                    }
                    self.pk = value;
                }
            });

            if (field.has_error) {
                self.error_handler.setKeyError(field.label, field.getMessage());
            }

            return self;
        };

        /**
         * Resgata valor de campo.
         * @param {string} field_name
         * @returns {*}
         */
        this.get = function (field_name) {
            init();
            if (!self.hasField(field_name)) {
                console.warn('Campo "' + field_name + '" não existe no model.');
                return undefined;
            }
            return self.getField(field_name).getValue();
        };

        /**
         * Resgata objeto de valores do modelo: nome do campo -> valor.
         * @returns {Object}
         */
        this.toPlainObject = function () {
            init();
            var data = {};
            Object.keys(_fields).forEach(function (field_name) {
                var field = _fields[field_name];
                var value = field.getValue();

                if (typeof value === 'undefined') {
                    value = null;
                }

                switch (field.type) {
                    case 'datetime':
                        data[field_name] = (value) ? value.format('YYYY-MM-DD HH:mm:ss') : '0000-00-00 00:00:00';
                        break;
                    case 'date':
                        data[field_name] = (value) ? value.format('YYYY-MM-DD') : '0000-00-00';
                        break;
                    case 'boolean':
                        data[field_name] = value === true;
                        break;
                    case 'string':
                        data[field_name] = (value) ? value : '';
                        break;
                    default:
                        data[field_name] = value;
                }
            });

            return data;
        };

        /**
         * Popula o modelo passando um objeto de chave e valor para preencher
         * os campos do de modelo.
         * @param {Object} data
         */
        this.populate = function (data) {
            init();

            if (!data) {
                return;
            }

            var pk_possibles = ['pk', 'id', 'uuid'];
            pk_possibles.forEach(function (pk) {
                if (data.hasOwnProperty(pk) && data[pk]) {
                    if (self.pk_type === 'integer') {
                        data[pk] = parseInt(data[pk]);
                    }
                    self.set('pk', data[pk]);
                }
            });

            self.getFieldNames().forEach(function(field_name) {
                if (!data.hasOwnProperty(field_name)) {
                    return;
                }

                if (pk_possibles.includes(field_name)) {
                    return;
                }

                if (!self.hasField(field_name)) {
                    return;
                }

                var field = self.getField(field_name);
                var value = data[field_name];

                switch (field.type) {
                    case 'boolean':
                        value = value === true;
                        break;
                    case 'integer':
                        value = parseInt(value);
                        break;
                    case 'float':
                        value = parseFloat(value);
                        break;
                }

                self.set(field_name, value);
            });

            _populated = true;
        };

        /**
         * Busca dados do modelo no servidor.
         * @returns {Promise}
         */
        this.fetch = function () {
            return new Promise(function (resolve, reject) {
                if (!self.error_handler.isValidForFetch()) {
                    reject();
                    return;
                }

                var uri = self.getUri();

                if (!uri) {
                    reject();
                    return;
                }

                self.client.fetch(uri).then(function (result) {
                    if (result.type !== 'success') {
                        _registerError(result.result);
                        return reject();
                    }

                    self.populate(result.result);
                    resolve();
                });
            });
        };

        /**
         * Exclui modelo.
         * @returns {Promise}
         */
        this.delete = function () {
            return new Promise(function (resolve, reject) {
                if (!self.error_handler.isValidForDelete()) {
                    reject();
                    return;
                }

                var uri = self.getUri();

                if (!uri) {
                    reject();
                    return;
                }

                self.client.delete(uri).then(function (result) {
                    if (result.type !== 'success') {
                        _registerError(result.result);
                        return reject();
                    }

                    resolve();
                });
            });
        };

        /**
         * Salva dados do modelo no servidor.
         * @returns {Promise}
         */
        this.save = function () {
            return new Promise(function (resolve, reject) {
                if (self.isNew()) {
                    self._create().then(function () {
                        resolve();
                    }, function(reason) {
                        reject(reason);
                    });
                    return;
                }

                self._update().then(function () {
                    resolve();
                }, function(reason) {
                    reject(reason);
                });
            });
        };

        /**
         * Cria modelo no servidor.
         * @returns {Promise}
         * @private
         */
        this._create = function () {
            return new Promise(function (resolve, reject) {
                if (!self.error_handler.isValidForCreate()) {
                    reject();
                    return;
                }

                var uri = self.getCreationUri();

                if (!uri) {
                    reject();
                    return;
                }

                self.client.create(uri, self.toPlainObject()).then(function (result) {
                    if (result.type !== 'success') {
                        _registerError(result.result);
                        return reject();
                    }

                    self.populate(result.result);
                    resolve();
                });
            });
        };

        /**
         * Atualiza modelo no servidor.
         * @returns {Promise}
         * @private
         */
        this._update = function () {
            return new Promise(function (resolve) {
                if (!self.error_handler.isValidForUpdate()) {
                    resolve();
                    return;
                }

                var uri = self.getUri();

                if (!uri) {
                    resolve();
                    return;
                }

                self.client.update(uri, self.toPlainObject()).then(function (result) {
                    if (result.type !== 'success') {
                        _registerError(result.result);
                    } else {
                        self.populate(result.result);
                    }

                    resolve();
                });
            });
        };

        /**
         * Registra erro conforme dados de resposta do servidor.
         * @param {Object} data
         * @private
         */
        var _registerError = function (data) {
            if (data.hasOwnProperty('responseJSON')) {
                data = data.responseJSON;
            }

            self.getFieldNames().forEach(function (name) {
                var field = self.getField(name);
                var msg = field.getMessage();

                if (!data.hasOwnProperty(name)) {
                    return;
                }

                var errors = data[name];

                if (errors instanceof Array) {
                    errors.forEach(function (error_msg) {
                        var config_msg = (msg) ? msg : error_msg;
                        self.error_handler.setKeyError(field.name, config_msg);
                    });
                } else {
                    self.error_handler.setKeyError(field.name, errors);
                }
            });
        };

        /**
         * Inicia construção de configurações do modelo.
         */
        var init = function () {
            if (_initialized) {
                return;
            }

            self.client.auth_token = self.uri_manager.getAuthToken();

            var f = new abstracts.domain.Field('pk', 'ID', self.pk_type, true);
            f.setMessage('ID deve ser informado.');
            if (self.pk) {
                if (self.type === 'integer') {
                    self.pk = parseInt(self.pk);
                }
                f.setValue(self.pk);
            }
            _fields['pk'] = f;
            _field_names.push('pk');

            Object.keys(self.fields).forEach(function (name) {
                var data = self.fields[name];

                if (!data.hasOwnProperty('type')) {
                    console.error('Campo mal configurado: "' + name + '" não possui "type".');
                    return;
                }

                if (!data.hasOwnProperty('required')) {
                    console.error('Campo mal configurado: "' + name + '" não possui "required."');
                    return;
                } else if (typeof data['required'] !== 'boolean') {
                    console.error('Campo mal configurado: valor de "required" para "' + name + '" deve ser boolean.');
                    return;
                }

                var label = name;
                if (data.hasOwnProperty('label')) {
                    label = data['label'];
                }

                var f = new abstracts.domain.Field(name, label, data['type'], data['required'] === true);

                if (!data.hasOwnProperty('message') && data['required'] === true) {
                    console.error('Campo mal configurado: "' + name + '" é obrigatório e não possiu "message".');
                    return;
                } else {
                    f.setMessage(data['message']);
                }

                if (data.hasOwnProperty('submittable') && data['submittable'] === false) {
                    f.submittable = false;
                } else {
                    _submittable_field_names.push(name);
                }

                if (data.hasOwnProperty('blank') && data['blank'] === true) {
                    f.blank = true;
                    _blank_field_names.push(name);
                }

                _fields[name] = f;
                _field_names.push(name);

                if (data['type'] === 'integer') {
                    _integer_field_names.push(name);
                }

                if (data['type'] === 'boolean') {
                    _boolean_field_names.push(name);
                }

                if (data['required'] === true) {
                    _required_field_names.push(name);
                }
            });
            _initialized = true;
        };
        window.setTimeout(function () {
            init()
        }, 50);
    };

})(window.cgsy.abstracts, moment);
