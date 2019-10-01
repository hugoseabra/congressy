from rest_framework import serializers

from installment.serializers import PartSerializer
from payment.helpers.pagarme_acquire_reponse_code import get_acquire_response
from payment.models import Transaction
from .transaction_status import TransactionStatusSerializer


class TransactionSerializer(serializers.ModelSerializer):
    part = PartSerializer()

    status_history = TransactionStatusSerializer(
        source="statuses",
        many=True,
        read_only=True
    )

    boleto_digits = serializers.SerializerMethodField()
    card_brand = serializers.SerializerMethodField()
    acquirer_name = serializers.SerializerMethodField()
    acquirer_response_code = serializers.SerializerMethodField()
    acquirer_response = serializers.SerializerMethodField()
    status_reason = serializers.SerializerMethodField()
    refuse_reason = serializers.SerializerMethodField()
    risk_level = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        exclude = ('data', 'lot',)

    def __init__(self, *args, **kwargs):
        self.last_status = None
        super().__init__(*args, **kwargs)

    def _get_last_status(self, obj):
        if not self.last_status and obj.statuses.count() > 0:
            self.last_status = obj.statuses.last()

        return self.last_status

    def get_boleto_digits(self, obj):
        last = self._get_last_status(obj)

        if not last:
            return None

        return last.data.get('transaction[boleto_barcode]') or None

    def get_card_brand(self, obj):
        last = self._get_last_status(obj)

        if not last:
            return None
        return last.data.get('transaction[card][brand]') or None

    def get_acquirer_name(self, obj):
        last = self._get_last_status(obj)

        if not last:
            return None

        return last.data.get('transaction[acquirer_name]') or None

    def get_acquirer_response_code(self, obj):
        last = self._get_last_status(obj)

        if not last:
            return None

        return last.data.get('transaction[acquirer_response_code]') or None

    def get_acquirer_response(self, obj):
        last = self._get_last_status(obj)

        if not last:
            return None

        pagarme_trans_id = last.data.get('transaction[id]')
        code = last.data.get('transaction[acquirer_response_code]')
        if not code:
            return None

        return get_acquire_response(pagarme_trans_id, code)

    def get_status_reason(self, obj):
        last = self._get_last_status(obj)

        if not last:
            return None

        return last.data.get('transaction[status_reason]') or None

    def get_refuse_reason(self, obj):
        last = self._get_last_status(obj)

        if not last:
            return None

        return last.data.get('transaction[refuse_reason]') or None

    def get_risk_level(self, obj):
        last = self._get_last_status(obj)

        if not last:
            return None

        return last.data.get('transaction[risk_level]') or None
