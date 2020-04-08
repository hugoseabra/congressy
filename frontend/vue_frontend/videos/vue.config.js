const BundleTracker = require("webpack-bundle-tracker");

const pages = {
    "category_list": {
        entry: "./src/category.js",
        chunks: ["chunk-vendors"],
    },
    "video_list": {
        entry: "./src/video.js",
        chunks: ["chunk-vendors"],
    },
};

module.exports = {
    pages: pages,
    filenameHashing: true,
    productionSourceMap: false,
    outputDir: '../../static/vue/videos/',
    publicPath: (process.env.NODE_ENV !== 'production')
        ? 'http://localhost:8080/'
        : '',

    chainWebpack: config => {
        config.output.filename('js/[name].[hash:8].js');
        config.output.chunkFilename('js/[name].[hash:8].js');

        config.optimization.splitChunks({
            cacheGroups: {
                vendor: {
                    test: /[\\/]node_modules[\\/]/,
                    name: "chunk-vendors",
                    chunks: "all",
                    priority: 1
                },
            },
        });

        Object.keys(pages).forEach(page => {
            config.plugins.delete(`html-${page}`);
            config.plugins.delete(`preload-${page}`);
            config.plugins.delete(`prefetch-${page}`);
        });

        const stats_file_type = (process.env.NODE_ENV === 'production')
            ? 'prod' :
            'local';
        const stats_file = `../webpack-stats.videos.${stats_file_type}.json`;

        config.plugin('BundleTracker').use(BundleTracker, [{
            filename: stats_file
        }]);

        config.resolve.alias.set('__STATIC__', 'static');

        config.devServer
            .public('http://localhost:8080')
            .host('localhost')
            .port(8080)
            .hotOnly(true)
            .watchOptions({poll: 1000})
            .https(false)
            .headers({"Access-Control-Allow-Origin": ["*"]});

        config.module
            .rule('images')
            .use('url-loader')
            .loader('url-loader')
            .tap(options => Object.assign(options, {limit: 10240}))
    }
};
