from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import random as ran

author = 'Alla K.'

doc = """
A (second attempt) version of Disposition Game without using classes 
and with only a single asset trading so it is easier to program
"""


class Constants(BaseConstants):
    name_in_url = 'my_single_disposition'
    players_per_group = None
    num_rounds = 2
    # ------
    product_names = ['A']  # these are assets (called products using neutral language)
    num_products = len(product_names)
    probability_to_switch_state = 0.2
    probability_up_when_good_state = 0.7
    probability_down_when_bad_state = 0.7
    updown = [1, -1]
    probabilities_when_good = [probability_up_when_good_state, 1 - probability_up_when_good_state]
    probabilities_when_bad = [1 - probability_down_when_bad_state, probability_down_when_bad_state]
    increments = [c(5), c(10), c(15)]
    initial_price = c(100)
    endowment = c(150)


class Subsession(BaseSubsession):

    def creating_session(self):
        """
        set initial values on fields on players, groups, participants, or the subsession
        :return:
        """
        print('in creating_session:')
        print('\t in Round ', self.round_number, ':')
        # set initial values on group fields: states, market_prices, market_fluctuations
        for g in self.get_groups():
            # for the 1st round  only
            if self.round_number == 1:
                # go through all products and initialize their state and market price
                for prod in Constants.product_names:
                    if prod == 'A' or 'a':
                        g.product_A_state_is_good = True
                        g.product_A_market_price = Constants.initial_price
                    elif prod == 'B' or 'b':
                        g.product_B_state_is_good = True
                        g.product_B_market_price = Constants.initial_price
                    elif prod == 'C' or 'c':
                        g.product_C_state_is_good = True
                        g.product_C_market_price = Constants.initial_price
            else:
                # go through all products and update their state and market price
                for prod in Constants.product_names:
                    if prod == 'A' or 'a':
                        g.product_A_state_is_good = False
                        g.product_A_market_fluctuation = c(10)
                        g.product_A_market_price = Constants.initial_price + g.product_A_market_fluctuation
                    elif prod == 'B' or 'b':
                        g.product_B_state_is_good = False
                        g.product_B_market_fluctuation = c(15)
                        g.product_B_market_price = Constants.initial_price + g.product_B_market_fluctuation
                    elif prod == 'C' or 'c':
                        g.product_C_state_is_good = False
                        g.product_C_market_fluctuation = c(5)
                        g.product_C_market_price = Constants.initial_price + g.product_C_market_fluctuation

        # set initial values on player fields: owned, acquisition_prices
        for p in self.get_players():
            # for the 1st round  only
            if self.round_number == 1:
                p.cash = Constants.endowment
                # go through all products and initialize their state and market price
                for prod in Constants.product_names:
                    if prod == 'A' or 'a':
                        p.product_A_owned = 0
                        p.product_A_acquisition_price = None
                    elif prod == 'B' or 'b':
                        p.product_B_owned = 0
                        p.product_B_acquisition_price = Constants.initial_price + c(1)
                    elif prod == 'C' or 'c':
                        p.product_C_owned = 0
                        p.product_C_acquisition_price = Constants.initial_price + c(1)

            else:
                p_prior = p.in_round(self.round_number - 1)
                print('Player in prior round {} is {}'.format(self.round_number - 1, p_prior))
                p.cash = p_prior.cash
                print('  In round {} player has {} in cash'.format(self.round_number, p.cash))
                # go through all products and update their state and market price
                for prod in Constants.product_names:
                    if prod == 'A' or 'a':
                        p.product_A_owned = p_prior.product_A_owned
                        p.product_A_acquisition_price = p_prior.product_A_acquisition_price
                    elif prod == 'B' or 'b':
                        p.product_B_owned = 1
                        p.product_B_acquisition_price = c(230) + self.round_number
                    elif prod == 'C' or 'c':
                        p.product_C_owned = 1
                        p.product_C_acquisition_price = c(250) + self.round_number


class Group(BaseGroup):
    # states
    product_A_state_is_good = models.BooleanField()
    product_B_state_is_good = models.BooleanField()
    product_C_state_is_good = models.BooleanField()
    # market prices
    product_A_market_price = models.CurrencyField()
    product_B_market_price = models.CurrencyField()
    product_C_market_price = models.CurrencyField()
    # market fluctuations
    product_A_market_fluctuation = models.CurrencyField()
    product_B_market_fluctuation = models.CurrencyField()
    product_C_market_fluctuation = models.CurrencyField()


