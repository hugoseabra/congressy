from .settings import WebpackLoader

LOADERS = {
    'VIDEOS': 'vue/videos/'
}


def get_frontend_loader(front_end_dir_path, debug_mode=True):
    frontend_loader = WebpackLoader(
        frontend_dir_path=front_end_dir_path,
        debug_mode=debug_mode,
    )

    for loader_name, bundle_dir_path in LOADERS.items():
        frontend_loader.add_loader(
            # to be used in template when loading files
            bundle_name=loader_name,
            # path where static files will be checked
            bundle_dir_path=bundle_dir_path,
        )

    return frontend_loader
