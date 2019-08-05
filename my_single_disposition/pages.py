from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class MyPage(Page):
    pass


class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(self):
        pass


class Results(Page):
    pass


class Trading(Page):

    form_model = 'player'

    def get_form_fields(self):

        # to check if the field left blank
        if self.player.product_A_owned is None:
            if self.player.product_A_acquisition_price is not None:
                return[
                    'cash',
                    " ".join(['product_{}_acquisition_price'.format(prod1) for prod1 in Constants.product_names])
                ]
            elif self.player.product_A_acquisition_price is None:
                return ['cash']
        elif self.player.product_A_acquisition_price is None:
            return [
                'cash',
                " ".join(['product_{}_owned'.format(prod) for prod in Constants.product_names])
            ]
        else:
            return [
                'cash',
                " ".join(['product_{}_owned'.format(prod) for prod in Constants.product_names]),
                " ".join(['product_{}_acquisition_price'.format(prod1) for prod1 in Constants.product_names])
            ]

    '''def vars_for_template(self):
        l = len(Constants.product_names)
        if l == 1:
            return [cash]
    '''


page_sequence = [
    MyPage,
    Trading,
    ResultsWaitPage,
    Results
]
