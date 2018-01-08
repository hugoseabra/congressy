from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import DetailView
from django.urls import reverse
from django.contrib import messages

from django.core.exceptions import ValidationError
from gatheros_event.forms import ProfileCreateForm
from gatheros_event.models import Event, Info, Person
from gatheros_subscription.models import Lot, Subscription


class HotsiteView(DetailView):
    # @TODO Use slug instead of PK to find event
    model = Event
    template_name = 'hotsite/base.html'
    form_template = 'hotsite/form.html'

    def get_context_data(self, **kwargs):
        context = super(HotsiteView, self).get_context_data(**kwargs)
        context['status'] = self._get_status()
        context['report'] = self._get_report()
        context['period'] = self._get_period()
        context['info'] = Info.objects.get(pk=self.object.pk)
        return context

    def _get_status(self):
        """ Resgata o status. """
        now = datetime.now()
        event = self.object
        remaining = self._get_remaining_datetime()
        remaining_str = self._get_remaining_days(date=remaining)

        result = {
            'published': event.published,
        }

        future = event.date_start > now
        running = event.date_start <= now <= event.date_end
        finished = now >= event.date_end

        if future:
            result.update({
                'status': 'future',
                'remaining': remaining_str,
            })

        elif running:
            result.update({
                'status': 'running',
            })

        elif finished:
            result.update({
                'status': 'finished' if event.published else 'expired',
            })

        return result

    def _get_remaining_datetime(self):
        """ Resgata diferença de tempo que falta para o evento finalizar. """
        now = datetime.now()
        return self.object.date_start - now

    def _get_remaining_days(self, date=None):
        """ Resgata tempo que falta para o evento finalizar em dias. """
        now = datetime.now()

        if not date:
            date = self._get_remaining_datetime()

        remaining = ''

        days = date.days
        if days > 0:
            remaining += str(date.days) + 'dias '

        remaining += str(int(date.seconds / 3600)) + 'h '
        remaining += str(60 - now.minute) + 'm'

        return remaining

    def _get_report(self):
        """ Resgata informações gerais do evento. """
        return self.object.get_report()

    def _get_period(self):
        """ Resgata o prazo de duração do evento. """
        return self.object.get_period()

    def post(self, request, *args, **kwargs):

        self.object = Event.objects.get(pk=kwargs['pk'])

        # Test if its soft post or hard post:
        # Soft post contains only 3 itens in the post:
        # name, email, csrftoken
        # hard post has  itens

        post_size = len(self.request.POST)

        if post_size <= 3:
            # soft post: we only have an email and a name

            # test if we have a person.
            email = self.request.POST.get('email')
            user = self.request.user
            try:
                person = Person.objects.get(email=email)

                if not user.is_authenticated:
                    messages.error(request, 'Faça login para continuar.')
                    return HttpResponseRedirect(reverse('front:login'))

                lot = Lot.objects.get(event=self.object)

                subscription = Subscription(person=person, lot=lot, created_by=user.id)

                try:
                    subscription.save()
                except ValidationError as e:
                    return HttpResponse('an error ocorred and prevented the subscription' + e.message)
                return HttpResponse('success')

            except Person.DoesNotExist:
                return HttpResponseRedirect(reverse('public:profile_create'))







            context = super(HotsiteView, self).get_context_data(**kwargs)
            context['status'] = self._get_status()
            context['report'] = self._get_report()
            context['period'] = self._get_period()
            context['info'] = Info.objects.get(pk=self.object.pk)
            return render(self.request, template_name=self.form_template, context=context)
        elif post_size > 3:
            # hard post
            pass
        else:
            # I dont know why this would happen but just render the inital event page anyway
            pass


        # name = self.request.POST.get('name')
        # if


        #
        # # Testing if we have a user.
        #
        # if request.user.is_authenticated:
        #     user = self.request.user
        #
        # else:
        #
        #     # Test if we have a
        #
        #     # Test if we have a person.
        #     # Every user has a person, but not every person has a user.
        #     # If person:
        #     # login()
        #     # else:
        #     # register()
        #
        #     # try:
        #     #
        #     # except:
        #     #     pass
        #
        #     return HttpResponseRedirect(reverse('front:login'))
        #
        #     # Test if user is already registered in the event
        #
        #     print('asdasd')

        #
        #
        #
        # if user:
        #     return HttpResponse('user')
        #     # We have a user. Find the person.
        #     # try:
        #     #     person =
        #
        # else:
        #     return HttpResponse('no user')
        # #
        # if self.request.POST.get('name') or self.request.POST.get('email'):
        #
        #
        #
        #     # if user:
        #         # If user is logged in, create inscription
        #         # If user is not logged in, check if he already has a user, if so, ask for a login.
        #         # If user is not logged in, check if he already has a user, if not, send him to a create page.
        #     # else if not user:
        #         # Redirect to create user then redirect to event:inscription_status page.
        #
        #     # Always redirect back to the event:inscription_status page.
        #
        #     name = self.request.POST.get('name')
        #     email = self.request.POST.get('email')
        #
        #     form = ProfileCreateForm(data={"name": name, "email": email})
        #     validated_form = form.is_valid()
        #
        #
        #
        #     try:
        #         found_person = Person.objects.get(email=email)
        #     except Person.DoesNotExist:
        #         pass
        #
        #
        #
        #     if validated_form:
        #         form.save()
        #     else:
        #         # Add the event to the session.
        #         self.request.session['signing_up_for'] = kwargs['pk']
        #         errors = form.errors.as_data()
        #         for _, error_list in errors.items():
        #             for error in error_list:
        #                 print(error.message)
        #                 if error.message == "Esse email já existe em nosso sistema. Tente novamente.":
        #                     # Tell inform the user that he already has an account and must login in.
        #                     return HttpResponseRedirect(reverse('front:login'))
        #                     print('er')
        #             """ START HERE"""
        #     person = Person.objects.get(email=email)
        #
        #     object_pk = kwargs['pk']
        #
        #     obj = Event.objects.get(pk=object_pk)
        #     info = Info.objects.get(pk=object_pk)
        #
        #     period = obj.get_period()
        #     return render(request, self.template_name, {"name": name,
        #                                                 "email": email,
        #                                                 "object": obj,
        #                                                 "info": info,
        #                                                 "peron": person,
        #                                                 "period": period,
        #                                                 })


