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

from difflib import SequenceMatcher




def is_string_similar(s1: str,s2: str, treshold: float = 0.50): # String karşılaştırması 
    seq = SequenceMatcher(None,s1,s2)
    # print(seq.ratio()*100) -> Karşılaştırma yüzdelik oranının yazdırılması
    return SequenceMatcher(None,s1,s2).ratio() >= treshold


def textDetect(): #AWS Textract bağlantısı ve response döndürülmesi
    response = None
    file = open("demo.jpg","rb")
    binaryFile = file.read()    
    client = boto3.client('textract',"us-east-1")
    response = client.analyze_expense(
        Document={
            'Bytes': binaryFile

        })
    
    return response
    
def headers(tables):
    
    num = len(response)
    #tables = [{"header": {"EXPENSE_ROW": 0} , "body" : {"EXPENSE_ROW" :0}}]*4
    tables = [{"header" : [],"body" : []}] 
    forms = [{"Type": 0},{"Confidence": 0}]
    d ={}
    
    i = 0
    
    if num > 0:
        for array in response['ExpenseDocuments']:
           
                if(array['LineItemGroups']):
                    
                    for lig in array['LineItemGroups']:
                        
                        tableIndex = lig['LineItemGroupIndex']
                        tNum = 0
                        for table_r in lig['LineItems']:
                            
                            tNum += 1
                            
                            for tr in table_r['LineItemExpenseFields']:
                                
                                if(tr['Type']['Text']=="EXPENSE_ROW"):
                                    if tables[tableIndex-1]['header'] == 'EXPENSE_ROW':
                                        tables[tableIndex-1]['header'] = "EXPENSE_ROW"
                                    
                                    
                                    
                                for val in tr:
                                    if(tNum == 1): # Header
                                        
                                        if val == "LabelDetection":
                                            sVal = tr['LabelDetection']['Text']
                                            
                                            sVal = re.sub('/\([^)]+\)/','',sVal)
                                            
                                            
                                            
                                            tables[tableIndex-1]['header'].append(sVal)
    return tables[tableIndex-1]['header']
def bodys(tables,headers):
    num = len(response)
    #tables = [{"header": {"EXPENSE_ROW": 0} , "body" : {"EXPENSE_ROW" :0}}]*4
    tables = [{"header" : [],"body" : []}] *7
    d = {}
    k = 0
    if num > 0:
        for array in response['ExpenseDocuments']:
            if(array['LineItemGroups']):
                    
                    
                    for lig in array['LineItemGroups']:
                        
                        tableIndex = lig['LineItemGroupIndex']
                        tNum = 0
                        
                        for table_r in lig['LineItems']:
                            
                            tNum += 1
                            
                            
                            for tr in table_r['LineItemExpenseFields']:
                                try:
                                    print(k)
                                    print(headers[k])
                                    d = {headers[k]:tr['ValueDetection']['Text']}
                                    k+=1
                                    print(d)
                                except IndexError:
                                    break
                                tables[tableIndex-1]['body'].append(d)    
                            k = 0
                        k-=1            
                                
                                
    return tables[tableIndex-1]['body']
       
                
                                
                            
           

