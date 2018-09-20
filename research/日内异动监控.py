"""
指定日期，指定间隔，指定涨幅的股票
生成两个文件， `日期.csv` 为对应行情信息,
`Table.txt` 为了方便导入东方财富进行行情查看

TODAY 为指定日期
START 为指定时间段起始
END 为指定时间段结束
TIME_INTERVAL 为指定观察时间段
Up_Percent 为指定涨幅
"""

from datetime import date, datetime, timedelta

import pandas as pd

import QUANTAXIS as QA

# Time Configuration
# format should be like '2018-08-02'
# TODAY = str(date.today())
TODAY = '2018-08-02'
# TODAY = '2018-07-03'
START = ' 13:00:00'
END = ' 15:00:00'
# default min bar
TIME_INTERVAL = 3

# Up Percent margin
Up_Percent = 2.0


code_list = list(QA.QA_fetch_stock_list_adv().code)

stock_info = QA.QA_fetch_stock_min_adv(
    code=code_list,
    start=TODAY+START,
    end=TODAY+END,
    frequence='1min').data

index_info = QA.QA_fetch_index_min_adv(
    code='000001',
    start=TODAY+START,
    end=TODAY+END,
    frequence='1min').data

index = index_info.index.levels[1]

# prevent min data loss
stock_info = stock_info.groupby(level=1).apply(
    lambda x: x.reset_index(level=1).reindex(index).reset_index(0))
stock_info = stock_info.fillna(method='pad').set_index(['datetime', 'code'])

diff = stock_info.groupby(level=1).close.diff(TIME_INTERVAL)\
    / stock_info.groupby(level=1).shift(TIME_INTERVAL).close*100
diff = diff.reset_index(level=[0, 1]).rename(
    columns={'close': 'close_diff'}).set_index(['datetime', 'code'])
stock_info = pd.concat([stock_info, diff], axis=1)

final_stock_info = stock_info[stock_info.close_diff > Up_Percent]
final_stock_info.to_csv('{}.csv'.format(TODAY))

# Easymoney can load such file
with open('Table.txt', 'w') as f:
    for item in set(final_stock_info.index.levels[1]):
        f.write(item+'\n')
