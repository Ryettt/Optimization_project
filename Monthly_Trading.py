from Monthly_Optimization import *

'''This file contains two trading classes related to the two optimization models.'''

bond_purchase_days = [datetime.datetime(2018, 1, 2),
                      datetime.datetime(2018, 7, 2),
                      datetime.datetime(2019, 1, 2),
                      datetime.datetime(2019, 7, 1)]

bond_mature_days = [datetime.datetime(2018, 6, 29),
                    datetime.datetime(2018, 12, 31),
                    datetime.datetime(2019, 6, 28),
                    datetime.datetime(2019, 12, 31)]


# For problem 2b
class Markowitz_Monthly_Trading:

    def __init__(self, bond_purchase_days, bond_mature_days, data_estimator):
        self.bond_purchase_days = bond_purchase_days
        self.bond_mature_days = bond_mature_days
        self.data_estimator = data_estimator
        self.open_monthly_data = self.data_estimator.get_trading_open_monthly_data()
        self.close_monthly_data = self.data_estimator.get_trading_close_monthly_data()
        self.buy_trading_dates = list(self.open_monthly_data.index)
        self.sell_trading_dates = list(self.close_monthly_data.index)

        self.freecash = pd.DataFrame(index = self.buy_trading_dates,
                                     columns = ['dollar'])
        self.freecash.iloc[0, 0] = 100000  # initial value=100000
        # append the end date
        self.freecash.loc[self.bond_mature_days[-1]] = 0
        self.portfolio_weight = pd.DataFrame(index = self.buy_trading_dates,
                                             columns = list(self.open_monthly_data.columns) + ['cash', 'bond'])
        self.portfolio_lot = pd.DataFrame(index = self.buy_trading_dates,
                                          columns = list(self.open_monthly_data.columns) + ['cash', 'bond'])
        self.bond_semiannual_return = 0.03 / 6
        self.cash_monthly_return = 0.005 / 100 * 30

    def get_all_related_trading_data(self):
        related_traing_data = pd.concat([self.open_monthly_data, self.close_monthly_data]).sort_index()
        self.all_trading_dates = list(related_traing_data.index)

    def Markowitz_trading(self, Monthly_optimization_Markowitz):
        # get all the buy and sell date(have already sorted)
        self.get_all_related_trading_data()

        for date in self.all_trading_dates:

            # At buy trading date: to optimize and record the weights and lots of the assets
            if date in self.buy_trading_dates:
                opt = Monthly_optimization_Markowitz(self.data_estimator, date)
                # buy at open price
                buy_price = (self.open_monthly_data.loc[date, :]).copy(deep = True)
                # could buy at any amount,price = 1
                buy_price['cash'] = 1
                buy_price['bond'] = 1

                if date in self.bond_purchase_days:
                    # add bond to optimize the portfolio
                    w = opt.markovitz_risky_cash_bond()
                    self.portfolio_weight.loc[date, :] = w.loc[date, :].values

                    self.portfolio_lot.loc[date, :] = self.freecash.loc[date][0] * np.array(
                        self.portfolio_weight.loc[date, :]) / np.array(buy_price)
                else:
                    # exclude bond to optimize
                    w = opt.markovitz_risky_cash()
                    self.portfolio_weight.loc[date, :'cash'] = w.loc[date, :].values
                    self.portfolio_weight.loc[date, 'bond'] = 0
                    self.portfolio_lot.loc[date, :'cash'] = self.freecash.loc[date][0] * np.array(
                        self.portfolio_weight.loc[date, :'cash']) / np.array(buy_price[:-1])
                    # the lot for bond just the same before its mature day
                    self.portfolio_lot.loc[date, 'bond'] = self.portfolio_lot.loc[
                        self.portfolio_lot.index[list(self.portfolio_lot.index).index(date) - 1], 'bond']

            # At sell trading date: to sell the available assets and record the free cash of the portfolio
            elif date in self.sell_trading_dates:
                # last trading date is buy trading date, use the index to get the portfolio lot
                last_trading_date = self.all_trading_dates[self.all_trading_dates.index(date) - 1]
                # sell at close price
                sell_price = (self.close_monthly_data.loc[date, :]).copy(deep = True)
                sell_price['cash'] = 1 * self.cash_monthly_return

                if date in self.bond_mature_days:
                    # sell all the stocks, cash and bond
                    # the bond price is:
                    sell_price['bond'] = 1 * (1 + self.bond_semiannual_return)
                    freecash = sum(np.array(self.portfolio_lot.loc[last_trading_date, :]) * np.array(sell_price))
                    # free cash put in the next trading day:ie buy trading date
                    if date != bond_mature_days[-1]:
                        self.freecash.loc[
                            self.all_trading_dates[self.all_trading_dates.index(date) + 1], 'dollar'] = freecash
                    else:
                        self.freecash.iloc[-1, 0] = freecash
                else:
                    # not bond mature days:only sell stocks and cash
                    freecash = sum(np.array(self.portfolio_lot.loc[last_trading_date, :'cash']) * np.array(sell_price))
                    self.freecash.loc[
                        self.all_trading_dates[self.all_trading_dates.index(date) + 1], 'dollar'] = freecash

                if freecash == 0:
                    print('You have ran out of all the freecash! Stop trading!')
                    break


