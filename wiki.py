#!/usr/bin/env python3
import zipfile
import bz2
import sys
import html
from xml.etree.ElementTree import XMLParser


def build(orig_index, new_index):
    bz = bz2.decompress(open(orig_index, "rb").read()).decode("utf-8")

    name2off = {}

    for line in bz.splitlines():
        f = line.find(":")
        offset = int(line[:f])
        f2 = line.find(":", f + 1) + 1
        name = line[f2:]
        name2off[name] = offset

    PER_FILE = 10 * 1000
    zf = zipfile.ZipFile(new_index, "w", zipfile.ZIP_DEFLATED)
    names = sorted(name2off)
    index = 0
    i = 0
    while index < len(names):
        s = []
        for name in names[index:index+PER_FILE]:
            s.append("%d:%s" % (name2off[name], name))
        zf.writestr("%08d" % i, "\n".join(s))
        index += PER_FILE
        i += 1

    zf.close()


def read(indexzf, which):
    f = indexzf.open(which)
    res = {}
    for line in f.readlines():
        line = line.decode("utf-8").strip()
        colon = line.find(":")
        offset = int(line[:colon])
        name = html.unescape(line[colon+1:])
        res[name] = offset
    return res


def get(datafile, indexfile, query=None):
    zf = zipfile.ZipFile(indexfile, "r")
    files = sorted(zf.namelist())
    if query is None:
        for fname in files:
            for name in sorted(read(zf, fname).keys()):
                print(name)
        return

    # TODO DEBUG, slow
    for i, f in enumerate(files):
        r = read(zf, f)
        if query in r:
            print("Yay in", i, r[query])

    lo = 0
    hi = len(files) - 1
    found = None
    while lo != hi:
        mi = (lo + hi) // 2
        print(lo, hi, mi)
        name2offset = read(zf, files[mi])
        if query in name2offset:
            found = name2offset[query]
            break
        else:
            key = next(iter(name2offset))
            if query < key:
                hi = mi - 1
            else:
                lo = mi + 1

    if found is None:
        name2offset = read(zf, files[lo])
        if query in name2offset:
            found = name2offset[query]

    zf.close()

    if found is None:
        print("Not found...")
        return

    dec = bz2.BZ2Decompressor()
    df = open(datafile, "rb")
    df.seek(found)
    

    class Parser(object):
        def __init__(self):
            self.stack = []
            self.done = False

        def start(self, tag, attrib):
            if self.done: return
            self.stack.append(tag)
            if tag == "title":
                self.title = ""
            elif tag == "text":
                self.text = ""

        def end(self, tag):
            if self.done: return
            self.stack.pop()
            if tag == "text" and self.title == query:
                self.done = True

        def data(self, data):
            if self.done: return
            if self.stack[-1] == "title":
                self.title += data
            elif self.stack[-1] == "text":
                self.text += data
        

    target = Parser()
    parser = XMLParser(target=target)
    parser.feed("<root>")
    while not target.done:
        data = dec.decompress(df.read(65536))
        parser.feed(data)

    print(target.title)
    print(target.text)
    

def main():
    cmd = sys.argv[1]
    if cmd == "build":
        orig_index = sys.argv[2]
        new_index = sys.argv[3]
        build(orig_index, new_index)
    elif cmd == "get":
        datafile = sys.argv[2]
        indexfile = sys.argv[3]
        query = sys.argv[4]
        get(datafile, indexfile, query)
    elif cmd == "list":
        datafile = sys.argv[2]
        indexfile = sys.argv[3]
        get(datafile, indexfile)
    else:
        usage()


if __name__ == "__main__":
    main()