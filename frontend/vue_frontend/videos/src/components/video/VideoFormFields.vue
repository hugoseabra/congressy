<template>
<form v-on:submit="submit" method="post">
    <div class="modal" id="video-form-fields-modal" role="dialog" data-backdrop="true">
        <div class="modal-dialog " role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                    <h4 class="modal-title">
                        Editar vídeo
                    </h4>
                </div>
                <div class="modal-body">

                    <div class="row">
                        <div class="col-md-12">
                            <div class="row">
                                <div class="col-md-12">

                                    asdf



                                </div>
                            </div>
                            <div class="row" v-show="pk">
                                <div class="col-md-12">
                                    <small class="text-muted" style="margin-left:10px;">
                                        <strong>ID:</strong> {{pk}}
                                    </small>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
                <div class="modal-footer">
                    <div class="text-right">
                        <button type="submit" class="btn btn-success">
                            <span v-if="!button_disabled">Salvar</span>
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
    export default {
        name: 'VideoFormField',
        data() {
            return {
                'button_disabled': false,
            }
        },
        computed: {
            pk() {
                return this.$video_store.state.item.pk;
            }
        },
        methods: {
            submit(e) {
                e.preventDefault();

            }
        },
    }
</script>