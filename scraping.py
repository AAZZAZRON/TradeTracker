from selenium import webdriver
from selenium.webdriver.common.by import By
import db_tools

trades_url = 'https://www.sportsnet.ca/hockey/nhl/trade-tracker'
signings_url = 'https://www.sportsnet.ca/hockey/nhl/signings'


# checks if an element exists with the given xpath
def element_exists(el, xpath):
    return len(el.find_elements(By.XPATH, xpath)) > 0


'''
scrapes website for trades
returns all the ones that have not been shown (up to however many on initial load)
'''
def get_trades():
    driver = webdriver.Chrome()
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


        if first is None:
            first = data

        
        # check if these are new trades
        if db_tools.isLastTradeShown(data):
            print("setting last trade:", first)
            db_tools.setLastTradeShown(first)
            break

        # if new trade, add to return list
        ret.append(data)


    driver.quit()
    return ret


'''
scrapes website for signings
returns all the ones that have not been shown (up to however many on initial load)
'''
def get_signings():
    driver = webdriver.Chrome()
    driver.get(signings_url)
    signings = driver.find_element(By.XPATH, '//div[@class="TradeSigningsTracker__inner signings"]').find_elements(By.XPATH, './/div[@class="event-details"]')
    date = ''
    ret = []
    first = None

    for signing in signings:
        # swap out the date if it changes
        if element_exists(signing, './/div[@class="event-date"]'):
            date = signing.find_element(By.XPATH, './/div[@class="event-date"]').text
        elif element_exists(signing, './/div[@class="event-date tail"]'):
            date = signing.find_element(By.XPATH, './/div[@class="event-date tail"]').text


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
                "name": teamAbbr, # TODO: change to full name
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
            print("setting last signup:", first)
            db_tools.setLastSigningShown(first)
            break

        ret.append(data)



    driver.quit()
    return ret


# if __name__ == '__main__':
#     create_driver()
#     get_trades()
#     get_signings()
