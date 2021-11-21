from datetime import datetime,timedelta
import matplotlib.pyplot as plt
from matplotlib import ticker
import pandas as pd
import numpy as np
import dateutil
import time
import os

class Context:
    def __init__(self, start_date, end_date, group_num, frequency, Path_factor):
        self.start_date=start_date  # Backtest period
        self.end_date=end_date
        self.td=None    # date now：%Y-%m-%d
        self.N=None  # the number of assets
        self.group_num=group_num # the gruop number for a single factor
        self.freq=frequency # the frequency of changing the position:daily 'd',weekly 'w', mothly 'm' 
        self.pos_matrix=None   # the matrix of asset position
        self.net_value=None # the net value of every group
        self.net_value_left=None    # the net value left at present for evry gruop
        self.last_td_mark=None
        self.history={}    #  history data for changing position: changing date,changing times,IC,factor value, price, stock pool, position   

        self.Path_trade_day=None
        self.trade_day=None # tarde day data 
        self.Path_factor=Path_factor
        self.factor=None # factor data
        self.Path_price=None
        self.price=None # Stock price data after recovery
        self.Path_ST=None
        self.ST=None #Wether the stock is ST or delisted, the value is 1 if yes, and 0 if no
        self.Path_suspension=None
        self.suspension=None #Wether the stock is suspended.The value is 1 if yes, and 0 if no
        self.Path_over1year=None
        self.over1year=None #Wether the stock has been listed for more than one year. The value is 1 if yes, and 0 if no.

def initialize(context):
    # read the information 
    context.Path_trade_day="./otherdata/trade_day.csv"
    context.Path_price="./otherdata/ElementaryFactor-复权收盘价.csv"
    context.Path_ST="./otherdata/ElementaryFactor-ST.csv"
    context.Path_suspension="./otherdata/ElementaryFactor-停复牌.csv"
    context.Path_over1year="./otherdata/ElementaryFactor-上市超过一年.csv"
    # information about trade day
    context.trade_day=pd.read_csv(context.Path_trade_day,parse_dates=['datetime'],index_col=['datetime'])
    context.trade_day=context.trade_day[context.start_date:context.end_date].index
    # information about stock price
    context.price=pd.read_csv(context.Path_price,parse_dates=['datetime'],index_col=['datetime'])
    context.price=context.price[context.start_date:context.end_date]
    # ST stock
    context.ST=pd.read_csv(context.Path_ST,parse_dates=['datetime'],index_col=['datetime'])
    context.ST=context.ST[context.start_date:context.end_date]
    # whether the stock is suspended
    context.suspension=pd.read_csv(context.Path_suspension,parse_dates=['datetime'],index_col=['datetime'])
    context.suspension=context.suspension[context.start_date:context.end_date]
    # whether the stock is on list over one year
    context.over1year=pd.read_csv(context.Path_over1year,parse_dates=['datetime'],index_col=['datetime'])
    context.over1year=context.over1year[context.start_date:context.end_date]

    # factor information，in“date*stockcode”form
    context.factor=pd.read_csv(context.Path_factor,parse_dates=[0],index_col=[0])
    context.factor=context.factor[context.start_date:context.end_date]
        
    if isinstance(context.freq,int):
        context.last_td_mark=0
    context.N=context.factor.shape[1]
    # Initialize the net value matrix
    group_col=['group '+str(i+1) for i in range(context.group_num)]
    group_col.append('benchmark')
    context.net_value=pd.DataFrame(index=context.trade_day,columns=group_col)
    context.net_value.iloc[0,:]=1   #initialize the assets of every group as 1
    # the historical data for changing position
    context.history={'td':[],'times':0,'IC':[],'factor':[],'price':[],'tradable':[],'position':[]}

