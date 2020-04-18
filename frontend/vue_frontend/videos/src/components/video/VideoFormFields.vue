<template>
<div>
    <form v-on:submit="submit" method="post">
    <h3 class="text-bold">
        <span v-if="item.pk">Editar</span>
        <span v-else>Adicionar</span>
        vídeo
    </h3>
    <hr />
    <div class="row">
        <div class="col-md-12">
            <div class="row">
                <div class="col-md-9">
                    <div class="form-group">
                        <label for="id_external_link" style="margin-bottom:0 ">
                            Link: <span style="color:#C9302C">*</span>
                        </label>
                        <div class="input-group date timepicker">
                            <span class="input-group-addon">
                                <span class="fab fa-youtube" v-if="provider === 'youtube'"></span>
                                <span class="fab fa-vimeo" v-else-if="provider === 'vimeo'"></span>
                                <span class="fas fa-video-camera" v-else></span>
                            </span>
                            <input type="text" disabled name="external_link" v-model="external_link" required="" maxlength="255" class="form-control" id="id_external_link">
                        </div>
                    </div>
                    <div class="clearfix"></div>
                </div>
                <div class="col-md-3">
                     <div class="form-group">
                        <label for="id_restrict">
                            Restrito:
                            <small>
                                <i class="fas fa-question-circle" data-toggle="tooltip" data-placement="right"
                                   title="Vídeo restrito a participantes com inscrição confirmada.
                                    Se desativado, todos poderão assistir o vídeo, incluindo pessoas não inscritas."></i>
                            </small>
                        </label>
                        <div>
                            <input type="checkbox" name="restrict" class="js-switch" id="id_restrict" v-model="restrict">
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-md-4">
            <img :src="thumbnail_large" class="img img-rounded" style="margin-left:10px;" />
        </div>
        <div class="col-md-8">

            <div class="row">
                <div class="col-md-12">
                    <div class="form-group" style="margin-top: 14px;">
                        <label for="id_name" style="margin-bottom:0 ">
                            Título: <span style="color:#C9302C">*</span>&ensp;
                            <small>
                                <i class="fas fa-question-circle" data-toggle="tooltip" data-placement="right" title="Título do vídeo a ser apresentado para o cliente."></i>
                            </small>
                        </label>
                        <input type="text" name="name" required="" maxlength="255" class="form-control" id="id_name" v-model="name">
                        <div class="clearfix"></div>
                    </div>
                    <div class="clearfix"></div>

                </div>
            </div>

            <div class="row" v-show="categories.length > 0">
                <div class="col-md-12">

                    <div class="form-group">
                        <label for="id_category" style="margin-bottom:0 ">
                            Categoria:
                            <small>
                                <i class="fas fa-question-circle" data-toggle="tooltip" data-placement="right" title="Assunto do vídeo."></i>
                            </small>
                        </label>

                        <select name="category" class="form-control" id="id_category" v-model="category_pk">
                            <option disabled value="">Escolha uma categoria</option>
                            <option>- Nenhuma -</option>
                            <option v-for="item in categories" :key="item.pk" :value="item.pk">{{ item.name }}</option>
                        </select>

                        <div class="clearfix"></div>
                    </div>

                </div>
            </div>

        </div>
    </div>
    <hr />
    <div class="row">
        <div class="col-md-12">
            <div class="form-group">
                <label for="id_description_html" style="margin-bottom:0 ">
                    Descrição:
                </label>
                <textarea name="description_html" id="id_description_html" class="form-control" rows="6" v-model="description_html"></textarea>
            </div>
        </div>
    </div>
    <hr />
    <div class="row">
        <div class="col-md-8">

            <div class="form-group">
                <label for="id_active">
                    Publicado:
                    <small>
                        <i class="fas fa-question-circle" data-toggle="tooltip" data-placement="right" title="Pessoas não podem acessar vídeos que não estejam publicados."></i>
                    </small>
                </label>
                <div>
                    <input type="checkbox" name="active" style="display:none" class="js-switch" id="id_active" v-model="active">
                </div>
            </div>

        </div>
        <div class="col-md-4">
            <div class="form-group">
                <label for="id_order">
                    Ordem:
                </label>
                <div>
                    <input type="number" name="order" class="form-control" id="id_order" v-model="order">
                </div>
            </div>
        </div>
    </div>

    <hr />
    <div class="row">
        <div class="col-md-12">
            <div class="form-group">
                <input type="checkbox" @change="show_schedule_dates" name="schedule_enabled" style="display:none" class="js-switch" id="id_schedule_enabled">
                <label for="id_schedule_enabled" style="margin-left:10px;margin-top:5px;">
                    Definir regras de pubicação:
                </label>
                <div class="help-block small">
                    Defina quando as pessoas poderão assistir o vídeo. Se desativado, o vídeo estará sempre disponível.
                </div>
            </div>
        </div>
    </div>

    <transition name="fade">
    <div class="row" v-show="schedule_enabled">
        <div class="col-md-12">
            <div style="margin-left:10px;font-weight: bold;font-size: large">Publicação</div>
            <br />
            <div class="row">
                <div class="col-md-6">
                    <div class="form-group">
                        <label for="id_starts_at_date" style="margin-bottom:0 ">
                            Inicia em:
                        </label>
                        <div class="input-group datapicker" style="margin-bottom:2px">
                            <input type="tel" class="form-control cgsy-date-input" placeholder="dd/mm/AAAA" name="starts_at_date" id="id_starts_at_date" maxlength="10" v-model="starts_at_date">
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                        </div>
                        <div class="input-group date timepicker">
                            <input type="tel" name="starts_at_time" class="form-control cgsy-time-input" placeholder="hh:mm" id="id_starts_at_time" maxlength="5" v-model="starts_at_time">
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-time"></span>
                            </span>
                        </div>
                        <div class="help-block small">
                            Pessoas só poderão assistir o vídeo somente a partir desta data e hora.
                        </div>
                        <div class="clearfix"></div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="form-group">
                        <label for="id_ends_at_date" style="margin-bottom:0 ">
                            Finaliza em:
                        </label>
                        <div class="input-group datapicker" style="margin-bottom:2px">
                            <input type="tel" class="form-control cgsy-date-input" placeholder="dd/mm/AAAA" name="ends_at_date" id="id_ends_at_date" maxlength="10" v-model="ends_at_date">
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                            </span>
                        </div>
                        <div class="input-group date timepicker">
                            <input type="tel" name="ends_at_time" class="form-control cgsy-time-input" placeholder="hh:mm" id="id_ends_at_time" maxlength="5" v-model="ends_at_time">
                            <span class="input-group-addon">
                                <span class="glyphicon glyphicon-time"></span>
                            </span>
                        </div>
                        <div class="help-block small">
                            Pessoas só poderão assistir o vídeo somente até esta data e hora.
                        </div>
                        <div class="clearfix"></div>
                    </div>
                </div>
            </div>

        </div>
    </div>
    </transition>
    <div class="row" v-show="item.pk">
        <div class="col-md-12">
            <small class="text-muted" style="margin-left:10px;">
                <strong>ID:</strong> {{item.pk}}
            </small>
        </div>
    </div>
    <hr />
    <div class="row">
        <div class="col-md-12 text-right">
            <small><a href="javascript:void(0)" @click="hideForm()" v-show="!button_disabled" style="margin-right:10px">Cancelar</a></small>
            <button class="btn btn-success" :disabled="button_disabled">
                <span class="fa fa-save"></span>&ensp;
                <span v-if="!button_disabled">Salvar</span>
                <span v-else>aguarde...</span>
            </button>
        </div>
    </div>

