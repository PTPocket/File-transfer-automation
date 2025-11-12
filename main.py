import os
from datetime import datetime
import shutil
import time
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        func(*args, **kwargs)
        print(f'Time: {time.perf_counter()-start}')
    return wrapper


class FileRule():
    def __init__(self, destination_dir:str, file_types:list, identifiers:list):
        self.destination_dir = destination_dir
        self.file_types  = file_types
        self.identifiers = identifiers

    def file_exists(self, file_name:str):
        path = os.path.join(self.destination_dir, file_name)
        if os.path.exists(path) is True:
            return True
        return False
    
    def get_destination_path(self, file_name:str):
        return os.path.join(self.destination_dir, file_name)
    
    def is_type_valid(self, file_name:str):
        if self.file_types == []:
            return True
        for file_type in self.file_types:
            if str(file_name).lower().endswith('.'+str(file_type).lower()):
                return True
        return False

    def is_identifier_valid(self, file_name:str):
        if self.identifiers == []:
            return True
        for identifier in self.identifiers:
            if str(identifier).lower() in file_name.lower():
                return True
        return False

    def is_valid(self, file_name:str):
        if self.is_type_valid(file_name) is False or self.is_identifier_valid(file_name) is False:
            return False
        return True

class FolderRule():
    def __init__(self, source_dir:str, files_in_dir:bool, max_depth:int, rules:list):
        self.source_dir = source_dir
        self.files_in_dir = files_in_dir
        self.max_depth = max_depth
        self.rules  = rules
        self.last_error = None

    def add_rule(self, destination_dir, file_types:list, identifiers:list):
        self.rules.append(
            FileRule(
                destination_dir=destination_dir,
                file_types=file_types,
                identifiers=identifiers
            )
        )

    def print_log(self, copy_type:str, file_name:str, source_dir, dest_dir:str):
        text = f'[{copy_type.capitalize()}] [{file_name}] [{source_dir}] >> [{dest_dir}]'
        logging.info(text)
    
    def validate_and_copy(self, file, file_dir):
        file_path = os.path.join(file_dir,file)
        rules = [rule for rule in self.rules if rule.is_valid(file)]
        for rule in rules:
            destination_dir = rule.destination_dir
            dest_path = rule.get_destination_path(file)
            if rule.file_exists(file) is False:
                shutil.copy2(file_path, dest_path)
                self.print_log('Copy', file, file_dir, destination_dir)
                continue
            #Checks if file in source has been modified
            if os.path.getmtime(file_path) > os.path.getmtime(dest_path):
                shutil.copy2(file_path, dest_path)
                self.print_log('Overwrite', file, file_dir,  destination_dir)
                continue

    def check_directory_for_files(self, dir_path, depth):
        if depth >= self.max_depth:
            return
        for file in os.listdir(dir_path):
            path = os.path.join(dir_path, file)
            if os.path.isdir(path):
                self.check_directory_for_files(path, depth+1)
                continue
            self.validate_and_copy(file, dir_path)

    def run(self):
        destination_dir = None
        try:
            for file in os.listdir(self.source_dir):
                file_path = os.path.join(self.source_dir, file)
                if self.files_in_dir is True and os.path.isdir(file_path):
                    self.check_directory_for_files(file_path,0)
                    continue
                self.validate_and_copy(file, self.source_dir)
            self.last_error = None
        except Exception as e:
            if self.last_error is None or (time.perf_counter()-self.last_error > 300):
                logging.error(f'[{self.source_dir}] >> [{destination_dir}] {e}')
                self.last_error = time.perf_counter()

if __name__ == '__main__':
    logging.info('Starting program')

    rule0 = FolderRule(
        source_dir = r'C:\Users\PT-PC\Documents\PDF',
        files_in_dir = True,
        max_depth = 1,
        rules = [
            FileRule(
                destination_dir=r'C:\Users\PT-PC\Documents\np',
                file_types=['pdf'],
                identifiers=[]
            )
        ]
    )

    transfer_rules = [
        rule0,
    ]
    # count = 0
    # avg_time = 0
    while True:
        for transfer_rule in transfer_rules:
            # start = time.perf_counter()
            transfer_rule.run()
            # avg_time+=time.perf_counter()-start
            # count+=1
            # print(f'AVG Time: {avg_time/count}')
        time.sleep(1)
