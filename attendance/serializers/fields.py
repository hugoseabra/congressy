from rest_framework import serializers

REST_FRAMEWORK = {
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
}


class CheckinsField(serializers.Field):
    def to_representation(self, obj):

        checkins = []

        service_pk = self.context.get('attendance_service_pk')
        if not service_pk:
            raise Exception(
                'You must provide "attendance_service_pk" in Serializer'
                ' context.'
            )

        subs_checkins = obj.filter(attendance_service__pk=service_pk)
        subs_checkins = subs_checkins.order_by(
            'created_on',
            'attendance_service__name'
        )

        for checkin in subs_checkins:

            service = checkin.attendance_service

            try:
                checkout = checkin.checkout
                checkout = {
                    'id': checkout.pk,
                    'created_by': checkout.created_by,
                    'created_on': checkin.created_on.strftime(
                        '%d/%m/%Y %H:%M:%S'
                    ),
                }
            except AttributeError:
                checkout = None

            checkins.append({
                'id': checkin.pk,
                'attendance_name': service.name,
                'attendance_pk': service.pk,
                'created_by': checkin.created_by,
                'printed_on': checkin.printed_on.strftime(
                    '%d/%m/%Y %H:%M:%S'
                ) if checkin.printed_on else None,
                'created_on': checkin.created_on.strftime(
                    '%d/%m/%Y %H:%M:%S'
                ),
                'checkout': checkout
            })

        return checkins


class AttendedStatusField(serializers.Field):
    def to_internal_value(self, data):
        pass

    def to_representation(self, obj):
        service_pk = self.context.get('attendance_service_pk')
        if not service_pk:
            raise Exception(
                'You must provide "attendance_service_pk" in Serializer'
                ' context.'
            )

        checkin = obj.checkins.filter(attendance_service__pk=service_pk)

        if checkin.count() == 0:
            return False

        checkin = checkin.last()

        return not hasattr(checkin, 'checkout')