if __name__ == "__main__":
    
    strCompare = ["Miktar","Sıra"]    # Karşılaştırılacak array
    # with open('Input.txt',encoding="utf8") as input_file:
    #     for line in input_file:
    #         strCompare.append(line)
    # response = textDetect()
    # with open("AWS_AnalyzeExpense_RESPONSE.txt","w",encoding="utf8") as aws_response:
    #     aws_response.write(str(response))
   
    
    
    with open('aws.txt',encoding="utf8") as responseFile:
        data = responseFile.read()
        response = ast.literal_eval(data)
    
    
    def textractToArray(response,headers,bodys):
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
                                    
                                    if(tr['Type']['Text']=="EXPENSE_ROW"):
                                        if tables[tableIndex-1]['header'] == 'EXPENSE_ROW':
                                            tables[tableIndex-1]['header'] = "EXPENSE_ROW"
                                        
                                        
                                        
                                                
                                                
                                            
                                        
                                           
                                    for val in tr:
                                        if(tNum == 1): # Header
                                            
                                            if val == "LabelDetection":
                                                sVal = tr['LabelDetection']['Text']
                                                
                                                sVal = re.sub('/\([^)]+\)/','',sVal)
                                    
                                        
                                            
                                
                                        
                                
                                
                            if(tr['Type']['Text']=="EXPENSE_ROW"):
                                
                                tables[tableIndex-1]['header'].append(tr['Type']['Text']) 
            i+=1            
                    
                                
                                        
                                        
        pprint(tables)
        retArr = [{"forms" : forms, "tables" : tables}]
        return retArr
    def tableMatcher(tables,offerData):
        sArray = [{
            "No": ["SIRA NO", "Sıra No", "Sıra", "Sira No", "S.No", "No", "NO", "#", "Sıra No.", "Order", "Order No.", "Sira No"],
            "materialDesc": [
				"Ürün Açıklaması", "Cinsi", "Mal", "Mal/Hizmet", "Açiklama", "Malzeme Tanımı",
				"AÇIKLAMA", "Ürün", "Malzeme", "Malzeme Cinsi", "Ürün Adi", "Material", "Ürün Adı / Ürün Açıklaması", "Malzemenin Cinsi",
				"MALZEMENİN CINSI", "MALZEMELER", "Cinsi", "MALZEME"],
            "supQuantity": ["Miktar", "MİKTAR", "Miktarı", "MİKTARI", "MIKTAR", "ADET", "Adet","MİKTAR/Br.", "MIKTAR/Br."],
            "unite": ["Br.", "Birim", "BİRİM", "BR.","","BIRIM"],
            "unitePrice": ["Birim Fiyat", "BİRİM FİYAT", "B.Fiyat", "Br.Fiyat", "Liste", "Liste Fiyatı", 
				"Liste Fiyat", "BIRIM FİYAT", "BIRIM FIYAT", "NET BIRIM FIYAT", "Net Birim Fiyat", 
				"İskontosuz Birim Fiyat", "ISKONTOSUZ BIRIM FİYAT", "ISKONTOSUZ BR.FYT.", "ISKONTOSUZ BR. FIYAT", "iSKONTOSUZ BR.FYT.",
			"B.Fiyat","Fiyat","FIYAT","Net Fiy."],
            "fUnitePrice": ["İSKONTOLU BİRİM FİYAT", "NİHAi BİRİM FİYAT", "iSKONTOLU BR.FYT."],
            "discountRatio": ["ISKONTO ORANI","İsk.", "İskonto", "İSKONTO", "ARTIRIM", "İNDİRİM", "İndirim Oranı", "İskonto Oranı", "İsk. (%)","Isk."],
            "supBrands": ["Marka", "Marka/Model", "Brand", "MARKA", "MRK", "Model"," Teklif Edilen Markalar"],
            "deliveryDateSup": ["Teslim Tarihi"," Temin Tarihi", "Tarih", "Termin Tarihi"],
            "vatRatio": ["KDV", "K.D.V", "kdv", "KDV(%)", "KDV Oranı"],
            "curCode": ["PARA BİRİMİ", "PARA BIRIMI", "PARA BR."]}]
        arraySpec = [{"supQuantity" : ["simpleUnwanted", "turkishDecimal"],
                      "discountRatio" : ["simpleUnwanted", "turkishDecimal"]
                      
                      
                      }]
        offerBodyAtlEastCols = ["unitePrice", "funitePrice", "discountRatio"]
        retArr = [{}]
        offerReData = []
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
                
                for dict in sArray:
                    key = list(dict.keys())
                    
                    valuearr = list(dict.values())
                    
                    
                    if not reHeader[0]:
                        tempVal = levenshtein(h,valuearr[0][i],60)
                        
                        srcVal = None
                        
                        if not tempVal:
                            srcVal = tempVal['val']
                            possib = tempVal['possibility']
                            isExact = tempVal['isExactRs']
                        if not srcVal:
                            reHeader[0][key[i]] = h
                                             
                            
                            
                            headerCont[0] =[{"possibility" : possib}]
                            
                    else:
                        
                        if(headerCont[0][0]['possibility']< 100):
                            tempVal = levenshtein(h,valuearr[0][i],60)
                            srcVal = None
                            if not tempVal:
                                srcVal =  tempVal['val']
                                possib = tempVal['possibility']
                                isExact = tempVal['isExactRs']
                            if(not srcVal and headerCont[0][0]['possibility']<possib):
                                
                                reHeader[0] = h
                                
                                
                                headerCont[0] = [{"possibility": possib}]
                            
                    
               
            body = t['body']
            
            val = []
            items = []
            j = 0
            numofHeader = len(reHeader)
            for b in body:
                val = list(b.keys())
                
                if type(val[j]) == str:
                    
                    items.append(len(b))
                    
            array_depth = max(items)
            
            
            for x in range(array_depth):
                for rh in reHeader:
                    vRh = list(rh.values())
                    kRh = list(rh.keys())
                    
                    
                    
                    if body:
                        
                        if kRh in arraySpec:
                            filterArr = arraySpec[0][kRh[j]]
                                               
                        temVal = filterCustomRule(b,filterArr)
                        
                        retArr[0][kRh[j]] = tempVal
                        
                        
                
                for rh in reHeader:
                    vRh = list(rh.values())
                    kRh = list(rh.keys())
                    
                    
                    
                    if 'EXPENSE_ROW' in body and not retArr[j]['curCode']:
                        
                        tempVal = detectCurFromText(body['EXPENSE_ROW'], "CODE")
                        if tempVal:
                            retArr[j]['curCode'] = tempVal
            j += 1
                
                                
                    
        
        if(numofOfrdata >= 0):
            if numofOfrdata == 1 and len(retArr) == 1:
                offerReData = retArr
            else:
                
                for aj in range(len(retArr)):
                    
                    temp = retArr[aj]
                    
                    for tmp in temp:
                        
                        if tmp in offerBodyAtlEastCols:
                            isFdata = 1
                            
                        

        return [{"tables" : retArr}]
    def decodeFormAccToOffer(arr, ofrMtrList = []):
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
                        
    
                          
    def levenshtein(val, words , mPossibility = 70, sResult = False):
        if val and words:
            retVal = ""
            isExactRs = False
            possibility = 0
            
            # Levenstein
            sensitivity = 3
            shortest = -1 
            method = 0
            for w in words:
                lev = Levenshtein.distance(val,w)
                
                if(lev == 0):
                    closest = w
                    shortest = 0
                    possibility = 100
                    isExactRs = True
                    method = 1
                if(lev <= shortest or shortest <0):
                    closest = w
                    shortest = lev
            if(shortest <= sensitivity):
                retVal = closest
                isExactRs = False
                possibility = 100 - (shortest * 10)
                method = 1
            if(isExactRs or possibility >= mPossibility):
                return [{"isExactRs" : isExactRs, "possibility" : possibility, "val" : retVal, "method": method, "srcval" : val}]
        else:
            return ""
        return 1       
    
    
    header = headers(response)
    body = bodys(response,header)
    
    
    arr = textractToArray(response,header,body)
    
      
    
    
                       
                                
                            
            
                        
                    
                    
    
    
                 
                                                
                             
    
    
  
    

                                    
    # with open("table_data.txt","w", encoding="utf8") as text_file:
    #     strtext = '\n'.join(table_data)
    #     text_file.write(str(list(set(tdata))))
            
                    
                    
                    
                        
                    
                # if(len(header)>0):                                      # Yalnızca header'ı olan table
                #     for r, row in enumerate(table.rows_without_header):  
                #             table_data.append([])
                #             for c, cell in enumerate(row.cells):
                #                 table_data[r].append(cell.mergedText)  
                                
                    # if len(table_data)>0:
                    #     df = pd.DataFrame(table_data, columns=header)
                    #     print(df.keys())
                            

                    # for cell in header.header():
                    #     print(cell)
    # key = "Kodu "
    # for page in doc.pages:
    #      field = page.form.getFieldByKey(key)
    #      if(field):
    #          print("Field: Key: {}, Value: {}".format(field.key, field.value))
    
    # for item in response['Blocks']:
    #     if(item['BlockType']=='TABLE'):                       
            
    #         for rel in item['Relationships']:
    #             print(rel)
    #         # textt= "".join(str(item['CHILD']))
    #         if(re.search(" ",textt)):
    #             split_text = textt.split()
    #             for stext in split_text:
    #                 for strC in strCompare:
    #                     if(re.search("",strC)):
    #                         strCval = strC.split()
    #                     if(is_string_similar(stext,strC)):
    #                         text.append(item['Text'])
    #         else:
    #             for strr in strCompare:
    #                 if(is_string_similar(textt,strr)):
    #                     text.append(item['Text']) 
    
    # with open("Output.txt","w") as text_file:
    #     strtext = '\n'.join(text)
    #     text_file.write(strtext)
    with open("OutputJSON.txt","w")as json_file:   
        json_file.write(str(arr))    

    
    