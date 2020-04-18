<template>

    <div class="modal" id="video-player-modal" role="dialog" data-backdrop="true">
        <div class="modal-dialog " role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                    <h4 class="modal-title">
                        Visualizar vídeo
                    </h4>
                </div>
                <div class="modal-body">

                    <video-form-preview :key="link" :provider="provider" :link="link" />

                </div>
                <div class="modal-footer">
                    <div class="text-right">
                        <button type="button" class="btn btn-default" data-dismiss="modal">
                            Fechar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

</template>

<script>
    import VideoFormPreview from "./VideoPreview";

    export default {
        name: "VideoPlayer",
        components: {VideoFormPreview},
        computed: {
            provider() {
                return this.$video_store.state.player_provider;
            },
            link() {
                return this.$video_store.state.player_link;
            }
        },
        mounted() {
            window.jQuery('#video-player-modal').on('hide.bs.modal', () => {
                this.$video_store.commit('clearPlayer');
            });
        }
    }
</script>