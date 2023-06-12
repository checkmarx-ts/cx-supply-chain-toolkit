

class ImageTagDefinition:

    def __init__(self, container, containerttl, exectimeout, execenv, execparams, envpropagate, dockerparams):
        self.__container = container
        self.__containerttl = containerttl
        self.__exectimeout = exectimeout
        self.__execenv = execenv
        self.__execparams = execparams
        self.__envpropagate = envpropagate
        self.__dockerparams = dockerparams

    def __str__(self):
        return f"Image: {self.container} TTL: {self.containerttl} Timeout: {self.exectimeout} Env Vars: {len(self.execenv.keys())} Params: {len(self.execparams)}"

    @property
    def dockerparams(self):
        return self.__dockerparams
    
    @property
    def container(self):
        return self.__container
    
    @property
    def containerttl(self):
        return self.__containerttl
    
    @property
    def exectimeout(self):
        return self.__exectimeout
    
    @property
    def execenv(self):
        return self.__execenv
    
    @property
    def execparams(self):
        return self.__execparams

    @property
    def envpropagate(self):
        return self.__envpropagate
