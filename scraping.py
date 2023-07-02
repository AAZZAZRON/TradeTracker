from selenium import webdriver
from selenium.webdriver.common.by import By

trades_url = 'https://www.sportsnet.ca/hockey/nhl/trade-tracker'
signings_url = 'https://www.sportsnet.ca/hockey/nhl/signings'


def element_exists(el, xpath):
    return len(el.find_elements(By.XPATH, xpath)) > 0


def get_trades():
    driver = webdriver.Chrome()
    driver.get(trades_url)
    trades = driver.find_elements(By.XPATH, '//div[@class="event-details"]')
    for trade in trades:
        date = trade.find_element(By.XPATH, './/div[@class="event-date"]')
        print(date.text)
        teamLeft = trade.find_element(By.XPATH, './/div[@class="team left"]')
        teamRight = trade.find_element(By.XPATH, './/div[@class="team right"]')

        isThirdTeam = element_exists(trade, './/div[@class="team center"]')
        teamCenter = trade.find_element(By.XPATH, './/div[@class="team center"]') if isThirdTeam else None

        print(repr(teamLeft.text), repr(teamCenter.text) if isThirdTeam else None, repr(teamRight.text))
        break
    driver.quit()


def get_signings():
    driver = webdriver.Chrome()
    driver.get(signings_url)
    signings = driver.find_elements(By.XPATH, '//div[@class="event-details"]')
    date = ''
    for signing in signings:
        if element_exists(signing, './/div[@class="event-date"]'):
            date = signing.find_element(By.XPATH, './/div[@class="event-date"]').text
        data = signing.find_element(By.XPATH, './/div[@class="EventDetails__cont"]')
        print(data.text)
        break
    driver.quit()


# if __name__ == '__main__':
#     create_driver()
#     get_trades()
#     get_signings()
