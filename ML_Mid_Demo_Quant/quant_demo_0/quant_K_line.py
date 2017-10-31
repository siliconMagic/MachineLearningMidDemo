#coding:utf-8

"""
本模块的主要工作是绘制2010-2017中国银行(601988)的K线数据
"""
import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY, date2num, MonthLocator
from matplotlib.finance import candlestick_ohlc

def get_raw_data():
    start_time = '2010-1-1'
    end_time   = '2017-10-25'
    BOC = ts.get_k_data('601988', start_time, end_time, ktype='D')
    BOC.index = pd.to_datetime(BOC['date'])
    BOC.drop([BOC.columns[0]], axis=1, inplace=True)

    # 将获取数据保存到csv文件中
    BOC.to_csv('BOC_10_17.csv')
    """
    选取预测工作需要的指标
    主要选取指标开盘价(open),收盘价(close),盘高价(high),盘低价(low),交易量(volume)
    """
    boc_df = BOC[['open', 'high', 'low', 'close']]
    return boc_df

def plot_candle(boc_df, title='stock_title'):
    # 设置字体类型为黑体(SimHei)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 将日期(index)转换成秒数(float)
    Date = [date2num(date) for date in boc_df.index]
    boc_df.loc[:,'date'] = Date

    # 将boc_df(DateFrame)类型转换为List类型
    list_data = []
    # 按行进行遍历
    for i in range(len(boc_df)):
        # 组合成为列表
        list_content = [boc_df.date[i], boc_df.open[i], boc_df.high[i], boc_df.low[i], boc_df.close[i]]
        list_data.append(list_content)

    # 设定绘图相关参数
    ax = plt.subplot()
    ax.set_title("BOC Candle Price")

    # 获取每周一的日期数据
    mondays = WeekdayLocator(MONDAY)
    monthdays = MonthLocator(interval= 12)
    # 日期格式 ‘17-Mar-09’
    week_formatter = DateFormatter('%Y %b %d')
    # 设置主要刻度
    ax.xaxis.set_major_locator(monthdays)
    # 设置次要刻度
    # ax.xaxis.set_minor_locator(DayLocator())
    ax.xaxis.set_minor_locator(mondays)
    ax.xaxis.set_major_formatter(week_formatter)

    candlestick_ohlc(ax, list_data, width=0.7, colorup='r', colordown = 'g')

    # 设定x轴上显示日期的角度
    plt.setp(plt.gca().get_xticklabels(), rotation=50, horizontalalignment='right')
    plt.show()


if __name__ == '__main__':
    boc_df = get_raw_data()
    plot_candle(boc_df)
