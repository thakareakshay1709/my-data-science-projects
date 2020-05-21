unseenData1 = ""
unseenData2 = ""
fileList = ["cafes_list.csv","gym_list.csv","restaurants_list.csv"]
for csv in fileList:
    for i in fileList:
        if i != csv:
            unseenData1 = i
            break

    for i in fileList:
        if i!= csv and i!=unseenData1:
            unseenData2 = i
            break
    if not (unseenData1 == None and unseenData2 == None and csv == None):
        print("Processing = ",csv, ", Unseen 1 = ",unseenData1, ", Unseen 2 = ", unseenData2)