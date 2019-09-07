import time
import threading 
import requests 
import re
import pickle
import json
from data.DST import News,Team,Member
import jieba

class NewsBrief:
    def __init__(self,title,content,ID):
        self.title = title 
        self.content = content 
        self.ID = ID 

def crawlTeam(): #cralwer team data from tencent
    teams = set()
    for i in range(30):
        url = "https://ziliaoku.sports.qq.com/cube/index?callback=&cubeId=1&dimId=1&params=t1%3A"+str(i+1)+"&from=sportsdatabase"
        response = requests.get(url)
        try:
            content = json.loads(response.text)
            info = content["data"]["baseInfo"]
            name = info["cnName"]+"({})".format(info["enName"])
            logoLink = info["propsLogo"]
            setup = info["joinNBADate"]
            city = info["city"]+"({})".format(info["cityEnName"])
            venue = info["venue"]
            coach = info["coach"]
            division = info["division"]
            historyChampion = info["historyChampion"]
            url = "https://ziliaoku.sports.qq.com/cube/index?callback=&cubeId=10&dimId=31&params=t2%3A2018%7Ct3%3A1%7Ct4%3A"+str(i+1)+"&from=sportsdatabase"
            response = requests.get(url)
            content = json.loads(response.text)
            members = set()
            for it in content["data"]["nbaTeamPlayerSeasonStat"]:
                url = "https://ziliaoku.sports.qq.com/cube/index?callback=&cubeId=8&dimId=5&params=t1%3A"+it["playerId"]+"&from=sportsdatabase"
                response = requests.get(url)
                info = json.loads(response.text)["data"]["playerBaseInfo"]
                pname = info["cnName"]+"({})".format(info["enName"])
                pimageLink = info["picFromSIB"]
                pnum = info["jerseyNum"]
                ppos =  info["position"]
                pheight = info["height"]
                pweight = info["weight"]
                pbirth = info["birthDate"]
                pplayAge = info["seasonExp"]
                tmp = Member(pname,pimageLink,pnum,ppos,pheight,pweight,pbirth,pplayAge)
                members.add(tmp)
            a = Team(name,logoLink,setup,city,venue,coach,division,historyChampion,members)
            teams.add(a)
            print("Finished {}".format(i+1))
            print(a)
        except:
            print("Error")
            continue
    with open("Teams.pkl","wb") as f:
        pickle.dump(teams,f)
        

def crawlHupu():

    news = set()
    patternKey = re.compile('<meta http-equiv="Keywords" content="(.*?)" />')
    patternTitle = re.compile('<meta property="og:title" content="(.*?)" />')
    patternSource = re.compile('来源：<a href=".*?" target="_blank">(.*?)</a>',re.S)
    patternPostTime = re.compile('<meta name="weibo:webpage:update_at" content="(.*?)" />')
    patternImageLink = re.compile('<div class="artical-importantPic">.*?<img src="(.*?)" alt=".*?">',re.S)
    patternContent = re.compile('<div class="artical-main-content">(.*?)</div>',re.S)

    for i in range(100):
        url = "https://voice.hupu.com/nba/"+str(i+1)
        response = requests.get(url)
        pattern = re.compile('<a href="(.*?)"  target="_blank">')
        for it in re.findall(pattern,response.text):
            url = it
            text = requests.get(url).text
            print(url)
            key = re.search(patternKey,text).group(1).split("-")
            title = re.search(patternTitle,text).group(1)
            source = re.search(patternSource,text).group(1)
            postTime = re.search(patternPostTime,text).group(1)
            try:
                imageLink = re.search(patternImageLink,text).group(1)
            except:
                imageLink = ""
            content = re.search(patternContent,text).group(1).replace("  ","").replace("\r\n","\r\n").replace("span","p")
            a = News(key,title,source,postTime,imageLink,content,url)
            news.add(a)
            time.sleep(1)
        print("page {} finished".format(i+1))

    with open("Hupu.pkl","wb") as f:
        pickle.dump(news,f)
    
class SpiderThread(threading.Thread):
    def __init__(self,pause,newsList,index):
        threading.Thread.__init__(self)
        self.pause=pause
        self.newsList=newsList
        self.stop=False
        self.index=index
    def run(self):
        patternKey = re.compile('<meta http-equiv="Keywords" content="(.*?)" />')
        patternTitle = re.compile('<meta property="og:title" content="(.*?)" />')
        patternSource = re.compile('来源：<a href=".*?" target="_blank">(.*?)</a>',re.S)
        patternPostTime = re.compile('<meta name="weibo:webpage:update_at" content="(.*?)" />')
        patternImageLink = re.compile('<div class="artical-importantPic">.*?<img src="(.*?)" alt=".*?">',re.S)
        patternContent = re.compile('<div class="artical-main-content">(.*?)</div>',re.S)

        for i in range(100):
            url = "https://voice.hupu.com/nba/"+str(i+1)
            response = requests.get(url)
            pattern = re.compile('<a href="(.*?)"  target="_blank">')
            for it in re.findall(pattern,response.text):
                if self.stop:
                    return 
                while True:
                    if not self.pause:
                        break
                url = it
                text = requests.get(url).text
                print(url)
                key = re.search(patternKey,text).group(1).split("-")
                title = re.search(patternTitle,text).group(1)
                source = re.search(patternSource,text).group(1)
                postTime = re.search(patternPostTime,text).group(1)
                try:
                    imageLink = re.search(patternImageLink,text).group(1)
                except:
                    imageLink = ""
                content = re.search(patternContent,text).group(1).replace("  ","").replace("\r\n","\r\n").replace("span","p")
                a = News(key,title,source,postTime,imageLink,content,url)
                duplicated=False 
                for it in self.newsList:
                    if it.title==a.title:
                        duplicated=True 
                        break 
                if not duplicated:
                    self.newsList.append(a)
                    raw=re.sub(re.compile("<.*?>"),'',a.content)
                    tmpNewsBrief=NewsBrief(a.title,a.content,len(self.newsList))
                    words=jieba.cut(it.title+it.content)
                    for word in words:
                        self.index[word].add(tmpNewsBrief)
                    with open('Hupu.pkl','wb') as f:
                        pickle.dump(self.newsList,f)
                    time.sleep(1)
                    print(a)
    def setPause(self,pause):
        self.pause=pause
    def setStop(self,stop):
        self.stop=stop

if __name__=="__main__":
    crawlHupu()
    #crawlTeam()
