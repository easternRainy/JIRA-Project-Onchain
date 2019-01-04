'''
这个程序目的是简化Onchain周报的工作流程
使用方法：
1. 在Jira的Search Issue中初步筛选，导出csv文件，并放入工作目录中，更名为worklogTest.csv
2. 运行程序，输入需要的项目编号
3. 输入起始时间 年/月/日 ****/**/**
4. 输入截止时间 年/月/日 ****/**/**
5. 程序会尝试从工作人员logwork的内容中提取链接，并登陆链接读取工作人员在github上增删记录
6. 如果5成功，则输出文件为 startdayToenddayPersonalStatistics_URL_SUCCESS.csv
7. 如果5失败，则输出文件为 startdayToenddayPersonalStatistics_URL_FAILURE.csv

程序的数据结构：
worklogTest.csv会存入df变量中，作为全局变量，任何函数都可以访问，但不建议修改
如果程序的使用者选择了Log Work这个Field，则Log Work到Log Work.j （j=some number） 的所有内容都会被分离，暂存到df_split全局变量中
如果程序的使用这选择了其他有重复的Field，则会合并到df_merge全局变量中，比如每一行的Comment到Comment.i （i=some number）会合并到一个单元格中
其他被选择的而且没有重复的Field，会存在df_need全局变量中
最后三个中间变量会合并，筛选，得到df_final

流程图：
       df_split
df     df_merge    df_final
       df_need

'''


import pandas as pd
import numpy as np
import string
import re
import requests

'''functions'''

# 获取根名相同的列的个数，比如 Log Work 到 Log Work.52 则返回52
def getRepetition(name):
    i = 0
    while True:
        try:
            if i==0:
                middle = df[name]
            else:
                middle = df[name + '.' + str(i)]
            i = i + 1
        except:
            break
    return i-1

# 处理Log Work，根据分号把信息分开，存储到df_split
def splitLogWork():
    # SPLIT FUNCTION IMPORTANT!!!!!!
    # df['Log Work Content'], df['Log Work Date'], df['Log Work Author'], df['Log Work Time'] = zip(*df['Log Work'].map(lambda x: x.split(';')))

    # Log Work         原表中所有信息合并在一个单元格里
    # Log Work Content 工作内容
    # Log Work Date    记录日志的日期和时间
    # Log Work Author  记录日志的人，不一定是Assignee
    # Log Work Hour    工作时长
    # Log Work Day     记录日志的日期 2018/12/03 for example

    # 分离 第一个Log Work
    df['Log Work'] = df['Log Work'].fillna(" ; ; ; ")  # 把空白值填写；；；否则报错
    df_split['Log Work Content'], df['Log Work Date'], df_split['Log Work Author'], df_split['Log Work Hour'] = zip(
        *df['Log Work'].map(lambda x: x.split(';')))

    # 分离 第一个Log Work Date
    df_split['Log Work Day'] = '20' + df['Log Work Date'].str[7:9] + '/' + df['Log Work Date'].str[3:6].map(MONTHS) + '/' + \
                         df['Log Work Date'].str[0:2]

    # 分离 剩下的Log Work 和 Log Work Date
    for i in range(1, getRepetition('Log Work') + 1):
        df['Log Work.' + str(i)] = df['Log Work.' + str(i)].fillna(" ; ; ; ")
        df_split['Log Work Content.' + str(i)], df['Log Work Date.' + str(i)], df_split['Log Work Author.' + str(i)], df_split[
            'Log Work Hour.' + str(i)] = zip(*df['Log Work.' + str(i)].map(lambda x: x.split(';')))

        df_split['Log Work Day.' + str(i)] = '20' + df['Log Work Date.' + str(i)].str[7:9] + '/' + df['Log Work Date.' + str(i)].str[3:6].map(MONTHS) + '/' + df['Log Work Date.' + str(i)].str[0:2]

# 比如把Comment 到 Comment.2 合并到df_need 的Comment in All这个新的列中
def processMerge(name):
    df[name] = df[name].fillna(' ')
    df_merge[name + ' in All'] = df[name]
    for i in range(1, getRepetition(name) + 1):
        df[name + '.' + str(i)] = df[name + '.' + str(i)].fillna(' ')
        df_merge[name + ' in All'] = df_merge[name+' in All'].astype(str) + '\n' + df[name + '.' + str(i)].astype(str)

