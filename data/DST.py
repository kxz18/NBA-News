class News:
    def __init__(self,key,title,source,postTime,imageLink,content,link):
        self.key = key
        self.title = title
        self.source = source
        self.postTime = postTime
        self.imageLink = imageLink
        self.content = content
        self.link = link
    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return str(self.__dict__)


class Member:
    def __init__(self,name,imageLink,num,pos,height,weight,birth,playAge):
        self.name = name
        self.imageLink = imageLink
        self.num = num
        self.pos = pos
        self.height = height
        self.weight = weight
        self.birth = birth
        self.playAge = playAge
    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return str(self.__dict__)


class Team:
    def __init__(self,name,logoLink,setup,city,venue,coach,division,historyChampion,members):
        self.name = name
        self.logoLink = logoLink
        self.setup = setup
        self.city = city
        self.venue = venue
        self.coach = coach
        self.division = division
        self.historyChampion = historyChampion
        self.members = members
    def __str__(self):
        return str(self.__dict__)
    def __repr__(self):
        return str(self.__dict__)
    

