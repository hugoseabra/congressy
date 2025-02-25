from .base import DataCleanerBase, EraserMixin


class MixBoletoDataCleaner(DataCleanerBase, EraserMixin):

    erase_list = [
        'mix_boleto.SyncSubscription',
        'mix_boleto.SyncBoleto',
        'mix_boleto.MixBoleto',
        'mix_boleto.SyncCategory',
        'mix_boleto.SyncResource',
    ]
