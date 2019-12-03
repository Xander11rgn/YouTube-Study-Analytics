# -*- coding: utf-8 -*-
import re
import datetime
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt, matplotlib.ticker
import jinja2
from pytrends.request import TrendReq



#меняем английское название дня недели на русское
def getDbName():
    dbname = datetime.datetime.now().strftime("%A_%d.%m.%Y_%H-%M-%S")+'.db'
    days={'Monday':'Понедельник','Tuesday':'Вторник','Wednesday':'Среда',
         'Thursday':'Четверг','Friday':'Пятница','Saturday':'Суббота','Sunday':'Воскресенье'}
    
    pattern=r'(^[a-zA-Z]+)'
    dayOfWeek=re.search(pattern,dbname).group(0)
    dbname=dbname.replace(dayOfWeek,days[dayOfWeek])
    return(dbname)





#создаем подключение к БД и наполняем ее таблицами

def createDb(dbname,root):
    conn=sqlite3.connect(root+dbname)
    cursor=conn.cursor()
    return(conn,cursor)

#после каждого запроса, меняющего содержимое БД - коммит
def fullfillDb(cursor,conn):
    cursor.execute("CREATE TABLE query (queryID PRIMARY KEY, queryText text NOT NULL)")
    conn.commit()
    cursor.execute("""CREATE TABLE result 
                   (resultID  NOT NULL, 
                   totalVideoCount  NOT NULL,
                   totalLikeCount  NOT NULL,
                   totalDislikeCount  NOT NULL,
                   totalCommentCount  NOT NULL,
                   totalViewCount  NOT NULL,
                   queryID  NOT NULL,
                   FOREIGN KEY (queryID) REFERENCES query (queryID))""")
    conn.commit()
    cursor.execute("""CREATE TABLE video 
                   (url text NOT NULL,
                    embed text NOT NULL,
                   title text NOT NULL,
                   likeCount  NOT NULL,
                   dislikeCount  NOT NULL,
                   commentCount  NOT NULL,
                   viewCount  NOT NULL,
                   date NULL,
                   queryID  NOT NULL,
                   FOREIGN KEY (queryID) REFERENCES query (queryID))""")
    conn.commit()


#считываем запросы из файла
def getQueriesFromFile(filename):
    queries=[]
    file=open(filename,'r', encoding='cp1251')
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
    plt.savefig(path+'\\1.png',bbox_inches='tight')
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
    plt.savefig(path+'\\2.png',bbox_inches='tight')
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
    plt.savefig(path+'\\3.png',bbox_inches='tight')
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
    plt.savefig(path+'\\4.png',bbox_inches='tight')
    conn.close()


def getLikesPerViews(dbname,root):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="SELECT DISTINCT queryText, totalLikeCount, totalViewCount from query q JOIN result r ON q.queryID=r.queryID"
    cursor.execute(sql)
    data=cursor.fetchall()
    query=[]
    likes=[]
    views=[]
    for row in data:
        query.append(row[0])
        likes.append(row[1])
        views.append(row[2])
    
    likePerView=[]
    for i in range(len(query)):
        if views[i]==0:
            likePerView.append('YouTube выдал некорректные данные по данному запросу')
        else:
            likePerView.append(round(likes[i]/views[i],5))
    conn.close()
    return(likePerView)

def likesPerViewsDia(dbname,path,root):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="SELECT DISTINCT queryText, totalLikeCount, totalViewCount from query q JOIN result r ON q.queryID=r.queryID"
    cursor.execute(sql)
    data=cursor.fetchall()
    query=[]
    likes=[]
    views=[]
    for row in data:
        query.append(row[0])
        likes.append(row[1])
        views.append(row[2])
    
    likePerView=[]
    for i in range(len(query)):
        if views[i]==0:
            #likePerView.append(0)
            query.remove(query[i])
            continue
        else:
            likePerView.append(likes[i]/views[i])
    
    
    df=pd.DataFrame()
    df['Запросы']=query
    df['Лайк/Просмотр']=likePerView
    df=df.sort_values(['Лайк/Просмотр'],ascending=False)
    ax=df.plot(x='Запросы',kind='bar', color='red', title='Среднее количество лайков на один просмотр',legend=True,figsize=(len(query), 8),grid=True)
    ax.set(xlabel="Запросы", ylabel="Лайк на просмотр")
    plt.savefig(path+'\\5.png',bbox_inches='tight')
    conn.close()



def getDislikesPerViews(dbname,root):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="SELECT DISTINCT queryText, totalDislikeCount, totalViewCount from query q JOIN result r ON q.queryID=r.queryID"
    cursor.execute(sql)
    data=cursor.fetchall()
    query=[]
    dislikes=[]
    views=[]
    for row in data:
        query.append(row[0])
        dislikes.append(row[1])
        views.append(row[2])
    
    dislikePerView=[]
    for i in range(len(query)):
        if views[i]==0:
            dislikePerView.append('YouTube выдал некорректные данные по данному запросу')
        else:
            dislikePerView.append(round(dislikes[i]/views[i],5))
    conn.close()
    return(dislikePerView)

def dislikesPerViewsDia(dbname,path,root):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="SELECT DISTINCT queryText, totalDislikeCount, totalViewCount from query q JOIN result r ON q.queryID=r.queryID"
    cursor.execute(sql)
    data=cursor.fetchall()
    query=[]
    dislikes=[]
    views=[]
    for row in data:
        query.append(row[0])
        dislikes.append(row[1])
        views.append(row[2])
    
    dislikePerView=[]
    for i in range(len(query)):
        if views[i]==0:
            query.remove(query[i])
            continue
            #dislikePerView.append(0)
        else:
            dislikePerView.append(dislikes[i]/views[i])
    
    
    df=pd.DataFrame()
    df['Запросы']=query
    df['Дизлайк/Просмотр']=dislikePerView
    df=df.sort_values(['Дизлайк/Просмотр'],ascending=False)
    ax=df.plot(x='Запросы',kind='bar', color='purple', title='Среднее количество дизлайков на один просмотр',legend=True,figsize=(len(query), 8),grid=True)
    ax.set(xlabel="Запросы", ylabel="Дизлайк на просмотр")
    plt.savefig(path+'\\6.png',bbox_inches='tight')
    conn.close()



