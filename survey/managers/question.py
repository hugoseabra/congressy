"""
Manager é a definição centralizada de manipulação de um Model. Ou seja,
a intenção é que ele seja um serviço de domínio (Domain Service) responsável
por:
- Salvar model com suas devidas validações (premissas e restrições);
- Exigir a preexistência de objetos de dependência;
"""

from django.utils.text import slugify

from survey.managers import Manager
from survey.models import Question


class QuestionManager(Manager):
    """ Manager """

    class Meta:
        """ Meta """
        model = Question
        fields = '__all__'

    def clean_name(self):
        """
        Slugify deve garantir que o nome de Question em um survey seja único.
        """
        name = self.cleaned_data.get('name')
        survey = self.cleaned_data.get('survey')

        original_slug = slugify(name)
        exists = Question.objects.filter(
            name=original_slug,
            survey=survey
        ).exists()

        slug = original_slug
        counter = 1

        while exists:
            query_set = Question.objects.filter(name=slug, survey=survey)
            exists = query_set.exists()
            if exists:
                slug = original_slug + '-' + str(counter)
                counter += 1

        return slug
