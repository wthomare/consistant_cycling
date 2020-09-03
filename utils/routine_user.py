# -*- coding: utf-8 -*-

import os

class Routine_user(object):
    
    def __init__(self, upload, name):
        self.user_path = os.path.join(upload, name)
    
    def check_path(self):
        if not os.path.isdir(self.user_path):
            return False
        return True
    
    def create_path(self):
        try:
            os.mkdir(self.user_path)
            os.mkdir(os.path.join(self.user_path, 'graphic'))
            
        except:
            print("Failed to create path :  [%s]" %self.user_path)
            return False
        else:
            return True
    
    def delete_path(self):
        os.remove(self.user_path)
        os.remove(os.path.join(self.user_path, 'graphic'))

    def after_log(self):
        if not self.check_path():
            return self.create_path()
        else:
            return True