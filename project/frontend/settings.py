import os


class WebpackLoaderConfig:
    def __init__(self,
                 bundle_name: str,
                 bundle_dir_path: str,
                 stats_file_path: str):
        self.bundle_name = bundle_name
        self.bundle_dir_path = bundle_dir_path.lstrip('/') + '/'
        self.stats_file_path = stats_file_path

        self.cache = False
        self.poll_internal = 0.1
        self.timeout = None
        self.ignore = [r'.+\.hot-update.js', r'.+\.map']

    def __iter__(self):
        iters = {
            self.bundle_name: {
                'CACHE': self.cache,
                'POLL_INTERVAL': self.poll_internal,
                'TIMEOUT': self.timeout,
                'IGNORE': self.ignore,
                'BUNDLE_DIR_NAME': self.bundle_dir_path,
                'STATS_FILE': self.stats_file_path,
            }
        }

        # now 'yield' through the items
        for x, y in iters.items():
            yield x, y


class WebpackLoader:
    def __init__(self, frontend_dir_path, debug_mode=True):
        self.frontend_dir_path = frontend_dir_path
        self.debug_mode = debug_mode
        self.loaders = list()
        self.loader_names = list()

    def add_loader(self, bundle_name: str, bundle_dir_path: str):
        alias = str(bundle_name).lower()

        if alias in self.loader_names:
            return

        config = WebpackLoaderConfig(
            bundle_name=bundle_name,
            bundle_dir_path=bundle_dir_path,
            stats_file_path=os.path.join(
                self.frontend_dir_path,
                'webpack-stats.{}.{}.json'.format(
                    alias,
                    'local' if self.debug_mode is True else 'prod'
                )
            )
        )
        config.cache = self.debug_mode is False
        self.loaders.append(config)
        self.loader_names.append(alias)

    def __iter__(self):
        iters = dict()

        for loader in self.loaders:
            iters.update(dict(loader))

        # now 'yield' through the items
        for x, y in iters.items():
            yield x, y
