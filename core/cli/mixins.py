import sys

import inquirer


class CliInteractionMixin:

    def choice_list(self, name: str, question: str, choices: list,
                    default=None):
        questions = [
            inquirer.List(name,
                          carousel=True,
                          message=question,
                          default=default,
                          choices=choices, ),
        ]
        return inquirer.prompt(questions)

    def multi_choice_list(self, name: str, question: str, choices: list,
                          defaults: list = None):
        questions = [
            inquirer.Checkbox(name,
                              message=question,
                              default=defaults,
                              choices=choices, ),
        ]
        answers = inquirer.prompt(questions)
        from pprint import pprint
        pprint(answers)

    def confirmation_yesno(self, question, default=False, exit_on_false=True):
        reply = inquirer.confirm(question, default=default)

        if reply is False and exit_on_false is True:
            self.exit()

        return reply

    def question(self, question_text, default=None):
        questions = [
            inquirer.Text('question', message=question_text, default=default),
        ]
        answer = inquirer.prompt(questions)
        return answer['question']

    def exit(self):
        # noinspection PyUnresolvedReferences
        self.stdout.write(self.style.NOTICE("Exit!"))
        sys.exit(0)