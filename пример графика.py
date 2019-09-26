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
    print(data)
    query=[]
    likes=[]
    for row in data:
        query.append(row[0])
        likes.append(row[1])
    
    print (query)
    print(likes)
    
        
    conn.close()
    
    df=pd.DataFrame()
    df['Запросы']=query
    df['Лайки']=likes
    ax=df.plot(x='Запросы',kind='bar', title='Запросы по убыванию лайков',legend=True,figsize=(len(query), 5),grid=True)
    ax.set(xlabel="Запросы", ylabel="Лайки")
    
    
    
if __name__ == "__main__":
    kowalski()