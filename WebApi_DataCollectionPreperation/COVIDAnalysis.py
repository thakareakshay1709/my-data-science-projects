#!/usr/bin/env python
# coding: utf-8

# # COMP47670 | Covid-19 | WorldTrends and Analysis

# *Please import below Python packages if you dont have on your machine which will help to run all code smoothly.*

# In[21]:


# Necessary import statements
# Please install below packages in order to print wordcloud
# pip install wordcloud
# conda install -c conda-forge wordcloud

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


# ## TASK 1 - PICKING UP APIs
# 
# <p>There are two APIs chosen for this assignment as given below.</p>
# <ol>
#     <li> <a href = "http://newsapi.org">News API</a> </li> <p>This api is chosen to receive the world wide trends and significant announcement by leading sources like WHO/ NewYork Times/ Irish Times etc. about COVID-19. Important words are collected from these trends for past 30 days, after removing stopwords and preprocessing the word cloud is used to represent the currently updated news about Corona Virus.This API updates around two or three times daily.</p><p>API Key is used for news is a8e793aa99b940ae9b75ce085eb392c7</p>
#     <li> <a href="https://rapidapi.com/astsiatsko/api/coronavirus-monitor">Covid Status Daily</a> </li><p>This is free API selected from Rapid API platform to get the quantative statistics about Covid-19. This API updates almost in every 2 hours and gives the world wide cases about CoronaVirus. </p><p>API Key is used for this is 079c8debbcmsh31a653d4e5ea7e1p19b967jsn130707a652e2</p>
# </ol>

# In[22]:


def getApiKey():
    '''
    Info: This method return the api key for  http://newsapi.org
    '''
    print("Returning APIKey")
    return 'a8e793aa99b940ae9b75ce085eb392c7'


# ## TASK 2 - COLLECTING DATA FROM API
# 
# **Data is collected from provided APIs in json format. However, it needs to be preprossed in order to get relevant data helpful to serve the purpose. In general, the data collected from these APIs are stored in JSON files in 'GenerateFiles' directory and then further preprocessing and processing is done on data collected daily on these Json files**
# 
# <ol>
#     <li>Data from News API</li><p>Each file is created on daily basis in order to keep the scope for further prediction and limited file size as every file here is updated with 30 days of data.</p><p>Json files starting with NewsJson and followed by today's date (for ex, NewsJson_2020-03-30) represent the file's data on that day</p>
#     <li>Data from Coronavirus Monitor API</li><p>This data is updated every 2 hours so files are open in write mode to fetch most updated data. This data is saved in Json file starting with StatsJson and followed by today's date (for ex, StatsJson_2020-03-30) repreent the file's data on that day. </p>
# </ol>

# In[23]:


# Calculating time to hit the query within range API permits
# strftime() converts a datetime object to string. Capital letter in format changes the format (y -> 20, Y -> 2020)
# A timedelta object represents a duration, the difference between two dates or times.

today_date = datetime.today().strftime("%Y-%m-%d")
lastMonth_date = (datetime.today() - timedelta(days=29)).strftime("%Y-%m-%d")

# Creating directory to save data from response files. GenerateFiles is the directory to save every generated response
# and Image directory is used to save all outputs

rootDirName = '\GenerateFiles'  
imageDir = '\Image'


# In[24]:


#Getting json response from CoronaMonitor API

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


# ## TASK 3 - Preprocessing Data
# 
# **Some points regarding what are the factors considered during preprocessing of data. These are generic points here, detailed description is present in every function while performing the particular actions.**
# 
# <ul>
#     <li>As free API, there is a restricted access of 30 days to collect all data for News API. So, URL is preprocessed to hit the API within the range of days to avoid exception</li>
#     <li>After getting Json respnse, the nested tags present in data provides irrelevant data and so needs to be preprocessed. Hence, this data is preprocessed.</li>
#     <li>Data after saving into text files, have invalid characters which reduces the readibility of data and increase noisy data, so these data is removed.</li>
#     <li>Sometimes the data gives null values which raise null pointer exception while processing the dataframe. So, unnecessary data is removed before saving it to text file.</li>
#     <li>While getting the statistics, the overall data is too large to display so particular columns are removed and processing is done on selected columns only. </li>
#     <li>Data in stats file returned in string format with characters like ',' which throws errors if not preprocessed. Also such data cannot be considered as integers. So this is handled by removing unwanted chars from each cell of data </li>
# </ul>

# In[25]:


#Creating URLs to hit as per need and relevance

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

    #Preparing URL to get everything about Corona related news from whole world for only 30 days
    
    if endpoint == 'everything':
        urlEverything = 'http://newsapi.org/v2/' + endpoints[
            0] + '?q=' + newsTopic + '&from=' + today_date + '&to=' + lastMonth_date + '&sortBy=popularity&language=en&apiKey=' + getApiKey()
        print("Get URL "+urlEverything)
        return urlEverything

    elif endpoint == 'top-headlines':
        urlTopheadlines = 'http://newsapi.org/v2/' + endpoints[
            1] + '?country=' + country + '&category=business&apiKey=' + getApiKey()
        return urlTopheadlines


