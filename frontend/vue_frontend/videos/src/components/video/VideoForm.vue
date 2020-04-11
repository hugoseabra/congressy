<template>
<form v-on:submit="submit" method="post">
    <div class="modal" id="video-form-modal" role="dialog" data-backdrop="static">
        <div class="modal-dialog " role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                    <h4 class="modal-title">
                        <span v-if="!pk">Novo</span>
                        <span v-else>Editar</span>
                        vídeo
                    </h4>
                </div>
                <div class="modal-body">

                    <video-form-preview :key="preview_key" :link="link" :provider="provider" v-show="preview_mode" />
                    <video-form-link @submitLink="setLink" :link="link" v-show="!preview_mode" />

                </div>
                <div class="modal-footer">
                    <div class="text-right">
                        <button type="button" v-show="preview_mode" :disabled="button_disabled" @click="closePreview()" class="btn btn-default">
                            <span v-if="!button_disabled">Voltar</span>
                            <span v-else>aguarde...</span>
                        </button>
                        <button type="submit" v-show="preview_mode" :disabled="button_disabled" class="btn btn-success">
                            <span v-if="!button_disabled">Salvar</span>
                            <span v-else>aguarde...</span>
                        </button>
                        <button type="submit" v-show="!preview_mode" :disabled="button_disabled" class="btn btn-primary">
                            <span v-if="!button_disabled">Verificar</span>
                            <span v-else>aguarde...</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</form>
</template>

<script>
    import VideoFormLink from "./VideoFormLink"
    import VideoFormPreview from "./VideoPreview"

    export default {
        name: 'VideoForm',
        components: {VideoFormLink, VideoFormPreview},
        data() {
            return {
                'preview_mode': false,
                'button_disabled': false,
                'preview_key': 0,
                'provider': null,
                'link': null,
            }
        },
        computed: {
            pk() {
                return this.$video_store.state.item.pk;
            }
        },
        updated() {},
        mounted() {
            this.$video_store.commit('addHook', {
                'type': 'after',
                'id': 'video.form.aftersave',
                'callback': () => {
                    window.jQuery('#video-form-modal').modal('hide');
                }
            });
            window.jQuery('#video-form-modal').on('hide.bs.modal', () => {
                this.closePreview();
            });
            window.jQuery('#video-form-modal').on('show.bs.modal', () => {
                this.closePreview(true);
            });

            this.closePreview();
        },
        methods: {
            setLink(link) {
                this.link = link;
            },
            closePreview() {
                this.preview_mode = false;
                this.button_disabled = false;
                this.preview_key += 1;
                this.provider = null;
            },
            openPreview() {
                this.preview_mode = true;
                this.button_disabled = false;

                if (this.link.includes('youtube')) {
                    this.provider = 'youtube';
                } else if (this.link.includes('vimeo')) {
                    this.provider = 'vimeo';
                } else {
                    this.provider = null;
                }
            },
            submit(e) {
                e.preventDefault();
                this.button_disabled = true;

                if (!this.preview_mode) {
                    this.openPreview();
                    return;
                }

                this.$video_store.dispatch('saveByLink', this.link);
            }
        },
    }
</script>