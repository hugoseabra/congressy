import Base from './base';
import Namespace from "./namespace";
import Project from "./project";

export default class Category extends Base {


    constructor() {
        super();

        this.createEndpoint = `/v1/videos/projects/[project.pk]/categories/`;
        this.itemEndpoint = `${this.createEndpoint}[pk]/`;

        this.project.pk = window.cgsy_environemnt.PROJECT_PK;
    }

    getFieldsManifest() {
        return {
            'pk': 'pk',
            'strings': {
                'name': null,
            },
            'integers': {
                'num_videos': 0,
            },
            'objects': {
                'project': {},
            },
            'booleans': {
                'active': false,
            },
            'lists': {},
            'datetimes': {
                'created_at': null,
                'updated_at': null,
            },
        };
    }

    populate(data) {
        if (data.hasOwnProperty('analytics')) {
            data['num_videos'] = data['analytics']['num_videos'];
        }
        super.populate(data);
    }
}