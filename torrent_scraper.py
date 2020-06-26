#!/usr/bin/env python3
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import subprocess
import re
import json
import web_scraper_lib
import abc

class site_scraper:
    def __init__(self, site_info, JD):
        self.sitename = site_info.get("name")
        avaliable_sites = web_scraper_lib.get_available_site_names()
        if self.sitename not in avaliable_sites:
            raise NotImplementedError("%s is not supported" % self.sitename)

        if self.sitename == "torrentboza":
            self.plugin = torrentboza(site_info, JD)
        elif self.sitename == "torrentmap":
            self.plugin = torrentmap(site_info, JD)
        elif self.sitename == "torrentdal":
            self.plugin = torrentdal(site_info, JD)
        elif self.sitename == "torrentwal":
            self.plugin = torrentwal(site_info, JD)
        elif self.sitename == "torrentwal":
            self.plugin = torrentwal(site_info, JD)

        self.mainUrl = site_info.get("main_url")
        self.JD = JD
        self.urls = site_info.get("urls")

    def saveNewLatestIDwithCate(self, category, newId):
        self.plugin.save_latest_id(category, newId)

    def needKeepGoing(self, category, id):
        return self.plugin.need_keep_going(category, id)

    def getMainUrl(self):
        return self.mainUrl

    def checkMainUrl(self):
        ret = web_scraper_lib.checkUrl(self.mainUrl)
        return ret

    def getName(self):
        return (self.name)
                
    def getScrapUrl(self, cateIdxNo, count):
        return (self.webpage_addr[cateIdxNo]+str(count))
                
    def getParseData(self, url):
        return self.plugin.get_parsed_data(url)

    #url을 기반으로 wr_id text를 뒤의 id parsing 
    def get_wr_id(self, url):
        return self.plugin.get_parsed_data(url)

    def get_magnet(self, url):
        return self.plugin.get_maget(url)


class site_plugin:
    def __init__(self, site_info, JD):
        self.sitename = site_info.get("name")
        self.JD = JD

    @abc.abstractmethod
    def need_keep_going(self, category, id):
        pass

    @abc.abstractmethod
    def get_maget(self, url):
        pass

    @abc.abstractmethod
    def get_wr_id(self, url):
        pass

    @abc.abstractmethod
    def get_parsed_data(self, url):
        pass

    @abc.abstractmethod
    def save_latest_id(self, category, newId):
        pass

class torrentboza(site_plugin):
    def __init__(self, site_info, JD):
        super().__init__(site_info, JD)
        self.kortv_ent_id = JD.get('history').get("%s_kortv_ent" % (self.sitename))
        self.kortv_soc_id = JD.get('history').get("%s_kortv_soc" % (self.sitename))

    def save_latest_id(self, category, new_id):
        tmp = self.JD.get('history')
        if category == 'kortv_ent':
            tmp.update(torrentboza_kortv_ent = new_id)
            self.kortv_ent_id = new_id
        elif category == 'kortv_social':
            tmp.update(torrentboza_kortv_soc = new_id)
            self.kortv_soc_id = new_id
        else:
            print("Something Wrong, category = %s" % category)
    
        self.JD.set('history', tmp)

    def get_parsed_data(self, url):
        bsObj = web_scraper_lib.getBsObj(url)
        nameList = bsObj.find('ul', attrs={'class' : 'list-body'}).find_all('a', href=True)
        return nameList

    def get_maget(self, url):
        bsObj = web_scraper_lib.getBsObj(url)
        magnet = bsObj.find('ul', attrs={'class' : 'list-group'}).find('a', href=True)
        magnet = magnet.get('href') 
        return magnet 

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

    def need_keep_going(self, category, id):
        tmp = None
        if category == 'kortv_ent':
            tmp = self.plugin.kortv_ent_id
        elif category == 'kortv_social':
            tmp = self.plugin.kortv_soc_id
        else:
            print("Something Wrong, category = %s" % category)
            return False
        
        if id > tmp:
            return True
        
        return False

class torrentmap(site_plugin):
    def __init__(self, site_info, JD):
        super().__init__(site_info, JD)
        self.kortv_ent_id = JD.get('history').get("%s_kortv_ent" % (self.sitename))
        self.kortv_soc_id = JD.get('history').get("%s_kortv_soc" % (self.sitename))

    def need_keep_going(self, category, id):
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

    def get_maget(self, url):
        bsObj = web_scraper_lib.getBsObj(url)
        magnetCandList = bsObj.find_all('section', attrs={'id' : 'bo_v_file'})

        for item in magnetCandList:
            magnetItem = item.find('a', href=re.compile(".*magnet.*"))
            if not magnetItem == None:
                magnet = magnetItem.get('href')
                break

        return magnet 

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

    def get_parsed_data(self, url):
        bsObj = web_scraper_lib.getBsObj(url)
        nameList = bsObj.find('div', attrs={'class' : 'tbl_head01 tbl_wrap'}).find_all('a', href=re.compile(".*wr_id.*"))
        return nameList

    def save_latest_id(self, category, newId):
        tmp = self.JD.get('history')
        if category == 'kortv_ent':
            tmp.update(torrentmap_kortv_ent = newId)
            self.kortv_ent_id = newId
        elif category == 'kortv_social':
            tmp.update(torrentmap_kortv_soc = newId)
            self.kortv_soc_id = newId
        else:
            print("Something Wrong, category = %s" % category)
        
        self.JD.set('history', tmp)
        return

