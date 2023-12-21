import requests as req
from bs4 import BeautifulSoup as bs 
import csv
import discord
from discord.ext import tasks
from constants import CHANNEL_ID, TOKEN
import os.path

def get_location(comp):
    return comp.find(attrs={'class':'location'}).text.strip()

def get_link(comp):
    return 'https://www.worldcubeassociation.org' + comp.find(attrs={'class':'competition-link'}).find('a')['href']

def get_name(comp):
    return comp.find(attrs={'class':'competition-link'}).find('a').text.strip()

def get_date(comp):
    return comp.find(attrs={'class':'date'}).text.strip()

def announcement(comp):
    return f'''Hey @everyone, the "*{comp['name']}*" competition has been posted on the WCA page! Here are the details: 

        **Date**: {comp['date']}, 
        **Location**: {comp['location']}
        Click [here]({comp['link']}) for more info!
        
Sign-up for these competitions goes quick, so get on it!
        '''

COMPS_URL = 'comps.csv'

def check_for_events():
    url = 'https://www.worldcubeassociation.org/competitions?region=USA&search=Michigan&state=present&year=all+years&from_date=&to_date=&delegate=&display=list'
    r = req.get(url)
    r.encoding = 'ISO-8859-1'
    content = r.content
    soup = bs(content, 'html.parser')
    comps = soup.find_all('li', attrs={'class':'list-group-item not-past'})
    S = set()
    with open(COMPS_URL, 'r') as f:
        reader = csv.reader(f) 
        for row in reader:
            S.add(str(row))

    new_comps = []
    with open(COMPS_URL, 'a') as f:
        writer = csv.writer(f)
        for comp in comps:
            name = get_name(comp)
            date = get_date(comp)
            if str([name, date]) not in S:
                new_comps.append({
                    'name':name,
                    'date':date,
                    'link':get_link(comp),
                    'location':get_location(comp)
                })
                writer.writerow([name, date])

    return new_comps

class MyClient(discord.Client):

    @tasks.loop(hours=24)
    async def slow_count(self):
        new_comps = check_for_events()
        if len(new_comps) > 0:
            channel = self.get_channel(CHANNEL_ID)
            for comp in new_comps:
                await channel.send(announcement(comp))

    async def on_ready(self):
        self.slow_count.start()
    
def main():
    if not os.path.exists(COMPS_URL):
        open(COMPS_URL, "x")
    intents = discord.Intents.default()
    intents.messages = True
    client = MyClient(intents=intents)
    client.run(TOKEN)

if __name__ == '__main__':
    main()