'''
    def vars_for_template(self):
        for prod in Constants.product_names:
            return {
                'state' + prod: 0,
                'market_price' + prod: 0,
                'fluctuation' + prod: 0,
            }
'''


class Player(BasePlayer):
    # cash
    cash = models.CurrencyField()

    # owned
    product_A_owned = models.IntegerField(blank=True
        # choices=[-1, 0, 1],
    )
    product_B_owned = models.IntegerField(
        # choices=[-1, 0, 1],
    )
    product_C_owned = models.IntegerField(
        # choices=[-1, 0, 1],
    )

    # acquisition prices
    product_A_acquisition_price = models.CurrencyField(blank=True)
    product_B_acquisition_price = models.CurrencyField(blank=True)
    product_C_acquisition_price = models.CurrencyField(blank=True)

    @staticmethod
    def update_acquisition_price(market_price):
        """
            for <<long>> BUY and for <<short>> SELL [owned becomes 1 and -1, resp.]
            sets acquisition price equal to market price; returns market price
        """
        return market_price

    @staticmethod
    def reset_acquisition_price():
        """
            for use when owned becomes 0
            resets acquisition price to None; returns None
        """
        return None

    @staticmethod
    def increment_owned(owned, count=0):
        """
            for BUY BUTTON
            increases owned by 1 if count is 0 (default)
            otherwise leaves it unchanged
            count should be used to control that only one unit can be bought per round
        """
        if count == 0:
            owned += 1
            count += 1

        return owned, count

    @staticmethod
    def decrement_owned(owned, count=0):
        """
            for SELL BUTTON
            decreases owned by 1 if count is 0 (default)
            otherwise leaves it unchanged
            count should be used to control that only one unit can be bought per round
        """
        if count == 0:
            owned -= 1
            count += 1

        return owned, count

    @staticmethod
    def decrease_cash(cash, price):
        """for BUY BUTTON: decreases cash by the amount of price"""
        return cash - price

    @staticmethod
    def increase_cash(cash, price):
        """for SELL BUTTON: increases cash by the amount of price"""
        return cash + price

    def on_click_buy_a(self):
        """
        Buy 1 unit product A:
            1) update acquisition price
            2) increase owned
            3) decrease cash
        :return:
        """
        print('In on_click_buy_a: ')
        g = self.group
        #  1) update acquisition price
        # acquisition_price = update_acquisition_price(g.product_A_market_price)
        acquisition_price = g.product_A_market_price
        print('acquisition_price is: {}, '.format(acquisition_price))
        print('self.product_A_acquisition_price is: {}, '.format(self.product_A_acquisition_price))

        #  2) increase owned
        # (owned, count) = increment_owned(self.product_A_owned)  # 'self.product_{}_owned'.format(A)
        if self.product_A_owned < 1:
            self.product_A_owned += 1
            print('incremented owned by 1, now own {} units of A'.format(self.product_A_owned))
        else:
            print('did NOT increment owned, already own {} units of A'.format(self.product_A_owned))
        # print('owned is: {}'.format(owned))
        print('self.product_A_owned is: {}, '.format(self.product_A_owned))
        # print('count is: {}'.format(count))
        #  3) decrease cash
        # self.cash = decrease_cash(self.cash, g.product_A_market_price)
        self.cash = self.cash - g.product_A_market_price
        print('self.cash is: {}, '.format(self.cash))
        return {
            'product_A_acquisition_price': acquisition_price,
            'product_A_owned': self.product_A_owned,  # owned,
            'cash': self.cash
        }

    def on_click_sell_a(self):
        """
        Buy 1 unit product A:
            1) update acquisition price
            2) increase owned
            3) decrease cash
        :return:
        """
        print('In on_click_sell_a: ')
        g = self.group
        #  1) update acquisition price
        # acquisition_price = update_acquisition_price(g.product_A_market_price)
        if self.product_A_owned == 0:
            acquisition_price = g.product_A_market_price
        elif self.product_A_owned == 1:
            acquisition_price = None
        else:
            print('Error in If: Number of units of product A is self.product_A_owned')
            acquisition_price = 0
        print('acquisition_price is: {}, '.format(acquisition_price))
        print('self.product_A_acquisition_price is: {}, '.format(self.product_A_acquisition_price))
        #  2) decrease owned
        # (owned, count) = decrement_owned('self.product_{}_owned'.format(A))
        if self.product_A_owned > -1:
            self.product_A_owned -= 1
            # owned = self.product_A_owned  # added 2 fix error BUT IS THIS NEEDED?!-used 4 print and return???
            print('decremented owned by 1, now own {} units of A'.format(self.product_A_owned))
        else:
            print('did NOT decrement owned, already own {} units of A'.format(self.product_A_owned))
        # print('owned is: {}'.format(owned))
        print('self.product_A_owned is: {}, '.format(self.product_A_owned))
        # print('count is: {}'.format(count))
        #  3) increase cash
        # self.cash = increase_cash(p.cash, 'g.product_{}_market_price'.format(A))
        ''' 
            Error: cannot add Currency(50) and string 'g.product_A_market_price' in:  
            self.cash = self.cash + 'g.product_{}_market_price'.format('A')
        '''
        self.cash = self.cash + g.product_A_market_price
        print('self.cash is: {}, '.format(self.cash))
        return{
            'product_A_acquisition_price': acquisition_price,
            'product_A_owned': self.product_A_owned,  # owned,
            'cash': self.cash,
        }


