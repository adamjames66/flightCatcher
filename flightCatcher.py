import googlemaps, simplejson, urllib, datetime
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver

API_KEY = ~
CHROMEDRIVER_PATH = ~ #path to chromedriver.exe

def main():
    #prints the recommended time you should leave to catch your flight
    #supports canadian international airports
    
    print('Enter your departure address (including city): ')
    orig = input()
    airport = 0
    print('Enter the value corresponding to the airport your flight will departure from.')
    print('| 1: Calgary | 2: Edmonton  | 3: Halifax    | 4: Kelowna  | 5: Montreal   | 6: Ottawa    | 7: Quebec City |')
    print('| 8: Regina  | 9: Saskatoon | 10: St. Johns | 11: Toronto | 12: Vancouver | 13: Victoria | 14: Winnipeg:  |')    
    while(airport < 1 or airport > 14):
        airport = input()
        airport = int(airport)
        if(airport < 1 or airport > 14):
            print('Please select a value from the given options')
    mode = 0
    print('Enter "1" if you are traveling by car or "2" if you are using transit: ')
    while(mode != 1 and mode != 2):
        mode = input()
        mode = int(mode)
        if(mode != 1 and mode != 14):
            print('Please select a value from the given options')    
    print('Enter the departure time of the flight (ex. "17:30"): ')
    time = input()
    travelingTo = 0
    print('Enter "1" if you are traveling domestically, "2" for internationally, or "3" to the United States: ')
    while(travelingTo < 1 or travelingTo > 3):
        travelingTo = input()
        travelingTo = int(travelingTo)
        if(travelingTo < 1 or travelingTo > 3):
            print('Please select a value from the given options')
    checkInBaggage = 0
    print('Will you be checking in any baggage? Enter "1" for yes or "2" for no: ')
    while(checkInBaggage != 1 and checkInBaggage != 2):
        checkInBaggage = input()
        checkInBaggage = int(checkInBaggage)
        if(checkInBaggage != 1 and checkInBaggage != 2):
            print('Please select a value from the given options')    
    
    if(airport == 1):
        airport = 'YYC'
    elif(airport == 2):
        airport = 'YEG'
    elif(airport == 3):
        airport = 'YHZ'
    elif(airport == 4):
        airport = 'YLW'
    elif(airport == 5):
        airport = 'YUL'
    elif(airport == 6):
        airport = 'YOW'
    elif(airport == 7):
        airport = 'YQB'
    elif(airport == 8):
        airport = 'YQR'
    elif(airport == 9):
        airport = 'YXE'
    elif(airport == 10):
        airport = 'YYT'
    elif(airport == 11):
        airport = 'YYZ'
    elif(airport == 12):
        airport = 'YVR'
    elif(airport == 13):
        airport = 'YYJ'
    elif(airport == 14):
        airport = 'YWG'
        
    if(mode == 1):
        mode = 'driving'
    else:
        mode = 'transit'
        
    if(travelingTo == 1):
        travelingTo = 'Domestic'
    elif(travelingTo == 2):
        travelingTo = 'International'
    else:
        travelingTo = 'United States'
        
    if(checkInBaggage == 1):
        checkInBaggage = True
    else:
        checkInBaggage = False
    
    print('We recommend that you leave for the airport at ' + findTime(orig, mode, time, airport, travelingTo, checkInBaggage) + ' at the latest')
    
