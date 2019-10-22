#import apiclient as api
from googleapiclient import discovery
import sys
import youtube_service as ys
import os

DEVELOPER_KEYS=["AIzaSyDJR3-A7UnPK6ZVPmYPvUfc35iEjb9TqFk",   #Я
                "AIzaSyBCNojrr4-HL23k0sGMMg7OhlDFOZvyTX4",   #Костя
                "AIzaSyDPs5drcMfvcRrqqkUrhPgnI647438WsdY",   #Я
                "AIzaSyA506GzoveUGAvXUib6Y8KTXAJxa4XMdLA",   #Костя
                "AIzaSyD-o3TMJ0nD--tmSmKp3t1-r88mI6Bc72c",   #Я
                "AIzaSyCzKUiwJ7WbbsQqJD7H_QAWNaUB0zzPcoA",   #Я
                "AIzaSyBD8tXjVqTDIvcG98zkvs44HS3xWIf_0io",   #Костя
                "AIzaSyCRHip38suqZie3s6VarjMzTdmSK6E6pDQ"]   #Костя
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

#получаем имя БД в формате ДЕНЬ_НЕДЕЛИ_ДД.ММ.ГГГГ_ЧЧ-ММ-СС, с которым потом постоянно работаем
dbname=ys.getDbName()

#создаем рабочую директорию, в которой создаем еще одну директорию для будущих картинок
os.mkdir(os.path.abspath(os.curdir)+'\\'+dbname.replace('.db',''))
path=os.path.abspath(os.curdir)+'\\'+dbname.replace('.db','')+'\\images'
root=os.path.abspath(os.curdir)+'\\'+dbname.replace('.db','')+'\\'
os.mkdir(path)

#создаем новое подключение к БД и получаем курсор для работы с ней
conncurs=ys.createDb(dbname,root)
conn=conncurs[0]
cursor=conncurs[1]

#заполняем БД
ys.fullfillDb(cursor,conn)

#начинаем вывод импровизированного прогрессбара
sys.stdout.write("Сбор и анализ данных [ %d"%0+"% ] ")
sys.stdout.flush()

