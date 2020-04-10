export default class UnknownHttpError extends Error {
    constructor(detail) {
        /* istanbul ignore next */
        super(detail || "");
        this.type = null;
        this.httpStatus = 0;
        this.title = "Some unknown error has occurred";
        this.detail = null;
        this.instance = null;
        this.detail = detail;
    }
}
//# sourceMappingURL=exceptions.js.map