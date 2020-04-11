<template>
<div class="row">
    <div class="col-md-12">
        <div class="row">
            <div class="col-md-12">
                <div class="form-group">
                    <label for="id_link" style="margin-bottom:0 ">
                        Link do evento
                    </label>
                    <div class="input-group">
                        <span class="input-group-addon">
                            <span class="glyphicon glyphicon-link"></span>
                        </span>
                        <input type="text" name="link" autofocus v-model="input_link" v-on:keyup="submitLink" required class="form-control" id="id_link">
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
</template>

<script>
    export default {
        name: 'VideoFormLink',
        props: {
            'link': String
        },
        data() {
            return {
                'input_link': null,
            }
        },
        mounted() {
            window.jQuery('#video-form-modal').on('show.bs.modal', () => {
                this.focus();
            });
            window.jQuery('#video-form-modal').on('hide.bs.modal', () => {
                this.input_link = null;
            });
            this.focus();
        },
        methods: {
            focus() {
                setTimeout(() => {
                    window.jQuery('#video-form-modal').find('input[autofocus]').focus();
                }, 500);
            },
            submitLink() {
                this.$emit('submitLink', this.input_link);
            }
        },
    }
</script>