import Vue from "vue/dist/vue.js"; // See note about import below
import CategoryGrid from "./components/category/CategoryGrid";
import category_store from "./store/category"
import messenger from "./store/messenger"
import CategoryForm from "./components/category/CategoryForm";

Vue.config.productionTip = false;
Vue.use(messenger);
Vue.use(category_store);

/* NOTE: in order to retrieve props from static HTML, we must instantiate Vue with
el/component style below instead of the render(h) -> h(MyWidget) / $mount syntax. However, doing so will
utilize a runtime build without the template compiler. To work around this, vue must be imported
from dist/vue/vue. Be careful about changing this import or the way vue is instantiated. */

new Vue({
    el: "#category-list",
    components: {CategoryGrid}
});
new Vue({
    el: "#category-form",
    components: {CategoryForm}
});

