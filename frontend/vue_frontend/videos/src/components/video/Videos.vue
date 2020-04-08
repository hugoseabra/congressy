<template>

<div class="row">
    <div class="col-md-12">

        <video-list />

    </div>
</div>




</template>

<script>
    import VideoList from './VideoList';

    export default {
        name: "Videos",
        components: {VideoList},
        mounted() {
            this.$category_store.dispatch('fetchCollection');
            this.$video_store.dispatch('fetchCollection');
        }
    }
</script>