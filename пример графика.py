import sqlite3
import datetime
import re
import pandas as pd

dbname = datetime.datetime.now().strftime("%A_%d-%m-%Y")
days={'Monday':'Понедельник','Tuesday':'Вторник','Wednesday':'Среда',
      'Thursday':'Четверг','Friday':'Пятница','Saturday':'Суббота','Sunday':'Воскресенье'}

pattern=r'(^[a-zA-Z]+)'
dayOfWeek=re.search(pattern,dbname).group(0)
dbname=dbname.replace(dayOfWeek,days[dayOfWeek])

conn=sqlite3.connect(dbname+".db")
cursor=conn.cursor()

def kowalski():
    
    
    sql="SELECT DISTINCT queryText, totalLikeCount FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID ORDER BY totalLikeCount DESC"
    cursor.execute(sql)
    data=cursor.fetchall()
    #print(data)
    query=[]
    likes=[]
    for row in data:
        query.append(row[0])
        likes.append(row[1])
    
    df=pd.DataFrame()
    df['Запросы']=query
    df['Лайки']=likes
    ax=df.plot(x='Запросы',kind='bar', title='Запросы по убыванию лайков',legend=True,figsize=(len(query), 5),grid=True)
    ax.set(xlabel="Запросы", ylabel="Лайки")
    
    sql="SELECT DISTINCT queryText, totalDislikeCount FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID ORDER BY totalDislikeCount DESC"
    cursor.execute(sql)
    data=cursor.fetchall()
    query.clear()
    dislikes=[]
    for row in data:
        query.append(row[0])
        dislikes.append(row[1])
    
    df=pd.DataFrame()
    df['Запросы']=query
    df['Дизлайки']=dislikes
    ax=df.plot(x='Запросы',kind='bar', title='Запросы по убыванию дизлайков',legend=True,figsize=(len(query), 5),grid=True)
    ax.set(xlabel="Запросы", ylabel="Дизлайки")
    
    sql="SELECT DISTINCT queryText, totalCommentCount FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID ORDER BY totalCommentCount DESC"
    cursor.execute(sql)
    data=cursor.fetchall()
    query.clear()
    comments=[]
    for row in data:
        query.append(row[0])
        comments.append(row[1])
    
    df=pd.DataFrame()
    df['Запросы']=query
    df['Комментарии']=comments
    ax=df.plot(x='Запросы',kind='bar', title='Запросы по убыванию комментариев',legend=True,figsize=(len(query), 5),grid=True)
    ax.set(xlabel="Запросы", ylabel="Комментарии")
    
    sql="SELECT DISTINCT queryText, totalViewCount FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID ORDER BY totalViewCount DESC"
    cursor.execute(sql)
    data=cursor.fetchall()
    #print(data)
    query.clear()
    views=[]
    for row in data:
        query.append(row[0])
        views.append(row[1])
    
    df=pd.DataFrame()
    df['Запросы']=query
    df['Просмотры']=views
    ax=df.plot(x='Запросы',kind='bar', title='Запросы по убыванию просмотров',legend=True,figsize=(len(query), 5),grid=True)
    ax.set(xlabel="Запросы", ylabel="Просмотры")
    
        
    conn.close()
    
    
    
    
    
if __name__ == "__main__":
    kowalski()