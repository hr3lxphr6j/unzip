#!/usr/bin/env python
import os
import zipfile
from argparse import ArgumentParser


class ZipFile(zipfile.ZipFile):
    def __init__(self, *args, charset=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.from_charset = 'cp437'
        self.charset = 'cp437'
        self._refine_filelist(charset)

    def _refine_filelist_with_charset(self, charset):
        for item in self.filelist:
            raw_name = item.filename.encode(self.from_charset)
            new_name = raw_name.decode(charset)
            item.filename = new_name
            self.NameToInfo[new_name] = item
        self.charset = charset

    def _refine_filelist(self, charset=None):
        # When the charset is specified,
        # the specified charset is used first.
        if charset:
            for c in charset:
                try:
                    self._refine_filelist_with_charset(c)
                    return
                except UnicodeDecodeError:
                    pass

        try:
            import chardet
            all_filename = b''.join(
                [f.filename.encode(self.from_charset) for f in self.filelist])
            charset = chardet.detect(all_filename).get(
                'encoding') or self.from_charset

            self._refine_filelist_with_charset(charset)
        except ImportError:
            pass


def listZip(zipf, charset):
    with ZipFile(zipf, 'r', charset=charset) as zipObj:
        print("Archive:  %s" % zipf)
        print("  Length      Date    Time    Name")
        print("---------  ---------- -----   ----")
        infoList = zipObj.infolist()
        totalNum = 0
        totalSize = 0
        for fInfo in infoList:
            totalNum += 1
            totalSize += fInfo.file_size
            print("%9d" % fInfo.file_size, end=' ')
            print("%04d-%02d-%02d" %
                  (fInfo.date_time[0], fInfo.date_time[1], fInfo.date_time[2]), end=' ')
            print("%02d:%02d" %
                  (fInfo.date_time[3], fInfo.date_time[4]), end='  ')
            print("{}({})".format(fInfo.filename, zipObj.charset))
        print("---------                     -------")
        print("%9d" % totalSize, end='')
        print("                   ", end='')
        print("%d files" % totalNum)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-l', '--list', action='store_true',
                        help='list files in zip file', dest='islist', default=False)
    parser.add_argument('-d', dest='exdir', default='./',
                        help='extract files into exdir')
    parser.add_argument('-O', dest='charset', nargs='*',
                        help='specify a character encoding')
    parser.add_argument('file', nargs='+', help='target file or directory')
    return parser.parse_args()


def main():
    args = parse_args()
    charset = args.charset
    for f in args.file:
        if args.islist:
            listZip(f, charset=charset)
        else:
            with ZipFile(f, 'r', charset=charset) as zipObj:
                zipObj.extractall(path=args.exdir)


if __name__ == "__main__":
    main()
