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
    


if __name__ == "__main__":
    
    strCompare = ["Miktar","Sıra"]    # Karşılaştırılacak array
    # with open('Input.txt',encoding="utf8") as input_file:
    #     for line in input_file:
    #         strCompare.append(line)
    # response = textDetect()
    # with open("AWS_AnalyzeExpense_RESPONSE.txt","w",encoding="utf8") as aws_response:
    #     aws_response.write(str(response))
   
    
    
    with open('AWS_AnalyzeExpense_RESPONSE.txt',encoding="utf8") as responseFile:
        data = responseFile.read()
        response = ast.literal_eval(data)
    
    
    def textractToArray(response):
        #tables = [{"header": {"EXPENSE_ROW": 0} , "body" : {"EXPENSE_ROW" :0}}]*4
        tables = [{"header":{"EXPENSE_ROW" : 0},"body": {}}] *2
        forms = [{"Type": 0},{"Confidence": 0}]
        i = 0
        tNum = 0
        array = response['ExpenseDocuments']
        
        for r in array:
            
            if(r['SummaryFields']):
                for sf in r['SummaryFields']:
                    
                    
                    for val in sf:
                                        
                        if val == "Type":
                            forms[i]['Type'] = [{"Type": sf['Type']['Text']}, {"Confidence": sf['Type']['Confidence']}]
                               
                        elif val == "ValueDetection":
                            
                            forms[i]['Value'] = [{"value" : sf["ValueDetection"]['Text']}]
                               
                            
                        elif val == "LabelDetection":
                            forms[i]['label'] = [{"value" : sf['LabelDetection']['Text']}, {"Confidence" : sf['LabelDetection']['Confidence']}]
                            
                        
            if(r['LineItemGroups']):
                
                for lig in r['LineItemGroups']:
                    
                    tableIndex = lig['LineItemGroupIndex']
                    
                    
                    
                    print(tNum)
                    for table_r in lig['LineItems']:
                        
                        tableIndex = tNum
                        
                        for tr in table_r['LineItemExpenseFields']:
                            tNum += 1
                            print(tNum)
                            if(tr['Type']['Text']=="EXPENSE_ROW"):
                                
                                tables[tableIndex]['header']['EXPENSE_ROW'] == "EXPENSE_ROW"
                                
                                
                            for val in tr:
                                if(tNum == 1): # Header
                                    
                                    if val == "LabelDetection":
                                        sVal = tr['LabelDetection']['Text']
                                        
                                        sVal = re.sub('/\([^)]+\)/','',sVal)
                                        print(sVal)
                                        tables[tableIndex]['header'][tr['Type']['Text']] = sVal
                                    
                                        
                                        
                                        
                                if val == 'ValueDetection':
                                    
                                    if(bool(tables[tableIndex]['header'][tr['Type']['Text']])):
                                        print(tables[tableIndex]['header'][tr['Type']['Text']])
                                        
                                        tables[tableIndex]['body'][tr['Type']['Text']] = tr['ValueDetection']['Text']
                            if(tr['Type']['Text']=="EXPENSE_ROW"):
                                tables[tableIndex]['body'][tables[tableIndex]['header']['EXPENSE_ROW']] = tr['ValueDetection']['Text']
            
        retArr = [{"forms" : forms, "tables" : tables}]
        return retArr
                                    
    arr = textractToArray(response)
    pprint(arr)
                       
                                
                            
            
                        
                    
                    
    
    
                 
                                                
                             
    
    
  
    

                                    
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

    
    