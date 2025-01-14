import os
import shutil
from tqdm import tqdm
import json
import time

source_path = 'Z:/data2/iena'

del_list = ['(auto_backup)', 'json변환', '데이터셋 있던 경로.json']

for root, dirs, files in os.walk(source_path):
    for file in files:
        for del_name in del_list:
            if del_name in file:
                os.remove(os.path.join(root, file))
                break