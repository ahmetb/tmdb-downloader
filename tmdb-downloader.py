#!/usr/bin/python
from sys import argv

usage = '''Usage: tmdb-downloader APIKEY STARTID ENDID [destFolder]

Downloads movie data with ids as filenames to the output folder. Fetches movies with ids [STARTID...ENDID] inclusively'''

def main():
    if len(argv) < 4 :
        print usage
        return
    
    api_key = argv[1]

    try:
        start = int(argv[2])
        end = int(argv[3])
        start = min(start,end)
        end = max(start,end);
    except:
        print 'STARTID ENDID invalid integers'
        return

    for i in range(start,end+1):
        print i

if __name__ == '__main__':
    main()