class HotsiteFormView(DetailView):
    template_name = 'hotsite/form.html'
    form = ProfileCreateForm
    model = Event



    def post(self, request, *args, **kwargs):

        # Testing if we have a user.

        if request.user.is_authenticated:
            user = self.request.user

        else:

            # Test if we have a


            # Test if we have a person.
            # Every user has a person, but not every person has a user.
            # If person:
                # login()
            # else:
                # register()

            # try:
            #
            # except:
            #     pass

            return HttpResponseRedirect(reverse('front:login'))

            # Test if user is already registered in the event

            print('asdasd')


        #
        #
        #
        # if user:
        #     return HttpResponse('user')
        #     # We have a user. Find the person.
        #     # try:
        #     #     person =
        #
        # else:
        #     return HttpResponse('no user')
        # #
        # if self.request.POST.get('name') or self.request.POST.get('email'):
        #
        #
        #
        #     # if user:
        #         # If user is logged in, create inscription
        #         # If user is not logged in, check if he already has a user, if so, ask for a login.
        #         # If user is not logged in, check if he already has a user, if not, send him to a create page.
        #     # else if not user:
        #         # Redirect to create user then redirect to event:inscription_status page.
        #
        #     # Always redirect back to the event:inscription_status page.
        #
        #     name = self.request.POST.get('name')
        #     email = self.request.POST.get('email')
        #
        #     form = ProfileCreateForm(data={"name": name, "email": email})
        #     validated_form = form.is_valid()
        #
        #
        #
        #     try:
        #         found_person = Person.objects.get(email=email)
        #     except Person.DoesNotExist:
        #         pass
        #
        #
        #
        #     if validated_form:
        #         form.save()
        #     else:
        #         # Add the event to the session.
        #         self.request.session['signing_up_for'] = kwargs['pk']
        #         errors = form.errors.as_data()
        #         for _, error_list in errors.items():
        #             for error in error_list:
        #                 print(error.message)
        #                 if error.message == "Esse email já existe em nosso sistema. Tente novamente.":
        #                     # Tell inform the user that he already has an account and must login in.
        #                     return HttpResponseRedirect(reverse('front:login'))
        #                     print('er')
        #             """ START HERE"""
        #     person = Person.objects.get(email=email)
        #
        #     object_pk = kwargs['pk']
        #
        #     obj = Event.objects.get(pk=object_pk)
        #     info = Info.objects.get(pk=object_pk)
        #
        #     period = obj.get_period()
        #     return render(request, self.template_name, {"name": name,
        #                                                 "email": email,
        #                                                 "object": obj,
        #                                                 "info": info,
        #                                                 "peron": person,
        #                                                 "period": period,
        #                                                 })