def rebalance(context):
    # Filter the stock pool, remove ST, listed less than a year, not listed stocks  
    td_ST=context.ST.loc[context.td,:].values
    td_suspension=context.suspension.loc[context.td,:].values
    td_over1year=context.over1year.loc[context.td,:].values
    # Get a matrix of tradable stocks
    tradable_matrix=(1-td_ST)*(1-td_suspension)*td_over1year
    # NaN is replced with the mean of the factor values in the market
    f=context.factor.loc[context.td,:]
    f_rank=f.rank(method='first').values   # Rank sorting is used to prevent uneven distribution between groups
    f_value=f_rank[tradable_matrix==1]
    f[np.isnan(f_rank)]=np.nanmean(f.values)
    f_rank[np.isnan(f_rank)]=np.nanmean(f_value)
    f_value=f_rank[tradable_matrix==1]   # Gets the updated value of the tradable factor
    # Calculate the weight matrix
    context.pos_matrix=np.zeros((context.N,context.group_num+1))
    for g in range(context.group_num):
        V_min=np.percentile(f_value,100*g/context.group_num,interpolation='linear')
        V_max=np.percentile(f_value,100*(g+1)/context.group_num,interpolation='linear')
        if g+1 == context.group_num:
            context.pos_matrix[:,g][(f_rank>=V_min) & (f_rank<=V_max)]=context.net_value_left[g]
        else:
            context.pos_matrix[:,g][(f_rank>=V_min) & (f_rank<V_max)]=context.net_value_left[g]
    context.pos_matrix[:,context.group_num][tradable_matrix==1]=context.net_value_left[context.group_num]
    # Get rid of the weights of stock that is not on list
    context.pos_matrix=context.pos_matrix*tradable_matrix.reshape([context.N,1])
    # every  asset is equal weighted within a group
    context.pos_matrix=context.pos_matrix/np.count_nonzero(context.pos_matrix,axis=0)
    # the position for evry stock=spended cash for the stock/stock price
    for g in range(context.group_num+1):
        context.pos_matrix[:,g]=context.pos_matrix[:,g]/context.price.loc[context.td,:].values
    context.pos_matrix[np.isnan(context.pos_matrix)]=0

    # saving the data for changing position
    context.history['td'].append(context.td)
    context.history['times']+=1
    context.history['factor'].append(f.values)
    context.history['price'].append(context.price.loc[context.td,:].values)
    context.history['tradable'].append(tradable_matrix)
    context.history['position'].append(context.pos_matrix)
    # calculate the IC ratio for last changing the position
    if context.last_td_mark:
        # ignore the first position
        stock_return=(context.history['price'][-1]-context.history['price'][-2])/context.history['price'][-2]
        stock_return=stock_return[context.history['tradable'][-2]==1]
        stock_return[np.isnan(stock_return)]=0  # If in ith or (i-1)th period the stock price is NAN,set the return as 0
        factor=context.history['factor'][-2][context.history['tradable'][-2]==1]
        corr=np.corrcoef(stock_return,factor)
        context.history['IC'].append(corr[0,1])

def MaxDrawdown(series):
    # Calculate the maximum withdraw
    drawdown=np.zeros(len(series))
    for i in range(len(series)-1):
        drawdown[i]=(series.iloc[i]-series.iloc[i+1:].min())/series.iloc[i]
    return drawdown.max()