def getLikesPerDislikes(dbname,root):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="SELECT DISTINCT queryText, totalDislikeCount, totalLikeCount from query q JOIN result r ON q.queryID=r.queryID"
    cursor.execute(sql)
    data=cursor.fetchall()
    query=[]
    dislikes=[]
    likes=[]
    for row in data:
        query.append(row[0])
        dislikes.append(row[1])
        likes.append(row[2])
    
    likePerDislike=[]
    for i in range(len(query)):
        if dislikes[i]==0:
            likePerDislike.append('YouTube выдал некорректные данные по данному запросу')
        else:
            likePerDislike.append(round(likes[i]/dislikes[i],1))
    conn.close()
    return(likePerDislike)


def likesPerDislikeViewsDia(dbname,path,root):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="SELECT DISTINCT queryText, totalDislikeCount, totalLikeCount from query q JOIN result r ON q.queryID=r.queryID"
    cursor.execute(sql)
    data=cursor.fetchall()
    query=[]
    dislikes=[]
    likes=[]
    for row in data:
        query.append(row[0])
        dislikes.append(row[1])
        likes.append(row[2])
    
    likePerDislike=[]
    for i in range(len(query)):
        if dislikes[i]==0:
#            likePerDislike.append(0)
            query.remove(query[i])
            continue
        else:
            likePerDislike.append(likes[i]/dislikes[i])
    
    
    df=pd.DataFrame()
    df['Запросы']=query
    df['Лайк/Дизлайк']=likePerDislike
    df=df.sort_values(['Лайк/Дизлайк'],ascending=False)
    ax=df.plot(x='Запросы',kind='bar', color='grey', title='Отношение лайков к дизлайкам',legend=True,figsize=(len(query), 8),grid=True)
    ax.set(xlabel="Запросы", ylabel="Лайк/Дизлайк")
    plt.savefig(path+'\\7.png',bbox_inches='tight')
    conn.close()


def getLastHalfYear(dbname,root):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="""SELECT queryText from query"""
    cursor.execute(sql)
    data=cursor.fetchall()
    query=[]
    for row in data:
        query.append(row[0])
    videoCount=[0 for i in range(len(query))]
    sql="""SELECT q.queryID, queryText, COUNT(v.date) from query q JOIN video v ON q.queryID=v.queryID 
        WHERE v.date>=date('now','-6 months') GROUP BY queryText ORDER BY q.queryID"""
    cursor.execute(sql)
    data=cursor.fetchall()
    queryBase=[]
    videoCountBase=[]
    for row in data:
        queryBase.append(row[1])
        videoCountBase.append(row[2])
    for i in range(len(query)):
        for j in range(len(queryBase)):
            if query[i]==queryBase[j]:
                videoCount[i]=videoCountBase[j]
                break
    conn.close()
    return(videoCount)

def lastHalfYearDia(dbname,path,root):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="""SELECT q.queryID, queryText, COUNT(v.date) from query q JOIN video v ON q.queryID=v.queryID 
        WHERE v.date>=date('now','-6 months') GROUP BY queryText ORDER BY q.queryID"""
    cursor.execute(sql)
    data=cursor.fetchall()
    query=[]
    videoCount=[]
    for row in data:
        query.append(row[1])
        videoCount.append(row[2])
        
    df=pd.DataFrame()
    df['Запросы']=query
    df['Количество видео']=videoCount
    df=df.sort_values(['Количество видео'],ascending=False)
    ax=df.plot(x='Запросы',kind='bar', color='orange', title='Количество видео за последние полгода',legend=True,figsize=(len(query), 8),grid=True)
    ax.set(xlabel="Запросы", ylabel="Количество видео")
    plt.savefig(path+'\\8.png',bbox_inches='tight')
    conn.close()

def queryTrendsDia(queryTrends,path):

    for i in range(len(queryTrends)):
        pytrends = TrendReq()
        tempQuery=[]
        tempQuery.append(queryTrends[i])
        pytrends.build_payload(tempQuery, cat=0, timeframe='all', geo='RU', gprop='')
        df = pytrends.interest_over_time()
        if df.empty:
            df = pd.DataFrame()
            df['X'] = [0]
            df['Y'] = [0]
            ax = df.plot(title='Популярность запроса "' + queryTrends[i] + '" (данные не были получены!)', legend=True, figsize=(12, 8))
            ax.set(xlabel="X", ylabel="Y")
            plt.savefig(path + '\\' + str(i + len(queryTrends) + 9) + '.png', bbox_inches='tight')
        else:
            ax=df.plot(title='Популярность запроса "' + queryTrends[i]+'"',legend=True,figsize=(12, 8))
            ax.set(xlabel="Года", ylabel="Количество запросов")
            plt.savefig(path+'\\'+str(i+len(queryTrends)+9)+'.png',bbox_inches='tight')


#по полугодиям за последние 3 года
def videosPerLastYearDia(dbname,path,root):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="""SELECT queryText from query"""
    cursor.execute(sql)
    data=cursor.fetchall()
    query=[]
    for row in data:
        query.append(row[0])

    curMonth=datetime.datetime.now().month

    pg=['1\n\n'+str(datetime.datetime.now().year-3)+' год','2','3','4','5','6\n\n'+str(datetime.datetime.now().year)+' год']


    n=0
    for i in range(len(query)):
        videos=[0 for i in range(6)]
        for y in range(6):
            sql="""SELECT date(v.date) from query q JOIN video v ON q.queryID=v.queryID 
            WHERE date('now','-"""+str(y*6)+ """ months','+1 day')>=v.date AND v.date>=date('now','-"""+str((y+1)*6)+ """ months') AND queryText='"""+query[i]+"""'"""
            cursor.execute(sql)
            data=cursor.fetchall()
            dates=[]
            for row in data:
                dates.append(row[0])
            videosPerHalfYear=[0 for h in range(12)]
            for j in range(curMonth-1,12):
                for k in range(len(dates)):
                    if datetime.datetime.strptime(dates[k],'%Y-%m-%d').month==j+1:
                        videosPerHalfYear[j-curMonth+1]=videosPerHalfYear[j-curMonth+1]+1
            for j in range(0,curMonth-1):
                for k in range(len(dates)):
                    if datetime.datetime.strptime(dates[k],'%Y-%m-%d').month==j+1:
                        videosPerHalfYear[13-curMonth+j]=videosPerHalfYear[13-curMonth+j]+1
            videos[5-y]=sum(videosPerHalfYear)
        if sum(videos)==0:
            continue
        df=pd.DataFrame()
        df['Полугодия']=pg
        df['Количество видео']=videos
        ax=df.plot(x='Полугодия', kind='bar',y='Количество видео', color='green', title='Динамика добавления видео по полугодиям за последние 3 года по запросу «'+query[i]+'»',legend=True,figsize=(12, 9),grid=True)
        ax.set(xlabel="Полугодия", ylabel="Количество видео")
        formatter = matplotlib.ticker.MaxNLocator(integer=True)
        ax.yaxis.set_major_locator (formatter)
        plt.savefig(path+'\\'+str(n+9)+'.png',bbox_inches='tight')
        n=n+1
    conn.close()

