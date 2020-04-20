<template>

<div class="row">
    <div class="col-md-12">
        <transition name="fade" @before-enter="hideList()" @after-leave="showList()">
            <video-form-fields :key="pk" :pk="pk" v-on:hideForm="hideForm" v-show="show_form" />
        </transition>
        <transition name="fade" @before-enter="hideForm()">
            <video-list :key="list_key" v-on:showForm="showForm" v-show="show_list" />
        </transition>
    </div>
</div>

</template>

<script>
    import VideoList from './VideoList';
    import VideoFormFields from './VideoFormFields';

    export default {
        name: "Videos",
        components: {VideoList, VideoFormFields},
        data() {
            return {
                'pk': null,
                'list_key': 1,
                'show_form': false,
                'show_list': true,
            }
        },
        mounted() {
            this.$category_store.dispatch('fetchCollection');
            this.$video_store.dispatch('fetchCollection');
        },
        methods: {
            showList() {
                this.list_key += 1;
                this.show_list = true;
                window.jQuery('#add-video-button').show();
            },
            hideList() {
                this.show_list = false;
                window.jQuery('#add-video-button').hide();
            },
            showForm() {
                this.show_form = true;
                this.pk = this.$video_store.state.item.pk;
                window.jQuery('#add-video-button').hide();
            },
            hideForm() {
                this.show_form = false;
                window.jQuery('#add-video-button').show();
            },
        }
    }
</script>
<style scoped>
    .fade-enter-active {
      transition: opacity .5s;
    }
    .fade-enter, .fade-leave-to /* .fade-leave-active em versões anteriores a 2.1.8 */ {
      opacity: 0;
    }
</style>