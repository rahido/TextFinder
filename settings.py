import configparser
from os.path import isfile

class Settings():
    config_filepath = './config.ini'
    settings_dict = None
    def __init__(self):
        print("Settings - init")
        if not self.isConfigFile():
            self.createConfigFile()
        self.settings_dict = self.getConfigAsDict()
        print("settings_dict",self.settings_dict)

    def isConfigFile(self):
        return isfile(self.config_filepath)
    
    def createConfigFile(self):
        print("Settings - Creating Config file on root folder")
        config = configparser.ConfigParser()
        # No sections, using only DEFAULT
        config['DEFAULT'] = {'default_search_folder' : './',
                             'recursive_search' : 0,
                             'extensions' : ''}
        with open(self.config_filepath, 'w') as f:
            config.write(f)

    def getConfigAsDict(self):
        print("Settings-getConfigAsDict")
        settings = {}
        config = configparser.ConfigParser()
        config.read(self.config_filepath)
        for k in config['DEFAULT']:
            settings[k] = config['DEFAULT'][k]
        return settings
    
    def getDefaultFolder(self):
        return self.settings_dict['default_search_folder']
    def getDefaultRecursive(self):
        return self.settings_dict['recursive_search']
    def getDefaultExtensions(self):
        return self.settings_dict['extensions']

    def updateOneAndSave(self, key:str, value:str):
        print("Settings-updateOneAndSave")
        config = configparser.ConfigParser()
        config.read(self.config_filepath)
        config['DEFAULT'][key] = value
        with open(self.config_filepath, 'w') as f:
            config.write(f)
        return
    
    def updateManyAndSave(self, new_dict:dict):
        print("Settings-updateManyAndSave")
        config = configparser.ConfigParser()
        config.read(self.config_filepath)
        for k in new_dict:
            config['DEFAULT'][str(k)] = new_dict[str(k)]
        with open(self.config_filepath, 'w') as f:
            config.write(f)
        return
    
    def updateFromApp(self, default_search_folder, recursive_search, extensions):
        print("Settings-updateFromApp")
        new_dict = {'default_search_folder' : str(default_search_folder),
                    'recursive_search' : str(recursive_search),
                    'extensions' : str(extensions)
                    }
        self.updateManyAndSave(new_dict)
        return
    