#по месяцам за последний год
#def videosPerLastYearDia(dbname,path,root):
#    conncurs=createDb(dbname,root)
#    conn=conncurs[0]
#    cursor=conncurs[1]
#    sql="""SELECT queryText from query"""
#    cursor.execute(sql)
#    data=cursor.fetchall()
#    query=[]
#    for row in data:
#        query.append(row[0])
#
#    monthsMain={'1':'Январь','2':'Февраль','3':'Март','4':'Апрель','5':'Май','6':'Июнь','7':'Июль','8':'Август',
#            '9':'Сентябрь','10':'Октябрь','11':'Ноябрь','12':'Декабрь'}
#    monthIndexes=[0,1,2,3,4,5,6,7,8,9,10,11]
#
#    curMonth=datetime.datetime.now().month
#    months=[]
#    for i in range(curMonth,13):
#        months.append(monthsMain[str(i)])
#
#    for i in range(1,curMonth):
#        months.append(monthsMain[str(i)])
#
#    months[0]=months[0]+'\n\n'+str(datetime.datetime.now().year-1)+' год'
#    if datetime.datetime.now().month==1:
#        months[11]=months[11]+'\n\n'+str(datetime.datetime.now().year-1)+' год'
#    else:
#        months[11]=months[11]+'\n\n'+str(datetime.datetime.now().year)+' год'
#
#    for i in range(len(query)):
#        sql="""SELECT date(v.date) from query q JOIN video v ON q.queryID=v.queryID
#        WHERE v.date>=date('now','-3 year','+1 day') AND queryText='"""+query[i]+"""'"""
#        cursor.execute(sql)
#        data=cursor.fetchall()
#        dates=[]
#        for row in data:
#            dates.append(row[0])
#        videosPerMonths=[0 for h in range(12)]
#        for j in range(curMonth-1,12):
#            for k in range(len(dates)):
#                if datetime.datetime.strptime(dates[k],'%Y-%m-%d').month==j+1:
#                    videosPerMonths[j-curMonth+1]=videosPerMonths[j-curMonth+1]+1
#        for j in range(0,curMonth-1):
#            for k in range(len(dates)):
#                if datetime.datetime.strptime(dates[k],'%Y-%m-%d').month==j+1:
#                    videosPerMonths[13-curMonth+j]=videosPerMonths[13-curMonth+j]+1
#        df=pd.DataFrame()
#        df['Месяца']=months
#        df['Количество видео']=videosPerMonths
#        ax=df.plot(x='Месяца',kind='bar', y='Количество видео', xticks=monthIndexes, color='green', title='Динамика за последний год по запросу «'+query[i]+'»',legend=True,figsize=(12, 9),grid=True)
#        ax.set(xlabel="Месяца", ylabel="Количество видео")
#        formatter = matplotlib.ticker.MaxNLocator(integer=True)
#        ax.yaxis.set_major_locator (formatter)
#        plt.tight_layout()
#        plt.savefig(path+'\\'+str(i+9)+'.png')
#    conn.close()



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
    sql="""SELECT queryID from query"""
    cursor.execute(sql)
    data=cursor.fetchall()
    queryID=[]
    for row in data:
        queryID.append(row[0])
    likes=[0 for i in range(len(queryID))]
    likesEmbeds=['' for i in range(len(queryID))]
    sql="SELECT q.queryID,MAX(likeCount), embed FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID GROUP BY q.queryID"
    cursor.execute(sql)
    data=cursor.fetchall()
    queryIDBase=[]
    likesBase=[]
    likesEmbedsBase=[]
    for row in data:
        queryIDBase.append(row[0])
        likesBase.append(row[1])
        likesEmbedsBase.append(row[2])
    for i in range(len(queryID)):
        for j in range(len(queryIDBase)):
            if queryID[i]==queryIDBase[j]:
                likes[i]=likesBase[j]
                likesEmbeds[i]=likesEmbedsBase[j]
                break
    likes=[x for x in likes if x!=0]
    likesEmbeds=[x for x in likesEmbeds if x!='']
    conn.close()
    return(likes,likesEmbeds)
    
def blabla(dbname,root,n):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="""SELECT queryID from query"""
    cursor.execute(sql)
    data=cursor.fetchall()
    queryID=[]
    for row in data:
        queryID.append(row[0])
    likes=[[] for i in range(len(queryID))]
    likesEmbeds=[[] for i in range(len(queryID))]
    for id in queryID:
        sql="SELECT likeCount, embed FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID WHERE q.queryID="+str(id)+" ORDER BY likeCount desc LIMIT "+str(n)
        cursor.execute(sql)
        data=cursor.fetchall()
        for row in data:
           likes[id-1].append(row[0])
           likesEmbeds[id-1].append(row[1])
#    likes=[x for x in likes if x!=0]
#    likesEmbeds=[x for x in likesEmbeds if x!='']
    conn.close()
    return(likes,likesEmbeds)


