class MixPanelOrganization:
    """
    Objeto de valor do MixPanel para dados da organização.
    """
    def __init__(self,
                 identity: str,
                 name: str,
                 num_members: str):
        self.identity = identity
        self.name = name
        self.num_members = num_members

        self.incremented_data = dict()

    def increment(self, key, value):
        self.incremented_data[key] = value

    def __iter__(self):
        iters = {
            'ID': self.identity,
            'Nome da organização': self.name,
            'Número de membros': self.num_members,
        }

        iters.update(self.incremented_data)

        # now 'yield' through the items
        for x, y in iters.items():
            yield x, y
