from curses.panel import top_panel
from email import header
from posixpath import split
from urllib import response
from xml.dom.minidom import Document
import boto3
import pandas as pd
import json
import re
import ast
import trp
from pprint import pprint
from trp.trp2 import TDocument, TDocumentSchema
from textractcaller.t_call import call_textract
from trp.t_pipeline import order_blocks_by_geo
from textractprettyprinter.t_pretty_print import Textract_Pretty_Print, get_string
from difflib import SequenceMatcher


def string_comparison(list1,list2): # -> Jaccard Similarity
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1)+ len(list2)) - intersection
    return float(intersection) / union
    
def is_string_similar(s1: str,s2: str, treshold: float = 0.48): # String karşılaştırması 
    seq = SequenceMatcher(None,s1,s2)
    # print(seq.ratio()*100) -> Karşılaştırma yüzdelik oranının yazdırılması
    return SequenceMatcher(None,s1,s2).ratio() >= treshold
def get_rows_columns_map(table_result, blocks_map):
    rows = {}
    for relationship in table_result['Relationships']:
        if relationship['Type'] == 'CHILD':
            for child_id in relationship['Ids']:
                cell = blocks_map[child_id]
                if cell['BlockType'] == 'CELL':
                    row_index = cell['RowIndex']
                    col_index = cell['ColumnIndex']
                    if row_index not in rows:
                        rows[row_index] = {} # Creating a new row
                    rows[row_index][col_index] = get_text(cell,blocks_map)
    return rows


def get_table_result():

        blocks = response['Blocks']
        blocks_map = {}
        table_blocks = []
        for block in blocks:
            blocks_map[block['Id']] = block
            if block['BlockType'] == "TABLE":
                table_blocks.append(block)
        if len(table_blocks) <= 0:
            return "<b> TABLO bulunamadı </b>"
        pprint(table_blocks)


def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
    return text



def textDetect(): #AWS Textract bağlantısı ve response döndürülmesi
    response = None
    file = open("demo.jpeg","rb")
    binaryFile = file.read()    
    client = boto3.client('textract',"us-east-1")
    response = client.get_expense_analysis(
        Document={
            'Bytes': binaryFile

        },FeatureTypes=['FORMS','TABLES'])
    
    
    return response
def combine_headers(top_h, bottom_h):
    
    
    bottom_h[2] = top_h[1] + " " + bottom_h[2]
    
    bottom_h[3] = top_h[1] + " " + bottom_h[3]
    

if __name__ == "__main__":
    
    strCompare = ["Liste Adi","Ürün Miktari"]    # Karşılaştırılacak array
    # with open('Input.txt',encoding="utf8") as input_file:
    #     for line in input_file:
    #         strCompare.append(line)
    # response = textDetect()
    # with open("AWS_RESPONSE.txt","w") as aws_response:
    #     aws_response.write(str(response))

    with open('AWS_RESPONSE.txt',encoding="utf8") as responseFile:
        data = responseFile.read()
    response = ast.literal_eval(data)
    doc = trp.Document(response)
    t_doc = TDocumentSchema().load(response)
    ordered_doc = order_blocks_by_geo(t_doc)
    trp_doc = trp.Document(TDocumentSchema().dump(ordered_doc))
    for page in trp_doc.pages:
        for table in page.tables:
            table_data = []
            headers = table.get_header_field_names()
            if(len(headers)>0):
                #print("Headerlar: "+repr(headers))
                bottom_header = headers[0]
                top_header = headers[1]
                print(top_header)
                combine_headers(top_header,bottom_header)
                
                
                
                for r, row in enumerate(table.rows_without_header):
                    table_data.append([])
                    for c, cell in enumerate(row.cells):
                        table_data[r].append(cell.mergedText)
                if len(table_data)>0:
                    df = pd.DataFrame(table_data, columns = top_header)                  

                
    

    # for pa    ge in doc.pages:    
    #     key ="Ürün Adı"
    #     field = page.form.getFieldByKey(key)
    #     if(field):
    #         print("Key {}, Value: {}".format(field.key,field.value))

    text = []
    
    for item in response['Blocks']:
        if(item['BlockType']=='LINE'):                       
            #print(item['Text'])
            textt= "".join(str(item['Text']))
            if(re.search(" ",textt)):
                split_text = textt.split()
                for stext in split_text:
                    for strC in strCompare:
                        if(is_string_similar(stext,strC)>0.4):
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

    
    