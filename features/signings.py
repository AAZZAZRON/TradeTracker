from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import db_tools
import asyncio
import discord


signings_url = 'https://www.sportsnet.ca/hockey/nhl/signings'


'''
scrapes website for signings
returns all the ones that have not been shown (up to however many on initial load)
'''
def scrape_signings():
  chrome_service = Service(r"/usr/lib/chromium-browser/chromedriver")

  driver = webdriver.Chrome(service=chrome_service)
  driver.get(signings_url)
  signings = driver.find_element(By.XPATH, '//div[@class="TradeSigningsTracker__inner signings"]').find_elements(By.XPATH, './/div[@class="event-details"]')
  date = ''
  ret = []

  for signing in signings[:10]:
    # swap out the date if it changes
    date_check = signing.find_elements(By.XPATH, './/div[contains(@class, "event-date")]')
    if len(date_check) > 0: # if there is a date
      date = date_check[0].text

    # get the data for the signing and ignore mobile data
    signingData = signing.find_element(By.XPATH, './/div[@class="EventDetails__cont"]')


    # team data
    teamDiv = signingData.find_element(By.XPATH, './/div[@class="signings-col team-details"]')
    teamAbbr = teamDiv.text
    teamIcon = teamDiv.find_element(By.XPATH, './/img').get_attribute('src')


    # contract data
    contract = signingData.find_element(By.XPATH, './/div[@class="signings-col contract-total"]').text
    length = signingData.find_element(By.XPATH, './/div[@class="signings-col contract-length"]').text.replace("yr", "year")
    capHit = signingData.find_element(By.XPATH, './/div[@class="signings-col contract-cap-hit"]').text 
    contractType = signingData.find_element(By.XPATH, './/div[@class="signings-col contract-type"]').text 


    # player data
    nameDiv = signingData.find_element(By.XPATH, './/div[@class="signings-col player-name"]')
    name = nameDiv.text
    # nameLink = nameDiv.find_element(By.XPATH, './/a').get_attribute('href')
    age = signingData.find_element(By.XPATH, './/div[@class="signings-col player-age"]').text 
    position = signingData.find_element(By.XPATH, './/div[@class="signings-col player-position"]').text 
    tradeDetails = signingData.find_element(By.XPATH, './/div[@class="signings-col signings-details"]').find_element(By.XPATH, './/a').get_attribute('href')


    data = {
      'date': date,
      'team': {
        "name": teamAbbr,  # TODO: change to full team name
        'abbr': teamAbbr,
        'icon': teamIcon
      },
      'contract': {
        'total': contract,
        'length': length,
        'capHit': capHit,
        'type': contractType
      },
      'player': {
        'name': name,
        # 'link': nameLink,
        'age': age or None,
        'position': position or "No Position",
      },
      'details': tradeDetails,
    }

    ret.append(data)

  driver.quit()
  return ret



def create_signing_embed(data):
  embed = discord.Embed(color=0xe1b51e)
  embed.title = f'SIGNING: {data["player"]["name"]} to {data["team"]["name"]}'
  embed.description = f'{data["date"]}'
  embed.url = data["details"]
  embed.set_thumbnail(url=data["team"]["icon"])

  player = data["player"]
  player_value = f"{player['name']} - {player['position']}"
  if player["age"]:
    player_value += f"\n{player['age']} years old"

  embed.add_field(name="Player: ", value=player_value, inline=False)

  contract = data["contract"]
  contract_value = f"{contract['capHit']} x {contract['length']}\nTotal: {contract['total']}\nType: {contract['type']}"
  embed.add_field(name="Contract: ", value=contract_value, inline=False)

  return embed





async def send_signing_embeds(client):
    # print("get signings")
    # get all subscribed channels
    channels = db_tools.getChannels()  # or [ADMIN_CHANNEL]
    removed = 0

    # signings
    coro = asyncio.to_thread(scrape_signings)
    signings = await coro

    check = db_tools.getLastSigningShown()

    while signings and signings[0]["player"]["name"] == "": # remove empty signings
      signings.pop(0)

    if signings:  
      db_tools.setLastSigningShown(signings[0])
    # print(signings[0])

    for signing in signings:
      if check == None or check == signing:
        break
      embed = create_signing_embed(signing)
      if removed:
        channels = db_tools.getChannels()
        removed = 0
      for channel in channels:
        try:
          await client.get_channel(channel).send(embed=embed)
        except AttributeError:
          # print(f"Channel {channel} not found. Removing from db.")
          db_tools.removeChannel(channel)
          removed = 1
      if check["player"]["name"] == signing["player"]["name"]:  # if signing is equal to last one displayed (as per db) but modified
        break
      await asyncio.sleep(1)
