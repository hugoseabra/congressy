import {
    BadGateway,
    BadRequest,
    Conflict,
    Forbidden,
    GatewayTimeout,
    HttpErrorBase,
    InternalServerError,
    MethodNotAllowed,
    NotAcceptable,
    NotFound,
    NotImplemented,
    RequestTimeout,
    ServiceUnavailable,
    TooManyRequests,
    Unauthorized,
    UnprocessableEntity
} from "@curveball/http-errors";
import UnknownHttpError from "./exceptions";

export default class InterceptorResponse {
    static resp(response: any) {
        return response;
    }

    public static handleError(error: any): HttpErrorBase {
        let message: string | null = null;

        /* istanbul ignore if */
        if (error.hasOwnProperty("message")) {
            message = error.message || null;
        }

        if (!error.response) {
            if (
                String(message)
                    .toLowerCase()
                    .indexOf("timeout") >= 0 &&
                String(message)
                    .toLowerCase()
                    .indexOf("exceeded") >= 0
            ) {
                return new GatewayTimeout(message);
            } else if (
                String(message)
                    .toLowerCase()
                    .indexOf("network error") >= 0
            ) {
                if (navigator.onLine) {
                    return new ServiceUnavailable(message);
                }

                return new UnknownHttpError(message);
            }

            /* istanbul ignore next */
            throw error;
        } else if (!error.response.hasOwnProperty("status")) {
            /* istanbul ignore next */
            return new UnknownHttpError(message);
        }

        /* istanbul ignore if */
        if (error.response.hasOwnProperty("message")) {
            message = error.response.message;
        }

        switch (error.response.status) {
            case 400:
                return new BadRequest(message);

            case 401:
                return new Unauthorized(message);

            case 403:
                return new Forbidden(message);

            case 404:
                return new NotFound(message);

            case 405:
                return new MethodNotAllowed(message);

            case 406:
                return new NotAcceptable(message);

            case 408:
                return new RequestTimeout(message);

            case 409:
                return new Conflict(message);

            case 422:
                return new UnprocessableEntity(message);

            case 429:
                return new TooManyRequests(message);

            case 500:
                return new InternalServerError(message);

            case 501:
                return new NotImplemented(message);

            case 502:
                return new BadGateway(message);

            case 503:
                return new ServiceUnavailable(message);

            case 504:
                return new GatewayTimeout(message);

            default:
                return new UnknownHttpError(message);
        }
    }
}