import { HttpErrorBase } from "@curveball/http-errors";
export default class InterceptorResponse {
    static resp(response: any): any;
    static handleError(error: any): HttpErrorBase;
}
