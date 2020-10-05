# import packages
import requests
import re
from bs4 import BeautifulSoup
import random

def GetHTMLText(url):
    '''
    Return text content of given LianJia urls.

    Arg:
    url: e.g. https://sh.lianjia.com/zufang
    Return:
    requests text content
    '''
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.9 Safari/537.36"}
        r = requests.get(url, timeout = 30, headers = headers)
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ''

def AreaParser(url):
    '''
    Scan through different districts and areas and create sub-pages urls
    ** This is used because web auto robot detection. Would minimize length of each srapying (not necessary)
    Arg:
    root page url: e.g. https://sh.lianjia.com/zufang
    Return:
    dictionary: 'jingan': {'jingansi': https://sh.lianjia.com/zufang/jingan/}
    '''
    html = GetHTMLText(url)
    soup = BeautifulSoup(html, 'html.parser')
    district_area_urls = {} # districts-areas urls
    # find district urls
    districts = soup.find('ul', {'data-target': 'area'}).find_all('li', class_='filter__item--level2')
    for district in districts[1:]:
        link1 = url+'/'+district.find('a')['href'].split('/')[-2]
        district_name = district.find('a')['href'].split('/')[-2]
        # find sub areas urls
        html = GetHTMLText(link1)
        soup = BeautifulSoup(html, "html.parser")
        areas = {} # subarea info
        area_list = soup.find_all("li",{"class":"filter__item--level3"})
        for area in area_list[1:]:
            link2 = url+'/'+area.find('a')['href'].split('/')[-2]
            area_name= area.find('a')['href'].split('/')[-2]
            areas[area_name] = link2
        district_area_urls[district_name] = areas
    return district_area_urls

# def GetCoords(url):
#     '''
#     Return coordinates for target listing.
#     Arg:
#     listing url
#     Return:
#     dictionary: {long: float, lat: float}
#     '''
#     html = GetHTMLText2(url, proxies)
#     coords = {}
#     lon = re.findall(r"longitude: '\d+\.?\d*'", html)
#     coords['lon'] = float(lon[0].split(':')[1].strip()[1:-1]) # get float longitude
#     lat = re.findall(r"latitude: '\d+\.?\d*'", html)
#     coords['lat'] = float(lat[0].split(':')[1].strip()[1:-1])
#     return coords

def GetListingDetails(soup):
    '''
    Get features of each listing.

    Arg:
    url for district-area-page: e.g. https://sh.lianjia.com/zufang/jingan/pg1
    Return:
    csv files: name, price, loc, features
    '''
    # get listings for each page
    listings = soup.find('div', class_='content__list').find_all('div', class_='content__list--item')
    # employ list to write
    ptpl = '{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'

    for listing in listings:
        try:
            basic_info = listing.find('a', class_='twoline').get_text().strip()
            name = basic_info.split('·')[1].split(' ')[0]
            rent_type = basic_info.split('·')[0]
            beds = basic_info.split('·')[1].split(' ')[1][0]
            price = float(listing.find('span', class_='content__list--item-price').get_text().split(' ')[0])
            link = listing.find('a', class_='twoline')['href']
            sub_link = url + link[7:] # get sublink
            # coord = GetCoords(sub_link)
            # get tags, generate 1, 0 for tag features
            taglist = ['独立阳台', '押一付一', '公寓', '月租', '随时看房', '近地铁', '独立卫生间', '精装', '新上']
            tag = listing.find('p', class_ = 'content__list--item--bottom oneline').get_text().strip().split("\n")
            tagnum = []
            for i in range(9):
                if taglist[i] in tag:
                    tagnum.append(1)
                else:
                    tagnum.append(0)
            # go to sub link to scrap more features
            r = requests.get(sub_link)

            # get cordinates
            coords = {}
            lon = re.findall(r"longitude: '\d+\.?\d*'", r.text)
            coords['lon'] = float(lon[0].split(':')[1].strip()[1:-1]) # get float longitude
            lat = re.findall(r"latitude: '\d+\.?\d*'", r.text)
            coords['lat'] = float(lat[0].split(':')[1].strip()[1:-1])

            soup = BeautifulSoup(r.text)
            # go to features
            features = soup.find_all('li', class_='fl oneline')
            size = int(features[1].get_text().strip()[3:-1])
            orientation = features[2].get_text().strip()[3:]
            level = features[7].get_text().strip()[3:]
            elevator = features[8].get_text().strip()[3:]
            parking = features[10].get_text().strip()[3:]
            amenities = len(features)-24
        except:
            continue

        with open('lianjia_shanghai.csv', 'a', encoding='utf-8') as f:
            f.write(ptpl.format(name, rent_type, beds, price, coords['lon'], coords['lat'], tagnum[0],
                                tagnum[1],tagnum[2],tagnum[3],tagnum[4],tagnum[5],tagnum[6],tagnum[7],tagnum[8],
                               size, orientation, level, elevator, parking, amenities))

if __name__ == '__main__':
    url = input('Please enter your url: ')
    try:
        for i in range(50): #page numbers
            target_url = url + '/pg' + str(i+1)
            html = GetHTMLText(url)
            soup = BeautifulSoup(html, 'html.parser')
            GetListingDetails(soup)
    except:
        continue
