#coding:utf-8

import pandas as pd
import math
import matplotlib.pyplot as plt

def get_data_csv_file():
    # BOC.csv为quant_forecast.py运行后写入的数据文件
    boc_df = pd.read_csv('BOC.csv', index_col='date')
    # 根据ARMA模型的需要提取数据中date列和close列重新组织data_frame
    boc_df = boc_df[['close']]
    return boc_df

"""
def dataframe_to_list(boc_df):
    boc_list = []
    for i in range(len(boc_df)):
        list_data = boc_df.index[i], boc_df.close[i]
        boc_list.append(list_data)
    return boc_list
"""

# 单位根检验函数
from arch.unitroot import ADF
# 白噪声检验
from statsmodels.tsa import stattools
# ACF和PACF
from statsmodels.graphics.tsaplots import *
# ARIMA模型
from statsmodels.tsa import arima_model

def arma_model_construct(boc_df):
    boc_df.index = pd.to_datetime(boc_df.index)
    # print boc_df
    forecast_out = int(math.ceil(0.01 * len(boc_df)))
    boc_train = boc_df[:-forecast_out]
    # 绘制当前训练集数据的时间序列图
    # boc_train.plot(title='BOC close')
    plt.show()

    boc_train = boc_train.dropna()
    print ADF(boc_train, max_lags=15).summary().as_text()

    LjungBox = stattools.q_stat(stattools.acf(boc_train)[1:12], len(boc_train))
    print LjungBox[1][-1]

    # 做一阶差分
    boc_diff = boc_train.diff(1)
    boc_diff.plot()
    # plt.show()

    ax_1 = plt.subplot(121)
    ax_2 = plt.subplot(122)
    # ACF
    plot_1 = plot_acf(boc_diff, lags = 30, ax=ax_1)
    # PACF
    plot_2 = plot_pacf(boc_diff, lags=30, ax=ax_2)
    # plt.show()

    # 获得参数p=0,d=1,q=1
    model_arima = arima_model.ARIMA(boc_train, order=(0,1,1)).fit()
    model_arima.summary()
    # 检测残差
    print model_arima.conf_int()

    print model_arima.forecast(10)[0]




if __name__ == '__main__':
    boc_df = get_data_csv_file()
    # boc_list = dataframe_to_list(boc_df)
    arma_model_construct(boc_df)