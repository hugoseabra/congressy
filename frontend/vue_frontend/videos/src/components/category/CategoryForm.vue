<template>
<form v-on:submit="submit" method="post">
    <div class="modal" id="category-form-modal" role="dialog" data-backdrop="true">
        <div class="modal-dialog " role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                    <h4 class="modal-title">
                        <span v-if="!pk">Nova</span>
                        <span v-else>Editar</span>
                        categoria
                    </h4>
                </div>
                <div class="modal-body">

                    <alert v-for="err in errors" :key="err" :msg="err" type="danger" />

                    <div class="row">
                        <div class="col-md-12">
                            <div class="form-group">
                                <label for="id_name" style="margin-bottom:0 ">
                                    Nome <span style="color:#C9302C">*</span>
                                </label>
                                <input type="text" name="name" autofocus v-model="name" required="" maxlength="255" class="form-control" id="id_name">
                                <div class="clearfix"></div>
                            </div>
                            <div class="clearfix"></div>
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
                <div class="modal-footer">
                    <div class="text-right">
                        <button :disabled="button_disabled" type="submit" class="btn btn-success">
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
    import Alert from "../Alert"
    export default {
        name: 'CategoryForm',
        components: {Alert},
        data() {
            return {
                'errors': [],
                'button_disabled': false,
                'input_name': null,
            }
        },
        computed: {
            name: {
                get() {
                    return this.$category_store.state.item.name;
                },
                set(value) {
                    this.input_name = value;
                }
            },
            pk() {
                return this.$category_store.state.item.pk;
            }
        },
        updated() {
            this.input_name = this.name;
        },
        mounted() {
            this.$category_store.commit('addHook', {
                'type': 'after',
                'id': 'category.form.aftersave',
                'callback': () => {
                    window.jQuery('#category-form-modal').modal('hide');
                    this.button_disabled = false;
                }
            });
            window.jQuery('#category-form-modal').on('hidden.bs.modal', () => {
                this.$category_store.commit('resetItem');
            });
            window.jQuery('#category-form-modal').on('show.bs.modal', () => {
                setTimeout(() => {
                    window.jQuery('#category-form-modal').find('input[autofocus]').focus();
                }, 300);
            });
        },
        methods: {
            submit(e) {
                e.preventDefault();
                this.button_disabled = true;
                this.$category_store.commit('updateItem', {
                    'name': this.input_name
                });
                this.$category_store.dispatch('save');
            }
        },
    }
</script>
