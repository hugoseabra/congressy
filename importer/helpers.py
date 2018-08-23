from survey.models import Survey, Question
from .constants import KEY_MAP, REQUIRED_KEYS


class MappingNotFoundError(Exception):
    def __init__(self, key, *args: object, **kwargs: object) -> None:
        self.message = '{} not found'.format(key)
        self.key = key
        super().__init__(*args, **kwargs)


def get_mapping_from_csv_key(key):
    for map_key, mapping in KEY_MAP.items():
        if key in mapping['csv_keys']:
            return map_key, KEY_MAP[map_key]

    raise MappingNotFoundError(key)


def get_required_keys(form_config) -> list:
    found_keys = list()
    required_keys = list()

    required_keys.extend(REQUIRED_KEYS)

    form_config_keys = form_config.get_required_keys(form_config)
    required_keys.extend(
        x for x in form_config_keys if x not in required_keys)

    for key in required_keys:
        mapping = KEY_MAP.get(key, None)
        if mapping is None:
            raise MappingNotFoundError(key)
        found_keys.append(key)

    return found_keys


def get_keys_mapping_dict(form_config) -> list:
    keys_mapping = list()

    keys = KEY_MAP.keys()
    required_keys = get_required_keys(form_config)

    for key in keys:

        if key in required_keys:
            required = True
        else:
            required = False

        keys_mapping.append({
            'mapping': KEY_MAP.get(key),
            'required': required
        })

    return keys_mapping


def get_survey_questions(survey: Survey) -> list:
    questions = list()

    all_questions = Question.objects.filter(
        survey=survey,
    )

    for question in all_questions:
        questions.append(question)

    return questions
