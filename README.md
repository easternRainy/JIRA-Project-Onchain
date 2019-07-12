# JIRA_Project_Management_Onchain
'''
这个程序目的是简化Onchain周报的工作流程
使用方法：
1. 在Jira的Search Issue中初步筛选，导出csv文件，并放入工作目录中，更名为worklogTest.csv
   搜索命令为：worklogDate >= "2019/07/02" AND worklogDate <= "2019/07/08" AND worklogAuthor in membersOf(jira-software-users) ORDER BY assignee
   需要更改日期
2. 运行程序，输入需要的column编号， 如果输入000则为默认值0,6,24,27,62（不一定适用，因为每次生成的csv字段数量不确定）
所需字段包括Summary、Project key、Description、Log Work、Custom field (gitBranch)
请在程序输入列表中寻找每个字段对应编号并输入
3. 输入起始时间 年/月/日 ****/**/**
4. 输入截止时间 年/月/日 ****/**/**
5. 程序会尝试从工作人员logwork的内容中提取链接，并登陆链接读取工作人员在github上增删记录
6. 如果5成功，则输出文件为 startdayToenddayPersonalStatistics_URL_SUCCESS.csv
7. 如果5失败，则输出文件为 startdayToenddayPersonalStatistics_URL_FAILURE.csv
8. 最后一列为累计工作时长，只需要关注某工作人员累计时长最后一项即可判断（for walter ^-^）

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
