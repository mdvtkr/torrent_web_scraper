#!/usr/bin/env python3
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import subprocess
import re
import json
import web_scraper_lib

webpage_addr = [
        "https://torrentdal.com/bbs/board.php?bo_table=todal_ent&page=",
        "https://torrentdal.com/bbs/board.php?bo_table=todal_docu&page="
        ]

class site_scraper:
    def __init__(self, JD):
        self.sitename = "torrentdal"
        self.name = "web_scraper_03"
        self.mainUrl = "https://torrentdal.com"
        self.JD = JD

        self.kortv_ent_id = JD.get('history').get("%s_kortv_ent" % (self.sitename))
        self.kortv_soc_id = JD.get('history').get("%s_kortv_soc" % (self.sitename))

    def saveNewLatestIDwithCate(self, category, newId):
        tmp = self.JD.get('history')
        if category == 'kortv_ent':
            tmp.update(torrentdal_kortv_ent = newId)
            self.kortv_ent_id = newId
        elif category == 'kortv_social':
            tmp.update(torrentdal_kortv_soc = newId)
            self.kortv_soc_id = newId
        else:
            print("Something Wrong, category = %s" % category)
        
        self.JD.set('history', tmp)
        return

    def needKeepGoing(self, category, id):
        tmp = None
        if category == 'kortv_ent':
            tmp = self.kortv_ent_id
        elif category == 'kortv_social':
            tmp = self.kortv_soc_id
        else:
            print("Something Wrong, category = %s" % category)
            return False
        
        if id > tmp:
            return True
        
        return False

    def getMainUrl(self):
        return self.mainUrl

    def checkMainUrl(self):
        ret = web_scraper_lib.checkUrl(self.mainUrl)
        return ret

    def getName(self):
        return (self.name)
                
    def getScrapUrl(self, cateIdxNo, count):
        return (webpage_addr[cateIdxNo]+str(count))
                
    def getParseData(self, url):
        bsObj = web_scraper_lib.getBsObj(url)
        nameList = bsObj.find('table', attrs={'class' : 'table div-table list-pc bg-white'}).find_all('a', href=re.compile(".*wr_id.*"))
        return nameList

    #url을 기반으로 wr_id text를 뒤의 id parsing 
    def get_wr_id(self, url):

        tmp = url.rfind('wr_id=')
        if (tmp < 0): # 둘다 검색 못하면 포기
            return 0
        else:
            checkStr = 'wr_id='

            startp = tmp+len(checkStr)
            endp = startp
           
            for endp in range(startp,len(url)):
                if (url[endp]).isdigit():
                    continue
                else:
                    endp = endp-1
                    break
        
            endp = endp+1
        return int((url[startp:endp]))

    def get_magnet(self, url):
        bsObj = web_scraper_lib.getBsObj(url)
        magnet = bsObj.find('ul', attrs={'class' : 'list-group'}).find('a', href=True)
        magnet = magnet.get('href')
        return magnet 
