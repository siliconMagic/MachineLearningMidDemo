#coding:utf-8

"""
根据Kaggle上的一个预测Titanic存活人数的Demo,利用xgboost进行预测
本代码有借鉴网上开源脚本的部分
仅用于学习
"""
__author__ = "Minux"

import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
import numpy as np

from sklearn.base import TransformerMixin
class DataFrameImputer(TransformerMixin):
    def fit(self, X, y=None):
        # 定义补全NA数值的函数
        # 如果X[c]是python对象，那么用出现次数最多的值补全,否则使用使用中位数补全
        self.fill = pd.Series([X[c].value_counts().index[0]
                            if X[c].dtype == np.dtype('O') else X[c].median() for c in X ],
                            index = X.columns)
        return self

    def transform(self, X, y = None):
        return X.fillna(self.fill)

class Forecast_Titanic(object):

    def __init__(self):
        self.feature_cols    = ['Pclass', 'Sex', 'Age', 'Fare', 'Parch']
        self.nonnumeric_cols = ['Sex']

    def load_data(self):
        self.train_df = pd.read_csv('./train.csv', header=0)
        self.test_df  = pd.read_csv('./test.csv', header=0)

    def data_anal(self):
        # 完成对train_df和test_df的NA值的处理
        big_X = self.train_df[self.feature_cols].append(self.test_df[self.feature_cols])
        big_X_imputed = DataFrameImputer().fit_transform(big_X)

        # XGBoost 不会自动处理分类特征,需要将他们转换为整型数值
        le = LabelEncoder()
        for feature in self.nonnumeric_cols:
            big_X_imputed[feature] = le.fit_transform(big_X_imputed[feature])

        # 构建模型的输入数据
        train_X = big_X_imputed[0:self.train_df.shape[0]].as_matrix()
        test_X  = big_X_imputed[self.train_df.shape[0]::].as_matrix()
        # 预测标签列为Survived
        trian_y = self.train_df['Survived']

        # 使用xgboost进行预测
        gbm = xgb.XGBClassifier(max_depth=3, n_estimators=300, learning_rate=0.05).fit(train_X, trian_y)
        predictions = gbm.predict(test_X)
        submissions = pd.DataFrame({'PassengerId':self.test_df['PassengerId'],
                                    'Survived':predictions })
        submissions.to_csv("submission.csv",index=False)


def main():
    ft = Forecast_Titanic()
    ft.load_data()
    ft.data_anal()

if __name__ == "__main__":
    main()

