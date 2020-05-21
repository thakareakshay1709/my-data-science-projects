#Imports required
import bs4
import urllib.request
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import *
from sklearn.model_selection import cross_val_score, RepeatedKFold
import seaborn as sean
import matplotlib.pyplot as plt

#This function is to scrape the HTML pages, fetch the data and store to the CSV files
def scrapeHtmlPages(names, categorylinks):

    #Defining rootDirectory to create a directory to save csv files
    rootDirName = os.getcwd() + '\\' + 'ConsumerReveiws'
    print("Category -> ",names, ", Link -> ", categorylinks)

    #Opening HTML files using urlopen method and decoding the response in variable
    responseHtml = urllib.request.urlopen(categorylinks + names +'.html')
    decodedHtmlRes =responseHtml.read().decode()

    #Applying Beautiful soup to parse the decoded HTML web page
    parserCategories = bs4.BeautifulSoup(decodedHtmlRes,"html.parser")

    #Defining Columns of the data frame
    cols = ['names', 'reviewText', 'reviewRating', 'label']
    df = pd.DataFrame(columns=cols)

    #Upper for loop is to find the links of sub-categories through major categories like 'cafes_list', 'gym_list', 'restaurants_list'
    #Also this upper for loop decode the subcategories to redirect to the review page
    for match in parserCategories.find_all("a"):
        #Getting the links of review set
        textReviewSet = match.get('href')
        #print(textReviewSet)

        #Combining major and subcategories to form a link to a web pages where reviews are present
        getReviewsLink = categorylinks + textReviewSet
        #print(getReviewsLink)

        #Decoding the urls and storing the responses
        reviewsResponse = urllib.request.urlopen(getReviewsLink)
        decodedRevResponse = reviewsResponse.read().decode()

        #Applying Beautiful Soup to the decoded response to parse the fetched HTML page
        parseReviews = bs4.BeautifulSoup(decodedRevResponse,"html.parser")

        #Above loob takes us to the web page where we can find all the reviews.
        #However, we again need to iterate over all the reviews so initiating inner for loop

        for rating, rtext in zip(parseReviews.find_all('p',class_='rating'), parseReviews.find_all('p', class_='review-text')):
        #Parallel iteration over two iterators rating & rtext with zip operation which collects relevant classes of HTML pages

            #Storing review text and its rating to a variables
            reviewText = rtext.get_text()
            reviewRating = rating.img.get('alt')

            #Null check for rating
            if reviewRating is not None:
                #Assigning target labels, rating <=3 leads to negative review else positive
                if(reviewRating == '4-star' or reviewRating == '5-star'):
                    label = 'positive'
                else:
                    label = 'negative'

                #Storing all values to the dataframe in dictionary format and appending as loop proceeds
                df = df.append({'names' : names, 'reviewText' : reviewText, 'reviewRating' : reviewRating, 'label' : label},ignore_index=True)


    #Validating the dataframe status after every major category
    #Checking the count of rows generated for every category
    print(df.head(10))
    print(df.describe())

    #Creating directory to save csv files if root directory does not exists
    if not os.path.exists(os.getcwd() + rootDirName):
        print('Creating directory -', rootDirName)
        os.makedirs(rootDirName, exist_ok=True)

    #File format to save csv
    filePath = rootDirName + '\\'
    print(filePath)

    #Load all data from dataframe to csv file into the relevant folder and name
    df.to_csv(filePath+names+'.csv')



#This function gives the flexibility to create categories and pass those for further scraping and processing
def selectCategories():
    #These are the major categories I have selected to work on
    #, 'gym_list', 'restaurants_list'
    categories = ['cafes_list', 'gym_list', 'restaurants_list']

    #Main link to the HTML page where you can see all the categories
    link = "http://mlg.ucd.ie/modules/yalp/"

    #This loop iterates to the number of categories we have selected
    for names in categories:
        #Calling function scrapeHtmlPages() with names and link as arguments for scraping
        scrapeHtmlPages(names, link)


