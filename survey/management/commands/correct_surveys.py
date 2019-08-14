from django.core.management.base import BaseCommand
from django.db.models import Count, ObjectDoesNotExist
from django.db.transaction import atomic

from gatheros_subscription.models import Lot


class Command(BaseCommand):
    def handle(self, *args, **options):
        lots = Lot.objects.filter(
            event_survey_id__isnull=False,
        ).order_by('name')

        ev_surveys = list()

        # Resgata lotes cujos vínculos de formulários não sejam do mesmo evento
        # do lote, coletando evento de origem e qual evento de destino (novo
        # evento copiado a partir da origem)
        for l in lots:
            ev_survey = l.event_survey

            # Quanto não é o mesmo, o Lote é o correto (evento novo, copiado)
            # mas o survey não.
            if ev_survey.event_id != l.event_id:

                # Formulário do mesmo lote encontrado, lote do evento novo.
                # Só temos um survey por enquanto
                to_ev_survey = l.event.surveys.last()

                # Este formulário de evento (ev_survey) é o formulário errado.
                # Devemos achar o formulário correto
                ev_surveys.append({
                    'from_event': ev_survey.event,
                    'from_ev_survey': ev_survey,
                    'to_event': l.event,
                    'to_lot': l,
                    'to_ev_survey': to_ev_survey,
                })

        # EventSurveys coletados cujos lotes vinculados não estão com vínculos
        # corretos.
        for item in ev_surveys:
            from_event = item['from_event']
            to_event = item['to_event']

            to_lot = item['to_lot']

            print('Origem: {} ({})'.format(from_event.name, from_event.pk))
            print('  Para: {} ({})'.format(to_event.name, to_event.pk))


            # Vamos preparar o formulário errado para coletar autores e
            # respostas
            from_ev_survey = item['from_ev_survey']
            from_survey = from_ev_survey.survey

            to_ev_survey = item['to_ev_survey']
            to_survey = to_ev_survey.survey

            # Autores do evento de origem
            from_authors = from_survey.authors.annotate(
                num_answers=Count('answers')
            ).filter(
                num_answers__gt=0,
            ).order_by('user__first_name')

            print()
            print('= Autores a transferir')

            # Peristência de nome aguardando o próximo autor para registra-lo
            wait_for_next = list()

            authors_to_transfer = list()
            for a in from_authors:

                if not hasattr(a.user, 'person'):
                    # Não possui usuário mas autor possui inscrição que não é
                    # do evento de origem
                    if hasattr(a, 'subscription') \
                        and a.subscription.event_id == to_event.pk:
                        person = a.subscription.person
                        print(' >> {}: {}'.format(person.name, 1))
                        authors_to_transfer.append(a)

                    continue

                person = a.user.person
                subs_qs = person.subscriptions

                sub_to = subs_qs.filter(event_id=to_event.pk).exists()

                if not sub_to:
                    # Não existe inscrição no evento novo, então, nada a fazer
                    continue

                sub_origin = subs_qs.filter(event_id=from_event.pk).exists()

                if sub_to and not sub_origin:
                    # Se existe inscrição no evento novo e não existe no evento
                    # de origem, vamos transferi-la.
                    print(' > {}'.format(person.name))
                    authors_to_transfer.append(a)
                    continue

                if person.pk not in wait_for_next:
                    # Se há inscrição no novo evento, certamente há um outro
                    # autor. Vamos persistir para resgatar o novo autor
                    wait_for_next.append(person.pk)
                    continue

                # Se há inscrição no próximo e já é reincidência de autoria
                # aqui, vamos registrar
                print(' > {}'.format(person.name))
                authors_to_transfer.append(a)

            print()
            print('= Respostas')

            # Transferir respostas pra as perguntas do survey novo
            answers_to_transfer = list()
            for a in authors_to_transfer:

                # Aqui temos respostas do formulário do evento de origem
                # que possui vínculo do perguntas com o formulário de evento
                # de origem.
                #
                # Devemos vincular as respostas com perguntas to formulário
                # de evento novo e, somente depois, vincular o formulário de
                # evento com o lote correto.
                answers = a.answers.all()

                if a.user_id:
                    print(' > author: {} - respostas: {}'.format(
                        a.user.person.name,
                        answers.count(),
                    ))
                else:
                    sub = a.subscription
                    print(' > author: {} - respostas: {}'.format(
                        sub.person.name,
                        answers.count(),
                    ))

                for answer in answers:
                    # pergunta do formulário de origem (errada)
                    question = answer.question

                    try:
                        # pergunta do formulário do evento destino (correto)
                        to_question = to_survey.questions.get(
                            name=question.name,
                        )
                    except ObjectDoesNotExist:
                        # Se o formulário destino não possui a pergunta
                        # que existe no formulário de origem, vamos ignorar.
                        print('ignorando: {}'.format(question.name))
                        continue

                    answers_to_transfer.append({
                        'from_question': question,
                        'to_question': to_question,
                        'author': a,
                        'answer': answer,
                    })

            # with atomic():
            #     print()
            #     print('= Ajustando')
            #     for item in answers_to_transfer:
            #         answer = item['answer']
            #         old_question = answer.question
            #         to_question = item['to_question']
            #
            #         author = item['author']
            #         author.survey = to_survey
            #         author.save()
            #
            #         print(' > author: {} -> {}'.format(
            #             from_survey.pk,
            #             to_survey.pk,
            #         ))
            #
            #         answer.question = to_question
            #         answer.save()
            #
            #         print(' > question: {} -> {}'.format(
            #             old_question.pk,
            #             to_question.pk,
            #         ))
            #
            #     old_ev_survey = to_lot.event_survey
            #
            #     to_lot.event_survey = to_ev_survey
            #     to_lot.save()
            #
            #     print()
            #     print(' > survey: {} -> {}'.format(
            #         old_ev_survey.pk,
            #         to_ev_survey.pk,
            #     ))

            print()