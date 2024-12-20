import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from twilio.rest import Client
from datetime import datetime

import db_tools
import asyncio


starting_goalies_url = 'https://www.dailyfaceoff.com/starting-goalies/'



def scrape_starting_goalies():
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
  chrome_options.add_argument("--enable-unsafe-swiftshader")

  driver = webdriver.Chrome(options=chrome_options)
  driver.get(starting_goalies_url)

  data = {}
  date = datetime.now().strftime("%b %d, %Y")

  games = driver.find_elements(By.XPATH, '//article')
  for game in games:
    divs = game.find_elements(By.XPATH, './div')

    # get teams and date/time
    teams, dateTime = divs[0].find_elements(By.XPATH, './/span')
    awayTeam, homeTeam = teams.get_attribute('innerText').split(" at ")
    date, time = dateTime.get_attribute('innerText').split(" | ")

    # get goalies
    awayGoalie, homeGoalie = divs[1].find_elements(By.XPATH, './div')
    awayGoalieStatus, awayGoalieInfo = scrape_goalie_info(awayGoalie)
    homeGoalieStatus, homeGoalieInfo = scrape_goalie_info(homeGoalie)

    data[awayTeam] = {
      "game": "away",
      "against": homeTeam,
      "status": awayGoalieStatus,
      "date": date,
      "time": time,
      "goalie": awayGoalieInfo,
    }

    data[homeTeam] = {
      "game": "home",
      "against": awayTeam,
      "status": homeGoalieStatus,
      "date": date,
      "time": time,
      "goalie": homeGoalieInfo,
    }

  driver.quit()
  return date, data


def scrape_goalie_info(goalie: webdriver.remote.webelement.WebElement):
  # get goalie name
  divs = goalie.find_element(By.XPATH, './/div').find_elements(By.XPATH, './/div')
  name = divs[3].get_attribute('innerText')
  img = divs[1].find_element(By.XPATH, './/img').get_attribute('src')

  status = divs[4].find_elements(By.XPATH, './/span')[1].get_attribute('innerText')
  statusTime = divs[4].find_elements(By.XPATH, './/span')[2].get_attribute('innerText')

  # get the stats
  stats = {}
  for row in goalie.find_elements(By.XPATH, './/tr'):
    stat, value = row.find_elements(By.XPATH, './/td')
    stats[stat.get_attribute('innerText')[:-1]] = value.get_attribute('innerText')

  # get blurb
  blurb = goalie.find_elements(By.XPATH, './div')[1].find_elements(By.XPATH, './div')
  if len(blurb) > 0:
    spans = blurb[0].find_elements(By.XPATH, './/span')
    blurb = {
      'time': spans[0].get_attribute('innerText'),
      'text': spans[1].get_attribute('innerText'),
      'source': spans[2].get_attribute('innerText').strip("Source: "),
    }
  else:
    blurb = None
  return {'status': status, 'time': statusTime}, {'name': name, 'img': img, 'stats': stats, 'blurb': blurb}



async def handle_starting_goalie_requests():
  ACCOUNT_SID = os.getenv("ACCOUNT_SID")
  MESSAGING_SID = os.getenv("MESSAGING_SID")
  AUTH_TOKEN = os.getenv("AUTH_TOKEN")
  TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
  MY_NUMBER = os.getenv("MY_NUMBER")

  client = Client(ACCOUNT_SID, AUTH_TOKEN)

  coro = asyncio.to_thread(scrape_starting_goalies)
  date, data = await coro

  prev_date = db_tools.getLastDateSaved()
  if prev_date == None or prev_date != date:
    db_tools.setLastDateSaved(date)
    db_tools.setLastGoalieData(data)
    # db_tools.setRequests({})
    return
  
  prev_data = db_tools.getLastGoalieData()
  for team in prev_data.keys():
    if data[team]["status"] != prev_data[team]["status"]:
      if data[team]["status"]["status"] == "Confirmed":
        goalie = data[team]["goalie"]
        against = data[team]["against"]
        name = goalie["name"]
        WLOTL = goalie["stats"]["W-L-OTL"]
        GAA = goalie["stats"]["GAA"]
        SV = goalie["stats"]["SV%"]
        SO = goalie["stats"]["SO"]
        message = f"Confirmed: {name} ({team}) against the {against}.\n\
          Stats:\n - W-L-OTL: {WLOTL}\n - GAA: {GAA}\n - SV%: {SV}\n - SOs: {SO}"
        client.messages.create(
          messaging_service_sid=MESSAGING_SID,
          body=message,
          to=MY_NUMBER,
        )

