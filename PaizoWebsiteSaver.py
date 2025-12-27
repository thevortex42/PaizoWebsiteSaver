import requests
from bs4 import BeautifulSoup
import lxml
import datetime
import csv
import getpass

# Define constants
## In Windows: Double the \ (for example: 'c:\\temp')
OUTPUT_PATH = '/home/holger/PaizoWebsiteSaver/Output/'
LOGIN_URL = 'https://paizo.com/organizedPlay/myAccount'
CHARACTERS_URL = 'https://paizo.com/organizedPlay/myAccount/player'
SESSION_URL = 'https://paizo.com/organizedPlay/myAccount/allsessions'
BOONS_URL = 'https://paizo.com/organizedPlay/myAccount/rewards'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'

def login(session):
    """Login and acquire a session cookie"""
    loginPage = session.get(LOGIN_URL)
    
    soup = BeautifulSoup(loginPage.content, 'lxml')
    loginForm = soup.find('form')
    
    #Read hidden input fields
    form_data = {}
    for input_tag in loginForm.find_all('input'):
        name = input_tag.get('name')
        value = input_tag.get('value', '')
        form_data[name] = value

    #Obligatory form fields that are usually created via AJAX
    form_data['AJAX_SUBMIT_BUTTON_NAME'] = 'StandardPageTemplate.0.1.15.11.3.1.3.2.3.3.7.3.2.1.3.1.1.5'
    form_data['p'] = 'v5748aid7tg62'
    
    #Username and Password - TODO: Read from file!
    username = input("Paizo.com email: ")
    password = password = getpass.getpass('Password: ')
    
    form_data['e'] = username
    form_data['zzz'] = password
    
    #Get the URL we need to post the form to
    form_action = loginForm.get('action')
    action_url = requests.compat.urljoin(LOGIN_URL, form_action)
    
    #Add URL parameters
    timestamp = int(datetime.datetime.now().timestamp() * 1000)
    URL_params = '?_u=BrowsePageAjaxSignIn&' + str(timestamp)
    action_url += URL_params
    
    #Post the Data to the Login URL
    
    response = requests.post(action_url, data=form_data)
    
    session.cookies.update(response.cookies)
    
    return response.status_code
    
def getSessions(session):
    """Get the session list"""
    print("Page 1")
    sessionList = session.get(SESSION_URL)

    path = OUTPUT_PATH + "sessions_1.html"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(sessionList.text)

    soup = BeautifulSoup(sessionList.content, 'lxml')

    #Loop trough more pages
    i = 2
    while soup.find('a', string='next >'):
        print("Page "+str(i))
        nextPage = soup.find('a', string='next >')['href']
        nextPageUrl = requests.compat.urljoin(LOGIN_URL, nextPage)
        sessionList = session.get(nextPageUrl)

        path = OUTPUT_PATH + "sessions_" + str(i) + ".html"
        with open(path, 'w', encoding='utf-8') as f:
            f.write(sessionList.text)

        soup = BeautifulSoup(sessionList.content, 'lxml')
        i = i+1

def main():
    #Initialize Session
    session = requests.Session()
    
    print("Logging in")
    
    loginForm = login(session)
    if (loginForm == 200):
        print("Login successful")
        
    print("Downloading Character List")
    characterList = session.get(CHARACTERS_URL)
    path = OUTPUT_PATH + "characters.html"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(characterList.text)
    
    print("Downloading Session List")
    getSessions(session)
        
    print("Downloading Boon List")
    boonList = session.get(CHARACTERS_URL)
    path = OUTPUT_PATH + "boons.html"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(boonList.text)

    
if __name__ == "__main__":
    main()