def getDislikeEmbeds(dbname,path,root):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="""SELECT queryID from query"""
    cursor.execute(sql)
    data=cursor.fetchall()
    queryID=[]
    for row in data:
        queryID.append(row[0])
    dislikes=[0 for i in range(len(queryID))]
    dislikesEmbeds=['' for i in range(len(queryID))]
    sql="SELECT q.queryID,MAX(dislikeCount), embed FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID GROUP BY q.queryID"
    cursor.execute(sql)
    data=cursor.fetchall()
    queryIDBase=[]
    dislikesBase=[]
    dislikesEmbedsBase=[]
    for row in data:
        queryIDBase.append(row[0])
        dislikesBase.append(row[1])
        dislikesEmbedsBase.append(row[2])
    for i in range(len(queryID)):
        for j in range(len(queryIDBase)):
            if queryID[i]==queryIDBase[j]:
                dislikes[i]=dislikesBase[j]
                dislikesEmbeds[i]=dislikesEmbedsBase[j]
                break
    dislikes=[x for x in dislikes if x!=0]
    dislikesEmbeds=[x for x in dislikesEmbeds if x!='']
    conn.close()
    return(dislikes,dislikesEmbeds)
    
def blabla1(dbname,root,n):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="""SELECT queryID from query"""
    cursor.execute(sql)
    data=cursor.fetchall()
    queryID=[]
    for row in data:
        queryID.append(row[0])
    dislikes=[[] for i in range(len(queryID))]
    dislikesEmbeds=[[] for i in range(len(queryID))]
    for id in queryID:
        sql="SELECT dislikeCount, embed FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID WHERE q.queryID="+str(id)+" ORDER BY dislikeCount desc LIMIT "+str(n)
        cursor.execute(sql)
        data=cursor.fetchall()
        for row in data:
           dislikes[id-1].append(row[0])
           dislikesEmbeds[id-1].append(row[1])
#    likes=[x for x in likes if x!=0]
#    likesEmbeds=[x for x in likesEmbeds if x!='']
    conn.close()
    return(dislikes,dislikesEmbeds)    


def getCommentEmbeds(dbname,path,root):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="""SELECT queryID from query"""
    cursor.execute(sql)
    data=cursor.fetchall()
    queryID=[]
    for row in data:
        queryID.append(row[0])
    comments=[0 for i in range(len(queryID))]
    commentEmbeds=['' for i in range(len(queryID))]
    sql="SELECT q.queryID,MAX(commentCount), embed FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID GROUP BY q.queryID"
    cursor.execute(sql)
    data=cursor.fetchall()
    queryIDBase=[]
    commentsBase=[]
    commentEmbedsBase=[]
    for row in data:
        queryIDBase.append(row[0])
        commentsBase.append(row[1])
        commentEmbedsBase.append(row[2])
    for i in range(len(queryID)):
        for j in range(len(queryIDBase)):
            if queryID[i]==queryIDBase[j]:
                comments[i]=commentsBase[j]
                commentEmbeds[i]=commentEmbedsBase[j]
                break
    comments=[x for x in comments if x!=0]
    commentEmbeds=[x for x in commentEmbeds if x!='']
    conn.close()
    return(comments,commentEmbeds)
    
    
def blabla2(dbname,root,n):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="""SELECT queryID from query"""
    cursor.execute(sql)
    data=cursor.fetchall()
    queryID=[]
    for row in data:
        queryID.append(row[0])
    comments=[[] for i in range(len(queryID))]
    commentEmbeds=[[] for i in range(len(queryID))]
    for id in queryID:
        sql="SELECT commentCount, embed FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID WHERE q.queryID="+str(id)+" ORDER BY commentCount desc LIMIT "+str(n)
        cursor.execute(sql)
        data=cursor.fetchall()
        for row in data:
           comments[id-1].append(row[0])
           commentEmbeds[id-1].append(row[1])
#    likes=[x for x in likes if x!=0]
#    likesEmbeds=[x for x in likesEmbeds if x!='']
    conn.close()
    return(comments,commentEmbeds)  


def getViewEmbeds(dbname,path,root):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="""SELECT queryID,queryText from query"""
    cursor.execute(sql)
    data=cursor.fetchall()
    queryID=[]
    query=[]
    for row in data:
        queryID.append(row[0])
        query.append(row[1])
    views=[0 for i in range(len(queryID))]
    viewEmbeds=['' for i in range(len(queryID))]
    sql="SELECT q.queryID,MAX(viewCount),embed FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID GROUP BY q.queryID"
    cursor.execute(sql)
    data=cursor.fetchall()
    queryIDBase=[]
    viewsBase=[]
    viewEmbedsBase=[]
    for row in data:
        queryIDBase.append(row[0])
        viewsBase.append(row[1])
        viewEmbedsBase.append(row[2])
    for i in range(len(queryID)):
        for j in range(len(queryIDBase)):
            if queryID[i]==queryIDBase[j]:
                views[i]=viewsBase[j]
                viewEmbeds[i]=viewEmbedsBase[j]
                break
    views=[x for x in views if x!=0]
    viewEmbeds=[x for x in viewEmbeds if x!='']
    queriesEmbed =[]
    for i in range(len(queryID)):
        if queryID[i] in queryIDBase:
            queriesEmbed.append(query[i])
    conn.close()
    return(views,viewEmbeds,queriesEmbed)



def blabla3(dbname,root,n):
    conncurs=createDb(dbname,root)
    conn=conncurs[0]
    cursor=conncurs[1]
    sql="""SELECT queryID,queryText from query"""
    cursor.execute(sql)
    data=cursor.fetchall()
    queryID=[]
    query=[]
    for row in data:
        queryID.append(row[0])
        query.append(row[1])
    views=[[] for i in range(len(queryID))]
    viewEmbeds=[[] for i in range(len(queryID))]
    for id in queryID:
        sql="SELECT viewCount, embed FROM query q JOIN result r ON q.queryID=r.queryID JOIN video v ON r.queryID=v.queryID WHERE q.queryID="+str(id)+" ORDER BY viewCount desc LIMIT "+str(n)
        cursor.execute(sql)
        data=cursor.fetchall()
        for row in data:
           views[id-1].append(row[0])
           viewEmbeds[id-1].append(row[1])
#    likes=[x for x in likes if x!=0]
#    likesEmbeds=[x for x in likesEmbeds if x!='']
    conn.close()
    return(views,viewEmbeds,query)  




