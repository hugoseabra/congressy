

class DataLineValidator(object):

    def __init__(self,
                 line: dict,
                 lot_pk: int,
                 extra_required_keys: dict) -> None:
        self.errors = {}
        self.valid = False
        super().__init__()

    def is_valid(self):
        # TODO implement clean logic here
        return self.valid

    def get_errors(self):
        return self.errors
