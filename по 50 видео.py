import sqlite3
import datetime
import re
from apiclient.discovery import build 
import pandas as pd
import sys

DEVELOPER_KEYS=["AIzaSyDJR3-A7UnPK6ZVPmYPvUfc35iEjb9TqFk",   #Я
                "AIzaSyBCNojrr4-HL23k0sGMMg7OhlDFOZvyTX4",   #Костя
                "AIzaSyDPs5drcMfvcRrqqkUrhPgnI647438WsdY",   #Я
                "AIzaSyA506GzoveUGAvXUib6Y8KTXAJxa4XMdLA"]   #Костя
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

#добавить время в имя
dbname = datetime.datetime.now().strftime("%A_%d-%m-%Y")
days={'Monday':'Понедельник','Tuesday':'Вторник','Wednesday':'Среда',
      'Thursday':'Четверг','Friday':'Пятница','Saturday':'Суббота','Sunday':'Воскресенье'}

pattern=r'(^[a-zA-Z]+)'
dayOfWeek=re.search(pattern,dbname).group(0)
dbname=dbname.replace(dayOfWeek,days[dayOfWeek])

conn=sqlite3.connect(dbname+".db")
cursor=conn.cursor()

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
               title text NOT NULL,
               likeCount  NOT NULL,
               dislikeCount  NOT NULL,
               commentCount  NOT NULL,
               viewCount  NOT NULL,
               date NULL,
               queryID  NOT NULL,
               FOREIGN KEY (queryID) REFERENCES query (queryID))""")
conn.commit()

sys.stdout.write("Сбор и анализ данных [ %d"%0+"% ] ")
sys.stdout.flush()

def kowalski():
    totalVideos={}
    totalLikes={}
    totalDislikes={}
    totalComments={}
    totalViews={}
    queries=[]
    
    file=open('test.txt','r')
    for line in file:
        queries.append(line)
    for i in range(len(queries)):
        queries[i]=queries[i].replace('\n','')
    
    
    for i in range(len(queries)):
        query=queries[i]
        cursor.execute("INSERT INTO query VALUES (?,?)",(i+1,query))
        conn.commit()
        
        for h in range(len(DEVELOPER_KEYS)):
            try:
                youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey = DEVELOPER_KEYS[h]) 
                results = youtube.search().list(q = query, part = "id, snippet", maxResults = 50).execute()
                break
            except:
                continue
            
        #типа так будет формироваться словарь с количеством видосов по каждому запросу
        totalVideos[query]=results['pageInfo']['totalResults']
        #print(query,' ',totalVideos[query])
        #nextPageToken=results['nextPageToken']
        likes,dislikes,comments,views=[0 for y in range(4)]
        
        #for i in range(11):
        for k in range(1):
            searchResults=results.get("items", [])
            videoIds=[]
            for result in searchResults:
                if result['id']['kind']=="youtube#video":
                    videoIds.append(result["id"]["videoId"])
            videoIds=','.join(videoIds)
        
            
            for j in range(len(DEVELOPER_KEYS)):
                try:
                    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey = DEVELOPER_KEYS[j]) 
                    results=youtube.videos().list(part = "snippet,statistics",id=videoIds).execute()
                    break
                except:
                    continue
            
        
        
            for videoResult in results.get("items", []):
                l,d,c,v=[0 for f in range(4)]
                t=videoResult['snippet']['title']
                date=videoResult['snippet']['publishedAt']
                url='https://www.youtube.com/watch?v='+videoResult['id']
                if 'likeCount' in videoResult['statistics']:
                    l=int(videoResult['statistics']['likeCount'])
                    likes=likes+l
                if 'dislikeCount' in videoResult['statistics']:
                    d=int(videoResult['statistics']['dislikeCount'])
                    dislikes=dislikes+d
                if 'commentCount' in videoResult['statistics']:
                    c=int(videoResult['statistics']['commentCount'])
                    comments=comments+c
                v=int(videoResult['statistics']['viewCount'])
                views=views+v
                cursor.execute("INSERT INTO video VALUES (?,?,?,?,?,?,?,?)",(url,t,l,d,c,v,date,i+1))
                conn.commit()
                
                
            '''for j in range(len(DEVELOPER_KEYS)):
                try:
                    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey = DEVELOPER_KEYS[j]) 
                    results=youtube.search().list(q = query, part = "id, snippet", pageToken=nextPageToken, maxResults = 2).execute()
                    break
                except:
                    continue
            if 'nextPageToken' in results:
                nextPageToken=results['nextPageToken']
            else:
                break'''
            
        
        totalLikes[query]=likes
        totalDislikes[query]=dislikes
        totalComments[query]=comments
        totalViews[query]=views
        
        cursor.execute("INSERT INTO result VALUES (?,?,?,?,?,?,?)",
                       (i+1,totalVideos[query],totalLikes[query],totalDislikes[query],
                       totalComments[query],totalViews[query],i+1))
        conn.commit()
        
        sys.stdout.write(("\rСбор и анализ данных [ %d"%((i+1)*100/(len(queries)))+"% ] ")+('='*(int((i+1)*10/len(queries)))))
        sys.stdout.flush()
        
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
    print('\nЗавершено')
    
if __name__ == "__main__":
    kowalski()