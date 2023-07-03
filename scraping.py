from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import db_tools
import functools
import typing
import asyncio

trades_url = 'https://www.sportsnet.ca/hockey/nhl/trade-tracker'
signings_url = 'https://www.sportsnet.ca/hockey/nhl/signings'
'''
scrapes website for trades
returns all the ones that have not been shown (up to however many on initial load)
'''


def get_trades():
  chrome_options = Options()
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument('--disable-dev-shm-usage')
  chrome_options.add_argument("--ignore-certificate-error")
  chrome_options.add_argument("--ignore-ssl-errors")
  chrome_options.add_argument("log-level=3")

  driver = webdriver.Chrome(options=chrome_options)
  driver.get(trades_url)
  trades = driver.find_elements(By.XPATH, '//div[@class="event-details"]')
  ret = []
  first = None

  # get all of the data
  for trade in trades:
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

      # TODO: fix this too
      teamName = icon.split("/")[-1].split(".")[0].replace("-", " ").title()

      teamData['name'] = teamName
      teamData['icon'] = icon
      teamData['acq'] = acq
      parsedTeams.append(teamData)

    # add data to the return list
    data["date"] = date.text[:-10]
    data["details"] = trade_details
    data["teams"] = parsedTeams

    if first is None:
      first = data

    # check if these are new trades
    if db_tools.isLastTradeShown(data):
      break

    # if new trade, add to return list
    ret.append(data)

  driver.quit()
  print("setting last trade:", first)
  db_tools.setLastTradeShown(first)
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
  signings = driver.find_element(
    By.XPATH,
    '//div[@class="TradeSigningsTracker__inner signings"]').find_elements(
      By.XPATH, './/div[@class="event-details"]')
  date = ''
  ret = []
  first = None

  for signing in signings:
    # swap out the date if it changes
    date_check = signing.find_elements(
      By.XPATH, './/div[contains(@class, "event-date")]')
    if len(date_check) > 0:
      date = date_check[0].text

    # get the data for the signing and ignore mobile data
    signingData = signing.find_element(By.XPATH,
                                       './/div[@class="EventDetails__cont"]')

    tmp = signingData.find_elements(By.XPATH, './/*')

    # team data
    teamAbbr = tmp[0].text
    teamIcon = tmp[0].find_element(By.XPATH, './/img').get_attribute('src')

    # contract data
    contract = tmp[6].text
    length = tmp[7].text.replace("yr", "year")
    capHit = tmp[8].text
    contractType = tmp[9].text

    # player data
    age = tmp[10].text
    position = tmp[11].text

    # urls
    links = signingData.find_elements(By.XPATH, './/a')
    nameLink = links[0].get_attribute('href')
    tradeDetails = links[1].get_attribute('href')

    # TODO: fix this lol
    name = nameLink.split("/")[-2].replace("-", " ").replace("%20",
                                                             " ").title()

    data = {
      'date': date,
      'team': {
        "name": teamAbbr,  # TODO: change to full name
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
        'age': age,
        'position': position,
      },
      'details': tradeDetails,
    }

    if first is None:
      first = data

    # check if these are new signings
    if db_tools.isLastSigningShown(data):
      break

    ret.append(data)

  driver.quit()
  print("setting last signup:", first)
  db_tools.setLastSigningShown(first)
  return ret


# if __name__ == '__main__':
#     create_driver()
#     get_trades()
#     get_signings()
