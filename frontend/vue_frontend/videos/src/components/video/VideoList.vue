<template>

<div class="row">
    <div class="col-md-12">

        <video-list-item v-on:showForm="showForm" v-for="item in items" :key="item.pk" :video_id="item.pk" />

    </div>
</div>




</template>

<script>
    import VideoListItem from './VideoListItem';

    export default {
        name: "VideoList",
        components: {VideoListItem},
        computed: {
            items() {
                return this.$video_store.state.items;
            }
        },
        mounted() {
            this.showAddVideoButton();
        },
        methods: {
            showForm() {
                this.$emit('showForm');
            },
            showAddVideoButton() {
                window.jQuery('#add-video-button').show();
            }
        }
    }
</script>

<style scoped>

</style>