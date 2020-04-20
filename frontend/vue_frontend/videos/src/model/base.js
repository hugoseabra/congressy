import HTTPClient from "../../../http/dist/client";

const dot = require('dot-object');

export default class Base {


    constructor() {
        this.fields = this.getFieldsManifest();
        this.reset();

        this.createEndpoint = null;
        this.itemEndpoint = null;

        this.setCredentials();
    }

    getFieldsManifest() {
        return {
            'pk': 'pk',
            'strings': {},
            'integers': {},
            'objects': {},
            'booleans': {},
            'lists': {},
            'datetimes': {},
        };
    }

    isFieldString(field_name) {
        let isString = false;
        this.fields.strings.forEach((f) => {
            if (f === field_name) {
                isString = true;
            }
        });
        return isString;
    }

    isFieldInteger(field_name) {
        let isInteger = false;
        this.fields.integers.forEach((f) => {
            if (f === field_name) {
                isInteger = true;
            }
        });
        return isInteger;
    }

    isFieldObject(field_name) {
        let isObject = false;
        this.fields.objects.forEach((f) => {
            if (f === field_name) {
                isObject = true;
            }
        });
        return isObject;
    }

    isFieldBoolean(field_name) {
        let isBoolean = false;
        this.fields.booleans.forEach((f) => {
            if (f === field_name) {
                isBoolean = true;
            }
        });
        return isBoolean;
    }

    isFieldList(field_name) {
        let isList = false;
        this.fields.lists.forEach((f) => {
            if (f === field_name) {
                isList = true;
            }
        });
        return isList;
    }

    isFieldDatetime(field_name) {
        let isDatetime = false;
        this.fields.datetimes.forEach((f) => {
            if (f === field_name) {
                isDatetime = true;
            }
        });
        return isDatetime;
    }

    getFieldNames() {
        let fields = [];
        fields.push(this.fields.pk);
        Object.keys(this.fields.strings).forEach(f => fields.push(f));
        Object.keys(this.fields.integers).forEach(f => fields.push(f));
        Object.keys(this.fields.objects).forEach(f => fields.push(f));
        Object.keys(this.fields.booleans).forEach(f => fields.push(f));
        Object.keys(this.fields.lists).forEach(f => fields.push(f));
        Object.keys(this.fields.datetimes).forEach(f => fields.push(f));

        return fields;
    }

    normalizaEndpoint(endpoint) {
        const regex = /\[([^\][\r\n]*)\]/gi;
        let placeholders_brackets = [];
        let placeholders = [];
        let match;
        let has_match = true;
        while (has_match) {
            match = regex.exec(endpoint);
            if (!match) {
                has_match = false;
                continue;
            }
            placeholders_brackets.push(match[0]);
            placeholders.push(match[1]);
        }

        const data = this.toData();

        let i = 0;
        placeholders.forEach((placeholder) => {
            const value = dot.pick(placeholder, data);
            if (value) {
                endpoint = endpoint.replace(placeholders_brackets[i], value);
            }
            i++;
        });
        return endpoint;
    }

    setCredentials() {
        const BASE_URL = window.cgsy_environemnt.API_BASE_URL;
        const API_TOKEN = window.cgsy_environemnt.API_TOKEN;

        this.client = new HTTPClient(BASE_URL);
        this.client.setAuthorizationCode('Token', API_TOKEN);
    }

    populate(data) {
        const self = this;
        this.getFieldNames().forEach((f_name) => {
            if (data.hasOwnProperty(f_name)) {
                self[f_name] = data[f_name];
            }
        });
    }

    reset() {
        this[this.fields.pk] = null;
        Object.keys(this.fields.strings).forEach(f => this[f] = this.fields.strings[f]);
        Object.keys(this.fields.integers).forEach(f => this[f] = this.fields.integers[f]);
        Object.keys(this.fields.objects).forEach(f => this[f] = this.fields.objects[f]);
        Object.keys(this.fields.booleans).forEach(f => this[f] = this.fields.booleans[f]);
        Object.keys(this.fields.lists).forEach(f => this[f] = this.fields.lists[f]);
        Object.keys(this.fields.datetimes).forEach(f => this[f] = this.fields.datetimes[f]);
    }

    toData() {
        let data = {};
        const self = this;
        this.getFieldNames().forEach((f) => {
            data[f] = self[f];
        });
        return data;
    }

    normalizeIncomingData(data) {
        data = dot.object(data);
        this.populate(data);
    }

    fetch() {
        const self = this;
        return new Promise((resolve, reject) => {
            if (!self.pk) {
                return reject(
                    'Model instance without primary key cannot be fetched.'
                );
            }

            const result = (item) => {
                self.normalizeIncomingData(item);
                resolve()
            };

            const uri = this.normalizaEndpoint(this.itemEndpoint);

            self.client
                .get(uri)
                .then(result)
                .catch(reason => reject(reason));
        });
    }

    save() {
        const self = this;
        return new Promise((resolve, reject) => {

            const uri = this.normalizaEndpoint(
                (self.pk) ? this.itemEndpoint : this.createEndpoint
            );

            const result = (item) => {
                self.normalizeIncomingData(item);
                resolve()
            };

            if (self.pk) {
                self.client
                    .patch(uri, self.toData())
                    .then(result)
                    .catch(reason => reject(reason));
            } else {
                self.client
                    .post(uri, self.toData())
                    .then(result)
                    .catch(reason => reject(reason));
            }
        });
    }

    delete() {
        const self = this;
        return new Promise((resolve, reject) => {
            if (!self.pk) {
                return reject(
                    'Model instance without primary key cannot be deleted.'
                );
            }

            const uri = this.normalizaEndpoint(this.itemEndpoint);
            self.client
                .delete(uri)
                .then(() => {
                    this.reset();
                    resolve();
                })
                .catch(reason => reject(reason));
        });
    }
}