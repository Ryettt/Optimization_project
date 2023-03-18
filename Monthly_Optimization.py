from Monthly_Estimator import *
from scipy.optimize import minimize
from coptpy import *

'''This file contains two classes, which represent two optimization model.
 One is Markowitz and another is to minimize CVaR'''

# Use Markowitz portpolio model for 2b
class Monthly_optimization_Markowitz:
    def __init__(self, data_estimator, trading_date, gamma = 1):
        # data_estimator: a object of Estimator class
        # trading date: the first date of every month (datetime.date)
        # gamma: the risk adverse coefficent

        self.data_estimator = data_estimator
        self.trading_date = trading_date
        self.gamma = gamma
        self.bond_monthly_return = 0.03 / 12
        self.cash_monthly_return = 0.005 / 100 * 30
        self.mean_return_risky = self.data_estimator.get_mean_monthly(self.trading_date)
        self.covm = self.data_estimator.get_historical_covariance_monthly(trading_date)

    def objective_function1(self, w, mean_return):
        # for stock and cash
        w_risky = w[:-1]
        obj = 1 / 2 * (np.dot(w_risky.dot(np.array(self.covm)), w_risky.T)) - self.gamma * w.dot(mean_return)
        return obj

    def objective_function2(self, w, mean_return):
        # for stock and cash and bond
        w_risky = w[:-2]
        obj = 1 / 2 * (np.dot(w_risky.dot(np.array(self.covm)), w_risky.T)) - self.gamma * w.dot(mean_return)
        return obj

    def markovitz_risky_cash(self):
        mean_return_all = self.mean_return_risky.copy(deep = True)
        mean_return_all['cash'] = self.cash_monthly_return
        mean_return = np.array(mean_return_all).reshape(-1, 1)

        # original:avarage
        w0 = np.ones((1, mean_return.shape[0])) * (1 / (mean_return.shape[0]))
        cons = ({'type': 'eq',
                 'fun': lambda w: w.sum() - 1},)
        x_bounds = []
        for j in range(len(mean_return)):
            x_bounds.append([0, 1])
        wm = minimize(self.objective_function1, w0, args = (mean_return), bounds = x_bounds, constraints = cons)
        w = wm.x
        wdf = pd.DataFrame(w.reshape(1, -1), columns = mean_return_all.index, index = [self.trading_date])
        return wdf

    def markovitz_risky_cash_bond(self):
        mean_return_all = self.mean_return_risky.copy(deep = True)
        mean_return_all['cash'] = self.cash_monthly_return
        mean_return_all['bond'] = self.bond_monthly_return
        mean_return = np.array(mean_return_all).reshape(-1, 1)

        # original:avarage
        w0 = np.ones((1, mean_return.shape[0])) * (1 / (mean_return.shape[0]))
        cons = ({'type': 'eq',
                 'fun': lambda w: w.sum() - 1},)
        x_bounds = []
        for j in range(len(mean_return)):
            x_bounds.append([0, 1])
        wm = minimize(self.objective_function2, w0, args = (mean_return), bounds = x_bounds, constraints = cons)
        w = wm.x
        wdf = pd.DataFrame(w.reshape(1, -1), columns = mean_return_all.index, index = [self.trading_date])
        return wdf


# to minimize CVaR for 2b
class Monthly_optimization_CVaR:
    def __init__(self, data_estimator, trading_date, alpha = 0.95):
        # data_estimator: a object of Estimator class
        # trading date: the first date of every month (datetime.date)
        # alpha : quantile for risk measure

        self.data_estimator = data_estimator
        self.trading_date = trading_date
        self.bond_monthly_return = 0.03 / 12
        self.cash_monthly_return = 0.005 / 100 * 30
        self.mean_return_risky = self.data_estimator.get_mean_monthly(self.trading_date)
        self.sample_mean = self.data_estimator.sample_mean_from_MV(self.trading_date)
        self.alpha = alpha

    def CVaR_risky_cash(self):
        env = Envr()
        model = env.createModel('risk measure')
        # decision variables
        all_asset_name_list = list(self.mean_return_risky.index) + ['cash']
        risky_asset_name_list = list(self.mean_return_risky.index)
        # portfolio weight
        w = model.addVars(all_asset_name_list, lb = 0, ub = 1, vtype = COPT.CONTINUOUS, nameprefix = 'w')
        # VaR
        v = model.addVar(lb = 0, vtype = COPT.CONTINUOUS, name = 'VaR')
        # theta
        theta = model.addVars(list(self.sample_mean.index), lb = 0, vtype = COPT.CONTINUOUS, nameprefix = 'theta')
        # constrains
        model.addConstr(w.sum() == 1)
        model.addConstrs(
            theta[i] >= - quicksum(w[name] * self.sample_mean.loc[i, name] - w[
                'cash'] * self.cash_monthly_return for name in risky_asset_name_list) - v for i in
            list(self.sample_mean.index))

        # objective function
        model.setObjective(
            -quicksum(w[name] * self.mean_return_risky.loc[name] for name in risky_asset_name_list) + w[
                'cash'] * self.cash_monthly_return + v + 1 / (1 - self.alpha) * theta.sum() / len(
                list(self.sample_mean.index)), sense = COPT.MINIMIZE)

        model.solve()

        if model.status == COPT.OPTIMAL:
            de_vars = model.getVars()
            name = {}
            for var in de_vars:
                name[var.name] = var.x
            wdf = pd.DataFrame(np.array(list(name.values())[:len(all_asset_name_list)]).reshape(1, -1),
                               index = [self.trading_date],
                               columns = all_asset_name_list)
            VaR = list(name.values())[len(all_asset_name_list)]

            return wdf, VaR

        else:
            print("Not optimal value.")

    def CVaR_risky_cash_bond(self):
        env = Envr()
        model = env.createModel('risk measure')
        # decision variables
        all_asset_name_list = list(self.mean_return_risky.index) + ['cash', 'bond']
        risky_asset_name_list = list(self.mean_return_risky.index)
        # portfolio weight
        w = model.addVars(all_asset_name_list, lb = 0, ub = 1, vtype = COPT.CONTINUOUS, nameprefix = 'w')
        # VaR
        v = model.addVar(lb = 0, vtype = COPT.CONTINUOUS, name = 'VaR')
        # theta
        theta = model.addVars(list(self.sample_mean.index), lb = 0, vtype = COPT.CONTINUOUS, nameprefix = 'theta')
        # constrains
        model.addConstr(w.sum() == 1)
        model.addConstrs(
            theta[i] >= - quicksum(w[name] * self.sample_mean.loc[i, name] - w[
                'cash'] * self.cash_monthly_return - w['bond'] * self.bond_monthly_return for name in
                                   risky_asset_name_list) - v for i in
            list(self.sample_mean.index))

        # objective function
        model.setObjective(
            -quicksum(w[name] * self.mean_return_risky.loc[name] for name in risky_asset_name_list) - w[
                'cash'] * self.cash_monthly_return - w['bond'] * self.bond_monthly_return + v + 1 / (
                    1 - self.alpha) * theta.sum() / len(list(self.sample_mean.index)), sense = COPT.MINIMIZE)

        model.solve()

        if model.status == COPT.OPTIMAL:
            de_vars = model.getVars()
            name = {}
            for var in de_vars:
                name[var.name] = var.x
            wdf = pd.DataFrame(np.array(list(name.values())[:len(all_asset_name_list)]).reshape(1, -1),
                               index = [self.trading_date],
                               columns = all_asset_name_list)
            VaR = list(name.values())[len(all_asset_name_list)]

            return wdf, VaR
        else:
            print("Not optimal value.")