def evaluateClassifierPerformances(processFile, unseenData1, unseenData2,rootDirectory):
    #print("Processing = ", processFile, ", Unseen 1 = ", unseenData1, ", Unseen 2 = ", unseenData2)




    print("*********** Processing %s ***********" % processFile)
    print()
    #Fetching data from csv and adding it to dataframe
    readdf = pd.read_csv(rootDirectory + processFile)
    #Setting up raw and target data
    rawDocument = readdf['reviewText']
    targetLabel = readdf['label']

    print("Length of document %s is %d " % (processFile, len(rawDocument)))

    # Begin tokenising the raw text
    print("First few chars of review of %s -> " % processFile, rawDocument[0][0:100])

    # Bag of words Representation
    # To avoid loss of tone of sentence we used to ngram_range for shortest and longest term sequence
    # Creating document-term matrix with some preprocessing of stop words and min frequency
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", min_df=5)
    X = vectorizer.fit_transform(rawDocument)

    print("Processing file shape = ", X.shape, " Target Shape ", targetLabel.shape)

    #Preprocessing unseen files to test the model
    # Preparing unseen files for prediction and testing model accuracy
    readUnseen1 = pd.read_csv(rootDirectory + unseenData1)
    unseen1Document = readUnseen1['reviewText']
    targetUnseen1 = readUnseen1['label']

    readUnseen2 = pd.read_csv(rootDirectory + unseenData2)
    unseen2Document = readUnseen2['reviewText']
    targetUnseen2 = readUnseen2['label']

    X_target1 = vectorizer.fit_transform(unseen1Document)
    X_target2 = vectorizer.fit_transform(unseen2Document)

    #Printing and validating the size of test dataset
    print("Unseen file %s has dimension ="%unseenData1, X_target1.shape, " and label has dimension ", targetUnseen1.shape[0])
    print("Unseen file %s has dimension ="%unseenData2, X_target2.shape, " and label has dimension ", targetUnseen2.shape[0])


    # Getting and printing distinct terms of processing files
    terms = vectorizer.get_feature_names()
    #vocab = vectorizer.vocabulary_
    print("Vocabulary of %s has %d distinct terms" % (processFile,len(terms)))
    #print("Vocabulary ", vocab)

    # Training own model
    print('Training model on own dataset')
    #Splitting dataset to train model on own train dataset
    dataset_train_own, dataset_test_own, target_train_own, target_test_own = train_test_split(X, targetLabel, test_size=0.30)

    print("Training set has %d examples" % dataset_train_own.shape[0])
    print("Test set has %d examples" % dataset_test_own.shape[0])

    #Building Naive Bayes model on own training dataset
    model = MultinomialNB()
    model.fit(dataset_train_own, target_train_own)
    print("Model for %s file ->"%processFile,model)

    #Evaluating accuracy of model trained on processFile i.e own dataset
    predicted_own = model.predict(dataset_test_own)
    accuracy = accuracy_score(target_test_own, predicted_own)
    print("Accuracy of model on %s = %.2f "%(processFile,accuracy))

    #Creating confusion matrix from the scores of model
    con_matrix = confusion_matrix(target_test_own, predicted_own)
    print(con_matrix)

    # Representing the confusion matrix with the help of seaborn package
    figure, axes = plt.subplots(figsize=(6, 4))
    sean.heatmap(con_matrix, annot=True, cbar=False, fmt='d', annot_kws={'size': 14}, cmap='Blues')
    sean.set(font_scale=1.5)

    # Display text in the middle
    btm, top = axes.get_ylim()
    axes.set_ylim(btm + 0.5, top - 0.5)

    # Setting labels to X and Y axes
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.show()

    #Printing accuracies of model and building other statistics measure
    print("Accuracy = %.2f" % accuracy_score(target_test_own, predicted_own))
    # We mentioned our interest of positive class labelled as "positive"
    print("Precision (Positive) = %.2f" % precision_score(target_test_own, predicted_own, pos_label="positive"))
    print("Recall (Positive) = %.2f" % recall_score(target_test_own, predicted_own, pos_label="positive"))
    print("F1 (Positive) = %.2f" % f1_score(target_test_own, predicted_own, pos_label="positive"))

    print("Precision (Negative) = %.2f" % precision_score(target_test_own, predicted_own, pos_label="negative"))
    print("Recall (Negative) = %.2f" % recall_score(target_test_own, predicted_own, pos_label="negative"))
    print("F1 (Negative) = %.2f" % f1_score(target_test_own, predicted_own, pos_label="negative"))

    print(classification_report(target_test_own, predicted_own, target_names=["negative", "positive"]))


    # Cross validation on unseen data set1
    #Using repeated cross validation folds to get the better accuracies
    repkfold = RepeatedKFold(n_splits=5, n_repeats=5)
    rep_scores_unseen1 = cross_val_score(model, X_target1, targetUnseen1, cv=repkfold, scoring="accuracy")
    print("Accuracies with cross validation = ", rep_scores_unseen1)
    labels = ["Fold %d" % i for i in range(1, len(rep_scores_unseen1) + 1)]
    score_accuracy_unseen1 = pd.Series(rep_scores_unseen1, index=labels)
    print(score_accuracy_unseen1)
    print("Mean accuracy of %s = %.2f" % (unseenData1, rep_scores_unseen1.mean()))
    ds_scr_acc = pd.Series(rep_scores_unseen1)
    ds_scr_acc.head(10)
    print("Overall mean accuracy: %.3f" % ds_scr_acc.mean())
    print("Overall standard deviation in accuracy: %.3f" % ds_scr_acc.std())
    print()

    # Similarly building same measures for unseen data set2
    scores_unseen2 = cross_val_score(model, X_target2, targetUnseen2, cv=repkfold, scoring="accuracy")
    #print("Accuracies with cross validation = ", scores_unseen2)
    labels = ["Fold %d" % i for i in range(1, len(scores_unseen2) + 1)]
    score_accuracy_unseen2 = pd.Series(scores_unseen2, index=labels)
    print(score_accuracy_unseen2)
    print("Mean accuracy of %s = %.2f" % (unseenData2, scores_unseen2.mean()))
    ds2_scr_acc = pd.Series(scores_unseen2)
    ds2_scr_acc.head(10)
    print("Overall mean accuracy: %.3f" % ds2_scr_acc.mean())
    print("Overall standard deviation in accuracy: %.3f" % ds2_scr_acc.std())
    print()



