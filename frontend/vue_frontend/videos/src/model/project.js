import Base from './base';
import Namespace from "./namespace";

export default class Project extends Base {
    constructor() {
        super();

        this.createEndpoint = `/v1/videos/projects/`;
        this.itemEndpoint = `${this.createEndpoint}[pk]/`;
    }

    getFieldsManifest() {
        return {
            'pk': 'pk',
            'strings': {
                'name': null,
            },
            'integers': {},
            'objects': {
                'namespace': null,
                'analytics': null,
            },
            'booleans': {},
            'lists': {},
            'datetimes': {
                'created_at': null,
                'updated_at': null,
            },
        };
    }
}