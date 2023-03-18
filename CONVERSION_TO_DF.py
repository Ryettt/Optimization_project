import os
import pandas as pd

'''This file is used to merge the csv data to dataframe structure'''

class Data_conversion:
    def __init__(self, train_dir_path, test_dir_path):
        self.train_dir_path = train_dir_path
        self.test_dir_path = test_dir_path

    def get_dataframe(self, path):
        df_data = pd.DataFrame()
        file_list = os.listdir(path)
        for file in file_list:
            file_name = path + r"/" + file
            if file.split('.')[1] == "csv":
                stock_name = file.split('.')[0]
                df_tmp = pd.read_csv(file_name, index_col = 0)
                df_tmp['code'] = stock_name
                df_tmp = pd.read_csv(file_name, index_col = 0)
                df_tmp['code'] = stock_name
                df_data = pd.concat([df_data, df_tmp])
        return df_data

    def get_train_df(self):
        self.train_df = self.get_dataframe(self.train_dir_path)
        return self.train_df

    def get_test_df(self):
        self.test_df = self.get_dataframe(self.test_dir_path)
        return self.test_df

    def get_all_df(self):
        self.get_train_df()
        self.get_test_df()
        self.all_df = pd.concat([self.train_df, self.test_df])
        self.all_df.sort_values(by = 'code', axis = 0, inplace = True)
        self.all_df = self.all_df.groupby(by = ['code']).apply(lambda x: x.sort_index())
        self.all_df = (self.all_df).droplevel(0)
        return self.all_df

