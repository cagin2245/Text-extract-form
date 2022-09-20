from posixpath import split
from urllib import response
from xml.dom.minidom import Document
import boto3
import pandas
import json
import re
import ast
import trp
from difflib import SequenceMatcher



def is_string_similar(s1: str,s2: str, treshold: float = 0.70): # String karşılaştırması 
    seq = SequenceMatcher(None,s1,s2)
    # print(seq.ratio()*100) -> Karşılaştırma yüzdelik oranının yazdırılması
    return SequenceMatcher(None,s1,s2).ratio() >= treshold


def textDetect(): #AWS Textract bağlantısı ve response döndürülmesi
    response = None
    file = open("demo.jpeg","rb")
    binaryFile = file.read()    
    client = boto3.client('textract',"us-east-1")
    response = client.analyze_document(
        Document={
            'Bytes': binaryFile

        },FeatureTypes=['FORMS','TABLES'])
    
    return response
    


if __name__ == "__main__":
    
    strCompare = []    # Karşılaştırılacak array
    # with open('Input.txt',encoding="utf8") as input_file:
    #     for line in input_file:
    #         strCompare.append(line)
    # response = textDetect()
    # with open("AWS_RESPONSE.txt","w") as aws_response:
    #     aws_response.write(str(response))
   
    
    
    
    
    with open('AWS_RESPONSE.txt',encoding="utf8") as responseFile:
        data = responseFile.read()
    response = ast.literal_eval(data)
    doc = Document(response)
    
    
    
    text = []
    for page in doc.tab:
        for table in page:
            for r, row in enumerate(table.rows):
    
    for item in response['Blocks']:
        if(item['BlockType']=='LINE'):                       
            print(item['Text'])
            textt= "".join(str(item['Text']))
            if(re.search(" ",textt)):
                split_text = textt.split()
                for stext in split_text:
                    for strC in strCompare:
                        if(is_string_similar(stext,strC)):
                            text.append(item['Text'])
            else:
                for strr in strCompare:
                    if(is_string_similar(textt,strr)):
                        text.append(item['Text']) 
    blocks = response['Blocks']
    strBlocks = json.dumps(blocks,indent=4)
    with open("Output.txt","w") as text_file:
        strtext = '\n'.join(text)
        text_file.write(strtext)
#   with open("OutputJSON.txt","w")as json_file:   -> JSON output
#   json_file.write(strBlocks)    

    
    