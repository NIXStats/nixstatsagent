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

    def get_agent_cache(self):
        """
        Return agent cached value for this specific plugin.
        """
        try:
            return self.agent_cache[0]
        except Exception:
            return {}

    def set_agent_cache(self, cache):
        """
        Set agent cache value previously passed to this plugin instance.
        To avoid errors self.agent_cache have to be set on agent side
        after plugin instance initialization.
        Minimally it should be set as [{}] (dict in list)
        Agent will be able to see only changes in zero element of self.agent_cache
        Do not manually override self.agent_cache, othervice cache will not be saved!

        If self.agent_cache does not exists or not a list
        appropriate exception will be raised.
        """
        self.agent_cache[0] = cache
