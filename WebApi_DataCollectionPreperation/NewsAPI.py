# http://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=a8e793aa99b940ae9b75ce085eb392c7

# Import important packages
import json
import urllib.request
import requests
import pandas as pd
import os
import numpy as np
from PIL import Image
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import seaborn as sns


# pip install wordcloud
# conda install -c conda-forge wordcloud


# The request can only hit the data for 30 days, if you try to hit before you will get error
# http://newsapi.org/v2/everything?q=corona&from=2020-01-01&to=2020-03-10&sortBy=popularity&apiKey=a8e793aa99b940ae9b75ce085eb392c7


def getApiKey():
    '''
    Info: This method return the api key for  http://newsapi.org
    '''
    print("Returning APIKey")
    return 'a8e793aa99b940ae9b75ce085eb392c7'


# Calculating time to hit the query within range API permits
# strftime() converts a datetime object to string. Capital letter in format changes the format (y -> 20, Y -> 2020)
# A timedelta object represents a duration, the difference between two dates or times.
today_date = datetime.today().strftime("%Y-%m-%d")
lastMonth_date = (datetime.today() - timedelta(days=29)).strftime("%Y-%m-%d")

rootDirName = '\GenerateFiles'  # Creating directory to save data generated
imageDir = '\Image'


def getCoronaMonitorResponse():
    '''
    :Info - This function returns response fetched from free Rapid api to
    monitor corona statistics which is updated twice every hour
    :return: Returns response in json
    '''
    urlCoronaMonitor = "https://coronavirus-monitor.p.rapidapi.com/coronavirus/cases_by_country.php"
    headers = {
        'x-rapidapi-host': "coronavirus-monitor.p.rapidapi.com",
        'x-rapidapi-key': "079c8debbcmsh31a653d4e5ea7e1p19b967jsn130707a652e2"
    }
    response = requests.request("GET", urlCoronaMonitor, headers=headers)
    json_res = response.json()
    json_res = json_res['countries_stat']

    print("Returning Json response from RapidAPI")
    return json_res


endpoints = ['everything', 'top-headlines']


def getUrl(endpoint):
    '''
    :Info Creating url as per the requirement according to specific endpoints.
    Free api can only hit upto 29 days, if tried prior dates, then error throws.
    :param endpoint: There are mainly two types of endpoint in newsapi
    1. top-headlines 2. everything. Can be checked here https://newsapi.org/docs/endpoints
    :return: Returns url according to end points - As of now focusing on Corona updates only
    '''

    newsTopic = 'corona'
    # ISO 3166 code is obtained for Ireland (ie)
    # from https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes
    country = 'ie'

    if endpoint == 'everything':
        urlEverything = 'http://newsapi.org/v2/' + endpoints[
            0] + '?q=' + newsTopic + '&from=' + today_date + '&to=' + lastMonth_date + '&sortBy=popularity&language=en&apiKey=' + getApiKey()
        print("Get URL "+urlEverything)
        return urlEverything

    elif endpoint == 'top-headlines':
        urlTopheadlines = 'http://newsapi.org/v2/' + endpoints[
            1] + '?country=' + country + '&category=business&apiKey=' + getApiKey()
        return urlTopheadlines


def generate_WordCloud(fileContent):
    mask = np.array(Image.open(os.getcwd()+rootDirName+imageDir+'\\'+'plainvirus.png'))
    wordcloud = WordCloud(stopwords=STOPWORDS, background_color='white',max_words=120,mask=mask).generate(fileContent)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

    imagePath = os.getcwd() + rootDirName + imageDir
    if not os.path.exists(imagePath):
        print('Creating directory -', imagePath)
        os.makedirs(imagePath, exist_ok=True)

    print("Printing WordCloud")
    wordcloud.to_file(imagePath + '\\' + 'Image' + today_date + '.png')


def getCoronaUpdatesWorldwide():
    # Establising connection and fetching response from api
    response = urllib.request.urlopen(getUrl(endpoints[0]))
    raw_json = response.read().decode("utf-8")
    data = json.loads(raw_json)
    jsondata = data['articles']
    print("In method getCoronaUpdatesWorldwide()")
    return jsondata


def cleanDataframe(dfCovidcsv):
    dfCovidcsv['active_cases'] = [int(i.replace(',', '')) for i in dfCovidcsv['active_cases']]
    dfCovidcsv['cases'] = [int(i.replace(',', '')) for i in dfCovidcsv['cases']]

    dfCovidcsv['deaths'] = [int(i.replace(',', '')) for i in dfCovidcsv['deaths']]
    dfCovidcsv['new_cases'] = [int(i.replace(',', '')) for i in dfCovidcsv['new_cases']]

    new_deaths = []
    for i in dfCovidcsv['new_deaths']:
        if isinstance(i, int) and int(i) <= 999:
            new_deaths.append(i)
        else:
            new_deaths.append(int(i.replace(',', '')))

    dfCovidcsv['new_deaths'] = new_deaths
    # print(dfCovidcsv['new_deaths'])

    dfCovidcsv['serious_critical'] = [int(i.replace(',', '')) for i in dfCovidcsv['serious_critical']]

    dfCovidcsv['total_recovered'] = [int(i.replace(',', '')) for i in dfCovidcsv['total_recovered']]

    return dfCovidcsv


