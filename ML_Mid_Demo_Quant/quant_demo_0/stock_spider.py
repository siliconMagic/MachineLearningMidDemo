#coding:utf-8

"""
爬虫实现功能:
1.利用网易财经爬取BOC历史交易数据
2.爬取BOC历史资金走向

"""

import requests
from bs4 import BeautifulSoup
import os
import time
import csv

'''
全局变量区
构造浏览器的请求头,只要传入列表中的任意一个即可
'''
_headers_0={
	"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0"
}

_headers_1={
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.1708.400 QQBrowser/9.5.9635.400'
}


'''
股票数据爬取操作类,实现功能1
2006年第三季度的数据目标url:
http://quotes.money.163.com/trade/lsjysj_601988.html?year=2006&season=3
'''
class StockSpider(object):

	url = 'http://quotes.money.163.com/trade/lsjysj_'

	def __init__(self,stock_code, begin_year, end_year):
		"""
		stock_code:需要爬取的股票代码
		year      :需要年份
		season    :需要的季度 取值范围是1-4
		"""
		try:
			if begin_year < 2006:
				print("para error")
				raise
			else: 
				self.stock_code = stock_code
				self.begin_year = begin_year
				self.end_year   = end_year+1 
		except Exception,e:
			print "other error! ",e

	def crawl_data(self, url, year, season):
		object_url = url + str(self.stock_code)+'.html?year='+str(year)+'&season='+str(season)
		print(object_url)
		html = requests.get(object_url, headers=_headers_0).content
		# 指定soup使用的解析器 lxml html5lib html.parser
		soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
		# print(soup.html())
		page_table = soup('table',{'class':'table_bg001 border_box limit_sale'})[0]
		# table = soup.findAll('table',{'class':'table_bg001 border_box limit_sale'})
		# day_k中保存是股票的属性以及值,数值在td标签对中
		# 具体属性包括日期 开盘价 最高价 最低价 收盘价 涨跌额 涨跌幅(%) 成交量 成交金额 振幅(%) 换手率(%)
		day_k = page_table('tr')
		# 取出td中的数值
		'''
		for item in day_k:
			if item('td') != []:
				for sub_item in item('td'):
					print(sub_item.get_text())
			else:
				print('出现空行！')
			print('-'*20)
		'''
		# 将爬取数据逆序返回，这样日期为顺序
		return day_k[::-1]

	def data_to_csv(self):
		# 创建需要被写入的文件
		csv_file = open('./stock_data/'+str(self.stock_code)+'.csv','wb')
		stock_wr = csv.writer(csv_file)
		# 写入head
		stock_wr.writerow(('date','open','high','low','close','delta','delta_rate','vol','vol_sum','vibration','turnover'))
		try:
			for year in range(self.begin_year,self.end_year):
				print('year '+str(year)+' is running')
				for i in range(1,5):
					year_datas = self.crawl_data(StockSpider.url, year, i)
					# 解析爬取到year_data数据
					if year_datas != []:
						for y_data in year_datas:
							csv_row = []
							if y_data('td') != []:
								for item in y_data('td'):
									csv_row.append(item.get_text().replace(',',''))
								if csv_row != []:
									stock_wr.writerow(csv_row)
			time.sleep(1)
		except Exception,e:
			print "Error! ",e
		finally:
			print("交易数据爬取完成")
			csv_file.close()


'''
资金历史流向操作类,用于实现功能2
历史资金流向的url为
http://quotes.money.163.com/trade/lszjlx_601988,page.html
page为分页数据
目前网站上共有21页数据
本处的import 主要处理anscii和utf-8编码写入文件的问题
'''

import sys
reload (sys)
sys.setdefaultencoding('utf-8')


class StockCapital(object):

	url = "http://quotes.money.163.com/trade/lszjlx_"

	def __init__(self, max_page, code=601988):
		self.max_page = max_page
		self.code     = code

	def crawl_data(self,page):
		object_url = StockCapital.url +str(self.code) + "," + str(page-1) + ".html"
		# print(object_url)
		html = requests.get(object_url, headers=_headers_0).content
		soup = BeautifulSoup(html, "html.parser", from_encoding='utf-8')
		table = soup('table',{'class':'table_bg001 border_box'})[0]
		stock_attr = table('th')
		# 统计表格的标题列表
		table_attr = []
		for item in stock_attr:
			table_attr.append(item.get_text())
		# 表格数据逆序返回
		stock_data = table('tr')
		return (table_attr, stock_data[::-1])

	def data_to_csv(self):
		# 构建csv表格
		csv_file = open('./stock_data/'+str(self.code)+'_hist_capital.csv','wb')
		capital = csv.writer(csv_file)
		table_attr, stock_data = self.crawl_data(1)
		# 处理属性行 将数据属性写入文件
		'''
		print(type(table_attr))
		for i in range(len(table_attr)):
			print(table_attr[i])
		attr = tuple("".join(table_attr))
		print(attr)
		'''
		try:
			capital.writerow(table_attr)
			for i in range(1,self.max_page+1):
				print('page %d data is crawling...' % i)
				table_attr, stock_attr = self.crawl_data(i)
				# 处理数据行
				for day_data in stock_data:
					# 构建一个日数据列表
					csv_row = []
					for item in day_data.find_all('td'):
						csv_row.append(item.get_text().replace(',','').replace('\n',''))
					capital.writerow(csv_row)
		except Exception,e:
			print("writer error!",e)
		finally:
			print("资金流数据爬取完成!")
			csv_file.close()

'''
601988中国银行的股票代号
2006为start_year
2017为end_year
'''
def main_trade():
	_spider = StockSpider(601988,2006,2017)
	_spider.data_to_csv()

def main_capital():
	_spider = StockCapital(21)
	# _spider.crawl_data(1)
	_spider.data_to_csv()


if __name__ == '__main__':
	main_trade()
	main_capital()
	
