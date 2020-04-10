<template>
    <div class="row">
        <div class="col-md-12">

            <div class="row">
                <div class="col-md-12">

                    <div class="form-group">
                        <label style="margin-bottom:0 ">
                            Link do evento
                        </label>
                        <div class="input-group">
                        <span class="input-group-addon">
                            <span :class="'fab fa-' + provider + ' fa-3x'"></span>
                        </span>
                            <input type="text" name="link" :value="link"
                                   disabled required class="form-control">
                        </div>
                    </div>

                </div>
            </div>
            <div class="row" v-show="player_uri">
                <div class="col-md-12">
                    <h4 class="text-bold">Pré-visualização</h4>

                    <iframe :src="player_uri"
                            allowtransparency="true"
                            id="player"
                            frameborder="0"
                            width="100%"
                            height="320px"
                            sandbox="allow-scripts allow-presentation allow-same-origin"
                            allow="fullscreen; accelerometer; encrypted-media; gyroscope; picture-in-picture"
                            webkitallowfullscreen mozallowfullscreen
                            allowfullscreen></iframe>

                    <div v-show="show_loader" class="player-loader">
                        <div class="text-center"
                             style="height: 100px;margin-top:50px">
                            <i class="fas fa-circle-notch text-muted fa-spin fa-4x"></i>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        name: 'VideoFormPreview',
        props: {
            link: String,
            provider: String,
        },
        data() {
            return {
                'show_loader': true,
            }
        },
        computed: {
            player_uri() {
                let uri = null;
                if (this.link) {
                    uri = window.cgsy_environemnt.API_BASE_URL;
                    uri += `/v1/videos/player-preview/?link=${this.link}`;
                }
                return uri;
            }
        },
        mounted() {
            setTimeout(() => this.show_loader = false,2000);
        }
    }
</script>

<style scoped>
    input[name=link] {
        padding: 30px 10px;
        font-size: 18px
    }

    .player-loader {
        height: 300px;
        position: absolute;
        top: 0;
        left: 0;
        z-index: 100;
        width: 100%;
        padding-top: 100px;
    }
</style>