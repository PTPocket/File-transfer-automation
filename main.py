import os
from datetime import datetime
import shutil
import time

class FileRule():
    def __init__(self, destination_folder:str, file_types:list, identifiers:list):
        self.destination_folder = destination_folder
        self.file_types  = file_types
        self.identifiers = identifiers

    def file_exists(self, file_name:str):
        path = os.path.join(self.destination_folder, file_name)
        if os.path.exists(path) is True:
            return True
        return False
    
    def get_destination_path(self, file_name:str):
        return os.path.join(self.destination_folder, file_name)
    
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
    def __init__(self, name:str, source_folder:str, rules=[]):
        self.name   = name
        self.source_folder = source_folder
        self.rules  = rules

    def add_rule(self, destination_folder, file_types:list, identifiers:list):
        self.rules.append(
            FileRule(
                destination_folder=destination_folder,
                file_types=file_types,
                identifiers=identifiers
            )
        )

    def print_log(self, copy_type:str, file_name:str, dest_path:str):
        text = f'''
Date   : {datetime.today().replace(microsecond=0)}
Name   : {self.name}
Action : {copy_type.capitalize()}
File   : {file_name}
From   : {self.source_folder}
To     : {dest_path}
____________________________
'''
        print(text)
    
    def run(self):
        try:
            for file in os.listdir(self.source_folder):
                source_path = os.path.join(self.source_folder, file)
                rules = [rule for rule in self.rules if rule.is_valid(file)]
                for rule in rules:
                    dest_folder = rule.destination_folder
                    dest_path = rule.get_destination_path(file)
                    if rule.file_exists(file) is False:
                        shutil.copy2(source_path, dest_path)
                        self.print_log('Copy', file, dest_folder)
                        continue
                    #Checks if file in source has been modified
                    if os.path.getmtime(source_path) > os.path.getmtime(dest_path):
                        shutil.copy2(source_path, dest_path)
                        self.print_log('Overwrite', file, dest_folder)
                        continue
        except Exception as e:
            text=f'''
!!!ERROR!!!
Rule Name  : {self.name}
Description: {e}
____________________________'''
            print(text)

if __name__ == '__main__':
    frule1 = FolderRule(
            name = 'default name',
            source_folder =r'C:\Users\PT-PC\Documents\PDF'
    )
    frule1.add_rule(
        destination_folder=r'C:\Users\PT-PC\Documents\np',
        file_types=['pdf'],
        identifiers=[]
    )

    transfer_rules = [
        frule1,
    ]
    print('File transfer started.')
    while True:
        for transfer_rule in transfer_rules:
            transfer_rule.run()
        time.sleep(1)