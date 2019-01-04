# JIRA_Project_Management_Onchain
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
