import ConfigParser
import pickle
import sys


class BasePlugin:
    """
    Abstract class for plugins
    """
    
    name = ''

    def run(self, config=None):
        """
        Virtual method for running the plugin
        """
        pass

    def execute(self):
        """
        Execution wrapper for the plugin
        argv[1]: ini_file
        """
        config = None
        if len(sys.argv) > 1:
            config = ConfigParser.RawConfigParser()
            config.read(sys.argv[1])
        pickle.dump(self.run(config), sys.stdout)