class torrentdal(site_plugin):
    def __init__(self, site_info, JD):
        super().__init__(site_info, JD)
        self.kortv_ent_id = JD.get('history').get("%s_kortv_ent" % (self.sitename))
        self.kortv_soc_id = JD.get('history').get("%s_kortv_soc" % (self.sitename))

    def need_keep_going(self, category, id):
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

    def get_maget(self, url):
        bsObj = web_scraper_lib.getBsObj(url)
        magnet = bsObj.find('ul', attrs={'class' : 'list-group'}).find('a', href=True)
        magnet = magnet.get('href')
        return magnet 

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

    def get_parsed_data(self, url):
        bsObj = web_scraper_lib.getBsObj(url)
        nameList = bsObj.find('table', attrs={'class' : 'table div-table list-pc bg-white'}).find_all('a', href=re.compile(".*wr_id.*"))
        return nameList

    def save_latest_id(self, category, newId):
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

class torrentwal(site_plugin):
    def __init__(self, site_info, JD):
        super().__init__(site_info, JD)
        self.kortv_ent_id = JD.get('history').get("%s_kortv_ent" % (self.sitename))
        self.kortv_soc_id = JD.get('history').get("%s_kortv_soc" % (self.sitename))
        self.kortv_dra_id = JD.get('history').get("%s_kortv_dra" % (self.sitename))
        self.movie_id = JD.get("history").get("%s_movie" % (self.sitename) )

    def need_keep_going(self, category, id):
        tmp = None
        if category == 'kortv_ent':
            tmp = self.kortv_ent_id
        elif category == 'kortv_social':
            tmp = self.kortv_soc_id
        elif category == 'kortv_dra':
            tmp = self.kortv_dra_id
        elif category == "movie":
            tmp = self.movie_id
        else:
            print("Something Wrong, category = %s" % category)
            return False
        #print("info: tmp=%s" % tmp)
        if id > tmp:
            return True

        return False

    def get_maget(self, url):
        #print("info, get_magnet url = %s" % url)
        bsObj = web_scraper_lib.getBsObj(url)
        tag = bsObj.findAll('a', href=re.compile('^magnet'))
        # > fieldset > ul ')
        #> li:nth-child(3)')
        #.find('div', attrs={'id' : "f_list"}).next_sibling()
        #.next_sibling()
        # > table > tr > td > a")
        #.find('div', attrs={'id' : 'main_body'}).find('table')
        #\
        #                        .find('tr').find('td')
        #.find('a', recursive=False)
        #print("info, get_magnet a tags %s" % a_tags)

        if len(tag)>0:
            magnet = tag[0].get('href')

        return magnet

    def get_wr_id(self, url):
        tmp = url.rfind('/')
        if (tmp < 0): # 둘다 검색 못하면 포기
            return 0
        else:
            checkStr = '/'

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

    def get_parsed_data(self, url):
        bsObj = web_scraper_lib.getBsObj(url)
        nameList = bsObj.find('table', attrs={'class' : 'board_list'}).find_all('a',href=True)
        return nameList

    def save_latest_id(self, category, newId):
        tmp = self.JD.get('history')
        if category == 'kortv_ent':
            tmp.update(torrentwal_kortv_ent = newId)
            self.kortv_ent_id = newId
        elif category == 'kortv_social':
            tmp.update(torrentwal_kortv_soc = newId)
            self.kortv_soc_id = newId
        elif category == 'kortv_dra':
            tmp.update(torrentwal_kortv_dra = newId)
            self.kortv_dra_id = newId
        elif category == "movie":
            tmp.update(torrentwal_movie = newId)
            self.movie_id = newId
        else:
            print("Something Wrong, category = %s" % category)

        self.JD.set('history', tmp)
        return

class torrentview:
    def __init__(self, site_info, JD):
        self.sitename = site_info.get("name")
        self.JD = JD

    def need_keep_going(self, category, id):
        tmp = None
        if category == 'kortv_ent':
            tmp = self.kortv_ent_id
        elif category == 'kortv_social':
            tmp = self.kortv_soc_id
        elif category == 'kortv_dra':
            tmp = self.kortv_dra_id
        elif category == "movie":
            tmp = self.movie_id
        else:
            print("Something Wrong, category = %s" % category)
            return False
        
        if id > tmp:
            return True

        return False

    def get_maget(self, url):
        bsObj = web_scraper_lib.getBsObj(url)
        magnet = None
        if not bsObj == None:
            magnetItem = bsObj.find('a', href=re.compile(".*magnet.*"))
            print(magnetItem)
            if not magnetItem == None:
                magnet = magnetItem.get('href')
                print(magnet)

        return magnet

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

    def get_parsed_data(self, url):
        bsObj = web_scraper_lib.getBsObj(url)
        nameList = bsObj.find('div', attrs={'class' : 'list-board'}).find_all('a', href=re.compile(".*wr_id.*"))
        return nameList

    def save_latest_id(self, category, newId):
        tmp = self.JD.get('history')
        if category == 'kortv_ent':
            tmp.update(torrentview_kortv_ent = newId)
            self.kortv_ent_id = newId
        elif category == 'kortv_social':
            tmp.update(torrentview_kortv_soc = newId)
            self.kortv_soc_id = newId
        else:
            print("Something Wrong, category = %s" % category)

        self.JD.set('history', tmp)