def generateResponsefiles(newsFilename, statsFilename):
    # File handling...
    print("In generateResponsefiles")
    if not os.path.exists(os.getcwd() + rootDirName):
        print('Creating directory -', os.getcwd() + rootDirName)
        os.makedirs(os.getcwd() + rootDirName, exist_ok=True)


    # Creating json respoonse file for Corona news api
    newsFilename = os.getcwd() + rootDirName + '\\' + newsFilename + '_' + today_date
    with open(newsFilename + '.json', mode='w') as newsjson:
        json.dump(getCoronaUpdatesWorldwide(), newsjson, sort_keys=True, indent=4)
        newsjson.close()

    readNewsfile = open(newsFilename + '.json', mode='r')
    df_news = pd.read_json(readNewsfile, typ='frame')
    loaded_df = pd.DataFrame(df_news)
    loaded_df.dropna()
    contentfile = os.getcwd() + rootDirName + '\\' + 'NewsCSV' + '_' + today_date
    loaded_df.to_csv(contentfile + '.csv')

    # iterating through content of news and saving it to another text file for analysis
    # replacing all unwanted numbers and characters with null values to clean data
    contenttxt = os.getcwd() + rootDirName + '\\' + 'Newstxt' + '_' + today_date
    f_newscontent_text = open(contenttxt + '.txt', mode='w')
    f_newscontent_text.write("\n" + "*******Written today - " + str(today_date) + "*******" + "\n")

    for contents in loaded_df['content']:
        if '[' in contents:
            unwantedChars = contents[contents.find('['):]
            contents = contents.replace(unwantedChars, '').strip()
            f_newscontent_text.write(str(contents) + "\n\n")
        else:
            f_newscontent_text.write(str(contents) + "\n\n")
    f_newscontent_text.close()


    statsFilename = os.getcwd() + rootDirName + '\\' + statsFilename + '_' + today_date
    with open(statsFilename + '.json', mode='w') as coronaStats:
        json.dump(getCoronaMonitorResponse(), coronaStats, sort_keys=True, indent=4)
        coronaStats.close()

    readStatsfile = open(statsFilename + '.json', mode='r')
    df_stats = pd.read_json(readStatsfile, typ='frame')
    loaded_stats = pd.DataFrame(df_stats)
    # loaded_df.dropna()
    #loaded_stats = cleanDataframe(loaded_stats)
    countryStatsfile = os.getcwd() + rootDirName + '\\' + 'CountrywiseCoronaStats' + '_' + today_date
    loaded_stats.to_csv(countryStatsfile + '.csv')


def plotTotalCasesInCountry(countryNames,totalCases):
    #print(list(countryNames),list(totalCases))
    totalCases = [int(i.replace(',','')) for i in totalCases]
    print("In plotTotalCasesInCountry")
    plt.figure(figsize=(10,10))
    plt.bar(list(countryNames),totalCases )
    plt.xticks(rotation = 90, fontsize = 15)
    plt.yticks(fontsize=15)
    plt.xlabel("Country", fontsize = 20)
    plt.ylabel("Total COVID Cases",fontsize = 20)
    plt.title("COVID | TOP 15 Impacted Countries "+today_date,fontsize = 25)

    plt.savefig(os.getcwd() + rootDirName + imageDir + '\\'+'MostImpactedCountries_'+today_date+'.png')
    plt.show()


def plotMultipleLineGraph(virusStats):
    data = virusStats
    print("In plotMultipleLineGraph")
    active_cases = list(data['active_cases'].head(15))
    int_active_cases = [int(i.replace(',','')) for i in active_cases]
    data['active_cases'] = [int(i.replace(',','')) for i in data['active_cases']]

    deaths = list(data['deaths'].head(15))
    int_deaths = [int(i.replace(',','')) for i in deaths]
    data['deaths'] = [int(i.replace(',', '')) for i in data['deaths']]




    for i in data['new_cases']:
        if isinstance(i,int) and int(i) <=999:
            data['new_cases'] = i
        else:
            data['new_cases'] = int(i.replace(',',''))


    new_cases = list(data['new_cases'].head(15))
    int_new_cases = []
    for i in new_cases:
        if isinstance(i,int) and int(i) <= 999:
            int_new_cases.append(i)
        else:
            int_new_cases.append(int(i.replace(',', '')))

    #int_new_cases = [int(i.replace(',','')) for i in new_cases]

    serious_critical = list(data['serious_critical'].head(15))
    int_serious_critical = [int(i.replace(',','')) for i in serious_critical]

    data['serious_critical'] = [int(i.replace(',','')) for i in data['serious_critical']]

    total_recovered = list(data['total_recovered'].head(15))
    int_total_Recovered = [int(i.replace(',','')) for i in total_recovered]

    data['total_recovered'] = [int(i.replace(',','')) for i in data['total_recovered']]

    country_names = list(data['country_name'].head(15))



    plt.figure(figsize=(10, 10))
    plt.plot(int_active_cases,country_names, color="purple", linewidth=3)
    plt.plot(int_deaths,country_names, color="green", linewidth=3)
    plt.plot(int_new_cases,country_names, color="blue", linewidth=3)
    plt.plot(int_serious_critical,country_names, color="red", linewidth=3)
    plt.plot(int_total_Recovered,country_names, color="yellow", linewidth=3)
    plt.grid(axis="x")

    plt.xlabel('Cases Count', fontsize=20)
    plt.ylabel('Countries', fontsize=20)
    plt.xticks(rotation=45, fontsize=15)
    plt.yticks(fontsize=15)

    plt.title("COVID | Country Statistics on " + today_date, fontsize=25)
    plt.legend(["Active Cases", "Deaths", "New Cases", "Serious Critical", "Total Recovered"], fontsize=15)
    plt.savefig(os.getcwd() + rootDirName + imageDir + '\\'+'COVIDCountriesStats_' + today_date + '.png')
    plt.show()

    #sns.pairplot(data)



