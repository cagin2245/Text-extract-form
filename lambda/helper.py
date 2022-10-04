
from array import array
from collections import defaultdict
from operator import is_not
from posixpath import split

from xml.dom.minidom import Document
import boto3
import pandas as pd
import json
import re
import ast
import itertools
import numpy as np
from pprint import pprint
from rapidfuzz.distance import Levenshtein
from similar_text import similar_text
import jellyfish
import difflib
from strsimpy.weighted_levenshtein import WeightedLevenshtein

from difflib import SequenceMatcher



def headers(tables,response): # header extract
    
    num = len(response)
    #tables = [{"header": {"EXPENSE_ROW": 0} , "body" : {"EXPENSE_ROW" :0}}]*4
    tables = [{"header" : [],"body" : []}] 
    forms = [{"Type": 0},{"Confidence": 0}]
    d ={}
    table_count = []
    i = 0
    
    if num > 0:
        for array in response['ExpenseDocuments']:
           
                if(array['LineItemGroups']):
                    
                    for lig in array['LineItemGroups']:
                        
                        tableIndex = lig['LineItemGroupIndex']
                        tNum = 0
                        for table_r in lig['LineItems']:
                            
                            tNum += 1
                            table_count.append(tNum)
                            
                            for tr in table_r['LineItemExpenseFields']:
                                
                                
                                    
                                    
                                for val in tr:
                                    if(tNum == 1): # Header
                                        
                                        if val == "LabelDetection":
                                            sVal = tr['LabelDetection']['Text']
                                            
                                            sVal = re.sub('/\([^)]+\)/','',sVal)
                                            
                                            
                                            
                                            tables[tableIndex-1]['header'].append(sVal)
    return tables[tableIndex-1]['header'],max(table_count)
def bodys(tables,headers,response): # extract bodys of headers
    num = len(response)
    
    #tables = [{"header": {"EXPENSE_ROW": 0} , "body" : {"EXPENSE_ROW" :0}}]*4
    tables = [{"header" : [],"body" : [{}]*len(headers)}] *7
    dict_sub = defaultdict(dict)
    d = defaultdict(list)
    k = 0
    i = 0
    if num > 0:
        for array in response['ExpenseDocuments']:
            if(array['LineItemGroups']):
                    
                    
                    for lig in array['LineItemGroups']:
                        
                        tableIndex = lig['LineItemGroupIndex']
                        tNum = 0
                        for table_r in lig['LineItems']:
                            
                            k = 0
                            tNum += 1
                            
                            
                            for tr in table_r['LineItemExpenseFields']:
                                try:
                                    # if headers[k] in d:
                                    #     d[k].append(tr['ValueDetection']['Text'])
                                    d[headers[k]].append (tr['ValueDetection']['Text'])
                                    
                                    
                                    
                                except IndexError:
                                    pass
                                k+=1
                                #tables[tableIndex-1]['body'][i].update(d)
                            #dict_sub[tableIndex].append(d)
                              
                                    
                            
                        dict_sub['body'] = d
                        
                        if len(dict_sub['body'][0]) == 0:
                            del dict_sub['body'][0]        
                            
                        
                        k+=1 
                                   
                                
                            
    #return tables[tableIndex-1]['body']
    return dict_sub['body']
def string_similarity(str1,str2):
    result = difflib.SequenceMatcher(a=str1.lower(), b=str2.lower())
    return result.ratio()

def is_string_similar(s1: str, s2: str, mPos = 50): # Strin Comparison
    seq = []    
    
    val = string_similarity(s1,s2)
    
    seq.append(val*100)
    
    
    return max(seq)
    
def textractToArray(response,headers,bodys,table_count): # Converting Textract output to python dictionary (JSON Format)
    num = len(response)
    #tables = [{"header": {"EXPENSE_ROW": 0} , "body" : {"EXPENSE_ROW" :0}}]*4
    tables = [{"header" : [],"body" : []}] 
    forms = [{"Type": 0},{"Confidence": 0}]
    d ={}
    
    i = 0
    k = 0
    if num > 0:
        for array in response['ExpenseDocuments']:
            
                if(array['SummaryFields']):
                    for sf in array['SummaryFields']:
                        
                        
                        for val in sf:
                                            
                            if val == "Type":
                                forms[i]['Type'] = [{"Type": sf['Type']['Text']}, {"Confidence": sf['Type']['Confidence']}]
                                
                            elif val == "ValueDetection":
                                
                                forms[i]['Value'] = [{"value" : sf["ValueDetection"]['Text']}]
                                
                                
                            elif val == "LabelDetection":
                                forms[i]['label'] = [{"value" : sf['LabelDetection']['Text']}, {"Confidence" : sf['LabelDetection']['Confidence']}]
                                
                            
                if(array['LineItemGroups']):
                    
                    for lig in array['LineItemGroups']:
                        
                        tableIndex = lig['LineItemGroupIndex']
                        tNum = 0
                        tables[tableIndex-1]['header'].append(headers)
                        tables[tableIndex-1]['body'].append(bodys)
                        for table_r in lig['LineItems']:
                            
                            tNum += 1
                            
                            for tr in table_r['LineItemExpenseFields']:
                        
                                for val in tr:
                                    if(tNum == 1): # Header
                                        
                                        if val == "LabelDetection":
                                            sVal = tr['LabelDetection']['Text']
                                            
                                            sVal = re.sub('/\([^)]+\)/','',sVal)
             
        i+=1            
                
                            
    
    
    
    dict_sub = [{"forms" : forms, "tables" : tables}]
    return dict_sub
