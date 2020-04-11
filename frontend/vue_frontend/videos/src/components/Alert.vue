<template>
<div :class="'alert alert-' + type">
    <div class="row">
        <div v-show="icon === true" class="col-xs-2 col-sm-2 col-md-1 text-center">
            <div v-show="type === 'warning'">
                <i v-if="intro" class="fas fa-exclamation-triangle warning-color fa-2x"></i>
                <i v-else class="fas fa-exclamation-triangle warning-color"></i>
            </div>
            <div v-show="type === 'danger'">
                <i v-if="intro" class="fas fa-exclamation-circle danger-color fa-2x"></i>
                <i v-else class="fas fa-exclamation-circle danger-color"></i>
            </div>
            <div v-show="type === 'info'">
                <i v-if="intro" class="fas fa-info-circle info-color fa-2x"></i>
                <i v-else class="fas fa-info-circle info-color"></i>
            </div>
            <div v-show="type === 'success'">
                <i v-if="intro" class="fas fa-check-circle success-color fa-2x"></i>
                <i v-else class="fas fa-check-circle success-color"></i>
            </div>
        </div>
        <div v-if="icon === true" class="col-xs-10 col-sm-10 col-md-11">
            <span v-show="intro" class="text-bold"><span v-html="intro"></span></span>
            <span v-html="msg"></span>
        </div>
        <div v-else class="col-md-12">
            <span v-show="intro" class="text-bold"><span v-html="intro"></span></span>
            <span v-html="msg"></span>
        </div>
    </div>
</div>
</template>

<script>
    export default {
        name: 'Alert',
        props: {
            type: {
                type: String,
                required: true
            },
            msg: {
                type: String,
                required: true
            },
            intro: String,
            icon: Boolean
        }
    }
</script>