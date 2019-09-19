from apiclient.discovery import build 

DEVELOPER_KEYS=["AIzaSyDJR3-A7UnPK6ZVPmYPvUfc35iEjb9TqFk",   #Я
                "AIzaSyBCNojrr4-HL23k0sGMMg7OhlDFOZvyTX4",   #Костя
                "AIzaSyDPs5drcMfvcRrqqkUrhPgnI647438WsdY",   #Я
                "AIzaSyA506GzoveUGAvXUib6Y8KTXAJxa4XMdLA"]   #Костя
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"



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
    #print(queries)
    
    for i in range(len(queries)):
        query=queries[i]
        for i in range(len(DEVELOPER_KEYS)):
            try:
                youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey = DEVELOPER_KEYS[i]) 
                results = youtube.search().list(q = query, part = "id, snippet", maxResults = 2).execute()
                break
            except:
                continue
            
        #типа так будет формироваться словарь с количеством видосов по каждому запросу
        totalVideos[query]=results['pageInfo']['totalResults']
        nextPageToken=results['nextPageToken']
        likes,dislikes,comments,views=[0 for i in range(4)]
        
        for i in range(11):
            searchResults=results.get("items", [])
            videoIds=[]
            for result in searchResults:
                if result['id']['kind']=="youtube#video":
                    videoIds.append(result["id"]["videoId"])
            videoIds=','.join(videoIds)
        
            
            for j in range(len(DEVELOPER_KEYS)):
                try:
                    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey = DEVELOPER_KEYS[j]) 
                    results=youtube.videos().list(part = "statistics",id=videoIds).execute()
                    break
                except:
                    continue
            
        
        
            for videoResult in results.get("items", []):
                if 'likeCount' in videoResult['statistics']:
                    likes=likes+int(videoResult['statistics']['likeCount'])
                if 'dislikeCount' in videoResult['statistics']:
                    dislikes=dislikes+int(videoResult['statistics']['dislikeCount'])
                if 'commentCount' in videoResult['statistics']:
                    comments=comments+int(videoResult['statistics']['commentCount'])
                views=views+int(videoResult['statistics']['viewCount'])
                
                
            for j in range(len(DEVELOPER_KEYS)):
                try:
                    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey = DEVELOPER_KEYS[j]) 
                    results=youtube.search().list(q = query, part = "id, snippet", pageToken=nextPageToken, maxResults = 2).execute()
                    break
                except:
                    continue
            if 'nextPageToken' in results:
                nextPageToken=results['nextPageToken']
            else:
                break
        
        totalLikes[query]=likes
        totalDislikes[query]=dislikes
        totalComments[query]=comments
        totalViews[query]=views
        
    print(totalLikes,totalDislikes,totalComments,totalViews)

if __name__ == "__main__":
    kowalski()