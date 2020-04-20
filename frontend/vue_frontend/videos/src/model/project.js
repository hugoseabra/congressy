import Base from './base';

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
                'main_video': null,
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