def findTime(orig: str, mode: str, time: str, airport: str, travelingTo: str, checkInBaggage: bool) -> str:
    #returns time taken to drive from orig to dest in minutes using google maps api as well as time should arrive at airport in a list
    #gives avg time

    orig = orig.replace(' ', '')
    
    arrivalTime = timeAtAirport(time, airport, travelingTo, checkInBaggage)
    dateList = convertTime(arrivalTime)
    date = datetime(int(dateList[0]), int(dateList[1]), int(dateList[2]), int(dateList[3]), int(dateList[4]),00) #your date
    time = int((date - datetime(1970, 1, 1)).total_seconds())

    url = "https://maps.googleapis.com/maps/api/directions/json?origin={0}&destination={1}&key={2}&mode={3}&arrivalTime_time={4}".format(orig, airport, API_KEY, mode, time)
    
    result = simplejson.load(urllib.request.urlopen(url)) #gives data from google maps
    drivingTime = result['routes'][0]['legs'][0]['duration']['text'] #gets the duration of trip
    
    if drivingTime.find('day') != -1:
        print('Your location is too far away from the selected airport. Sorry...')
        quit()
    
    if drivingTime.find('hours') != -1: #if it has hours seperate the hours from mins, convert hours to mins, and add them back together
        drivingTime = drivingTime.split('hours')
        drivingTimeHour = drivingTime[0]
        drivingTimeMin = drivingTime[1]
        drivingTimeHour = int(''.join(filter(str.isdigit, drivingTimeHour)))
        drivingTimeMin = int(''.join(filter(str.isdigit, drivingTimeMin)))
        drivingTime = drivingTimeHour * 60 + drivingTimeMin
    else:
        drivingTime = int(''.join(filter(str.isdigit, drivingTime))) #removes everything but the integers
    
    arrivalTimeList = arrivalTime.split(':')
    arrivalTimeHour = int(arrivalTimeList[0])
    arrivalTimeMin = int(arrivalTimeList[1])
    leavingTimeMin = int(arrivalTimeMin) - drivingTime
    
    if leavingTimeMin < 0:
        remainderHour = abs(int(leavingTimeMin / 60))
        remainderMin = leavingTimeMin % 60
        leavingTimeHour = arrivalTimeHour - remainderHour
        leavingTimeMin = remainderMin
    else:
        leavingTimeHour = arrivalTimeHour
        
    leavingTimeMin = str(leavingTimeMin)
    
    if len(leavingTimeMin) < 2:
        leavingTimeMin = '0' + leavingTimeMin
    
    return str(leavingTimeHour) + ':' + leavingTimeMin


def convertTime(time: str) -> list:
    #convert 24:00 format to a list containing year, month, day, hour, minute, second for todays date
    
    date = datetime.today().strftime('%Y-%m-%d')
    return date.split('-') + time.split(':')

def timeAtAirport(flightTime: str, airport: str, travelingTo: str, checkInBaggage: bool) -> str:
    #takes a flightTime and estimates what time you should arrive at the airport
    #flightTime - (securityWaitTime + baggage + customs + check in + walking to boarding gate) 
    
    securityTime = securityWaitTime(airport, travelingTo)
    baggageTime = 0
    customsTime = 0
    boardingGateTime = 10 #guess
    checkInTime = 20 #guess
    
    if checkInBaggage == True:
        baggageTime = 10 #guess
    
    if travelingTo == 'Domestic': #checkin deadline
        deadline = 45             #per https://www.aircanada.com/ca/en/aco/home/plan/check-in-information/check-in-and-boarding-times.html#/
    elif airport == 'YYZ': # toronto is different
        deadline = 90
    else:
        deadline = 60
        
    if travelingTo == 'United States':
        customsTime = 30 #guess
        
    totalTime = securityTime + baggageTime + customsTime + boardingGateTime + checkInTime
    
    if totalTime <= deadline + checkInTime:
        totalTime = deadline + checkInTime
          
    totalTimeHour = int(totalTime / 60)
    totalTimeMin = totalTime % 60
    
    flightTimeSplit = flightTime.split(':')
    totalMinusFlightTime = [0,0]
    totalMinusFlightTime[0] = int(flightTimeSplit[0]) - int(totalTimeHour)
    totalMinusFlightTime[1] = int(flightTimeSplit[1]) - int(totalTimeMin)
    
    totalMinusFlightTime = updateTime(totalMinusFlightTime[0], totalMinusFlightTime[1])
    airportTimeStr = str(totalMinusFlightTime[0]) + ':' + str(totalMinusFlightTime[1])
    
    return airportTimeStr
    
def updateTime(hour: int, mins: int) -> list:
    
    if mins < 0:
        remainder = abs(mins % 60)
        mins = remainder
        hour = hour - 1
    
    if hour < 0:
        remainder = abs(hour % 24)
        hour = remainder       
    
    return [hour, mins]
    

