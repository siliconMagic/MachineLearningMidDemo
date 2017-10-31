#coding:utf-8
"""
@author: Liangyu Min
"""

import pandas as pd
import numpy as np

import datetime
import time
# import pandas_datareader as web 该接口出现bad handshake Error
import tushare as ts
import math
import matplotlib.pyplot as plt
from matplotlib import style
from sklearn.model_selection import cross_val_score
from sklearn import preprocessing, cross_validation, svm
from sklearn.linear_model import LinearRegression

# global vars
start_time = '2014-01-01'
end_time   = '2017-10-25'
"""
获取数据&处理数据指标
@return: boc_df 处理后的数据集
"""
def get_stock_data():
    # df = web.DataReader("MSFT", "yahoo", start_time, end_time)
    # 默认索引是date,使用reset_index()将date变成列,重新排列(解决方案不佳)
    #ts.get_hist_data()
    BOC = ts.get_k_data('601988', start_time, end_time, ktype='D')
    BOC.index = pd.to_datetime(BOC['date'])
    BOC.drop([BOC.columns[0]],axis=1, inplace=True)

    # 将获取数据保存到csv文件中
    BOC.to_csv('BOC.csv')
    """
    选取预测工作需要的指标
    主要选取指标开盘价(open),收盘价(close),盘高价(high),盘低价(low),交易量(volume)
    """
    boc_df = BOC[['open', 'high', 'low', 'close', 'volume']]
    # 日震幅指标
    boc_df['flucate'] = (boc_df['high']-boc_df['low']) / boc_df['close'] * 100.0
    # 日股价变化率指标
    boc_df['price_change'] = (boc_df['close'] - boc_df['open']) / boc_df['close'] * 100.0

    """
    构建新指标数据集
    """
    boc_df = boc_df[['close', 'flucate', 'price_change', 'volume']]
    # print boc_df
    return boc_df

def forecast_data(boc_df):
    """
    预测函数
    :param boc_df: 传入已经被处理的data frame
    :return: 预测数据集
    """
    # 需要被预测的列为close
    forecast_col = 'close'
    boc_df.fillna(value=-99999, inplace=True)
    # 需要被预测的天数 forecast_out
    forecast_out = int(math.ceil(0.01 * len(boc_df)))
    # 对数据进行滞后处理(shfit),处理后的数据作为label
    boc_df['label'] = boc_df[forecast_col].shift(-forecast_out)
    # print boc_df.shape
    # print boc_df.tail()
    X = np.array(boc_df.drop(['label'], 1))
    # 标准化处理数据
    X_scale = preprocessing.scale(X)
    # mean:-1.1935276172e-16 std:1.0
    # print X_scale.mean(),X_scale.std()
    # 将数据集切分成两块 X_scale和X_delay
    X_delay = X_scale[-forecast_out:]
    # print X_delay
    X_scale = X_scale[:-forecast_out]

    # 标签集y
    boc_df.dropna(inplace=True)
    y = np.array(boc_df['label'])

    X_train, X_test, y_train, y_test = cross_validation.train_test_split(X_scale, y,test_size=0.10)
    clf = LinearRegression()
    clf.fit(X_train, y_train)
    accuracy = clf.score(X_test, y_test)
    # test_size=0.10时准确率为91.5%
    # print accuracy
    # 测试使用SVM的效果
    svm_forecast(X_train, y_train, X_test, y_test, X_delay)

    forecast_set = clf.predict(X_delay)
    print forecast_set, accuracy, forecast_out
    return forecast_set

"""
利用SVM进行数据模型训练,输出精确度
"""
def svm_forecast(X_train, y_train, X_test, y_test, X_delay):
    forecast_set = []
    for k in ['linear', 'poly', 'rbf', 'sigmoid']:
        clf = svm.SVR(k)
        clf.fit(X_train, y_train)
        # 测试结果显示rbf核的效果比较好
        if k == 'rbf':
            forecast_set = clf.predict(X_delay)
            print 'svm(rbf) predict ',forecast_set
        accuracy = clf.score(X_test, y_test)
        print "accuracy in svm ", accuracy
    return forecast_set


def plot_function(forecast_set, boc_df):
    """
    绘图函数
    :param forecast_set:
    :param boc_df:
    :return:
    """
    style.use('ggplot')
    boc_df['forecast'] = np.nan

    # last_date是最新日期, last_unix是将日期转换成秒数(从1970-1-1开始计时)
    last_date = boc_df.iloc[-1].name
    last_sec = time.mktime(last_date.timetuple())
    # print last_date, last_sec
    day_sec = 86400
    next_sec = last_sec + day_sec

    for i in forecast_set:
        next_date = datetime.datetime.fromtimestamp(next_sec)
        next_sec += day_sec
        boc_df.loc[next_date] = [np.nan for _ in range(len(boc_df.columns)-1)]+[i]

    print boc_df.tail(50)
    boc_df['close'].plot()
    boc_df['forecast'].plot()
    plt.ylabel('BOC_price')
    plt.xlabel('Date')
    plt.show()

if __name__ == "__main__":
    boc_df = get_stock_data()
    # print boc_df
    forecast_set = forecast_data(boc_df)
    plot_function(forecast_set, boc_df)