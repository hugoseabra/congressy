import Base from './base';

export default class Namespace extends Base {
    constructor() {
        super();

        this.createEndpoint = `/v1/videos/namespaces//`;
        this.itemEndpoint = `${this.createEndpoint}[pk]/`;
    }

    getFieldsManifest() {
        return {
            'pk': 'pk',
            'strings': {
                'name': null,
                'slug': null,
                'external_id': null,
            },
            'integers': {},
            'objects': {},
            'booleans': {},
            'lists': {},
            'datetimes': {
                'created_at': null,
                'updated_at': null,
            },
        };
    }
}