import Base from './base';

export default class Video extends Base {
    constructor() {
        super();

        this.createEndpoint = `/v1/videos/videos/`;
        this.itemEndpoint = `${this.createEndpoint}[pk]/`;
    }

    getFieldsManifest() {
        return {
            'pk': 'pk',
            'strings': {
                'name': null,
                'description_html': null,
                'description': null,
                'provider': null,
                'external_id': null,
                'link': null,
                'external_link': null,
                'duration': null,
                'thumbnail_small': null,
                'thumbnail_default': null,
                'thumbnail_large': null,
                'status': null,
                'future': null,
                'running': null,
                'finished': null,
                'restriction_reason': null,
            },
            'integers': {
                'order': 0,
                'restriction_code': 0,
            },
            'objects': {
                'project': {},
                'category': {},
                'video_360': {},
                'video_normal': {},
                'analytics': {},
            },
            'booleans': {
                'active': false,
                'restrict': false,
                'is_360': false,
                'allowed': false,
            },
            'lists': {
                'playlists': [],
            },
            'datetimes': {
                'starts_at': null,
                'ends_at': null,
                'created_at': null,
                'updated_at': null,
            },
        };
    }

    saveByLink(link) {
        const self = this;

        return new Promise((resolve, reject) => {
            if (!link) {
                return reject('Não é possível salvar um vídeo por link sem informar o link.');
            }

            const project_pk = window.cgsy_environemnt.PROJECT_PK;
            const uri = `/v1/videos/projects/${project_pk}/link/`;

            this.client.post(uri, {'link': link}).then((item) => {
                self.normalizeIncomingData(item);
                resolve();
            }).catch(reason => reject(reason));
        });
    }
}