import { HttpProblem } from "@curveball/http-errors";
export default class UnknownHttpError extends Error implements HttpProblem {
    type: string | null;
    httpStatus: number;
    title: string;
    detail: string | null;
    instance: string | null;
    constructor(detail: string | null);
}
