from Monthly_Trading import *
from CONVERSION_TO_DF import *

'''This file imports all the classes and run to get the outcome'''

# csv_file convert to df
train_dir_path = "./train"
test_dir_path = "./sample_test"
data_c = Data_conversion(train_dir_path, test_dir_path)
all_df = data_c.get_all_df()
all_df.to_csv("./all_data_dataframe.csv")

# solution for 2b
data = pd.read_csv("./all_data_dataframe.csv", index_col = 0, parse_dates = True)
data_estimator = Estimator(data)
MT = Markowitz_Monthly_Trading(bond_purchase_days, bond_mature_days, data_estimator)
MT.Markowitz_trading(Monthly_optimization_Markowitz)
freecash_MAK = MT.freecash
portfolio_weight_MAK = MT.portfolio_weight
portfolio_lot_MAR = MT.portfolio_lot
portfolio_weight_MAK.to_csv("./2b_portfolio_weight.csv")
portfolio_lot_MAR.to_csv("./2b_portfolio_lot.csv")
freecash_MAK.to_csv("./2b_freecash.csv")
# return
r_MAR = (freecash_MAK.iloc[-1, 0] - freecash_MAK.iloc[0, 0]) / freecash_MAK.iloc[0, 0]

# solution for 2c
CT = CVaR_Monthly_Trading(bond_purchase_days, bond_mature_days, data_estimator)
CT.CVaR_trading(Monthly_optimization_CVaR)
freecash_CVaR = CT.freecash
portfolio_weight_CVaR = CT.portfolio_weight
portfolio_lot_CVaR = CT.portfolio_lot
VaR = CT.VaR
portfolio_weight_CVaR.to_csv("./2c_portfolio_weight.csv")
portfolio_lot_CVaR.to_csv("./2c_portfolio_lot.csv")
freecash_CVaR.to_csv("./2c_freecash.csv")
VaR.to_csv("./2c_VaR.csv")
# return
r_CVaR = (freecash_CVaR.iloc[-1, 0] - freecash_CVaR.iloc[0, 0]) / freecash_CVaR.iloc[0, 0]
