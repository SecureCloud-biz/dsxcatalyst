from __future__ import print_function
from configobj import ConfigObj


class VMDict(ConfigObj):

    def __init__(self, infile=None):
        ConfigObj.__init__(self, infile)

    def write(self, outfile=None, **kwargs):
        with open(self.filename, "r+")as f:
            f.seek(0)

            if len(self.initial_comment) > 0:
                print('\n'.join(str(l) for l in self.initial_comment), file=f)

            for k in self:
                if len(self.comments[k]) > 0:
                    print('\n'.join(str(l) for l in self.comments[k]), file=f)
                print(str(k + ' = "' + self[k] + '" ' + str(self.inline_comments[k] or '')).rstrip(), file=f)

            if len(self.final_comment) > 0:
                print('\n'.join(str(l) for l in self.final_comment), file=f)

            f.truncate()
            f.flush()
            f.close()