<template>
    <div class="well well-sm">
        <div class="row">
            <div class="col-sm-4 col-lg-3">
                <div class="video-image-block">
                    <div style="position:absolute;margin: 5px 0 0 5px;z-index:10;">
                        <div>
<!--                            <button title="Editar dados do vídeo"-->
<!--                                    data-toggle="tooltip"-->
<!--                                    class="btn btn-sm video-config-button">-->
<!--                                <span class="fas fa-edit"></span>-->
<!--                                Editar-->
<!--                            </button>-->
                        </div>
                        <div>
                            <button type="button" @click="deleteVideo"
                                    title="Excuir vídeo" data-toggle="tooltip"
                                    class="btn btn-sm video-config-button">
                                <span class="fas fa-trash"></span>
                            </button>
                        </div>
                    </div>
                    <div v-show="restricted"
                         style="position:absolute;right:5px;margin-top:8px;z-index:10;font-size:12px"
                         class="badge badge-danger">Restrito
                    </div>
                    <img :src="thumbnail_small"
                         class="img img-responsive video-thumbnail"
                         style="min-height: 140px"/>
                    <div class="overlay">
                        <a href="javascript:void(0)" @click="openPlayer"
                           class="icon" data-toggle="tooltip"
                           data-placement="bottom"
                           title="Clique para visualizar">
                            <i class="fas fa-play" style="font-size:85px"></i>
                        </a>
                    </div>
                </div>
            </div>
            <div class="col-sm-8 col-lg-9">
                <div style="font-size: smaller;font-weight: 600">
                    {{name}}
                </div>
                <div style="line-height: 0.95"
                     v-if="description && description.length > 80">
                    <small><small class="text-muted">
                        {{description|truncate(80, '...')}}
                    </small></small>
                </div>
                <div style="line-height: 0.95" data-toggle="tooltip" v-else>
                    <small><small class="text-muted">
                        {{description}}
                    </small></small>
                </div>
                <hr/>
                <div class="row">
                    <div class="col-sm-6">

                        <div class="row">
                            <div class="col-md-12">
                                <div style="font-size: smaller">
                                    <strong>Programação:</strong>
                                    <div v-show="starts_at"
                                         style="margin-left:4px;font-size: smaller">
                                        <strong>Inicia em:</strong>
                                        {{formatDateTime(starts_at)}}
                                    </div>
                                    <div v-show="ends_at"
                                         style="margin-left:4px;font-size: smaller">
                                        <strong>Encerra em:</strong>
                                        {{formatDateTime(ends_at)}}
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="row" v-show="playlists.length">
                            <div class="col-md-12" style="font-size:smaller">
                                <div style="margin-top: 4px;"><strong>Playlists:</strong>
                                </div>
                                <div v-for="item in playlists" :key="item.pk">-
                                    {{item.name}}
                                </div>
                                <small v-show="playlists_more > 0"
                                       class="text-muted">mais
                                    {{playlists_more}} playlists.</small>
                            </div>
                        </div>

                    </div>
                    <div class="row">
                        <div class="col-sm-6 text-right">
                            <div class="col-sm-12">
                                <small><strong>Categoria:</strong></small>
                                <div v-show="!category_edition_mode"
                                     style="margin-left:4px;margin-bottom:8px;font-size: smaller">
                                    <small>
                                        <span v-if="category_name">{{category_name}}</span>
                                        <span v-else class="text-muted">sem categoria</span>
                                        &ensp;
                                        <span @click="category_edition_mode = true"
                                              class="fas fa-pencil-alt"
                                              style="font-size:12px;cursor:pointer"
                                              data-toggle="tooltip"
                                              title="Alterar a categoria"></span>
                                    </small>
                                </div>
                                <div v-show="category_edition_mode">
                                    <select @change="setCategory"
                                            class="form-control"
                                            style="height:25px;padding:0 0 2px 8px;margin-bottom:3px;font-size:12px">
                                        <option value="">- Nenhuma -</option>
                                        <option v-for="item in categories"
                                                :key="item.pk" :value="item.pk"
                                                :selected="item.pk === category_pk">
                                            {{item.name}}
                                        </option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-sm-12">
                                <div v-show="provider === 'vimeo'"
                                     class="badge badge-success"
                                     style="font-size:16px">
                                    <i class="fab fa-vimeo-v"></i>
                                    Vimeo
                                </div>
                                <div v-show="provider === 'youtube'"
                                     class="badge badge-success"
                                     style="font-size:16px">
                                    <i class="fab fa-youtube"></i>
                                    Youtube
                                </div>
                            </div>
                            <div class="col-sm-12">
                                <div style="margin-top: 10px">
                                    <span style="font-size: smaller">Ativo:</span>&ensp;
                                    <input type="checkbox"
                                           @change="toggleActive"
                                           :checked="active" name="active"
                                           style="display:none"
                                           class="js-switch"
                                           :id="'id_active_' + this.pk">
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        name: "VideoListItem",
        props: {
            'video_id': {
                type: String,
                required: true,
            }
        },
        data() {
            return {
                'pk': null,
                'name': null,
                'description': null,
                'restricted': false,
                'active': false,
                'playlists': [],
                'playlists_more': 0,
                'starts_at': null,
                'ends_at': null,
                'provider': null,
                'thumbnail_default': null,
                'thumbnail_large': null,
                'thumbnail_small': null,
                'link': null,

                'category_edition_mode': false,
                'categories': this.$category_store.state.items,

                'category_name': null,
                'category_pk': null,
            }
        },
        mounted() {
            this.loadVideos();
        },
        methods: {
            loadSwitchery() {
                window.setTimeout(() => window.app.switcheryToggle(), 300);
            },
            loadVideos() {
                if (!this.video_id) {
                    return;
                }

                this.$video_store.state.items.forEach((item) => {
                    if (item.pk !== this.video_id) {
                        return;
                    }
                    this.pk = item.pk;
                    this.name = item.name;
                    this.description = item.description;
                    this.restricted = item.restrict;
                    this.active = item.active;
                    this.link = item.link;
                    this.external_link = item.external_link;
                    this.thumbnail_default = item.thumbnail_default;
                    this.thumbnail_large = item.thumbnail_large;
                    this.thumbnail_small = item.thumbnail_small;

                    if (item.playlists.length > 2) {
                        this.playlists = [item.playlists[0], item.playlists[1]];
                        this.playlists_more = this.playlists.length - 2;
                    } else {
                        this.playlists = item.playlists;
                        this.playlists_more = 0;
                    }

                    if (item.category) {
                        if (item.category.hasOwnProperty('name')) {
                            this.category_name = item.category.name;
                            this.category_pk = item.category.pk;
                        } else {
                            this.category_name = null;
                            this.category_pk = null;
                        }
                    }

                    if (item.starts_at) {
                        this.starts_at = new Date(item.starts_at);
                    }
                    if (item.ends_at) {
                        this.ends_at = new Date(item.ends_at);
                    }
                    this.provider = item.provider;
                });
                this.loadSwitchery();
            },
            formatDateTime(datetime) {
                if (!datetime) {
                    return;
                }
                const day = datetime.getDay().toString().padStart(2, '0');
                const month = (datetime.getMonth() + 1).toString().padStart(2, '0');
                const year = datetime.getFullYear();
                const hours = datetime.getHours().toString().padStart(2, '0');
                const minutes = datetime.getMinutes().toString().padStart(2, '0');

                return `${day}/${month}/${year} ${hours}h${minutes}`;
            },
            setCategory(e) {
                this.category_pk = e.target.value || null;
                this.category_name = e.target.selectedOptions[0].text || null;
                this.$video_store.commit('selectItem', this.pk);
                this.$video_store.commit('updateItem', {
                    'category': {
                        'pk': this.category_pk,
                        'name': this.category_name,
                    }
                });
                this.$video_store.dispatch('save');
                this.$video_store.commit('resetItem');
                setTimeout(() => this.category_edition_mode = false, 500);
            },
            toggleActive() {
                this.active = !this.active;
                this.$video_store.commit('selectItem', this.pk);
                this.$video_store.commit('updateItem', {
                    'active': this.active
                });
                this.$video_store.dispatch('save');
                this.$video_store.commit('resetItem');
                window.setTimeout(() => window.app.switcheryToggle(), 300);
            },
            openPlayer() {
                this.$video_store.commit('setPlayer', {
                    'provider': this.provider,
                    'link': this.external_link,
                });
                window.jQuery('#video-player-modal').modal();
            },
            deleteVideo() {
                if (!confirm(`Deseja realmente excluir o vídeo "${this.name}"?`)) {
                    return;
                }
                this.$video_store.commit('selectItem', this.pk);
                this.$video_store.commit('updateItem', {
                    'active': this.active
                });
                this.$video_store.dispatch('remove');
                this.$video_store.commit('resetItem');
            }
        }
    }
</script>