'''
uses selenium to scrape sportsnet for trades and signings
'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

trades_url = 'https://www.sportsnet.ca/hockey/nhl/trade-tracker'
signings_url = 'https://www.sportsnet.ca/hockey/nhl/signings'


'''
scrapes website for trades
returns all the ones that have not been shown (up to however many on initial load)
'''
def get_trades():
  chrome_options = Options()
  chrome_options.add_argument('--no-sandbox') # required for replit
  chrome_options.add_argument('--disable-dev-shm-usage')
  chrome_options.add_argument("--ignore-certificate-error")
  chrome_options.add_argument("--ignore-ssl-errors")
  chrome_options.add_argument("log-level=3")

  driver = webdriver.Chrome(options=chrome_options)
  driver.get(trades_url)
  trades = driver.find_elements(By.XPATH, '//div[@class="event-details"]')
  ret = []

  # get all of the data
  for trade in trades[:5]:
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


'''
scrapes website for signings
returns all the ones that have not been shown (up to however many on initial load)
'''
def get_signings():
  chrome_options = Options()
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument('--disable-dev-shm-usage')
  chrome_options.add_argument("--ignore-certificate-error")
  chrome_options.add_argument("--ignore-ssl-errors")
  chrome_options.add_argument("log-level=3")

  driver = webdriver.Chrome(options=chrome_options)
  driver.get(signings_url)
  signings = driver.find_element(By.XPATH, '//div[@class="TradeSigningsTracker__inner signings"]').find_elements(By.XPATH, './/div[@class="event-details"]')
  date = ''
  ret = []

  for signing in signings[:5]:
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
    nameLink = nameDiv.find_element(By.XPATH, './/a').get_attribute('href')
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
        'link': nameLink,
        'age': age or None,
        'position': position or "No Position",
      },
      'details': tradeDetails,
    }

    ret.append(data)

  driver.quit()
  return ret
