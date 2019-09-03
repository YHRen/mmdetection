import pandas as pd
from pathlib import Path
from datetime import date

data_dir = Path('./')

cnt = 0

filenames = []
abs_path  = []

for f in data_dir.iterdir():
    if f.suffix == '.xml':
        filenames.append(f.stem)
        abs_path.append(str(f.resolve()))
df = pd.DataFrame({'image-name' : filenames, 
                   'path': abs_path})
print(df)

df.to_csv('./images_'+str(date.today())+'.csv')