# In[26]:


def getCoronaUpdatesWorldwide():
    # Establising connection and fetching response from api
    response = urllib.request.urlopen(getUrl(endpoints[0])) #endpoints[0] = everything
    raw_json = response.read().decode("utf-8")
    data = json.loads(raw_json)
    #Filter nested Json tags and only take relevant information from data['articles']
    jsondata = data['articles']
    print("In method getCoronaUpdatesWorldwide()")
    return jsondata


# ## TASK 4 - Processing response files
# 
# **This part consist of all file handling and generation of output files in order to process the collected data and save this data to particular files. Generic tasks are mentioned below->**
# 
# <ul>
#     <li>Generation of file directory 'GenerateFiles' to save output files</li>
#     <li>Generate Json response from API</li>
#     <li>Processing responses and storing processed data into text and csv files to use further</li>
#     <li>Conversion of json object to pandas dataframe</li>
#     <li>Processing the dataframe, removing invalid data and get cleaned data</li>
#     <li>Exception handling</li>
# </ul>

# In[27]:


def generateResponsefiles(newsFilename, statsFilename):
    # File handling...
    #Input file names are received as an arguments
    print("In generateResponsefiles")
    
    # Creating 'Generatefiles' directory if not present already in the same root location of this Python file
    if not os.path.exists(os.getcwd() + rootDirName):
        print('Creating directory -', os.getcwd() + rootDirName)
        os.makedirs(os.getcwd() + rootDirName, exist_ok=True)


    # Creating json respoonse file for Corona news api
    newsFilename = os.getcwd() + rootDirName + '\\' + newsFilename + '_' + today_date
    # Getting response and converting it to json object
    with open(newsFilename + '.json', mode='w') as newsjson:
        json.dump(getCoronaUpdatesWorldwide(), newsjson, sort_keys=True, indent=4)
        newsjson.close()

    #Reading Json file created for worldwide trends from NewsApi
    readNewsfile = open(newsFilename + '.json', mode='r')
    
    #Loading data into pandas dataframe
    df_news = pd.read_json(readNewsfile, typ='frame')
    loaded_df = pd.DataFrame(df_news)
    #dropping null values to avoid null pointer exception from dataframe
    loaded_df.dropna()
    #Loading preprocessed data into csv files with relevant columns
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

    #Fetching data from corona virus monitor API
    statsFilename = os.getcwd() + rootDirName + '\\' + statsFilename + '_' + today_date
    with open(statsFilename + '.json', mode='w') as coronaStats:
        #Dumping data into json objects and generationg of json files
        json.dump(getCoronaMonitorResponse(), coronaStats, sort_keys=True, indent=4)
        coronaStats.close()

    #Reading CoronaMonitor Json response files
    readStatsfile = open(statsFilename + '.json', mode='r')
    #Loading data into dataframe
    df_stats = pd.read_json(readStatsfile, typ='frame')
    loaded_stats = pd.DataFrame(df_stats)
    
    #Generating CSV files for latest Corona udpates
    countryStatsfile = os.getcwd() + rootDirName + '\\' + 'CountrywiseCoronaStats' + '_' + today_date
    loaded_stats.to_csv(countryStatsfile + '.csv')


# ## TASK 5 - Creating Visualizations
# 
# **Below part shows the implementations of visualization created with the help of numpy and matplotlib packages. The generic
# functionality is as follows->**
# <ul>
#     <li>Created word cloud to show the trends about Corona Virus for 30 days. Cloud image is similar to virus image</li>
#     <li>Importantly, plainvirus.png should present in Image Directory to implement mask functionality.</li>
#     <li>Top 15 impacted countries due to Coronavirus as per latest data is shown as bar graph name starting with 'MostImpactedCountries_' followed by today's date</li>
#     <li>Multi line graph is shown to represent the trend of top 15 countries in terms of active cases, deaths, new cases, critical cases and recoverd</li>
# </ul>

# In[41]:


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


# In[42]:


def plotTotalCasesInCountry(countryNames,totalCases):
    #print(list(countryNames),list(totalCases))
    totalCases = [int(i.replace(',','')) for i in totalCases]
    print("In plotTotalCasesInCountry")
    plt.figure(figsize=(10,10))
    plt.bar(list(countryNames),totalCases )

    for i, v in enumerate(totalCases):
        plt.text(v + 3, i + .25, str(v), color='red', fontweight='bold')

    plt.xticks(rotation = 90, fontsize = 15)
    plt.yticks(fontsize=15)
    plt.xlabel("Country", fontsize = 20)
    plt.ylabel("Total COVID Cases",fontsize = 20)
    plt.title("COVID | TOP 15 Impacted Countries "+today_date,fontsize = 25)

    plt.savefig(os.getcwd() + rootDirName + imageDir + '\\'+'MostImpactedCountries_'+today_date+'.png')
    plt.show()


