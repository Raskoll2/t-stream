#! /usr/bin/python
from pprint import pprint
import unicodedata

import requests
from bs4 import BeautifulSoup

import unicodedata
import logging

def get_json(soup):
    json_obj = {
        "movie_info": []
    }
    
    table = soup.find('table', id='searchResult')
    
    if not table:
        logging.warning("No search results table found")
        return json_obj
    
    rows = table.find_all('tr', class_=lambda x: x != 'header')
    
    for row in rows:
        tds = row.find_all('td')
        
        if len(tds) < 6:
            logging.debug(f"Skipping row with insufficient columns: {row}")
            continue
        
        title_link = tds[1].find('a')
        if not title_link:
            logging.debug(f"Skipping row without title link: {row}")
            continue
        
        try:
            title = title_link.text.strip()
            
            magnet_link = row.find('a', href=lambda href: href and href.startswith('magnet:'))
            if not magnet_link:
                logging.debug(f"No magnet link found for {title}")
                continue
            magnet_url = magnet_link['href']
            
            size = tds[4].text.strip()
            seeders = tds[5].text.strip()
            leechers = tds[6].text.strip()
            
            json_obj["movie_info"].append({
                "title": title,
                "magnet_url": magnet_url,
                "size": unicodedata.normalize("NFKD", size),
                "seeders": seeders,
                "leeches": leechers
            })
        
        except Exception as e:
            logging.error(f"Error processing row: {e}")
            continue
    
    return json_obj

def pirate(query = None):
    if not query:
        url = "https://tpb.party/top/200"
    else:
        url = f"https://tpb.party/search/{query}"
    res = requests.get(url)
    if res.status_code != 200:
        raise ValueError("Ops didn't get valid response")
    content = res.content
    soup = BeautifulSoup(content , "html.parser")
    obj = get_json(soup)
    return obj