def summary(context):
    # visualize
    plt.rcParams['font.sans-serif'] = ['SimHei']  # Used to display Chinese labels normally
    plt.rcParams['axes.unicode_minus'] = False  # Used to display the minus sign normally

    ICIR=np.mean(context.history['IC'])/np.std(context.history['IC'], ddof=1)
    title='IC均值:'+'{:.2%}'.format(np.mean(context.history['IC']))+\
        '   IC最大值:'+'{:.2%}'.format(np.max(context.history['IC']))+\
        '   IC最小值:'+'{:.2%}'.format(np.min(context.history['IC']))+\
        '   IC标准差:'+'{:.2%}'.format(np.std(context.history['IC'], ddof=1))+\
        '   ICIR:'+'{:.2f}'.format(ICIR)+\
        '   T统计量:'+'{:.2f}'.format(ICIR*np.sqrt(context.history['times']-2))
    factor_name=context.Path_factor.split('/')[-1].split('.')[0]
    # IC picture
    fig = plt.figure(figsize=(12, 9), dpi=100)
    x_label=[t.strftime('%Y-%m-%d') for t in context.history['td'][:-1]]
    plt.bar(x_label,context.history['IC'])
    if isinstance(context.freq,int):
        plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(int(252/(2*context.freq))))
    elif context.freq == 'd':
        plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(126))
    elif context.freq == 'w':
        plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(26))
    elif context.freq == 'm':
        plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(6))
    elif context.freq == 'f':
        plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(1))
    plt.gca().yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1, decimals=2))
    plt.grid(axis="y")
    plt.xticks(rotation=-45)
    plt.title(title)
    #plt.show()
    plt.savefig('./result/IC_'+factor_name+'_'+str(context.freq)+'.png')

    # long-short return picture
    LS=context.net_value['group 10']-context.net_value['group 1']
    td_num=len(context.trade_day)
    Drawdown=MaxDrawdown(1+LS)   #maximum withdraw
    year_return=(1+LS[context.end_date])**(252/td_num)-1 #annualized return
    title='多空总收益率:'+'{:.2%}'.format(LS[context.end_date])+\
        '   年化收益率:'+'{:.2%}'.format(year_return)+\
        '   最大回撤:'+'{:.2%}'.format(Drawdown)
    fig = plt.figure(figsize=(12, 9), dpi=100)    
    ax = fig.add_subplot(2, 1, 1)
    ax.bar(context.net_value.columns,context.net_value.iloc[-1,:]-1,color=10*['cyan']+['silver'])
    ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1, decimals=2))
    plt.grid(axis="y")
    ax = fig.add_subplot(2, 1, 2)
    ax.plot(LS,label='long-short')
    ax.plot(context.net_value['benchmark']-1,label='benchmark')
    ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1, decimals=2))
    plt.grid(axis="y")
    plt.xticks(rotation=-45)
    ax.legend()
    fig.suptitle(title)
    #plt.show()
    plt.savefig('./result/L-S_'+factor_name+'_'+str(context.freq)+'.png')

def handle_data(context):
    if not context.last_td_mark:
        # initial the position
        context.net_value_left=context.net_value.loc[context.td,:].values
        rebalance(context)
    else:
        # use the position to calculate the net value
        td_price=context.price.loc[context.td,:].fillna(value=0)
        context.net_value.loc[context.td,:]=td_price.dot(context.pos_matrix)
        # renew the net value left
        context.net_value_left=context.net_value.loc[context.td,:].values

        rebalance_month=[5,9,11]
        # changing the position
        if isinstance(context.freq,int) and context.last_td_mark == context.freq:
            #changing the position at fixed dates
            rebalance(context)
            context.last_td_mark=0
        elif context.freq == 'd':
            #changing the position everyday
            rebalance(context)
        elif context.freq == 'w' and (context.td.strftime('%W') != context.last_td_mark):
            #changing the position every week
            rebalance(context)
        elif context.freq == 'm' and (context.td.month != context.last_td_mark):
            #changing the position every month
            rebalance(context)
        elif context.freq == 'f' and (context.td.month in rebalance_month and context.td.month != context.last_td_mark):
            #changing the position on the first trade day of May, September,and November.
            rebalance(context)

def run(context):
    initialize(context)
    for td in context.trade_day:
        context.td=td
        handle_data(context)
        # Change mark, used to determine whether to change positions
        if isinstance(context.freq,int):
            context.last_td_mark+=1
        elif context.freq == 'w':
            context.last_td_mark=td.strftime('%W')
        else:
            context.last_td_mark=td.month
    summary(context)



file_path="./factor/"
file_list=os.listdir(file_path)
#file_list=[]
for f in file_list:
    context=Context('20170101', '20201231', 10, 'm', file_path+f)
    run(context)
