from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import db_tools
import asyncio
import discord


trades_url = 'https://www.sportsnet.ca/hockey/nhl/trade-tracker'

'''
scrapes website for trades
returns all the ones that have not been shown (up to however many on initial load)
'''
def scrape_trades():
  chrome_service = Service(r"/usr/lib/chromium-browser/chromedriver")
  
  chrome_options = Options()
  chrome_options.add_argument("start-maximized")
  chrome_options.add_argument("disable-infobars")
  chrome_options.add_argument("--disable-extensions")
  chrome_options.add_argument("--disable-gpu")
  chrome_options.add_argument("--disable-dev-shm-usage")
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument("--ignore-certificate-error")
  chrome_options.add_argument("--ignore-ssl-errors")
  chrome_options.add_argument("log-level=3")


  driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
  driver.get(trades_url)
  trades = driver.find_elements(By.XPATH, '//div[@class="event-details"]')
  ret = []

  # get all of the data
  for trade in trades[:10]:
    data = {}

    # get date
    date = trade.find_element(By.XPATH, './/div[@class="event-date"]')
    trade_details = date.find_element(By.XPATH, './/a').get_attribute('href')

    # get teams
    teams = trade.find_elements(By.XPATH, './/div[contains(@class, "team ")]')

    # parse the data from the teams
    parsedTeams = []
    for team in teams:
      teamData = {}
      teamName = team.find_element(By.XPATH, './/div[@class="team-name"]').text
      details = team.find_elements(By.XPATH, './/div[@class="playerDetails"]')
      acq = []
      for detail in details:
        desc = detail.text
        link = detail.find_elements(By.XPATH, './/a')
        if len(link) == 0:
          link = None
        else:
          link = link[0].get_attribute('href')
        acq.append({'desc': desc, 'link': link})
      icon = team.find_element(By.XPATH, './/img').get_attribute('src')

      # TODO: fix this too // currently gets team name from image url
      teamName = icon.split("/")[-1].split(".")[0].replace("-", " ").title()

      teamData['name'] = teamName
      teamData['icon'] = icon
      teamData['acq'] = acq
      parsedTeams.append(teamData)

    # add data to the return list
    data["date"] = date.text[:-10]
    data["details"] = trade_details
    data["teams"] = parsedTeams

    ret.append(data)

  driver.quit()
  return ret



def create_trade_embed(data):
  embed = discord.Embed(color=0x50afaa)
  embed.title = f'TRADE: {data["date"]}'
  embed.url = data["details"]
  embed.set_thumbnail(url=data["teams"][0]["icon"])  # TODO: merge team icons together

  for team in data["teams"]:
    name = team["name"]
    icon = team["icon"]
    acq = team["acq"]

    value = ""
    for player in acq:
      desc = player["desc"]
      link = player["link"]
      if link:
        value += f"- [{desc}]({link})\n"
      else:
        value += f"- {desc}\n"

    embed.add_field(name=f"{name} Acquire:", value=value, inline=False)

  return embed



async def send_trade_embeds(client):
    # print("get trades")
    # get all subscribed channels
    channels = db_tools.getChannels()  # or [ADMIN_CHANNEL]
    removed = 0

    # get the trades
    coro = asyncio.to_thread(scrape_trades)
    trades = await coro

    check = db_tools.getLastTradeShown()  # last one displayed
    db_tools.setLastTradeShown(trades[0])
    # print(trades[0])

    for trade in trades:
      if check == None or check == trade:  # if trade is equal to last one displayed (as per db)
        break
      embed = create_trade_embed(trade) # create embed
      if removed:
        channels = db_tools.getChannels()
        removed = 0
      for channel in channels:
        try:
          await client.get_channel(channel).send(embed=embed)
        except AttributeError:  # if channel is deleted
          # print(f"Channel {channel} not found. Removing from db.")
          db_tools.removeChannel(channel)
          removed = 1
      if check["details"] == trade["details"]:  # if trade is equal to last one displayed (as per db) but modified
        break
      await asyncio.sleep(1)


