__author__ = 'user'


import nltk.metrics
import distance

#  transposition flag allows transpositions edits (e.g., “ab” -> “ba”),

s1 = '@user1 apple launched new product iphone xr #newlaunched #iphone'
s1a = '@user1a apple launched new product iphone xr #newlaunched #iphone #appleproduct'
s1b = '@user1b new product iphone xr #iphone #appleproduct #latestnews #bestnews'
s1c = '@user1c new iphone xr product #iphone #newlaunched #latestnews #bestnews'

s2 = '@user2 all iphones will get new os update 13.03 #newupdate #iphoneupdates #technews'
s2a = '@users2a all iphones will get new os update 13.03 #newupdate #iphoneupdates #technews #geekiphone'
s2b = '@users2b iphones new os update 13.03 #newupdate #iphoneupdates #technews #firstnews #bestnews'

s3 = '@user3 weather in dublin faces new storm #weahterreport #ucdnews'
s3a = '@user3a weather in dublin faces new storm #weahterreport #ucdnews #dublincheck #latestnews'
s3b = '@user3b weather in dub faces storm #weahterreport #ucdnews #weathercheck #liveupdate'

s4 = '@user4 ucd will celebrate hallowen for all departments #festival #studentfestival #ucdlife'
s4a = '@user4a ucd will celebrate hallowen for all departments #festival #studentfestival #ucdlife #mylife #halloween'
s4b = '@user4b hallowen for all departments in ucd #festival #studentfestival #ucdlife #student #life'

s5 = '@user5 text analytics course consists in nlp learning #ml #nlp'
s5a = '@user5a text analytics course consists in nlp learning #ml #nlp #ds'
s5b = '@user5b text analytics consists nlp learning #ml #nlp #ta'

#ans = nltk.metrics.distance.edit_distance(s1, s2, transpositions=False)
#print(ans)

#ans = nltk.metrics.distance.edit_distance(s3, s4, transpositions=False)
#print(ans)

#ans = nltk.metrics.distance.edit_distance(s5, s6, transpositions=False)
#print(ans)

ans = distance.levenshtein(s5, s5a)
print(ans)

ans = distance.levenshtein(s5, s5b)
print(ans)

ans = distance.levenshtein(s1, s1c)
print(ans)

ans = distance.levenshtein(s2, s2b)
print(ans)
