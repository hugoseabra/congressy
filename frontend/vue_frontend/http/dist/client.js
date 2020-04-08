import axios from "axios";
import InterceptorResponse from "./interceptors";
/**
 * Classe cliente Http, reutilizável para outras classes que
 * façam requisições Http
 */
export default class HttpClient {
    /**
     * Inicia uma instância de axios
     * @param baseUrl
     */
    constructor(baseUrl) {
        this._fetchResultKey = "results";
        this.baseUrl = HttpClient.normalizeBaseUrl(baseUrl);
    }
    /**
     * Sets authorization token.
     * @param tokenType - Token type: Bearer, Token, etc.
     * @param token - token string
     */
    setAuthorizationCode(tokenType, token) {
        tokenType = tokenType.toLowerCase();
        tokenType = tokenType.charAt(0).toUpperCase() + tokenType.slice(1);
        this._authorizationToken = `${tokenType} ${token}`;
    }
    /**
     * Gets authorization token
     */
    get authorizationToken() {
        return this._authorizationToken;
    }
    setFethResultKey(key) {
        this._fetchResultKey = key;
    }
    get fetchResultKey() {
        return this._fetchResultKey;
    }
    /**
     *
     * @param path
     */
    get(path) {
        return new Promise((resolve, reject) => {
            /* istanbul ignore if */
            if (this.getCancelToken) {
                clearTimeout(this.getCancelToken);
                this.getCancelToken = undefined;
            }
            // @ts-ignore
            this.getCancelToken = setTimeout(() => {
                this.getWrappedClient()
                    .get(this.getUri(path, false))
                    .then((response) => {
                    this.getCancelToken = undefined;
                    resolve(this.retrieveFetchResult(response.data));
                })
                    .catch((httpError) => {
                    this.getCancelToken = undefined;
                    reject(httpError);
                });
            }, HttpClient.REQUEST_QUEUE_TIMEOUT);
        });
    }
    /**
     *
     * @param path
     */
    delete(path) {
        return new Promise((resolve, reject) => {
            /* istanbul ignore if */
            if (this.deleteCancelToken) {
                clearTimeout(this.deleteCancelToken);
                this.deleteCancelToken = undefined;
            }
            // @ts-ignore
            this.deleteCancelToken = setTimeout(() => {
                this.getWrappedClient()
                    .delete(this.getUri(path, false))
                    .then((response) => {
                    this.deleteCancelToken = undefined;
                    resolve(this.retrieveFetchResult(response.data));
                })
                    .catch((httpError) => {
                    this.deleteCancelToken = undefined;
                    reject(httpError);
                });
            }, HttpClient.REQUEST_QUEUE_TIMEOUT);
        });
    }
    /**
     *
     * @param path
     */
    head(path) {
        return new Promise((resolve, reject) => {
            /* istanbul ignore if */
            if (this.headCancelToken) {
                clearTimeout(this.headCancelToken);
                this.headCancelToken = undefined;
            }
            // @ts-ignore
            this.headCancelToken = setTimeout(() => {
                this.getWrappedClient()
                    .head(this.getUri(path, false))
                    .then((response) => {
                    this.headCancelToken = undefined;
                    resolve(this.retrieveFetchResult(response.data));
                })
                    .catch((httpError) => {
                    this.headCancelToken = undefined;
                    reject(httpError);
                });
            }, HttpClient.REQUEST_QUEUE_TIMEOUT);
        });
    }
    /**
     *
     * @param path
     * @param data
     */
    post(path, data) {
        return new Promise((resolve, reject) => {
            /* istanbul ignore if */
            if (this.postCancelToken) {
                clearTimeout(this.postCancelToken);
                this.postCancelToken = undefined;
            }
            // @ts-ignore
            this.headCancelToken = setTimeout(() => {
                this.getWrappedClient()
                    .post(this.getUri(path, false), data)
                    .then((response) => {
                    this.postCancelToken = undefined;
                    resolve(this.retrieveFetchResult(response.data));
                })
                    .catch((httpError) => {
                    this.postCancelToken = undefined;
                    reject(httpError);
                });
            }, HttpClient.REQUEST_QUEUE_TIMEOUT);
        });
    }
    /**
     *
     * @param path
     * @param data
     */
    put(path, data) {
        return new Promise((resolve, reject) => {
            /* istanbul ignore if */
            if (this.putCancelToken) {
                clearTimeout(this.putCancelToken);
                this.putCancelToken = undefined;
            }
            // @ts-ignore
            this.putCancelToken = setTimeout(() => {
                this.getWrappedClient()
                    .put(this.getUri(path, false), data)
                    .then((response) => {
                    this.putCancelToken = undefined;
                    resolve(this.retrieveFetchResult(response.data));
                })
                    .catch((httpError) => {
                    this.putCancelToken = undefined;
                    reject(httpError);
                });
            }, HttpClient.REQUEST_QUEUE_TIMEOUT);
        });
    }
    /**
     *
     * @param path
     * @param data any
     */
    patch(path, data) {
        return new Promise((resolve, reject) => {
            /* istanbul ignore if */
            if (this.patchCancelToken) {
                clearTimeout(this.patchCancelToken);
                this.patchCancelToken = undefined;
            }
            // @ts-ignore
            this.patchCancelToken = setTimeout(() => {
                this.getWrappedClient()
                    .patch(this.getUri(path, false), data)
                    .then((response) => {
                    this.patchCancelToken = undefined;
                    resolve(this.retrieveFetchResult(response.data));
                })
                    .catch((httpError) => {
                    this.patchCancelToken = undefined;
                    reject(httpError);
                });
            }, HttpClient.REQUEST_QUEUE_TIMEOUT);
        });
    }
    /**
     * Se o endpoint não começar com barra será
     * adicionado uma barra (/) para a uri
     * @param endpoint
     * @param includeBaseUrl
     * @return {string}
     */
    getUri(endpoint, includeBaseUrl = true) {
        let endpointSplit = endpoint.split("?");
        /* istanbul ignore next */
        const queryString = endpointSplit.length > 1 ? endpointSplit[1] : "";
        endpoint = endpointSplit[0];
        /* istanbul ignore if */
        if (!endpoint.startsWith("/")) {
            endpoint = `/${endpoint}`;
        }
        if (!endpoint.endsWith("/")) {
            endpoint = `${endpoint}/`;
        }
        /* istanbul ignore if */
        if (queryString) {
            endpoint = `${endpoint}?${queryString}`;
        }
        return includeBaseUrl ? this.baseUrl + endpoint : endpoint;
    }
    /**
     * Cria instância de objeto que lida com a comunicação HTTP.
     */
    getWrappedClient() {
        if (this.client) {
            return this.client;
        }
        this.client = axios.create(this.getClientDefaultOptions());
        this.client.interceptors.response.use(response => InterceptorResponse.resp(response), error => Promise.reject(InterceptorResponse.handleError(error)));
        return this.client;
    }
    /**
     * Se a url começar com barra no final,
     * splitamos e pagamos o ultimo resultado no caso o barra (/)
     * e retornamos a url, caso contrario retorna ela mesma por
     * inteiro
     * @param baseUrl
     * @return {baseUrl}
     */
    static normalizeBaseUrl(baseUrl) {
        /* istanbul ignore if */
        if (baseUrl.endsWith("/")) {
            return baseUrl.substring(0, baseUrl.length - 1);
        }
        return baseUrl;
    }
    /**
     * Retorna as configurações padrões da Headers
     * da Instância axios
     * @returns
     */
    getDefaultHeaders() {
        let headerContent = {
            "Content-Type": "application/json"
        };
        /* istanbul ignore if */
        if (this._authorizationToken) {
            headerContent["Authorization"] = this._authorizationToken;
        }
        return headerContent;
    }
    /**
     * Retronando Options Default para a Instância de axios
     * @return {object}
     */
    getClientDefaultOptions() {
        return {
            baseURL: this.baseUrl,
            timeout: HttpClient.REQUEST_TIMEOUT,
            headers: this.getDefaultHeaders()
        };
    }
    /**
     * Resgata valor correto da resposta de uma requisição.
     * @param responseData
     */
    retrieveFetchResult(responseData) {
        let result;
        if (typeof responseData == "object" &&
            responseData.hasOwnProperty(this.fetchResultKey)) {
            result = responseData[this.fetchResultKey];
        }
        else {
            result = responseData;
        }
        return result;
    }
}
HttpClient.REQUEST_TIMEOUT = 60000;
HttpClient.REQUEST_QUEUE_TIMEOUT = 100;
//# sourceMappingURL=client.js.map