# for problem 2c
class CVaR_Monthly_Trading:

    def __init__(self, bond_purchase_days, bond_mature_days, data_estimator):
        self.bond_purchase_days = bond_purchase_days
        self.bond_mature_days = bond_mature_days
        self.data_estimator = data_estimator
        self.open_monthly_data = self.data_estimator.get_trading_open_monthly_data()
        self.close_monthly_data = self.data_estimator.get_trading_close_monthly_data()
        self.buy_trading_dates = list(self.open_monthly_data.index)
        self.sell_trading_dates = list(self.close_monthly_data.index)

        self.VaR = pd.DataFrame(index = self.buy_trading_dates,
                                columns = ['VaR'])
        self.freecash = pd.DataFrame(index = self.buy_trading_dates,
                                     columns = ['dollar'])
        self.freecash.iloc[0, 0] = 100000  # initial value=100000
        # append the end date
        self.freecash.loc[self.bond_mature_days[-1]] = 0
        self.portfolio_weight = pd.DataFrame(index = self.buy_trading_dates,
                                             columns = list(self.open_monthly_data.columns) + ['cash', 'bond'])
        self.portfolio_lot = pd.DataFrame(index = self.buy_trading_dates,
                                          columns = list(self.open_monthly_data.columns) + ['cash', 'bond'])
        self.bond_semiannual_return = 0.03 / 6
        self.cash_monthly_return = 0.005 / 100 * 30

    def get_all_related_trading_data(self):
        related_traing_data = pd.concat([self.open_monthly_data, self.close_monthly_data]).sort_index()
        self.all_trading_dates = list(related_traing_data.index)

    def CVaR_trading(self, Monthly_optimization_CVaR):
        # get all the buy and sell date(have already sorted)
        self.get_all_related_trading_data()

        for date in self.all_trading_dates:

            # At buy trading date: to optimize and record the weights and lots of the assets
            if date in self.buy_trading_dates:
                opt = Monthly_optimization_CVaR(self.data_estimator, date)
                # buy at open price
                buy_price = (self.open_monthly_data.loc[date, :]).copy(deep = True)
                # could buy at any amount,price = 1
                buy_price['cash'] = 1
                buy_price['bond'] = 1

                if date in self.bond_purchase_days:
                    # add bond to optimize the portfolio
                    w, VaR = opt.CVaR_risky_cash_bond()
                    self.portfolio_weight.loc[date, :] = w.loc[date, :].values

                    self.portfolio_lot.loc[date, :] = self.freecash.loc[date][0] * np.array(
                        self.portfolio_weight.loc[date, :]) / np.array(buy_price)
                    self.VaR.loc[date] = VaR
                else:
                    # exclude bond to optimize
                    w, VaR = opt.CVaR_risky_cash()
                    self.portfolio_weight.loc[date, :'cash'] = w.loc[date, :].values
                    self.portfolio_weight.loc[date, 'bond'] = 0
                    self.portfolio_lot.loc[date, :'cash'] = self.freecash.loc[date][0] * np.array(
                        self.portfolio_weight.loc[date, :'cash']) / np.array(buy_price[:-1])
                    # the lot for bond just the same before its mature day
                    self.portfolio_lot.loc[date, 'bond'] = self.portfolio_lot.loc[
                        self.portfolio_lot.index[list(self.portfolio_lot.index).index(date) - 1], 'bond']
                    self.VaR.loc[date] = VaR

            # At sell trading date: to sell the available assets and record the free cash of the portfolio
            elif date in self.sell_trading_dates:
                # last trading date is buy trading date, use the index to get the portfolio lot
                last_trading_date = self.all_trading_dates[self.all_trading_dates.index(date) - 1]
                # sell at close price
                sell_price = (self.close_monthly_data.loc[date, :]).copy(deep = True)
                sell_price['cash'] = 1 * self.cash_monthly_return

                if date in self.bond_mature_days:
                    # sell all the stocks, cash and bond
                    # the bond price is:
                    sell_price['bond'] = 1 * (1 + self.bond_semiannual_return)
                    freecash = sum(np.array(self.portfolio_lot.loc[last_trading_date, :]) * np.array(sell_price))
                    # free cash put in the next trading day:ie buy trading date
                    if date != bond_mature_days[-1]:
                        self.freecash.loc[
                            self.all_trading_dates[self.all_trading_dates.index(date) + 1], 'dollar'] = freecash
                    else:
                        self.freecash.iloc[-1, 0] = freecash
                else:
                    # not bond mature days:only sell stocks and cash
                    freecash = sum(np.array(self.portfolio_lot.loc[last_trading_date, :'cash']) * np.array(sell_price))
                    self.freecash.loc[
                        self.all_trading_dates[self.all_trading_dates.index(date) + 1], 'dollar'] = freecash

                if freecash == 0:
                    print('You have ran out of all the freecash! Stop trading!')
                    break
