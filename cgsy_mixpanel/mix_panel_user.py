class MixPanelUser:
    """
    Objeto de valor do MixPanel para dados do usuário.
    """

    def __init__(self,
                 identity: str,
                 name: str,
                 email: str,
                 age: str,
                 gender: str,
                 city_name: str,
                 state_name: str,
                 country_name: str):
        self.identity = identity
        self.name = name
        self.email = email
        self.age = age
        self.gender = gender
        self.city_name = city_name
        self.state_name = state_name
        self.country_name = country_name

        self.incremented_data = dict()

    def increment(self, key, value):
        self.incremented_data[key] = value

    def _get_age_range(self):

        if not self.age:
            return 'Não identificado'

        age_ranges = {
            'Abaixo de 13 anos': (1, 12),
            '13 a 17 anos': (13, 17),
            '18 a 25 anos': (18, 25),
            '26 a 30 anos': (26, 30),
            '31 a 40 anos': (31, 40),
            '41 a 50 anos': (41, 50),
            '51 a 60 anos': (51, 60),
            '61 a 70 anos': (61, 70),
            '71 a 80 anos': (71, 80),
            '81 a 90 anos': (81, 90),
            '91 a 100 anos': (91, 100),
        }

        for range, age_range in age_ranges.items():
            min = age_range[0]
            max = age_range[1]

            if min <= self.age <= max:
                return range

        return 'Não identificado'

    def __iter__(self):
        names = self.name.split(' ')

        iters = {
            'ID': self.identity,
            '$name': self.name,
            '$email': self.email,
            '$city': self.city_name,
            'age': self.age,
            'Faixa Etária': self._get_age_range(),
            'Sexo': self.gender,
            '$region': self.state_name,
            '$country_code': self.country_name.upper(),
        }

        iters.update(self.incremented_data)

        # now 'yield' through the items
        for x, y in iters.items():
            yield x, y