'''
    def on_click(self, order, product):
        # """
        Buy 1 unit product C:
            1) update acquisition price
            2) increase owned
            3) decrease cash
        Sell 1 unit product C:
            1) update acquisition price
            2) decrease owned
            3) increase cash
        :return:
        # """
        g = self.group
        #  1) update acquisition price

        acquisition_price = update_acquisition_price('g.product_{}_market_price'.format(product))

        if order == "Buy" or order == 'buy':
            #  2) increase owned
            (owned, count) = increment_owned('self.product_{}_owned'.format(product))
            #  3) decrease cash
            self.cash = decrease_cash(p.cash, 'g.product_{}_market_price'.format(product))
        elif order == "Sell" or order == 'sell':
            #  2) decrease owned
            (owned, count) = decrement_owned('self.product_{}_owned'.format(product))
            #  3) increase cash
            self.cash = increase_cash(p.cash, 'g.product_{}_market_price'.format(product))

        if product == 'A' or product == 'a':
            self.product_A_owned = owned
            self.product_A_acquisition_price = acquisition_price
        elif product == 'B' or product == 'b':
            self.product_B_owned = owned
            self.product_B_acquisition_price = acquisition_price
        elif product == 'C' or product == 'c':
            self.product_C_owned = owned
            self.product_C_acquisition_price = acquisition_price

        return acquisition_price, owned
'''

'''
    def set_owned(self, product, order): 'change value of owned for product A'
 
        if product == 'A' or 'a':

            if order == 'Buy' or 'buy':
                if self.product_A_owned < 1:
                    self.product_A_owned = self.product_A_owned + 1
                    print(order, ": holding increased by 1 to ", self.product_A_owned)
            elif order == 'Sell' or 'sell':
                if self.product_A_owned > -1:
                    self.product_A_owned = self.product_A_owned - 1
                    print(order, ": holding decreased by 1 to ", self.product_A_owned)
            else:
                print("ERROR: This is a dead branch of set_owned oTree")
                                                              
        if product == 'B' or 'b':

            if order == 'Buy' or 'buy':
                if self.product_B_owned < 1:
                    self.product_B_owned = self.product_B_owned + 1
                    print(order, ": holding increased by 1 to ", self.product_B_owned)
            elif order == 'Sell' or 'sell':
                if self.product_B_owned > -1:
                    self.product_B_owned = self.product_B_owned - 1
                    print(order, ": holding decreased by 1 to ", self.product_B_owned)
            else:
                print("ERROR: This is a dead branch of set_owned oTree")

        if product == 'C' or 'c':

            if order == 'Buy' or 'buy':
                if self.product_C_owned < 1:
                    self.product_C_owned = self.product_C_owned + 1
                    print(order, ": holding increased by 1 to ", self.product_C_owned)
            elif order == 'Sell' or 'sell':
                if self.product_C_owned > -1:
                    self.product_C_owned = self.product_C_owned - 1
                    print(order, ": holding decreased by 1 to ", self.product_C_owned)
            else:
                print("ERROR: This is a dead branch of set_owned oTree")


    def on_click_set_owned(self, name, order):
        print('in on_click_set_owned')
        self.player.set_owned(name, order)
        print('end of on_click_set_owned')
        
'''

'''
    def vars_for_template(self):
        for prod in Constants.product_names:
            return{
                'acquired_price' + prod: 0,
                'owned' + prod: 0,
            }
'''