# In[43]:


def plotMultipleLineGraph(virusStats):
    data = virusStats
    print("In plotMultipleLineGraph")
    active_cases = list(data['active_cases'].head(15))
    int_active_cases = [int(i.replace(',','')) for i in active_cases]

    deaths = list(data['deaths'].head(15))
    int_deaths = [int(i.replace(',','')) for i in deaths]

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

    total_recovered = list(data['total_recovered'].head(15))
    int_total_Recovered = [int(i.replace(',','')) for i in total_recovered]

    country_names = list(data['country_name'].head(15))

    #plt.scatter(country_names,total_recovered)
    #y = [int_serious_critical,int_total_Recovered,int_new_cases,int_deaths,int_active_cases]
    #for xe,ye in zip(country_names,y):
    #    plt.scatter([xe] * len(ye),ye)


    plt.figure(figsize=(10, 10))
    plt.plot(int_active_cases,country_names, color="purple", linewidth=3,marker='o')
    plt.plot(int_deaths,country_names, color="green", linewidth=3,marker='*')
    plt.plot(int_new_cases,country_names, color="blue", linewidth=3,marker='^')
    plt.plot(int_serious_critical,country_names, color="red", linewidth=3,marker='s')
    plt.plot(int_total_Recovered,country_names, color="yellow", linewidth=3,marker='v')
    plt.grid(axis="x")

    plt.xlabel('Cases Count', fontsize=20)
    plt.ylabel('Countries', fontsize=20)
    plt.xticks(rotation=45, fontsize=15)
    plt.yticks(fontsize=15)

    plt.title("COVID | Country Statistics on " + today_date, fontsize=25)
    plt.legend(["Active Cases", "Deaths", "New Cases", "Serious Critical", "Total Recovered"], fontsize=15)
    plt.savefig(os.getcwd() + rootDirName + imageDir + '\\'+'COVIDCountriesStats_' + today_date + '.png')
    plt.show()


# In[44]:


def plotPieChart(virusStats):
    print("In plotPieChart")
    virusStats['cases'] = [int(i.replace(',', '')) for i in virusStats['cases']]
    totalCases = virusStats['cases'].sum()

    virusStats['deaths'] = [int(i.replace(',', '')) for i in virusStats['deaths']]
    deaths = virusStats['deaths'].sum()

    virusStats['total_recovered'] = [int(str(i).replace(',', '')) for i in virusStats['total_recovered']]
    recovered = virusStats['total_recovered'].sum()

    active = totalCases - (deaths + recovered)

    labels = ['Total Cases', 'Deaths', 'Recovered', 'Active']
    stats = [totalCases,deaths,recovered,active]

    print("Total=", totalCases, " Deaths=", deaths, " Recovered=", recovered, " Active=", active)
    plt.figure(figsize=(10, 10))
    plt.pie(stats,labels=labels,autopct='%1.1f%%')
    plt.savefig(os.getcwd()+rootDirName+imageDir+'\\'+'COVIDPIE_' + today_date + '.png')
    plt.show()


# In[45]:


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
    plt.plot(dates,totalCases,color="coral",linewidth=5,marker='*',linestyle='--')
    plt.plot(dates,totalDeath,color="red",linewidth=5,marker='*',linestyle='--')
    plt.grid(axis="y")
    plt.xlabel('Days', fontsize=20)
    plt.xticks(rotation=45, fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel('Total CoronaViurs Cases/Deaths', fontsize=20)
    plt.legend(["Total Cases","Total Deathes"], fontsize=15)
    plt.title('Overall COVID-19 Cases & Deathes', fontsize=20)
    plt.savefig(os.getcwd()+rootDirName+imageDir+'\\'+'COVIDOverall_' + today_date + '.png')
    plt.show()


# In[46]:


def process_stats_csv(csvFileName):
    print("In process_stats_csv")
    virusStats = pd.read_csv(csvFileName + '.csv')
    return virusStats
    #plotTotalCasesInCountry(virusStats['country_name'].head(15), virusStats['cases'].head(15))
    #plotMultipleLineGraph(virusStats)
    #plotPieChart(virusStats)
    #plotLineChart()


# In[47]:


generateResponsefiles('NewsJson', 'StatsJson')


# In[48]:


generate_WordCloud(open(os.getcwd() + rootDirName + '\\' + 'Newstxt' + '_' + today_date + '.txt').read())


# In[49]:


vstats = process_stats_csv(os.getcwd() + rootDirName + '\\' + 'CountrywiseCoronaStats' + '_' + today_date)


# In[50]:


plotTotalCasesInCountry(vstats['country_name'].head(15), vstats['cases'].head(15))


# In[51]:


plotMultipleLineGraph(vstats)


# In[52]:


plotPieChart(vstats)


# In[53]:


plotLineChart()


# In[ ]:




