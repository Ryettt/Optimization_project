import pandas as pd
import numpy as np
import datetime
import warnings
warnings.filterwarnings("ignore")

'''This file is used to caculate the estimators need for optimization
 and extract some data we needed'''

# calculate the moving avarage mean and historical covariance
class Estimator:
    def __init__(self, data_all):
        # data:a dataframe containing all the data(test and train)
        self.data_all = data_all

    def get_end_monthly_data(self):
        self.end_monthly_data = (
            self.data_all.groupby(by = ['code', self.data_all.index.year, self.data_all.index.month]).apply(
                lambda x: x.tail(1))).droplevel(
            [0, 1, 2])
        return self.end_monthly_data

    def get_start_monthly_data(self):
        self.start_monthly_data = (
            self.data_all.groupby(by = ['code', self.data_all.index.year, self.data_all.index.month]).apply(
                lambda x: x.head(1))).droplevel(
            [0, 1, 2])
        return self.start_monthly_data

    def get_adj_close_return_monthly_data(self):
        self.get_end_monthly_data()
        # all adj_close_data
        self.adj_close_data = (self.data_all.loc[:, ['Adj Close', 'code']]).reset_index()
        self.adj_close_data = self.adj_close_data.pivot(index = 'Date', columns = 'code',
                                                        values = 'Adj Close')
        # monthly adj_close_data
        self.adj_close_monthly_data = (self.end_monthly_data.loc[:, ['Adj Close', 'code']]).reset_index()
        self.adj_close_monthly_data = self.adj_close_monthly_data.pivot(index = 'Date', columns = 'code',
                                                                        values = 'Adj Close')

        # monthly return
        self.adj_close_return_monthly_data = (
                (self.adj_close_monthly_data - self.adj_close_monthly_data.shift(
                    1)) / self.adj_close_monthly_data.shift(
            1)).copy(
            deep = True)

    def get_historical_covariance_monthly(self, trading_date):
        # date:Datetime.date,should be in the test set:ie:2018-2019
        self.get_adj_close_return_monthly_data()
        # get the date before trading_date
        sample_end_date = self.adj_close_data.index[
            list(self.adj_close_data.index).index(trading_date) - 1]
        if sample_end_date < datetime.date(2017, 12, 29):
            print("Not the date in the test set")
        else:
            # first caculate one half
            covm = pd.DataFrame(index = self.adj_close_return_monthly_data.columns,
                                columns = self.adj_close_return_monthly_data.columns)
            for stock1 in covm.columns:
                index = list(covm.columns).index(stock1)
                covm.loc[stock1, stock1] = np.var(self.adj_close_return_monthly_data[stock1])
                for i in range(index + 1, len(covm.columns)):
                    stock2 = covm.columns[i]
                    datapair = ((self.adj_close_return_monthly_data).loc[:sample_end_date,
                                [stock2, stock1]]).dropna()
                    covm.loc[stock1, stock2] = np.cov(datapair)[0, 1]
            covm.fillna(0, inplace = True)
            covm_t = (covm.T).copy(deep = True)

            for i in range(len(covm_t)):
                covm_t.iloc[i, i] = 0

            covm = covm.add(covm_t)

            return covm

    def get_mean_monthly(self, trading_date):
        self.get_adj_close_return_monthly_data()
        # get the date before trading_date
        sample_end_date = self.adj_close_data.index[
            list(self.adj_close_data.index).index(trading_date) - 1]

        self.mean_data = (self.adj_close_return_monthly_data.shift(1)).copy(deep = True).dropna()
        return self.mean_data.loc[sample_end_date, :]

    def sample_mean_from_MV(self, trading_date, sample_size = 10000):
        #sample from multivariate normal distribution
        cov = self.get_historical_covariance_monthly(trading_date)
        mean = self.get_mean_monthly(trading_date)
        np.random.seed(42)
        sample_mean = pd.DataFrame(index = range(sample_size), columns = mean.index)
        for i in range(sample_size):
            mean_s = np.random.multivariate_normal(np.array(mean), np.array(cov))
            sample_mean.iloc[i, :] = mean_s
        return sample_mean

    def get_trading_close_monthly_data(self):
        self.get_end_monthly_data()
        # all adj_close_data
        trading_close_data = (self.end_monthly_data.loc[:, ['Close', 'code']]).reset_index()
        trading_close_data = (trading_close_data.pivot(index = 'Date', columns = 'code',
                                                       values = 'Close')).loc['2018':, :]
        return trading_close_data

    def get_trading_open_monthly_data(self):
        self.get_start_monthly_data()
        # all adj_close_data
        trading_open_data = (self.start_monthly_data.loc[:, ['Open', 'code']]).reset_index()
        trading_open_data = (trading_open_data.pivot(index = 'Date', columns = 'code',
                                                     values = 'Open')).loc['2018':, :]
        return trading_open_data