def tableMatcher(tables,offerData): # Comparing and Matching tables with inline keywords      
    sArray = [{
        "No": ["SIRA NO", "Sıra No", "Sıra", "Sira No", "S.No", "No", "NO", "#", "Sıra No.", "Order", "Order No.", "Sira No"],
        "materialDesc": [
            "Ürün Adı / Ürün Açıklaması","Ürün Açıklaması", "Cinsi", "Mal", "Mal/Hizmet", "Açiklama", "Malzeme Tanımı",
            "AÇIKLAMA", "Ürün", "Malzeme", "Malzeme Cinsi", "Ürün Adi", "Material",  "Malzemenin Cinsi",
            "MALZEMENİN CINSI", "MALZEMELER", "Cinsi", "MALZEME"],
        "supQuantity": ["Miktar", "MİKTAR", "Miktarı", "MİKTARI", "MIKTAR", "ADET", "Adet","MİKTAR/Br.", "MIKTAR/Br."],
        "unite": ["Br.", "Birim", "BİRİM", "BR.","","BIRIM"],
        "unitePrice": ["Birim Fiyat", "BİRİM FİYAT", "B.Fiyat", "Br.Fiyat", "Liste", "Liste Fiyatı", 
            "Liste Fiyat", "BIRIM FİYAT", "BIRIM FIYAT", "NET BIRIM FIYAT", "Net Birim Fiyat", 
            "İskontosuz Birim Fiyat", "ISKONTOSUZ BIRIM FİYAT", "ISKONTOSUZ BR.FYT.", "ISKONTOSUZ BR. FIYAT", "iSKONTOSUZ BR.FYT.",
        "B.Fiyat","Fiyat","FIYAT","Net Fiy."],
        "fUnitePrice": ["İSKONTOLU BİRİM FİYAT", "NİHAi BİRİM FİYAT", "iSKONTOLU BR.FYT."],
        "discountRatio": ["ISKONTO ORANI","İsk.", "İskonto", "İSKONTO", "ARTIRIM", "İNDİRİM", "İndirim Oranı", "İskonto Oranı", "İsk. (%)","Isk."],
        "totalAmount" : ["Toplam Tutar", "TOPLAM TUTAR"],
        "deliveryDateSup": ["Teslim Tarihi"," Temin Tarihi", "Tarih", "Termin Tarihi"],
        "vatRatio": ["KDV", "K.D.V", "kdv", "KDV(%)", "KDV Oranı"],
        "curCode": ["PARA BİRİMİ", "PARA BIRIMI", "PARA BR."]}]
    arraySpec = [{"supQuantity" : ["simpleUnwanted", "turkishDecimal"],
                    "discountRatio" : ["simpleUnwanted", "turkishDecimal"]
                    
                    
                    }]
    offerBodyAtlEastCols = ["unitePrice", "funitePrice", "discountRatio"]
    dict_sub = defaultdict(list)
    
    
    reHeader = [{}]
    offerReturn = []
    numofOfrdata = len(offerData)
    headerCont = [{}]
    possib = 0
    i = 0
    isFdata = 0
    filterArr = []
    for t in tables[0]['tables']:
        header = t['header']
        for h in header:
            for he in h:
                for i in range(len(sArray[0])):
                    
                    for dct in sArray:
                    
                    
                        key = list(dct.keys())
                        
                        valuearr = list(dct.values())
                        
                        tempVal = stringCompareMatch(he,valuearr[i],60)
                        
                        
                        if tempVal[0]['possibility'] >= 60:
                            srcVal = tempVal[0]['srcval']
                            
                        
                        if len(tempVal) != 0:
                            
                            srcVal = tempVal[0]['val']
                            
                            possib = tempVal[0]['possibility']
                            isExact = tempVal[0]['isExactRs']
                           
                        if len(srcVal)!=0:
                            
                            val = {key[i]:he}
                            reHeader[0].update(val)
                            
                            
                            headerCont[0] =[{"possibility" : possib}]
                                
                            
                        else:
                            
                            if(headerCont[0][0]['possibility']< 100):
                                tempVal = stringCompareMatch(he,valuearr[i],60)
                                
                                if len(tempVal)==0:
                                    
                                    
                                    
                                    srcVal =  tempVal[0]['val']
                                    possib = tempVal[0]['possibility']
                                    isExact = tempVal[0]['isExactRs']
                                if(len(srcVal) != 0 and headerCont[0][0]['possibility']<possib):
                                    
                                    reHeader[i][key[i]] = h
                                    
                                    
                                    
                                    headerCont[0] = [{"possibility": possib}]
                    i+=1                      
                    
            
        body = t
        
        val = []
        items = []
        dtolist = [[]]*3
        keys = []
        numofHeader = len(reHeader[0])
        
        
        for b in body['body']:
            items.append(len(b))
            
        
        array_depth = max(items)
        # ~| TODO |~
        # Implement new data appending and accessing with defaultdict
        count = 0
        
        
        bAsKey = list(b.keys())
        rAsVal = list(reHeader[0].values())
        
        
       
        
        for kk in reHeader[0]:   
            dict_sub[kk]. append(b[rAsVal[count]])
            
           
             
               
            # if b in list(dict_sub.items()):
            #     dict_sub[count][b[iter]]  = dict_sub[count][b[iter]] + b[iter]
            #     print(dict_sub[count])
            # else:
            #     dict_sub[count].append(b[iter])
            count+=1    
        
    result_dict = dict(dict_sub)
    return result_dict
