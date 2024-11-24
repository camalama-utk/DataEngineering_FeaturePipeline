
import requests
import datetime as datetime
import pandas as pd
import os 
url ='http://ballings.co/data.py'
#The following line will create an object called data
exec(requests.get(url).content)
#The data will be stored in an object called data

#Save the data to DataFrame
df = pd.DataFrame(data)

# Get the current date
current_date = datetime.date.today().strftime("%m-%d")

outname = f'545_data_{current_date}.csv'  
  
outdir = './group_project_data'  
if not os.path.exists(outdir):  
    os.mkdir(outdir)  
  
fullname = os.path.join(outdir, outname)      
  
df.to_csv(fullname,index=False)

#Example crontab edit based on your file path. Downloads from noon-2:00 pm everyday
# * 12-14 * * * /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 /Users/laneslawson/Downloads/Data_Engr/data_download.py