def securityWaitTime(airport: str, travelingTo: str) -> int:
    #returns the current wait time of the given airport using https://www.catsa-acsta.gc.ca/en/waittimes
    #travelingTo = Domestic or International or United States
    
    driver = webdriver.Chrome(executable_path = CHROMEDRIVER_PATH)
    
    #this block gives the page we want and formats travelingTo to match the page
    if airport == 'YYC':
        driver.get('https://www.catsa-acsta.gc.ca/en/airport/calgary-international-airport')
        if travelingTo == 'Domestic':
            travelingToNew = 'C Domestic'
        elif travelingTo == 'International':
            travelingToNew = 'D International'
        elif travelingTo == 'United States':
            travelingToNew = 'E United States'               
    elif airport == 'YEG':
        driver.get('https://www.catsa-acsta.gc.ca/en/airport/edmonton-international-airport')
        if travelingTo == 'United States':
            travelingToNew = 'U.S.'
        else: 
            travelingToNew = 'Domestic and International'              
    elif airport == 'YHZ':
        driver.get('https://www.catsa-acsta.gc.ca/en/airport/halifax-stanfield-international-airport')
        if travelingTo == 'United States':
            travelingToNew = 'U.S.'
        else: 
            travelingToNew = 'Domestic and International'            
    elif airport == 'YLW':
        driver.get('https://www.catsa-acsta.gc.ca/en/airport/kelowna-international-airport')
        travelingToNew = 'All flights'
    elif airport == 'YUL':
        driver.get('https://www.catsa-acsta.gc.ca/en/airport/montreal-trudeau-international-airport')
        if travelingTo == 'United States':
            travelingToNew = 'C United States'
        else: 
            travelingToNew = 'A Domestic and International'            
    elif airport == 'YOW':
        driver.get('https://www.catsa-acsta.gc.ca/en/airport/ottawa-international-airport')
        if travelingTo == 'United States':
            travelingToNew = 'U.S.'
        else: 
            travelingToNew = 'Canada/International'            
    elif airport == 'YQB':
        driver.get('https://www.catsa-acsta.gc.ca/en/airport/quebec-city-jean-lesage-international-airport')
        travelingToNew = 'All flights'
    elif airport == 'YQR':
        driver.get('https://www.catsa-acsta.gc.ca/en/airport/regina-international-airport')
        travelingToNew = 'All flights'
    elif airport == 'YXE':
        driver.get('https://www.catsa-acsta.gc.ca/en/airport/saskatoon-international-airport')
        travelingToNew = 'All flights'
    elif airport == 'YYT':
        driver.get('https://www.catsa-acsta.gc.ca/en/airport/st-johns-international-airport')
        travelingToNew = 'All flights'
    elif airport == 'YYZ':
        driver.get('https://www.catsa-acsta.gc.ca/en/airport/toronto-pearson-international-airport')
        if travelingTo == 'Domestic':
            travelingToNew = 'T3 Canada'
        elif travelingTo == 'International':
            travelingToNew = 'T3 International'
        elif travelingTo == 'United States':
            travelingToNew = 'T3 United States'            
    elif airport == 'YVR':
        driver.get('https://www.catsa-acsta.gc.ca/en/airport/vancouver-international-airport')
        if travelingTo == 'Domestic':
            travelingToNew = 'C Canada'
        elif travelingTo == 'International':
            travelingToNew = 'D International'
        elif travelingTo == 'United States':
            travelingToNew = 'E United States'
    elif airport == 'YYJ':
        driver.get('https://www.catsa-acsta.gc.ca/en/airport/victoria-international-airport')
        travelingToNew = 'All flights'
    elif airport == 'YWG':
        driver.get('https://www.catsa-acsta.gc.ca/en/airport/winnipeg-james-armstrong-richardson-international-airport')
        if travelingTo == 'United States':
            travelingToNew = 'U.S.'
        else: 
            travelingToNew = 'Domestic and International'
        
    content = driver.page_source #sites content
    soup = BeautifulSoup(content, features='lxml')
    soup = soup.find('tbody') #content we need
    
    result = soup.get_text()
    result = result.replace('\n', '')
    result = result.replace('                  ', '\n')
    result = result.replace('  ', '')
    result = result.splitlines() #make same as what appears on catsa acsta site and seperate content into list
    
    for element in result:
        if result.index(travelingToNew) == result.index(element): #if element = travelingTo then waitTime = next element
            waitTime = result.pop(result.index(element)+1)
    
    if waitTime.find('-') != -1: #if it is a range it takes the highest num ex. 15-20min = 20min
        waitTime = waitTime.split('-')
        waitTime = waitTime[1]
    waitTime = int(''.join(filter(str.isdigit, waitTime))) #keep only digits
    return waitTime

if __name__ == "__main__":
    main()
