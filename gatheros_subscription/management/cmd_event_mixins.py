from gatheros_event.models import Event


class CommandEventMixin:
    def _get_event(self, pk=None):
        event = None

        while not event:
            if not pk:
                self.stdout.write("\n")
                self.stdout.write("Informe o evento (ou encerre com Ctrl+c)")
                pk = input("Event PK: ")
                continue

            try:
                event = self.get_event_instance(pk)

                print()
                confirmed = self.confirmation_yesno(
                    'Confirmar evento encontrado?',
                    exit_on_false=False
                )

                if confirmed is False:
                    pk = None
                    event = None

            except Exception as e:
                self.stderr.write(str(e))
                pk = None
                event = None

        return event

    def get_event_instance(self, event_pk):
        try:
            event = Event.objects.get(pk=event_pk)

            self.stdout.write('----------------------------------------------')
            if len(event.name) > 30:
                self.stdout.write(
                    'EVENT: ' + self.style.SUCCESS(event.name[:30] + '...'))
            else:
                self.stdout.write('EVENT: ' + self.style.SUCCESS(event.name))

            org = event.organization

            if len(org.name) > 30:
                self.stdout.write(
                    'ORG: ' + self.style.SUCCESS(org.name[:30] + '...'))
            else:
                self.stdout.write('ORG: ' + self.style.SUCCESS(org.name))

            return event

        except Event.DoesNotExist as e:
            raise e
