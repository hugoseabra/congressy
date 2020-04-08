import { AxiosInstance } from "axios";
/**
 * Classe cliente Http, reutilizável para outras classes que
 * façam requisições Http
 */
export default class HttpClient {
    static REQUEST_TIMEOUT: number;
    static REQUEST_QUEUE_TIMEOUT: number;
    protected baseUrl: string;
    private _authorizationToken;
    private client;
    private getCancelToken;
    private postCancelToken;
    private putCancelToken;
    private patchCancelToken;
    private headCancelToken;
    private deleteCancelToken;
    private _fetchResultKey;
    /**
     * Inicia uma instância de axios
     * @param baseUrl
     */
    constructor(baseUrl: string);
    /**
     * Sets authorization token.
     * @param tokenType - Token type: Bearer, Token, etc.
     * @param token - token string
     */
    setAuthorizationCode(tokenType: string, token: string): void;
    /**
     * Gets authorization token
     */
    get authorizationToken(): string;
    setFethResultKey(key: string): void;
    get fetchResultKey(): string;
    /**
     *
     * @param path
     */
    get(path: string): Promise<any>;
    /**
     *
     * @param path
     */
    delete(path: string): Promise<any>;
    /**
     *
     * @param path
     */
    head(path: string): Promise<any>;
    /**
     *
     * @param path
     * @param data
     */
    post(path: string, data?: any): Promise<any>;
    /**
     *
     * @param path
     * @param data
     */
    put(path: string, data: any): Promise<any>;
    /**
     *
     * @param path
     * @param data any
     */
    patch(path: string, data: any): Promise<any>;
    /**
     * Se o endpoint não começar com barra será
     * adicionado uma barra (/) para a uri
     * @param endpoint
     * @param includeBaseUrl
     * @return {string}
     */
    getUri(endpoint: string, includeBaseUrl?: boolean): string;
    /**
     * Cria instância de objeto que lida com a comunicação HTTP.
     */
    getWrappedClient(): AxiosInstance;
    /**
     * Se a url começar com barra no final,
     * splitamos e pagamos o ultimo resultado no caso o barra (/)
     * e retornamos a url, caso contrario retorna ela mesma por
     * inteiro
     * @param baseUrl
     * @return {baseUrl}
     */
    protected static normalizeBaseUrl(baseUrl: string): string;
    /**
     * Retorna as configurações padrões da Headers
     * da Instância axios
     * @returns
     */
    protected getDefaultHeaders(): object;
    /**
     * Retronando Options Default para a Instância de axios
     * @return {object}
     */
    protected getClientDefaultOptions(): object;
    /**
     * Resgata valor correto da resposta de uma requisição.
     * @param responseData
     */
    protected retrieveFetchResult(responseData: {
        [s: string]: any;
    }): any;
}
