
## for reading files
import dask.dataframe as dd
from tqdm import tqdm
import json
import os

## for storing db
import pickle

## for downloading excel
import pandas as pd
import base64
import io



'''
Class managing the DB, storing and querying
'''
class DB:
    def __init__(self):
        ## folder
        self.folder = "stored"
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        ## log json
        if not os.path.exists(self.folder+"/log.json"):
            self.log = {} 
        else:
            with open(self.folder+'/log.json', mode='r', errors='ignore') as dic:
                self.log = json.load(dic)
        print(self.log)

        ## db pickle
        if not os.path.exists(self.folder+"/db.pickle"):
            print("--- Creaing DB ---")
            self.db = pd.DataFrame()
            self.write_db()
        else:
            print("--- Loading stored DB ---")
            self.db = pickle.load( open(self.folder+'/db.pickle', mode="rb") )
            print("--- DB up and running ---")


    def write_db(self):
        pickle_out = open(self.folder+"/db.pickle", mode="wb")
        pickle.dump(self.db, pickle_out)
        pickle_out.close()


    def read_files(self):
        dtf = pd.DataFrame()
        for file in tqdm(os.listdir("db")):
            if (file not in self.log.keys()) or (self.log[file] != "done"):
                try:
                    tmp = dd.read_csv("db/"+file, sep="|", dtype='object').compute()
                    tmp["ADDRESS"] = tmp["PARTICELLA_TOP"].fillna("").str.upper().str.strip()+" "+tmp["INDIRIZZO"].fillna("").str.upper().str.strip()
                    dtf = dtf.append(tmp)
                    self.log[file] = "done"

                except Exception as e:
                    self.log[file] = e
                    continue
        self.dtf = dtf.reset_index(drop=True) 


    def update_log(self):
        with open(self.folder+'/log.json', mode='w') as dic: 
            json.dump(self.log, dic, indent=4, separators=(',',' : '))


    def update_db(self):
        self.db = self.db.append(self.dtf).reset_index(drop=True)
        self.write_db()


    def run(self):
        self.read_files()
        self.update_log()
        if len(self.dtf) > 0:
            print("--- Updating DB ---")
            self.update_db()
        print("--- DB ready ---")
        return self.db
    


'''
Write excel
:parameter
    :param dtf: pandas table
:return
    link
'''
def download_file(dtf):
    xlsx_io = io.BytesIO()
    writer = pd.ExcelWriter(xlsx_io)
    dtf.to_excel(writer, index=False)
    writer.save()
    xlsx_io.seek(0)
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    data = base64.b64encode(xlsx_io.read()).decode("utf-8")
    link = f'data:{media_type};base64,{data}'
    return link 
    




