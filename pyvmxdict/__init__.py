"""
The MIT License (MIT)

Copyright (c) 2016 Dave Parsons

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the 'Software'), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

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