def htmlGenerator(images,images1,images2,dbname,date,queries,queriesEmbed,totalVideos,root,totalLikes,
                  totalDislikes,totalComments,totalViews,maxLikeEmbeds,maxDislikeEmbeds,
                  maxCommentsEmbeds,maxViewsEmbeds,maxLikes,maxDislikes,maxComments,maxViews,
                  meanLikesViews,meanDislikesViews,likesPerDislikes,lastHalfYear,n):
    template=jinja2.Template("""
                             <html>
                                 <head>
                                 <style>
    /*!
     * chiefSlider (https://itchief.ru/lessons/php/feedback-form-for-website)
     * Copyright 2018 Alexander Maltsev
     * Licensed under MIT (https://github.com/itchief/feedback-form/blob/master/LICENSE)
     */

    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
      color: #0;
      height: 300px;
    }

    .slider {
      position: relative;
      overflow: hidden;
    }
    .slider1 {
      position: relative;
      overflow: hidden;
    }
    
    .slider2 {
      position: relative;
      overflow: hidden;
    }
    {% for i in range(length) %}
        .slider{{i+3}} {
      position: relative;
      overflow: hidden;
    }
        
    {% endfor %}

    .slider__wrapper {
      display: flex;
      transition: transform 0.6s ease;
    }

    .slider__item {
      flex: 0 0 100%;
      max-width: 100%;
    }

    .slider__control {
      position: absolute;
      top: 50%;
      display: none;
      align-items: center;
      justify-content: center;
      width: 40px;
      color: #fff;
      text-align: center;
      opacity: 0.5;
      height: 50px;
      transform: translateY(-50%);
      background: rgba(0, 0, 0, .5);
    }

    .slider__control_show {
      display: flex;
    }

    .slider__control:hover,
    .slider__control:focus {
      color: #fff;
      text-decoration: none;
      outline: 0;
      opacity: .9;
    }

    .slider__control_left {
      left: 0;
    }

    .slider__control_right {
      right: 0;
    }

    .slider__control::before {
      content: '';
      display: inline-block;
      width: 20px;
      height: 20px;
      background: transparent no-repeat center center;
      background-size: 100% 100%;
    }

    .slider__control_left::before {
      background-image: url("data:image/svg+xml;charset=utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%23fff' viewBox='0 0 8 8'%3E%3Cpath d='M5.25 0l-4 4 4 4 1.5-1.5-2.5-2.5 2.5-2.5-1.5-1.5z'/%3E%3C/svg%3E");
    }

    .slider__control_right::before {
      background-image: url("data:image/svg+xml;charset=utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='%23fff' viewBox='0 0 8 8'%3E%3Cpath d='M2.75 0l-1.5 1.5 2.5 2.5-2.5 2.5 1.5 1.5 4-4-4-4z'/%3E%3C/svg%3E");
    }

    .slider__item>div {
      line-height: 500px;
      font-size: 100px;
      text-align: center;
    }
  </style>
  <link rel="icon" href="../youtube_ico.png" type="image/png">
                                     <title>Отчет - {{dbname.replace('.db','')}}</title>
                                 </head>
                                 <body>
                                     <p><center><h2>Отчет об анализе популярности тематических роликов на YouTube</center></p>
                                     <p><center><h2>на {{ date }}</center></p>
                                     <table width="100%">
                                         <tr>
                                             <td>
                                                 <ul>
                                                     <li style="list-style-type:none;font-size:21px">Количество видео по категориям</li>
                                                     {% for i in range(length) %}
                                                     <li style="margin-left:30px"><b>{{ queries[i] }}:</b> {{ totalVideos[i] }} в.</li>
                                                     {% endfor %}
                                                </ul>
                                             </td>
                                             <td>
                                                 <ul>
                                                     <li style="list-style-type:none;font-size:21px;color:tomato">Количество лайков по категориям</li>
                                                     {% for i in range(length) %}
                                                     <li style="margin-left:30px"><b>{{ queries[i] }}:</b> {{ totalLikes[i] }} л.</li>
                                                     {% endfor %}
                                                </ul>
                                             </td>
                                             <td>
                                                 <ul>
                                                     <li style="list-style-type:none;font-size:21px;color:deepskyblue">Количество дизлайков по категориям</li>
                                                     {% for i in range(length) %}
                                                     <li style="margin-left:30px"><b>{{ queries[i] }}:</b> {{ totalDislikes[i] }} д.</li>
                                                     {% endfor %}
                                                </ul>
                                             </td>
                                        </tr>
                                        <tr>
                                             <td>
                                                 <ul>
                                                     <li style="list-style-type:none;font-size:21px;color:magenta">Количество комментариев по категориям</li>
                                                     {% for i in range(length) %}
                                                     <li style="margin-left:30px"><b>{{ queries[i] }}:</b> {{ totalComments[i] }} к.</li>
                                                     {% endfor %}
                                                </ul>
                                             </td>
                                             <td>
                                                 <ul>
                                                     <li style="list-style-type:none;font-size:21px;color:gold">Количество просмотров по категориям</li>
                                                     {% for i in range(length) %}
                                                     <li style="margin-left:30px"><b>{{ queries[i] }}:</b> {{ totalViews[i] }} п.</li>
                                                     {% endfor %}
                                                </ul>
                                             </td>
                                             <td>
                                                 <ul>
                                                     <li style="list-style-type:none;font-size:21px;color:red">Среднее количество лайк/просмотр</li>
                                                     {% for i in range(length) %}
                                                     <li style="margin-left:30px"><b>{{ queries[i] }}:</b> {{ meanLikesViews[i] }} л/п</li>
                                                     {% endfor %}
                                                 </ul>
                                             </td>
                                        </tr>
                                        <tr>
                                             <td>
                                                 <ul>
                                                     <li style="list-style-type:none;font-size:21px;color:purple">Среднее количество дизлайк/просмотр</li>
                                                     {% for i in range(length) %}
                                                     <li style="margin-left:30px"><b>{{ queries[i] }}:</b> {{ meanDislikesViews[i] }} д/п</li>
                                                     {% endfor %}
                                                 </ul>
                                             </td>
                                             <td>
                                                 <ul>
                                                     <li style="list-style-type:none;font-size:21px;color:grey">Отношение лайков к дизлайкам</li>
                                                     {% for i in range(length) %}
                                                     <li style="margin-left:30px"><b>{{ queries[i] }}:</b> {{ likesPerDislikes[i] }} л/д</li>
                                                     {% endfor %}
                                                 </ul>
                                             </td>
                                             <td>
                                                 <ul>
                                                     <li style="list-style-type:none;font-size:21px;color:orange">Количество видео за последние полгода</li>
                                                     {% for i in range(length) %}
                                                     <li style="margin-left:30px"><b>{{ queries[i] }}:</b> {{ lastHalfYear[i] }} в.</li>
                                                     {% endfor %}
                                                 </ul>
                                             </td>
                                        </tr>
                                     </table>
                                     </br>
                                     <p><center><h2>Графики зависимостей</center></p>
                                     <div class="slider" >
                                         <div class="slider__wrapper">
                                             {% for image in images %}
                                                 <div class="slider__item">
                                                     <div style="height: auto; background: white;"> <img src="{{ image }}"> </div>
                                                     </div>
                                            {% endfor %}
                                            </div>
                                            <a class="slider__control slider__control_left" href="#" role="button"></a>
                                            <a class="slider__control slider__control_right slider__control_show" href="#" role="button"></a>
                                            </div>
                                     
                                     <p><center><h2>Динамика добавления новых видео за последние 3 года</center></p>
                                     <div class="slider1" >
                                         <div class="slider__wrapper">
                                             {% for image in images1 %}
                                                 <div class="slider__item">
                                                     <div style="height: auto; background: white;"> <img src="{{ image }}"> </div>
                                                     </div>
                                            {% endfor %}
                                            </div>
                                            <a class="slider__control slider__control_left" href="#" role="button"></a>
                                            <a class="slider__control slider__control_right slider__control_show" href="#" role="button"></a>
                                            </div>
                                     
                                     
                                     <p><center><h2>Популярность запросов согласно Google Trends</center></p>
                                     <div class="slider2" >
                                         <div class="slider__wrapper">
                                             {% for image in images2 %}
                                                 <div class="slider__item">
                                                     <div style="height: auto; background: white;"> <img src="{{ image }}"> </div>
                                                     </div>
                                            {% endfor %}
                                            </div>
                                            <a class="slider__control slider__control_left" href="#" role="button"></a>
                                            <a class="slider__control slider__control_right slider__control_show" href="#" role="button"></a>
                                            </div>
                                     
                                     <p><center><h2>Топ-{{n}} видео категорий</center></p>
                                     
                                     {% for i in range(lengthEmbed) %}
                                         <h3><center><p style="color:blue">Категория <b>«{{queriesEmbed[i]}}»</b></p></center></h3>
                                         <div class="slider{{i+3}}" >
                                         <div class="slider__wrapper">
                                         {% for j in range(n) %}
                                         
                                         
                                         <div class="slider__item">
                                             <h3><center><p style="color:green">{{j+1}}-e место</p></center></h3>
                                             <table width="100%">
                                                 <tr align="center">
                                                     <td>
                                                         <center><b>Максимум лайков ({{maxLikes[i][j]}})</b></center>
                                                         {{ maxLikeEmbeds[i][j] }}
                                                     </td>
                                                     <td>
                                                         <center><b>Максимум дизлайков ({{maxDislikes[i][j]}})</b></center>
                                                         {{ maxDislikeEmbeds[i][j] }}
                                                     </td>
                                                 </tr>
                                                 <tr align="center">
                                                     <td>
                                                         </br><center><b>Максимум комментариев ({{maxComments[i][j]}})</b></center>
                                                         {{ maxCommentsEmbeds[i][j] }}
                                                     </td>
                                                     <td>
                                                         </br><center><b>Максимум просмотров ({{maxViews[i][j]}})</b></center>
                                                         {{ maxViewsEmbeds[i][j] }}
                                                     </td>
                                                 </tr>
                                             </table>
                                             </br></br>
                                             </div>
                                         {% endfor %}
                                         </div>
                                            <a class="slider__control slider__control_left" href="#" role="button"></a>
                                            <a class="slider__control slider__control_right slider__control_show" href="#" role="button"></a>
                                         </div>
                                     {% endfor %}
                                 </body>
                                 <script>
    'use strict';
    var multiItemSlider = (function () {
      return function (selector, config) {
        var
          _mainElement = document.querySelector(selector), // основный элемент блока
          _sliderWrapper = _mainElement.querySelector('.slider__wrapper'), // обертка для .slider-item
          _sliderItems = _mainElement.querySelectorAll('.slider__item'), // элементы (.slider-item)
          _sliderControls = _mainElement.querySelectorAll('.slider__control'), // элементы управления
          _sliderControlLeft = _mainElement.querySelector('.slider__control_left'), // кнопка "LEFT"
          _sliderControlRight = _mainElement.querySelector('.slider__control_right'), // кнопка "RIGHT"
          _wrapperWidth = parseFloat(getComputedStyle(_sliderWrapper).width), // ширина обёртки
          _itemWidth = parseFloat(getComputedStyle(_sliderItems[0]).width), // ширина одного элемента
          _positionLeftItem = 0, // позиция левого активного элемента
          _transform = 0, // значение транфсофрмации .slider_wrapper
          _step = _itemWidth / _wrapperWidth * 100, // величина шага (для трансформации)
          _items = []; // массив элементов
        // наполнение массива _items
        _sliderItems.forEach(function (item, index) {
          _items.push({ item: item, position: index, transform: 0 });
        });
        var position = {
          getMin: 0,
          getMax: _items.length - 1,
        }
        var _transformItem = function (direction) {
          if (direction === 'right') {
            if ((_positionLeftItem + _wrapperWidth / _itemWidth - 1) >= position.getMax) {
              return;
            }
            if (!_sliderControlLeft.classList.contains('slider__control_show')) {
              _sliderControlLeft.classList.add('slider__control_show');
            }
            if (_sliderControlRight.classList.contains('slider__control_show') && (_positionLeftItem + _wrapperWidth / _itemWidth) >= position.getMax) {
              _sliderControlRight.classList.remove('slider__control_show');
            }
            _positionLeftItem++;
            _transform -= _step;
          }
          if (direction === 'left') {
            if (_positionLeftItem <= position.getMin) {
              return;
            }
            if (!_sliderControlRight.classList.contains('slider__control_show')) {
              _sliderControlRight.classList.add('slider__control_show');
            }
            if (_sliderControlLeft.classList.contains('slider__control_show') && _positionLeftItem - 1 <= position.getMin) {
              _sliderControlLeft.classList.remove('slider__control_show');
            }
            _positionLeftItem--;
            _transform += _step;
          }
          _sliderWrapper.style.transform = 'translateX(' + _transform + '%)';
        }

        // обработчик события click для кнопок "назад" и "вперед"
        var _controlClick = function (e) {
          var direction = this.classList.contains('slider__control_right') ? 'right' : 'left';
          e.preventDefault();
          _transformItem(direction);
        };

        var _setUpListeners = function () {
          // добавление к кнопкам "назад" и "вперед" обрботчика _controlClick для событя click
          _sliderControls.forEach(function (item) {
            item.addEventListener('click', _controlClick);
          });
        }
        // инициализация
        _setUpListeners();

        return {
          right: function () { // метод right
            _transformItem('right');
          },
          left: function () { // метод left
            _transformItem('left');
          }
        }

      }
    }());
    var slider = multiItemSlider('.slider')
  </script>
  <script>
    'use strict';
    var multiItemSlider1 = (function () {
      return function (selector, config) {
        var
          _mainElement = document.querySelector(selector), // основный элемент блока
          _sliderWrapper = _mainElement.querySelector('.slider__wrapper'), // обертка для .slider-item
          _sliderItems = _mainElement.querySelectorAll('.slider__item'), // элементы (.slider-item)
          _sliderControls = _mainElement.querySelectorAll('.slider__control'), // элементы управления
          _sliderControlLeft = _mainElement.querySelector('.slider__control_left'), // кнопка "LEFT"
          _sliderControlRight = _mainElement.querySelector('.slider__control_right'), // кнопка "RIGHT"
          _wrapperWidth = parseFloat(getComputedStyle(_sliderWrapper).width), // ширина обёртки
          _itemWidth = parseFloat(getComputedStyle(_sliderItems[0]).width), // ширина одного элемента
          _positionLeftItem = 0, // позиция левого активного элемента
          _transform = 0, // значение транфсофрмации .slider_wrapper
          _step = _itemWidth / _wrapperWidth * 100, // величина шага (для трансформации)
          _items = []; // массив элементов
        // наполнение массива _items
        _sliderItems.forEach(function (item, index) {
          _items.push({ item: item, position: index, transform: 0 });
        });
        var position = {
          getMin: 0,
          getMax: _items.length - 1,
        }
        var _transformItem = function (direction) {
          if (direction === 'right') {
            if ((_positionLeftItem + _wrapperWidth / _itemWidth - 1) >= position.getMax) {
              return;
            }
            if (!_sliderControlLeft.classList.contains('slider__control_show')) {
              _sliderControlLeft.classList.add('slider__control_show');
            }
            if (_sliderControlRight.classList.contains('slider__control_show') && (_positionLeftItem + _wrapperWidth / _itemWidth) >= position.getMax) {
              _sliderControlRight.classList.remove('slider__control_show');
            }
            _positionLeftItem++;
            _transform -= _step;
          }
          if (direction === 'left') {
            if (_positionLeftItem <= position.getMin) {
              return;
            }
            if (!_sliderControlRight.classList.contains('slider__control_show')) {
              _sliderControlRight.classList.add('slider__control_show');
            }
            if (_sliderControlLeft.classList.contains('slider__control_show') && _positionLeftItem - 1 <= position.getMin) {
              _sliderControlLeft.classList.remove('slider__control_show');
            }
            _positionLeftItem--;
            _transform += _step;
          }
          _sliderWrapper.style.transform = 'translateX(' + _transform + '%)';
        }

        // обработчик события click для кнопок "назад" и "вперед"
        var _controlClick = function (e) {
          var direction = this.classList.contains('slider__control_right') ? 'right' : 'left';
          e.preventDefault();
          _transformItem(direction);
        };

        var _setUpListeners = function () {
          // добавление к кнопкам "назад" и "вперед" обрботчика _controlClick для событя click
          _sliderControls.forEach(function (item) {
            item.addEventListener('click', _controlClick);
          });
        }
        // инициализация
        _setUpListeners();

        return {
          right: function () { // метод right
            _transformItem('right');
          },
          left: function () { // метод left
            _transformItem('left');
          }
        }

      }
    }());
    var slider1 = multiItemSlider1('.slider1')
  </script>
  <script>
    'use strict';
    var multiItemSlider2 = (function () {
      return function (selector, config) {
        var
          _mainElement = document.querySelector(selector), // основный элемент блока
          _sliderWrapper = _mainElement.querySelector('.slider__wrapper'), // обертка для .slider-item
          _sliderItems = _mainElement.querySelectorAll('.slider__item'), // элементы (.slider-item)
          _sliderControls = _mainElement.querySelectorAll('.slider__control'), // элементы управления
          _sliderControlLeft = _mainElement.querySelector('.slider__control_left'), // кнопка "LEFT"
          _sliderControlRight = _mainElement.querySelector('.slider__control_right'), // кнопка "RIGHT"
          _wrapperWidth = parseFloat(getComputedStyle(_sliderWrapper).width), // ширина обёртки
          _itemWidth = parseFloat(getComputedStyle(_sliderItems[0]).width), // ширина одного элемента
          _positionLeftItem = 0, // позиция левого активного элемента
          _transform = 0, // значение транфсофрмации .slider_wrapper
          _step = _itemWidth / _wrapperWidth * 100, // величина шага (для трансформации)
          _items = []; // массив элементов
        // наполнение массива _items
        _sliderItems.forEach(function (item, index) {
          _items.push({ item: item, position: index, transform: 0 });
        });
        var position = {
          getMin: 0,
          getMax: _items.length - 1,
        }
        var _transformItem = function (direction) {
          if (direction === 'right') {
            if ((_positionLeftItem + _wrapperWidth / _itemWidth - 1) >= position.getMax) {
              return;
            }
            if (!_sliderControlLeft.classList.contains('slider__control_show')) {
              _sliderControlLeft.classList.add('slider__control_show');
            }
            if (_sliderControlRight.classList.contains('slider__control_show') && (_positionLeftItem + _wrapperWidth / _itemWidth) >= position.getMax) {
              _sliderControlRight.classList.remove('slider__control_show');
            }
            _positionLeftItem++;
            _transform -= _step;
          }
          if (direction === 'left') {
            if (_positionLeftItem <= position.getMin) {
              return;
            }
            if (!_sliderControlRight.classList.contains('slider__control_show')) {
              _sliderControlRight.classList.add('slider__control_show');
            }
            if (_sliderControlLeft.classList.contains('slider__control_show') && _positionLeftItem - 1 <= position.getMin) {
              _sliderControlLeft.classList.remove('slider__control_show');
            }
            _positionLeftItem--;
            _transform += _step;
          }
          _sliderWrapper.style.transform = 'translateX(' + _transform + '%)';
        }

        // обработчик события click для кнопок "назад" и "вперед"
        var _controlClick = function (e) {
          var direction = this.classList.contains('slider__control_right') ? 'right' : 'left';
          e.preventDefault();
          _transformItem(direction);
        };

        var _setUpListeners = function () {
          // добавление к кнопкам "назад" и "вперед" обрботчика _controlClick для событя click
          _sliderControls.forEach(function (item) {
            item.addEventListener('click', _controlClick);
          });
        }
        // инициализация
        _setUpListeners();

        return {
          right: function () { // метод right
            _transformItem('right');
          },
          left: function () { // метод left
            _transformItem('left');
          }
        }
      }
    }());
    var slider2 = multiItemSlider2('.slider2')
  </script>
  
  {% for i in range(length) %}
      <script>
    'use strict';
    var multiItemSlider{{i+3}} = (function () {
      return function (selector, config) {
        var
          _mainElement = document.querySelector(selector), // основный элемент блока
          _sliderWrapper = _mainElement.querySelector('.slider__wrapper'), // обертка для .slider-item
          _sliderItems = _mainElement.querySelectorAll('.slider__item'), // элементы (.slider-item)
          _sliderControls = _mainElement.querySelectorAll('.slider__control'), // элементы управления
          _sliderControlLeft = _mainElement.querySelector('.slider__control_left'), // кнопка "LEFT"
          _sliderControlRight = _mainElement.querySelector('.slider__control_right'), // кнопка "RIGHT"
          _wrapperWidth = parseFloat(getComputedStyle(_sliderWrapper).width), // ширина обёртки
          _itemWidth = parseFloat(getComputedStyle(_sliderItems[0]).width), // ширина одного элемента
          _positionLeftItem = 0, // позиция левого активного элемента
          _transform = 0, // значение транфсофрмации .slider_wrapper
          _step = _itemWidth / _wrapperWidth * 100, // величина шага (для трансформации)
          _items = []; // массив элементов
        // наполнение массива _items
        _sliderItems.forEach(function (item, index) {
          _items.push({ item: item, position: index, transform: 0 });
        });
        var position = {
          getMin: 0,
          getMax: _items.length - 1,
        }
        var _transformItem = function (direction) {
          if (direction === 'right') {
            if ((_positionLeftItem + _wrapperWidth / _itemWidth - 1) >= position.getMax) {
              return;
            }
            if (!_sliderControlLeft.classList.contains('slider__control_show')) {
              _sliderControlLeft.classList.add('slider__control_show');
            }
            if (_sliderControlRight.classList.contains('slider__control_show') && (_positionLeftItem + _wrapperWidth / _itemWidth) >= position.getMax) {
              _sliderControlRight.classList.remove('slider__control_show');
            }
            _positionLeftItem++;
            _transform -= _step;
          }
          if (direction === 'left') {
            if (_positionLeftItem <= position.getMin) {
              return;
            }
            if (!_sliderControlRight.classList.contains('slider__control_show')) {
              _sliderControlRight.classList.add('slider__control_show');
            }
            if (_sliderControlLeft.classList.contains('slider__control_show') && _positionLeftItem - 1 <= position.getMin) {
              _sliderControlLeft.classList.remove('slider__control_show');
            }
            _positionLeftItem--;
            _transform += _step;
          }
          _sliderWrapper.style.transform = 'translateX(' + _transform + '%)';
        }

        // обработчик события click для кнопок "назад" и "вперед"
        var _controlClick = function (e) {
          var direction = this.classList.contains('slider__control_right') ? 'right' : 'left';
          e.preventDefault();
          _transformItem(direction);
        };

        var _setUpListeners = function () {
          // добавление к кнопкам "назад" и "вперед" обрботчика _controlClick для событя click
          _sliderControls.forEach(function (item) {
            item.addEventListener('click', _controlClick);
          });
        }
        // инициализация
        _setUpListeners();

        return {
          right: function () { // метод right
            _transformItem('right');
          },
          left: function () { // метод left
            _transformItem('left');
          }
        }
      }
    }());
    var slider{{i+3}} = multiItemSlider{{i+3}}('.slider{{i+3}}')
  </script>
  {% endfor %}
                             </html>
                             """)
    with open(root+dbname.replace('.db','')+".html", "w") as file:
        file.write(template.render(length=len(queries),lengthEmbed=len(queriesEmbed),queriesEmbed=queriesEmbed,dbname=dbname,images=images,images1=images1,images2=images2,date=date,queries=queries,totalVideos=totalVideos,totalLikes=totalLikes,totalDislikes=totalDislikes,totalComments=totalComments,totalViews=totalViews,
                                   maxLikeEmbeds=maxLikeEmbeds,maxDislikeEmbeds=maxDislikeEmbeds,maxCommentsEmbeds=maxCommentsEmbeds,maxViewsEmbeds=maxViewsEmbeds,
                                   maxLikes=maxLikes,maxDislikes=maxDislikes,maxComments=maxComments,maxViews=maxViews,
                                   meanLikesViews=meanLikesViews,meanDislikesViews=meanDislikesViews,likesPerDislikes=likesPerDislikes,lastHalfYear=lastHalfYear,n=n))







