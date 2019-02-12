class MixPanelEnvironment:
    """
    Objeto de valor do MixPanel para dados do ambiente.
    """
    def __init__(self, version: str):
        self.version = version

        self.incremented_data = dict()

    def increment(self, key, value):
        self.incremented_data[key] = value

    def __iter__(self):
        iters = {
            'versão do sistema': self.version,
        }

        iters.update(self.incremented_data)

        # now 'yield' through the items
        for x, y in iters.items():
            yield x, y
