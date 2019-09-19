from apiclient.discovery import build 

# Arguments that need to passed to the build function 
#DEVELOPER_KEY = "AIzaSyDJR3-A7UnPK6ZVPmYPvUfc35iEjb9TqFk"
DEVELOPER_KEYS=["AIzaSyDJR3-A7UnPK6ZVPmYPvUfc35iEjb9TqFk",   #Я
                "AIzaSyBCNojrr4-HL23k0sGMMg7OhlDFOZvyTX4",   #Костя
                "AIzaSyDPs5drcMfvcRrqqkUrhPgnI647438WsdY",   #Я
                "AIzaSyA506GzoveUGAvXUib6Y8KTXAJxa4XMdLA"]   #Костя
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# creating Youtube Resource Object 



def main():
    
    
    
    for i in range(len(DEVELOPER_KEYS)):
        try:
            youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey = DEVELOPER_KEYS[i]) 
            results = youtube.search().list(q = 'гавно гавна', part = "id, snippet", maxResults = 50).execute().get("items", [])
            break
        except:
            continue
        
        
        
    print(results)

if __name__ == "__main__":
    main()