# 获取HEAD列表，根据根名相同去重
def getHeadUnique(df_in):
    HEAD = {}
    j = 0
    for i in range(0, len(df_in.columns)):
        if i == 0:
            HEAD.update({str(j): df_in.columns[i]})
            j = j + 1
        else:
            if (df_in.columns[i].find('.') == -1):
                HEAD.update({str(j): df_in.columns[i]})
                j = j + 1
    return HEAD

# 获取网页信息，Showing # changed files 等信息
def processURL(args):
    result = ' '
    for i in args:
        if (str(i).find('commit') != -1) and (str(i).find('github') != -1):
            r = requests.get(i)
            if r.text.find('deletions</strong>.') != -1:
                result = result + '\n' + i + '\n' + r.text[
                                                    r.text.find('Showing'):r.text.rfind('deletions</strong>.') + len(
                                                        'deletions</strong>.')]
            if r.text.find('deletion</strong>.') != -1:
                result = result + '\n' + i + '\n' + r.text[
                                                    r.text.find('Showing'):r.text.rfind('deletion</strong>.') + len(
                                                        'deletion</strong>.')]
    return result

'''global constants'''

MAX_DAY_LENGTH = 8   # 比如01/Jan/18 最后一位的index=8
MONTHS = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06', 'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}

'''gloabal dataframes'''

df = pd.read_csv('worklogTest.csv', encoding='utf-8')
df.to_csv('worklogTest.csv', index=False)
df = pd.read_csv('worklogTest.csv', encoding='utf-8')

df_split = pd.DataFrame()
df_merge = pd.DataFrame()
df_need = pd.DataFrame()
df_final = pd.DataFrame()

'''global variables'''
is_log_work = 0  # 存储用户是否选择了Log Work
HEAD1 = getHeadUnique(df)  # 预处理之前的Head字典,按照根名去重
out_put_name = ''


'''start'''
print(HEAD1)
print('\n\n')
print('Please input the key of columns you want, split by comma:')
columnsNeed = input().split(',')
print('\n')
print('The columns you need are:')
for i in columnsNeed:
    print(HEAD1[str(i)])

print('Please input start date, format year/month/day ####/##/##:')
start_day = input()
print('Please input end date, format year/month/day ####/##/##:')
end_day = input()


for j in columnsNeed:
    if HEAD1[str(j)] == 'Log Work':
        splitLogWork()
        is_log_work = 1

    elif getRepetition(HEAD1[str(j)]) > 0:
        processMerge(HEAD1[str(j)])
    else:
        df_need[HEAD1[str(j)]] = df[HEAD1[str(j)]]

if is_log_work == 1:
    df_final = pd.concat([df_need, df_merge], axis=1)
    df_final['Log Work Content'] = df_split['Log Work Content']
    df_final['Log Work Author'] = df_split['Log Work Author']
    df_final['Log Work Hour'] = df_split['Log Work Hour']
    df_final['Log Work Day'] = df_split['Log Work Day']

    for j in range(1, getRepetition('Log Work') + 1):
        df_middle = pd.DataFrame()
        df_middle = pd.concat([df_need, df_merge], axis=1)
        df_middle['Log Work Content'] = df_split['Log Work Content.'+str(j)]
        df_middle['Log Work Author'] = df_split['Log Work Author.'+str(j)]
        df_middle['Log Work Hour'] = df_split['Log Work Hour.'+str(j)]
        df_middle['Log Work Day'] = df_split['Log Work Day.'+str(j)]
        df_final = pd.concat([df_final, df_middle], ignore_index=True)

    df_final = df_final.loc[(df_final['Log Work Day'] >= start_day) & (df_final['Log Work Day'] <= end_day)]

    try:
        df_final['Log Work URL'] = df_final['Log Work Content'].apply(
            lambda x: re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+', str(x)))
        df_final['URL Content'] = df_final['Log Work URL'].apply(lambda x: processURL(x))
        df_final = df_final.drop(columns='Log Work URL')
        out_put_name = start_day[0:4] + start_day[5:7] + start_day[8:10] + 'To' + end_day[0:4] + end_day[5:7] + end_day[8:10] + 'PersonalStatistics_URL_SUCCESS.csv'
    except:
        out_put_name = start_day[0:4] + start_day[5:7] + start_day[8:10] + 'To' + end_day[0:4] + end_day[5:7] + end_day[8:10] + 'PersonalStatistics_URL_Failure.csv'
else:
    out_put_name = start_day[0:4] + start_day[5:7] + start_day[8:10] + 'To' + end_day[0:4] + end_day[5:7] + end_day[8:10] + 'PersonalStatistics.csv'


df_final.to_csv(out_put_name, index=False)

