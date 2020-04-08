import Video from "./video"
import HTTPClient from "../../../http/dist/client";

export default class VideoCollection {
    constructor() {
        this.reset();

        const BASE_URL = window.cgsy_environemnt.API_BASE_URL;
        const API_TOKEN = window.cgsy_environemnt.API_TOKEN;

        this.client = new HTTPClient(BASE_URL);
        this.client.setAuthorizationCode('Token', API_TOKEN);
        this.project_pk = window.cgsy_environemnt.PROJECT_PK;
    }

    add(item) {
        this.items.push(item);
    }

    reset() {
        this.items = [];
    }

    fetch() {
        return new Promise((resolve, reject) => {
            this.reset();
            const uri = `/v1/videos/projects/${this.project_pk}/videos/`;
            this.client.get(uri).then((items) => {
                if (items instanceof Array) {
                    items.forEach((item) => {
                        const new_item = new Video();

                        // if (item.hasOwnProperty('project')) {
                        //     const project = new Project();
                        // }
                        item['project'] = this.project_pk;
                        new_item.populate(item);
                        this.add(new_item);
                    });
                }
                resolve();
            }).catch((reason) => reject(reason));
        });
    }
}