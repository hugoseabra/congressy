import {HttpProblem} from "@curveball/http-errors";

export default class UnknownHttpError extends Error implements HttpProblem {
    type: string | null = null;
    httpStatus: number = 0;
    title: string = "Some unknown error has occurred";
    detail: string | null = null;
    instance: string | null = null;

    constructor(detail: string | null) {
        /* istanbul ignore next */
        super(detail || "");
        this.detail = detail;
    }
}
