# Wikipedia dump reader

This project allows you to quickly browse Wikipedia offline, by using
predownloaded Wiki dumps (google it).

It comes with an index, but it's sorted by page id, which is useless
for searching purposes - we need to make our own, just one time:

```
$ python3 wiki.py build ~/Downloads/enwiki-20170820-pages-articles-multistream-index.txt.bz2 ~/wiki-index
```
This operation should take about 2 minutes - it could be slightly quicker,
but almost half of the time is taken by bz2 decompression itself. Instead
I focused on memory optimizations. A few numbers:

- original Wiki dump index is 186MB
- uncompressed, that takes 819MB
- there are 17 million entries
- building our sorted index takes 1.5GB of RAM (difference mostly due to 
Python string overhead, for example, "abc" takes 52 bytes)
- quickly searchable index stored on disk takes 208MB

Afterwards, searching the dump is instantaneous and uses next to no RAM:
```
$ /usr/bin/time -f "%E %M" python3 wiki.py get ~/Downloads/enwiki-20170820-pages-articles-multistream.xml.bz2 ~/wiki-index "Radare2" | head -n 20
Radare2
{{Infobox Software
| name                       = Radare2
| logo                       = 
| screenshot                 = File:Radare2 webui.png
| caption                    = 
| collapsible                = 
| author                     = Sergi Alvarez [https://twitter.com/trufae (pancake)]
| developer                  = pancake and the core-contributors
| released                   = 
0:00.17 21484
```
