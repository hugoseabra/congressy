
class CommandFileLogger:

    # noinspection PyMethodMayBeStatic
    def write_to_file(self, file_name: str, org_dict: dict):

        with open(file_name, 'w') as f:

            for key, item in org_dict.items():

                org = item['organization']

                org_headline = \
                    "Organization: {} \n" \
                    " Email: {}\n".format(
                        org.name,
                        self.get_org_email(
                            org),
                    )

                f.write(org_headline)
                if org.phone:
                    f.write(" Phone: {}\n\n".format(org.phone))
                else:
                    f.write("\n")

                if len(item['events']) > 0:
                    f.write('  Eventos: \n')

                    for i, event in enumerate(item['events']):

                        f.write("    {} (ID: {})\n".format(
                            event.name,
                            event.pk,
                        ))

                        if i == len(item['events']) - 1:
                            f.write("\n\n")

                else:
                    f.write('  Nenhum evento! \n')

    # noinspection PyMethodMayBeStatic
    def get_org_email(self, org):
        if org.email:
            return org.email

        return org.members.order_by('created').first().person.email