def plotPieChart(virusStats):
    print("In plotPieChart")
    virusStats['cases'] = [int(i.replace(',', '')) for i in virusStats['cases']]
    totalCases = virusStats['cases'].sum()

    #virusStats['deaths'] = [int(i.replace(',', '')) for i in virusStats['deaths']]
    #deaths_ = []
    #for i in virusStats['deaths']:
    #    if isinstance(i, int) and int(i) <= 999:
    #        deaths_.append(i)
    #    else:
    #        deaths_.append(i.replace(',', ''))

    #virusStats['deaths'] = deaths_
    deaths = virusStats['deaths'].sum()

    virusStats['total_recovered'] = [int(i.replace(',', '')) for i in virusStats['total_recovered']]
    recovered = virusStats['total_recovered'].sum()

    active = totalCases - (deaths + recovered)

    labels = ['Total Cases', 'Deaths', 'Recovered', 'Active']
    stats = [totalCases,deaths,recovered,active]

    print("Total=", totalCases, " Deaths=", deaths, " Recovered=", recovered, " Active=", active)
    plt.figure(figsize=(10, 10))
    plt.pie(stats,labels=labels,autopct='%1.1f%%')
    plt.savefig(os.getcwd()+rootDirName+imageDir+'\\'+'COVIDPIE_' + today_date + '.png')
    plt.show()


def plotLineChart():
    print("In plotLineChart")
    dailyStatsDir = []
    totalCases = []
    totalDeath = []
    for dirs in os.listdir('GenerateFiles'):
        if str(dirs).startswith('CountrywiseCoronaStats'):
            dailyStatsDir.append(dirs)
            df = pd.read_csv(os.getcwd()+rootDirName+'\\'+dirs)
            df['cases'] = [int(i.replace(',', '')) for i in df['cases']]
            totalCases.append(df['cases'].sum())

            df['deaths'] = [int(i.replace(',', '')) for i in df['deaths']]
            totalDeath.append(df['deaths'].sum())


    dates = []
    for eachFile in dailyStatsDir:
        dates.append(eachFile[str(eachFile).find('_')+1:str(eachFile).find('.')])

    #print(dates)
    #print(totalDeath)
    #print(totalCases)

    plt.figure(figsize=(10, 10))
    plt.plot(dates,totalCases,color="coral",linewidth=5)
    plt.plot(dates,totalDeath,color="red",linewidth=5)
    plt.grid(axis="y")
    plt.xlabel('Days', fontsize=20)
    plt.xticks(rotation=45, fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel('Total CoronaViurs Cases/Deaths', fontsize=20)
    plt.legend(["Total Cases","Total Deathes"], fontsize=15)
    plt.title('Overall COVID-19 Cases & Deathes', fontsize=20)
    plt.savefig(os.getcwd()+rootDirName+imageDir+'\\'+'COVIDOverall_' + today_date + '.png')
    plt.show()

def process_stats_csv(csvFileName):
    print("In process_stats_csv")

    virusStats = pd.read_csv(csvFileName + '.csv')
    #virusStats = cleanDataframe(virusStats)
    return virusStats
    #plotTotalCasesInCountry(virusStats['country_name'].head(15), virusStats['cases'].head(15))
    #plotMultipleLineGraph(virusStats)
    #plotPieChart(virusStats)
    #plotLineChart()


generateResponsefiles('NewsJson', 'StatsJson')
generate_WordCloud(open(os.getcwd() + rootDirName + '\\' + 'Newstxt' + '_' + today_date + '.txt').read())
vstats = process_stats_csv(os.getcwd() + rootDirName + '\\' + 'CountrywiseCoronaStats' + '_' + today_date)

plotTotalCasesInCountry(vstats['country_name'].head(15), vstats['cases'].head(15))
plotMultipleLineGraph(vstats)
plotPieChart(vstats)
plotLineChart()

