# -*- coding: utf-8 -*-
import re
import datetime
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


#меняем английское название дня недели на русское
def getDbName():
    dbname = datetime.datetime.now().strftime("%A_%d.%m.%Y_%H-%M-%S")+'.db'
    days={'Monday':'Понедельник','Tuesday':'Вторник','Wednesday':'Среда',
         'Thursday':'Четверг','Friday':'Пятница','Saturday':'Суббота','Sunday':'Воскресенье'}
    
    pattern=r'(^[a-zA-Z]+)'
    dayOfWeek=re.search(pattern,dbname).group(0)
    dbname=dbname.replace(dayOfWeek,days[dayOfWeek])
    return(dbname)





#создаем подключение к БД
def createDb(dbname,root):
    conn=sqlite3.connect(root+dbname)
    cursor=conn.cursor()
    return(conn,cursor)



#считываем запросы из файла
def getQueriesFromFile(filename):
    queries=[]
    file=open(filename,'r')
    for line in file:
        if line!=None and line!='' and line!='\n':
            queries.append(line)
        
    for i in range(len(queries)):
        queries[i]=queries[i].replace('\n','')
        
    return(queries)



#построение и сохранение графиков
def queriesLikesDia(dbname,path,root):
    sql="SELECT DISTINCT queryText, totalLikeCount FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID ORDER BY totalLikeCount DESC"
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    cursor.execute(sql)
    data=cursor.fetchall()
    query=[]
    likes=[]
    for row in data:
        query.append(row[0])
        likes.append(row[1])
    df=pd.DataFrame()
    df['Запросы']=query
    df['Лайки']=likes
    ax=df.plot(x='Запросы',kind='bar', color='tomato', title='Запросы по убыванию лайков',legend=True,figsize=(len(query), 8),grid=True)
    ax.set(xlabel="Запросы", ylabel="Лайки")
    plt.tight_layout()
    plt.savefig(path+'\\1.png')
    conn.close()



def queriesDislikesDia(dbname,path,root):
    sql="SELECT DISTINCT queryText, totalDislikeCount FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID ORDER BY totalDislikeCount DESC"
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    cursor.execute(sql)
    data=cursor.fetchall()
    query=[]
    dislikes=[]
    for row in data:
        query.append(row[0])
        dislikes.append(row[1])
    df=pd.DataFrame()
    df['Запросы']=query
    df['Дизлайки']=dislikes
    ax=df.plot(x='Запросы',kind='bar', color='deepskyblue', title='Запросы по убыванию дизлайков',legend=True,figsize=(len(query), 8),grid=True)
    ax.set(xlabel="Запросы", ylabel="Дизлайки")
    plt.tight_layout()
    plt.savefig(path+'\\2.png')
    conn.close()



def queriesCommentsDia(dbname,path,root):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="SELECT DISTINCT queryText, totalCommentCount FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID ORDER BY totalCommentCount DESC"
    cursor.execute(sql)
    data=cursor.fetchall()
    query=[]
    comments=[]
    for row in data:
        query.append(row[0])
        comments.append(row[1])
    df=pd.DataFrame()
    df['Запросы']=query
    df['Комментарии']=comments
    ax=df.plot(x='Запросы',kind='bar', color='magenta', title='Запросы по убыванию комментариев',legend=True,figsize=(len(query), 8),grid=True)
    ax.set(xlabel="Запросы", ylabel="Комментарии")
    plt.tight_layout()
    plt.savefig(path+'\\3.png')
    conn.close()




def queriesViewsDia(dbname,path,root):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="SELECT DISTINCT queryText, totalViewCount FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID ORDER BY totalViewCount DESC"
    cursor.execute(sql)
    data=cursor.fetchall()
    query=[]
    views=[]
    for row in data:
        query.append(row[0])
        views.append(row[1])
    
    df=pd.DataFrame()
    df['Запросы']=query
    df['Просмотры']=views
    ax=df.plot(x='Запросы',kind='bar',color='gold', title='Запросы по убыванию просмотров',legend=True,figsize=(len(query), 8),grid=True)
    ax.set(xlabel="Запросы", ylabel="Просмотры")
    plt.tight_layout()
    plt.savefig(path+'\\4.png')
    conn.close()


#генерируем красивое понятное отображение даты для дальнейшего отображения в отчете
def dateConverter(dbname):
    days={'Понедельник':'понедельник','Вторник':'вторник','Среда':'среду',
      'Четверг':'четверг','Пятница':'пятницу','Суббота':'субботу','Воскресенье':'воскресенье'}
    pattern=r'(^[а-яА-Я]+)'
    dayOfWeek=re.search(pattern,dbname).group(0)
    months={'1':'января','2':'февраля','3':'марта','4':'апреля','5':'мая','6':'июня','7':'июля','8':'августа','9':'сентября',
            '10':'октября','11':'ноября','12':'декабря'}
    date=days[dayOfWeek]+' '+str(datetime.datetime.now().day)+' '+months[str(datetime.datetime.now().month)]+' '+str(datetime.datetime.now().year)+'г.'
    return(date)





#получаем максимальное кол-во лайков, дизлайков, комментов и просмотров
#а также ссылки для дальнейшей вставки соответствующих видео в отчет
def getLikeEmbeds(dbname,path,root):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="SELECT q.queryID,MAX(likeCount), embed FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID GROUP BY q.queryID"
    cursor.execute(sql)
    data=cursor.fetchall()
    likes=[]
    likesEmbeds=[]
    for row in data:
        likes.append(row[1])
        likesEmbeds.append(row[2])
    conn.close()
    return(likes,likesEmbeds)


def getDislikeEmbeds(dbname,path,root):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="SELECT q.queryID,MAX(dislikeCount), embed FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID GROUP BY q.queryID"
    cursor.execute(sql)
    data=cursor.fetchall()
    dislikes=[]
    dislikesEmbeds=[]
    for row in data:
        dislikes.append(row[1])
        dislikesEmbeds.append(row[2])
    conn.close()
    return(dislikes,dislikesEmbeds)


def getCommentEmbeds(dbname,path,root):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="SELECT q.queryID,MAX(commentCount), embed FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID GROUP BY q.queryID"
    cursor.execute(sql)
    data=cursor.fetchall()
    comments=[]
    commentEmbeds=[]
    for row in data:
        comments.append(row[1])
        commentEmbeds.append(row[2])
    conn.close()
    return(comments,commentEmbeds)


def getViewEmbeds(dbname,path,root):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="SELECT q.queryID,MAX(viewCount),embed FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID GROUP BY q.queryID"
    cursor.execute(sql)
    data=cursor.fetchall()
    views=[]
    viewEmbeds=[]
    for row in data:
        views.append(row[1])
        viewEmbeds.append(row[2])
    conn.close()
    return(views,viewEmbeds)


















































