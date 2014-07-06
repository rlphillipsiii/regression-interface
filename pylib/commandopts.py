
class CommandLineError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Opts:
    def __init__(self):
        self.options = []
        self.args = []
        self.cmd = {}

    def add_option(self, arg, alternate=None, value=False):
        self.options.append([arg, alternate, value])

    def parse_args(self, args):
        try:
            i = 0
            while i < len(args):
                arg = args[i]
                for option in self.options:
                    if arg == option[0] or arg == option[1]:
                        if option[2]:
                            i += 1
                            self.cmd[option[0]] = args[i]
                        else:
                            self.cmd[option[0]] = ''

                i += 1
    
            return self.cmd
        except:
            raise CommandLineError('Incorrect Number of Args')
            
    def get_args(self):
        return self.cmd
        
