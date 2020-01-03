import pandas as pd
base_dir = "/kaggle/input/elliptic-data-set/elliptic_bitcoin_dataset/elliptic_bitcoin_dataset/"
classes_file = "elliptic_txs_classes.csv"
class_data = pd.read_csv(base_dir + classes_file)
ill_anoId = class_data[class_data['class']=='1']['txId']#非法数据的序号


Result = pd.read_csv("../input/deanonymized-995-pct-of-elliptic-transactions/Result.csv")
TXID = pd.merge(ill_anoId,Result)['transaction']#所有的非法交易TXID，序号对应Txid
TXID.to_csv('TXID.csv',index=False,header=True)#保存到CSV中

#
from google.cloud import bigquery
client = bigquery.Client()
def get_atts(obj, filter=""):#查看属性
    return [a for a in dir(obj) if not a.startswith('_') and filter in a]
    

BYTES_PER_GB = 2**30
#获取数据集，列出表
btc_dataset = client.get_dataset(client.dataset('crypto_bitcoin', project='bigquery-public-data'))
[ds.table_id for ds in client.list_tables(btc_dataset)]

#获取输入表，显示表属性和机构
btc_inputs_table = client.get_table(btc_dataset.table('inputs'))
get_atts(btc_inputs_table)
print(btc_inputs_table.schema)
#获取输出表，显示表属性和机构
btc_outputs_table = client.get_table(btc_dataset.table('outputs'))
get_atts(btc_outputs_table)
print(btc_outputs_table.schema)

#在inputs表查询非法交易地址
query1 = """
    SELECT
        addresses
    FROM `bigquery-public-data.crypto_bitcoin.inputs`
    where transaction_hash in UNNEST(@Li)
"""
List_TXID = TXID.tolist()#将dataframe转为list

query_params = [
    bigquery.ArrayQueryParameter("Li", "STRING", List_TXID)#交List_TXID作为参数，传入Sql查询
]
job_config = bigquery.QueryJobConfig()
job_config.query_parameters = query_params
query_job = client.query(
    query1,
    job_config=job_config,
)  

result = query_job.result()
df = result.to_dataframe()
inaddr = []
for i in range(len(df)):#去除地址项多余字符
    inaddr.append(df['addresses'][i][0])
inilladdr = set(inaddr)#用set去重
test=pd.DataFrame(columns=['address'],data=inilladdr)
test.to_csv('InputAddress.csv')#写入CSV文件


#在outputs表查询非法交易地址
query2 = """
    SELECT
        addresses
    FROM `bigquery-public-data.crypto_bitcoin.outputs`
    where transaction_hash in UNNEST(@Li)
"""

query_params = [
    bigquery.ArrayQueryParameter("Li", "STRING", List_TXID)
]
job_config = bigquery.QueryJobConfig()
job_config.query_parameters = query_params
query_job = client.query(
    query2,
    job_config=job_config,
)  
result = query_job.result()
df = result.to_dataframe()
outaddr = []
for i in range(len(df)):#去除地址项多余字符
    outaddr.append(df['addresses'][i][0])
print(len(outaddr))
outilladdr = set(outaddr)#用set去重
print(len(outilladdr))
test=pd.DataFrame(columns=['address'],data=outilladdr)
test.to_csv('OutputAddress.csv')#写入CSV文件




