from django.shortcuts import render
from django.http import HttpResponseRedirect
from collections import defaultdict
import data 
from data.Spider import SpiderThread 
import pickle
import re 
import time
import jieba
import jieba.analyse

Teams = list(pickle.load(open('data/Teams.pkl','rb')))
HupuNews = list(pickle.load(open('data/Hupu.pkl','rb')))
AllNews = HupuNews
newsIndex = defaultdict(set)

class NewsBrief:
    def __init__(self,title,content,ID):
        self.title = title 
        self.content = content 
        self.ID = ID 

def processNews(news,index):
    i=0
    tmpNewsList=[]
    for it in news:
        raw=re.sub(re.compile("<.*?>"),'',it.content)
        tmpNewsList.append(NewsBrief(it.title,raw,i))
        i+=1
    for it in tmpNewsList:
        words=jieba.cut(it.title+it.content)
        for word in words:
            index[word].add(it)
        
processNews(AllNews,newsIndex)

def addHyperLink(src):
    i=0
    content = src.content 
    for team in Teams:
        teamKey=[]
        for it in list(team.members)+[team]:
            tmp=it.name.replace(r"(",'@')
            tmp=tmp.replace(r')','')
            teamKey+=tmp.split("@")
        for key in teamKey: 
            content = content.replace(key,'<a href="/teams/{}">{}</a>'.format(i,key))
        i+=1
    a = data.DST.News(src.key,src.title,src.source,src.postTime,src.imageLink,content,src.link)
    return a

def index(request):
    return render(request,'index.html')

def results(request):
    #keywords = request.GET['search'].split(' ')
    jiebaKey = jieba.analyse.extract_tags(request.GET['search'],withWeight=True)
    if len(jiebaKey)==0:
        jiebaKey=[]
        for i in jieba.cut(request.GET['search']):
            jiebaKey.append((i,1))
    keywords = {}
    for it in jiebaKey:
        if it[0]=='' or it[0]==' ':
            continue 
        else:
            keywords[it[0]]=it[1]
    news = defaultdict(list)

    time_s=time.time()
    
    Ans=set()
    for key in keywords:
        for fromNewsIndex in newsIndex[key]:
            Ans.add(fromNewsIndex)

    time_e=time.time()


    for it in Ans: 
        cnt=0
        content=''
        title=it.title 
        for key in keywords:
            title = title.replace(key,'<font color="#ff0000">{}</font>'.format(key))
            first = it.content.find(key)
            if it.title!=title:
                cnt+=10*float(keywords[key])
            if first!=-1:
                cnt+=float(keywords[key])
            if first!=-1 and content=='':
                content = it.content[first:first+len(key)]
                if first<=50:
                    left = it.content[0:first]
                else:
                    left = "..."+it.content[first-50:first]
                if len(it.content)-len(key)-first>=50:
                    right = it.content[first+len(key):first+len(key)+50]+"..."
                else:
                    right = it.content[first+len(key):-1]
                content = left+content+right
            content=content.replace(key,'<font color="#ff0000">{}</font>'.format(key))
        if content=='':
            content=it.content[0:100]+"..."
        tmp = NewsBrief(title,content,it.ID)
        news[cnt].append(tmp)
    
    resultList = []
    for i in sorted(news,reverse=True):
        print(i)
        resultList+=news[i]
    count = len(resultList)
    if 'page' in request.GET:
        page_now = int(request.GET['page'])
    else:
        page_now = 1
    
    if count%30==0:
        pagemax=int(count/30)
    else:
        pagemax=int(count/30)+1
    
    if pagemax==0:
        pagemax=1

    pagenums=[]
    for i in range(max(1,page_now-5),min(pagemax+1,max(1,page_now-5)+11)):
        pagenums.append(i)

    returnData = {
            'keywords':request.GET['search'],
            'matchNews':resultList[30*(page_now-1):min(30*page_now,count)],
            'timeUsed':str(time_e-time_s),
            'count':count,
            'pagenums':pagenums,
            'pagemax':pagemax,
            'pagenow':page_now,
            }
    return render(request,'searchResults.html',returnData)

def teamIndex(request):
    class TeamBrief:
        def __init__(self,ID,name,logoLink):
            self.ID = ID
            self.name = name 
            self.logoLink = logoLink
 
    rankedTeams=[]
    i=0
    for team in Teams:
        cnt=0
        tmp = team.name.replace("(",'#')
        tmp = tmp.replace(')','').split('#')[0]
        for news in AllNews:
            if tmp in news.key:
                cnt+=1
        a = TeamBrief(i,team.name,team.logoLink)
        rankedTeams.append((cnt,a))
        i+=1
    rankedTeams.sort(key=lambda x:x[0],reverse=True)
    returnData = {
            'teams':rankedTeams,
            }
    return render(request,'teamIndex.html',returnData)

def team(request):
    num = int(request.path[7:])
    tmp = Teams[num].name.replace(r"(","#")
    tmp = tmp.replace(r")",'').split('#')[0]

    relatedNews=[]
    i=0
    for news in AllNews:
        if news.key.count(tmp)!=0:
            tmpNews=NewsBrief(news.title,"",i)
            relatedNews.append(tmpNews)
        i+=1
    print(relatedNews)
    count = len(relatedNews)
    if 'page' in request.GET:
        page_now = int(request.GET['page'])
    else:
        page_now = 1
    if count%30==0:
        pagemax=int(count/30)
    else:
        pagemax=int(count/30)+1
    if pagemax==0:
        pagemax=1
    pagenums=[]
    for i in range(max(1,page_now-5),min(pagemax+1,max(1,page_now-5)+11)):
        pagenums.append(i)
    returnData = {
            'team':Teams[num],
            'news':relatedNews[30*(page_now-1):min(30*page_now,count)],
            'pagenow':page_now,
            'pagenums':pagenums,
            'id':num,
            'total':len(relatedNews),
            }
    return render(request,'team.html',returnData)

def news(request):
    id = int(request.path[6:])
    returnData={
            'news':addHyperLink(AllNews[id])
            }
    return render(request,'news.html',returnData)

spider_thread = SpiderThread(False,AllNews,newsIndex)

def spider(request):
    global spider_thread
    if 'start' in request.GET:
        spider_thread = SpiderThread(False,AllNews,newsIndex)
        spider_thread.start()
    elif 'pause' in request.GET:
        spider_thread.setPause(not spider_thread.pause)
    elif 'stop' in request.GET:
        spider_thread.setStop(True)
        time.sleep(2)
        print(AllNews[-1])
    returnData = {
            'status':'',
            'start':'disabled',
            'pause':'',
            'stop':'',
            'buttontext':'Pause',
            }
    if not spider_thread.isAlive():
        returnData['status']='Spider not started'
        returnData['start']=''
        returnData['pause']='disabled'
        returnData['stop']='disabled'
    elif spider_thread.pause:
        returnData['status']='Spider has been paused'
        returnData['buttontext']='Continue'
    elif not spider_thread.pause:
        returnData['status']='Spider is running'
    return render(request,'spider.html',returnData)

