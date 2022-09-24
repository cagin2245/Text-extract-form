from posixpath import split

from xml.dom.minidom import Document
import boto3
import pandas as pd
import json
import re
import ast
import itertools
import numpy as np


from difflib import SequenceMatcher




def is_string_similar(s1: str,s2: str, treshold: float = 0.50): # String karşılaştırması 
    seq = SequenceMatcher(None,s1,s2)
    # print(seq.ratio()*100) -> Karşılaştırma yüzdelik oranının yazdırılması
    return SequenceMatcher(None,s1,s2).ratio() >= treshold


def textDetect(): #AWS Textract bağlantısı ve response döndürülmesi
    response = None
    file = open("demo.jpeg","rb")
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
    # with open("AWS_AnalyzeExpense_RESPONSE.txt","w") as aws_response:
    #     aws_response.write(str(response))
   
    
    
    
    
    with open('AWS_AnalyzeExpense_RESPONSE.txt') as responseFile:
        data = responseFile.read()
        response = ast.literal_eval(data)
    print(response)
    
    
    
    valSet = set()
    text = []
    l1 = []
    tdata = []
    
                 
                                                
                             
    
    
  
    

                                    
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
    blocks = response['Blocks']
    strBlocks = json.dumps(blocks,indent=4)
    with open("Output.txt","w") as text_file:
        strtext = '\n'.join(text)
        text_file.write(strtext)
        #   with open("OutputJSON.txt","w")as json_file:   -> JSON output
        #   json_file.write(strBlocks)    

    
    