def segregateFiles_BuildClassifier():
    '''
    This function is created to segregate the csv files created earlier consists of reviews
    :return: None
    '''

    # Fetching the files in root directory and storing them to the list
    rootDirectory = os.getcwd() + '\\' + 'ConsumerReveiws' + '\\'
    fileList = os.listdir(rootDirectory)
    print(fileList)

    #Two string variables are created to store file names of unseen data
    unseenData1 = ""
    unseenData2 = ""

    #Purpose of this for loop is to distinguish files
    # processFile = The file on which classifier will be trained
    # unseenData1 & unseenData2 will have the file names on which model is to be tested
    for processFile in fileList:
        for i in fileList:
            if i != processFile:
                unseenData1 = i
                break

        for i in fileList:
            if i != processFile and i != unseenData1:
                unseenData2 = i
                break

        #Null check validation for files
        if not (unseenData1 == None and unseenData2 == None and processFile == None):
            #Passing file attributes in a sequence of combination in a loop
            #When cafes_list.csv will be processFile, rest two gym_list.csv & restaurants_list.csv
            #will be unseenData1 & 2 respectively. Likewise everyfile will be processfile in one term
            #so model is built on this file and rest two will act as test data
            evaluateClassifierPerformances(processFile,unseenData1,unseenData2,rootDirectory)


#Program execution point - main function
def main():
    # Calling selectCategories
    #This is the 1st part of assignment
    selectCategories()

    segregateFiles_BuildClassifier()


#Main function called
main()