def youtube_study_analytics():
    totalVideos={}
    totalLikes={}
    totalDislikes={}
    totalComments={}
    totalViews={}
    
    #построчно читаем запросы из файла
    #здесь кстати можно будет замутить выбор файла пользователем путем ввода его имени
    queries=ys.getQueriesFromFile('test.txt')
    
    #общий главный цикл
    for i in range(len(queries)):
        query=queries[i]
        #вносим изменения в таблицу, коммитим, вопросы это защита от инъекций
        cursor.execute("INSERT INTO query VALUES (?,?)",(i+1,query))
        conn.commit()
        
        #пробегаемся по АПИ ключам в поисках свободной квоты и выполняем поиск видео по i-ому запросу
        for h in range(len(DEVELOPER_KEYS)):
                try:
                    youtube = discovery.build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey = DEVELOPER_KEYS[h]) 
                    results = youtube.search().list(q = query, part = "id, snippet", maxResults = 50, order="date").execute()
                    break;
                except:
                    continue
            
        #выцепляем общее кол-во видео по даннной тематике
        totalVideos[query]=results['pageInfo']['totalResults']
        
        #получаем токен следующей страницы поиска, если она существует
        if 'nextPageToken' in results:
            nextPageToken=results['nextPageToken']
        else:
            nextPageToken='null'
        #первичная инициализация четырех статистических переменных
        likes,dislikes,comments,views=[0 for y in range(4)]
        
        #цикл для сбора всех идентификаторов видео
        #и отсеивание лишнего, поскольку в поиске кроме видео есть плейлисты и каналы
        #for k in range(11):
        for k in range(2):
            searchResults=results.get("items", [])
            videoIds=[]
            for result in searchResults:
                if result['id']['kind']=="youtube#video":
                    videoIds.append(result["id"]["videoId"])
            videoIds=','.join(videoIds)
        
            #пробегаемся по АПИ ключам в поисках свободной квоты 
            #и выполняем сбор данных по всем собранным выше видео
            for j in range(len(DEVELOPER_KEYS)):
                try:
                    youtube = discovery.build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey = DEVELOPER_KEYS[j]) 
                    results=youtube.videos().list(part = "snippet,statistics,player",id=videoIds).execute()
                    break
                except:
                    continue
            
        
            #собираем все необходимые данные по каждому видео данной тематики
            #лайки, дизлайки, комменты, просмотры, название, дату, ссылку, ссылку для вставки на сайт
            for videoResult in results.get("items", []):
                l,d,c,v=[0 for f in range(4)]
                t=videoResult['snippet']['title']
                date=videoResult['snippet']['publishedAt']
                url='https://www.youtube.com/watch?v='+str(videoResult['id'])
                if 'player' in videoResult:
                    embed=videoResult['player']['embedHtml'].replace('//','https://')
                if 'statistics' in videoResult:
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
#                    if v==0 or v==None:
#                        views=views+1
#                    else:
#                        views=views+v
                    views=views+v
                #вносим изменения в таблицу, коммитим
                cursor.execute("INSERT INTO video VALUES (?,?,?,?,?,?,?,?,?)",(url,embed,t,l,d,c,v,date,i+1))
                conn.commit()
                
            
            
            #читаем следующую страницу поиска, если она существует
            if nextPageToken!='null':
                for j in range(len(DEVELOPER_KEYS)):
                    try:
                        youtube = discovery.build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey = DEVELOPER_KEYS[j]) 
                        results=youtube.search().list(q = query, part = "id, snippet", pageToken=nextPageToken, maxResults = 50, order="date").execute()
                        break
                    except:
                        continue
            '''if 'nextPageToken' in results:
                nextPageToken=results['nextPageToken']
            else:
                break'''
            
        #получаем общее кол-во статистических данных по категории
        totalLikes[query]=likes
        totalDislikes[query]=dislikes
        totalComments[query]=comments
        totalViews[query]=views
        
        #вносим изменения в таблицу, коммитим
        cursor.execute("INSERT INTO result VALUES (?,?,?,?,?,?,?)",
                       (i+1,totalVideos[query],totalLikes[query],totalDislikes[query],
                       totalComments[query],totalViews[query],i+1))
        conn.commit()
        
        #в конце каждой итерации меняем значение на прогрессбаре
        sys.stdout.write(("\rСбор и анализ данных [ %d"%((i+1)*100/(len(queries)))+"% ] ")+('='*(int((i+1)*10/len(queries)))))
        sys.stdout.flush()
        
    
    maxLike=ys.getLikeEmbeds(dbname,path,root)
    maxLikes=maxLike[0]
    maxLikeEmbeds=maxLike[1]
    maxDislike=ys.getDislikeEmbeds(dbname,path,root)
    maxDislikes=maxDislike[0]
    maxDislikeEmbeds=maxDislike[1]
    maxComment=ys.getCommentEmbeds(dbname,path,root)
    maxComments=maxComment[0]
    maxCommentsEmbeds=maxComment[1]
    maxView=ys.getViewEmbeds(dbname,path,root)
    maxViews=maxView[0]
    maxViewsEmbeds=maxView[1]
    queriesEmbed=maxView[2]
    
    #images=[path+'\\1.png',path+'\\2.png',path+'\\3.png',path+'\\4.png',
            #path+'\\5.png',path+'\\6.png',path+'\\7.png',path+'\\8.png']
    images=[]
    for i in range(len(queries)+9):
        images.append(path+'\\'+str(i+1)+'.png')
    
    #генерируем кучу графиков и сохраняем их в папку images
    ys.queriesLikesDia(dbname,path,root)
    
    ys.queriesDislikesDia(dbname,path,root)
    
    ys.queriesCommentsDia(dbname,path,root)
    
    ys.queriesViewsDia(dbname,path,root)
    
    ys.likesPerViewsDia(dbname,path,root)
    
    ys.dislikesPerViewsDia(dbname,path,root)
    
    ys.likesPerDislikeViewsDia(dbname,path,root)
    
    ys.lastHalfYearDia(dbname,path,root)
    
    ys.videosPerLastYearDia(dbname,path,root)
    
    date=ys.dateConverter(dbname)
    
    meanLikesViews=ys.getLikesPerViews(dbname,root)
    
    meanDislikesViews=ys.getDislikesPerViews(dbname,root)
    
    likesPerDislikes=ys.getLikesPerDislikes(dbname,root)
    
    lastHalfYear=ys.getLastHalfYear(dbname,root)
    
    #генерируем html-страничку
    ys.htmlGenerator(images,dbname,date,queries,queriesEmbed,list(totalVideos.values()),root,
                     list(totalLikes.values()),list(totalDislikes.values()),list(totalComments.values()),
                     list(totalViews.values()),maxLikeEmbeds,maxDislikeEmbeds,maxCommentsEmbeds,maxViewsEmbeds,
                     maxLikes,maxDislikes,maxComments,maxViews,meanLikesViews,meanDislikesViews,likesPerDislikes,
                     lastHalfYear)
    
    conn.close()
    
    print('\nЗавершено')
    
if __name__ == "__main__":
    youtube_study_analytics()