<!--    <hr />-->
<!--    <div class="row">-->
<!--        <div class="col-md-12">-->
<!--            <div class="form-group">-->
<!--                <input type="checkbox" name="add_playlists" style="display:none" class="js-switch" id="id_add_playlists">-->
<!--                <label for="id_add_playlists" style="margin-left:10px;margin-top:5px;">-->
<!--                    Adicionar a playlists:-->
<!--                </label>-->
<!--                <div class="help-block small">-->
<!--                    Adicione o vídeo a uma mais playlists para restringi-lo de acordo com ingressos.-->
<!--                </div>-->
<!--            </div>-->
<!--        </div>-->
<!--    </div>-->
    </form>
</div>

</template>

<script>
    export default {
        name: 'VideoFormField',
        props: {
            pk: String,
        },
        data() {
            return {
                'button_disabled': false,
                'schedule_enabled': false,
                'categories': this.$category_store.state.items.filter((i) => i.active === true),
                'item': {},

                'name': null,
                'provider': null,
                'thumbnail_large': null,
                'external_link': null,
                'description_html': null,
                'order': null,
                'active': false,
                'restrict': false,
                'category_pk': '',
                'starts_at_date': null,
                'starts_at_time': null,
                'ends_at_date': null,
                'ends_at_time': null,
            }
        },
        mounted() {
            this.$video_store.commit('selectItem', this.pk);
            this.item = this.$video_store.state.item;
            this.loadData();

            this.loadSwitchery();
            if (this.$category_store.state.items.length === 0) {
                this.$category_store.dispatch('fetchCollection');
            }
            this.button_disabled = false;
        },
        methods: {
            loadSwitchery() {
                window.setTimeout(() => {
                    window.app.switcheryToggle();
                }, 300);
                window.setTimeout(() => {
                    window.app.setSwitchery('input#id_restrict', this.restrict);
                    window.app.setSwitchery('input#id_active', this.active);
                    window.app.setSwitchery('input#id_schedule_enabled', (!this.ends_at_time) === false);
                }, 600);
            },
            show_schedule_dates() {
                this.schedule_enabled = !this.schedule_enabled;
            },
            hideForm() {
                this.$emit('hideForm');
            },
            loadData() {
                const strings = [
                    'name',
                    'provider',
                    'external_link',
                    'description_html',
                    'thumbnail_large',
                    'order',
                ]

                strings.forEach((f) => {
                    if (this.item.hasOwnProperty(f) && this.item[f]) {
                        this[f] = this.item[f];
                    } else {
                        this[f] = null;
                    }
                });

                if (this.item.category) {
                    this.category_pk = this.item.category.pk;
                } else {
                    this.category_pk = '';
                }

                this.restrict = this.item.restrict;
                this.active = this.item.active;
                this.starts_at_date = this.get_date(this.item.starts_at);
                this.starts_at_time = this.get_time(this.item.starts_at);
                this.ends_at_date = this.get_date(this.item.ends_at);
                this.ends_at_time = this.get_time(this.item.ends_at);

                this.loadSwitchery();
            },
            get_date(datetime) {
                if (!datetime) {
                    return;
                }

                if (!(datetime instanceof Date)) {
                    datetime = new Date(datetime);
                }

                const day = datetime.getDate().toString().padStart(2, '0');
                const month = (datetime.getMonth() + 1).toString().padStart(2, '0');
                const year = datetime.getFullYear();

                return `${day}/${month}/${year}`;
            },
            get_time(datetime) {
                if (!datetime) {
                    return;
                }
                if (!(datetime instanceof Date)) {
                    datetime = new Date(datetime);
                }
                const hours = datetime.getHours().toString().padStart(2, '0');
                const minutes = datetime.getMinutes().toString().padStart(2, '0');
                return `${hours}:${minutes}`;
            },
            getDateString(date_str, time_str) {
                if (!date_str || !time_str) {
                    return null;
                }
                const d_split = date_str.split('/');
                const time_split = time_str.split(':');

                const d = new Date(d_split[2], d_split[1]-1, d_split[0], time_split[0], time_split[1], 0);
                const tzo = -d.getTimezoneOffset();
                const dif = tzo >= 0 ? '+' : '-';
                const pad = (num) => {
                    const norm = Math.floor(Math.abs(num));
                    return (norm < 10 ? '0' : '') + norm;
                };
                return d.getFullYear() +
                        '-' + pad(d.getMonth() + 1) +
                        '-' + pad(d.getDate()) +
                        'T' + pad(d.getHours()) +
                        ':' + pad(d.getMinutes()) +
                        ':' + pad(d.getSeconds()) +
                        dif + pad(tzo / 60) +
                        ':' + pad(tzo % 60);
                
            },
            submit(e) {
                e.preventDefault();
                this.button_disabled = true;
                const data = {
                    'name': this.name,
                    'provider': this.provider,
                    'description_html': this.description_html,
                    'order': this.order,
                    'restrict': this.restrict,
                    'active': this.active,
                    'starts_at': this.getDateString(this.starts_at_date, this.starts_at_time),
                    'ends_at': this.getDateString(this.ends_at_date, this.ends_at_time),
                    'category': {
                        'pk': this.category_pk,
                    },
                }
                this.$video_store.commit('updateItem', data);
                this.$video_store.dispatch('save').then(() => {
                    this.$video_store.commit('resetItem');
                    this.$video_store.dispatch('fetchCollection').then(() => {
                        this.button_disabled = false;
                        this.hideForm();
                    });
                });
            }
        },
    }
</script>
<style scoped>
    .fade-enter-active, .fade-leave-active {
      transition: opacity .5s;
    }
    .fade-enter, .fade-leave-to /* .fade-leave-active em versões anteriores a 2.1.8 */ {
      opacity: 0;
    }
</style>