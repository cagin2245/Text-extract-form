import json
import boto3
import helper

def lambda_handler(event, context):
    textract = boto3.client("textract")
    if event:
        file_obj = event["Records"][0]
        bucketName = str(file_obj['s3']['bucket']['name'])
        fileName = str(file_obj['s3']['object']['key'])
        
        print(f'Bucket: {bucketName} :::: Key: {fileName}')
        response = textract.analyze_expense(
                Document= {
                    'S3Object':{
                        'Bucket': bucketName,
                        'Name': fileName
                }})
    print(json.dumps(response))
    header,table_count = helper.headers(response)
    body = helper.bodys(response,header)
    
    
    arr = helper.textractToArray(response,header,body,table_count)
    
    
    res =helper.tableMatcher(arr,arr)
    print(res)
    json_res = json.dumps(res,indent=2,ensure_ascii=False)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

    