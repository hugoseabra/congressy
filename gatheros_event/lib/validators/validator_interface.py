from abc import ABCMeta, abstractmethod


class ValidatorInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def normalize(self, data):
        raise Exception('Você deve de implementar clean_data()')

    @abstractmethod
    def is_valid(self, data):
        raise Exception('Você deve de implementar is_valid()')

    @abstractmethod
    def validate(self, data):
        raise Exception('Você deve de implementar validate()')
