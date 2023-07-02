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
    ret = []
    for trade in trades:
        data = {}


        # get date
        date = trade.find_element(By.XPATH, './/div[@class="event-date"]')
        trade_details = date.find_element(By.XPATH, './/a').get_attribute('href')


        # get teams
        teamLeft = trade.find_element(By.XPATH, './/div[@class="team left"]')
        teamRight = trade.find_element(By.XPATH, './/div[@class="team right"]')
        isThirdTeam = element_exists(trade, './/div[@class="team center"]')
        if isThirdTeam:
            teamCenter = trade.find_element(By.XPATH, './/div[@class="team center"]')
            teams = [teamLeft, teamCenter, teamRight]
        else:
            teams = [teamLeft, teamRight]
        

        # parse the data from the teams
        parsedTeams = []
        for team in teams:
            teamData = {}
            teamName = team.find_element(By.XPATH, './/div[@class="team-name"]').text
            details = team.find_elements(By.XPATH, './/div[@class="playerDetails"]')
            acq = []
            for detail in details:
                desc = detail.text
                if element_exists(detail, './/a'):
                    link = detail.find_element(By.XPATH, './/a').get_attribute('href')
                else:
                    link = None
                acq.append({'desc': desc, 'link': link})            
            icon = team.find_element(By.XPATH, './/img').get_attribute('src')
            
            teamData['name'] = teamName
            teamData['icon'] = icon
            teamData['acq'] = acq
            parsedTeams.append(teamData)

        # add data to the return list
        data["date"] = date.text[:-10]
        data["details"] = trade_details
        data["teams"] = parsedTeams


        ret.append(data)
        print(data)
        break

    driver.quit()
    return ret


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
