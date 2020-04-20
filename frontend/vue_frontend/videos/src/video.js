import Vue from "vue/dist/vue.js"; // See note about import below
import "./filters"
import messenger from "./store/messenger"

import project_store from "./store/project"
import category_store from "./store/category"
import video_store from "./store/video"

import Videos from "./components/video/Videos";
import VideoForm from "./components/video/VideoForm";
import VideoPlayer from "./components/video/VideoPlayer";

Vue.config.productionTip = false;
Vue.use(messenger);
Vue.use(project_store);
Vue.use(category_store);
Vue.use(video_store);

/* NOTE: in order to retrieve props from static HTML, we must instantiate Vue with
el/component style below instead of the render(h) -> h(MyWidget) / $mount syntax. However, doing so will
utilize a runtime build without the template compiler. To work around this, vue must be imported
from dist/vue/vue. Be careful about changing this import or the way vue is instantiated. */

new Vue({
    el: "#video-list",
    components: {Videos}
});
new Vue({
    el: "#video-link-form",
    components: {VideoForm}
});
new Vue({
    el: "#video-player",
    components: {VideoPlayer}
});