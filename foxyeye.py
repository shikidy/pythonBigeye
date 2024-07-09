import os
import requests
import shutil
import tarfile
import time
from pathlib import Path

from src.pypi import PyPi
from src.observer import Observer



if __name__ == '__main__':

    # project_files = list(Path("input").rglob("*.[pP][yY]"))
    # for sub_path in project_files:
    #     o = Observer(sub_path)
    #     if not o.logs: continue
    #     print(o.logs)
    # exit()
    checked_links = []
    p = PyPi()
    while 1:
        latest = p.latest
        for late in latest:
            if late in checked_links: continue
            checked_links.append(late)
            if len(checked_links) == 100:
                checked_links.remove(checked_links[-1])
            download_link = p.get_project_downloadlink(late)
            if not download_link: continue
            print(download_link)
            with open("input/to_check.tar.gz", "wb") as f:
                data = requests.get(download_link)
                f.write(data.content)
            tarfile.open("input/to_check.tar.gz", "r:gz").extractall(path='input/')

            # os.remove("input/to_check.tar.gz")

            project_files = list(Path("input").rglob("*.[pP][yY]"))
            logs_txt_name = late.split('/')[-2]
            all_logs = ""
            if_crit = False

            
            for sub_path in project_files:
                try:
                    o = Observer(sub_path)
                except: continue
                if not o.logs: continue
                if o.critical_logs:
                    if_crit  = True
                all_logs += f"\n\n[{sub_path}]\n {o.logs}"
            try:
                shutil.rmtree("input")
            except: ...
            try:
                os.mkdir('input')
            except: ...
            
            if not all_logs: continue
            print(f"FOUND LOGS AT {logs_txt_name} | IsCrit: {if_crit}")
            if if_crit:
                logs_txt_name = "CRIT_" + logs_txt_name
            
            with open('logs/' + logs_txt_name + '.txt', 'w', encoding='utf-8') as f:
                f.write(all_logs)

    time.sleep(5)













 

