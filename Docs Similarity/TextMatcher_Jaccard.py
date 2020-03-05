def JaccardIndex(str1, str2):
    set1 = set(str1.split())
    set2 = set(str2.split())
    ans = float(len(set1 & set2)) / len(set1 | set2)
    return round(ans, 2)

def JaccardDistance(strd1,strd2):
    setd1 = set(strd1.split())
    setd2 = set(strd2.split())

    J_distance = 1 - (float(len(setd1 & setd2)) / len(setd1 | setd2))
    return round(J_distance,2)

def DiceDistance(strd1, strd2):
    setdice1 = set(strd1.split())
    setdice2 = set(strd2.split())

    dice_coef = 1 - (float(2*(len(setdice1 & setdice2))) / len(setdice1 | setdice2))
    return round(dice_coef,2)

base = "akshay ucd text analytics machine learning"
target1 = "machine learning artificial intelligence deep stroming"
target2 = "machine akshay thakare ucd data mining course"
target3 = "ucd university negotiated learning course akshay text"
target4 = "data analytics new module ucd mark keane"


ans1 = JaccardIndex(base, target1)
ans2 = JaccardIndex(base, target2)
ans3 = JaccardIndex(base, target3)
ans4 = JaccardIndex(base, target4)

dis1 = JaccardDistance(base, target1)
dis2 = JaccardDistance(base, target2)
dis3 = JaccardDistance(base, target3)
dis4 = JaccardDistance(base, target4)

#triangle inequality measure
# distance between targets

dis_t12 = JaccardDistance(target1,target2)
dis_t13 = JaccardDistance(target1,target3)
dis_t14 = JaccardDistance(target1,target4)
dis_t23 = JaccardDistance(target2,target3)
dis_t24 = JaccardDistance(target2,target4)
dis_t34 = JaccardDistance(target3,target4)

ddis1 = DiceDistance(base, target1)
ddis2 = DiceDistance(base, target2)
ddis3 = DiceDistance(base, target3)
ddis4 = DiceDistance(base, target4)

ddis12 = DiceDistance(target1, target2)
ddis13 = DiceDistance(target1, target3)
ddis14 = DiceDistance(target1, target4)
ddis23 = DiceDistance(target2, target3)
ddis24 = DiceDistance(target2, target4)
ddis34 = DiceDistance(target3, target4)

print("JaccardIndex", [ans1, ans2, ans3,ans4])
print("JaccardDistance",[dis1,dis2,dis3,dis4])
print("Triangle",[dis_t12,dis_t13,dis_t14,dis_t23,dis_t24,dis_t34])
print("\n\n\n\n")
print("Dice Coef distance", [ddis1,ddis2,ddis3,ddis4])
print("\nBase -> T1 ",ddis1,"Base -> T2 -> ",ddis2,"-> T12",ddis12)
print("\nBase -> T3 ",ddis3,"Base -> T4 -> ",ddis4,"-> T34",ddis34)
      # "Base -> T2 ",ddis2,"\nBase -> T3 -> ",ddis3,"\nT23 ",ddis23])





