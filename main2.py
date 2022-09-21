import enum
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
import numpy
import jellyfish

def string_comparison(list1,list2): # -> Jaccard Similarity
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1)+ len(list2)) - intersection
    return float(intersection) / union
def splitList(list):
    return [i.split(' ',1) for i in list]

data = pd.read_excel('exampleForMatch.xlsx',header= None)
l1 = data[0].values.tolist()
l2 = data[1].values.tolist()
list1 = splitList(l1)
list2 = splitList(l2)
rows, cols = (8,2)
listResult = []

print("\n\n\n\n")
similarities = []
idx = 0
idy = 0
for idx, i in enumerate(list1,start=0):
       
    for idy, j in enumerate(list2,start=0):
        similarities.append(jellyfish.jaro_similarity(str(i),str(j)))
        
                
    print(i,"->", j, "Oran: ", max(similarities))
    listResult.append(str(i)+" ile " +str(j)+ " %{:.2f} ".format(max(similarities)*100)+ " güven düzeyiyle eşleşiyor.")
    
    similarities = []
print(listResult)
data['3'] = " -> "
data['Sonuçlar'] = listResult
data.to_excel('new_excel_file.xlsx')

     