def decodeFormAccToOffer(arr, ofrMtrList = []): #
    returnVals = [{}]
    table = []
    form = []
    table = tableMatcher(arr,ofrMtrList)
    returnVals[0]['table'] = table
    return returnVals
def filterCustomRule(val, rules):
    reval = val
    if val:
        if len(rules) > 0 :
            for r in rules:
                val = reval
                if r == "simpleUnwanted":
                    val2 = re.sub([":", "*", "**", "***", "!", " : "],'',val)
                    reval = val2
                if r == "turkishChar":
                    val2 = re.sub([""],'İ',val)
                    reval = val2
                if r == "convertInteger":
                    val2 = re.sub("/[^0-9.,]/",'',val)
                    reval = int(val2)
                if r == "turkishDecimal":
                    val2 = re.sub([":", "*", "**", "***", "!", " : "],'',val)
                    pointArr = split(".",val2)
                    commaArr = split(',', val2)
                    lang = "TR"
                    if(lang == "TR"):
                        reval = val2
    return reval            
def stringCompareMatch(val, words , mPossibility = 60, sResult = False):
    isExactRs = False
    possibility = 0
    sensitivity = 3
    retVal = ""
    shortest = -1
    k = 0
    j = 0
    if val and words:
        for word in words: 
            
            
            
            if(isExactRs == False  or possibility < 100 ):
                
                
                temp = is_string_similar(word,val,mPossibility)
                maximum = max(len(val),len(word))
                pWord = temp / maximum * 10
                
                
                
                
                if(pWord >possibility):
                    
                    possibility = pWord
                    
                    retVal = word
                    
                    
                    isExactRs = False
                
                if isExactRs == True or possibility >= mPossibility: 
                    return [{"isExactRs" : isExactRs, "possibility" : possibility, "val" : retVal,  "srcval" : val}]
                k+=1
                j+=1
            return [{"isExactRs" : isExactRs, "possibility" : 0, "val" : '',  "srcval" : ''}]
    
    return [{"isExactRs" : isExactRs, "possibility" : 0, "val" : '',  "srcval" : ''}]       
def detectCurFromText(text , rType = "INT"):
    caughtElement = ""
    retVal = None
    if(text):
        wordArr = text.split(' ')
        arrTL = ["TL", "TÜRK LİRASI", "₺", "TRY", "Türk Lirası"]
        arrUsd = ["$", "USD", "DOLAR", "Amerikan Doları", "USA Dolar"]
        arrEuro = ["€", "Avro", "Euro"]
        arrGbp =["£", "GBP", "Sterlin", "İngiliz Sterlini"]
        for wor in wordArr:
            if wor in arrTL:
                caughtElement = 1
            if wor in arrEuro:
                caughtElement = 2
            if wor in arrUsd:
                caughtElement = 3
            if wor in arrGbp:
                caughtElement = 4
    if caughtElement:
        if rType == "INT":
            retVal = caughtElement
        if rType == "CODE":
            if caughtElement == 1:
                retVal = "TL"
            if caughtElement == 2:
                retVal = "EURO"
            if caughtElement == 3:
                retVal = "USD"
            if caughtElement == 4:
                retVal = "GBP"
    return retVal            
                    