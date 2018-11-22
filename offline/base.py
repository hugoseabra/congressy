import django.apps


# noinspection PyProtectedMember,PyProtectedMember
class OfflineBase(object):
    models = None
    stdout = None
    style = None

    # noinspection PyUnusedLocal
    def __init__(self, *args, **kwargs) -> None:
        self.models = django.apps.apps.get_models()

        if 'stdout' in kwargs:
            self.stdout = kwargs.get('stdout')

        if 'style':
            self.style = kwargs.get('style')

    def get_model(self, label):

        m = None

        for model in self.models:
            model_label = str(model._meta.label)

            if model_label == label:
                m = model

        assert m is not None, "m is None for label {}".format(label)

        nl = str(m._meta.label)
        assert nl == label

        assert m is not None, "m is None for label {}".format(label)

        return m


# noinspection PyProtectedMember, PyUnresolvedReferences
class EraserMixin:
    erase_list = None

    def erase_all(self):

        assert self.erase_list is not None

        for label in self.erase_list:
            model = self.get_model(label)

            instances = model.objects.all()

            msg = 'Deleting {} from {}'.format(instances.count(),
                                               model._meta.label)

            if self.stdout and self.style:
                self.stdout.write(self.style.SUCCESS(
                    msg
                ))
            else:
                print(msg)

            instances.delete()

        return self


# noinspection PyProtectedMember,PyUnresolvedReferences
class FilterMixin:
    filter_dict = None

    def filter(self, event_pk):
        assert self.filter_dict is not None

        for label, criteria in self.filter_dict.items():
            model = self.get_model(label)

            exclude = {criteria: event_pk}

            instances = model.objects.all().exclude(**exclude)

            msg = 'Deleting {} from {}'.format(instances.count(),
                                               model._meta.label)

            if self.stdout and self.style:
                self.stdout.write(self.style.SUCCESS(
                    msg
                ))
            else:
                print(msg)

            instances.delete()

        return self
