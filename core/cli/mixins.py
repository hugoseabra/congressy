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

    @staticmethod
    def progress_bar(iteration, total, prefix='', suffix='', decimals=1,
                     length=100, fill='█'):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent
                                      complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(
            100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
        # Print New Line on Complete
        if iteration == total:
            print()

    def exit(self):
        # noinspection PyUnresolvedReferences
        self.stdout.write(self.style.NOTICE("Exit!"))
        sys.exit(0)
