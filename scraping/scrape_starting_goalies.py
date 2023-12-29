from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


starting_goalies_url = 'https://www.dailyfaceoff.com/starting-goalies/'



def get_starters():
  chrome_options = Options()
  chrome_options.add_argument('--no-sandbox') # required for replit
  chrome_options.add_argument('--disable-dev-shm-usage')
  chrome_options.add_argument("--ignore-certificate-error")
  chrome_options.add_argument("--ignore-ssl-errors")
  chrome_options.add_argument("log-level=3")

  driver = webdriver.Chrome(options=chrome_options)
  driver.get(starting_goalies_url)

  games = driver.find_elements(By.XPATH, '//article')
  for game in games:
    divs = game.find_elements(By.XPATH, './div')

    # get teams and date/time
    teams, dateTime = divs[0].find_elements(By.XPATH, './/span')
    away, home = teams.get_attribute('innerText').split(" at ")
    date, time = dateTime.get_attribute('innerText').split(" | ")
    print(away, home, date, time)

    # get goalies
    awayGoalie, homeGoalie = divs[1].find_elements(By.XPATH, './div')
    print(get_goalie_info(awayGoalie))



  driver.quit()


def get_goalie_info(goalie: webdriver.remote.webelement.WebElement):
  # get goalie name
  divs = goalie.find_element(By.XPATH, './/div').find_elements(By.XPATH, './/div')
  name = divs[2].get_attribute('innerText')
  img = divs[0].find_element(By.XPATH, './/img').get_attribute('src')

  status = divs[3].find_elements(By.XPATH, './/span')[1].get_attribute('innerText')
  statusTime = divs[3].find_elements(By.XPATH, './/span')[2].get_attribute('innerText')

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

  return {'name': name, 'status': {'status': status, 'time': statusTime}, 'img': img, 'stats': stats, 'blurb': blurb}

