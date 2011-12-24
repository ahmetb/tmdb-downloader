#!/usr/bin/python

# Author: Ahmet Alp Balkan <ahmetalpbalkan at gmail.com>
# http://ollaa.com
import os
from sys import argv
from sys import exit
from urllib import urlopen
from time import sleep

usage = '''Usage: %s APIKEY STARTID ENDID [DESTFOLDER] [SLEEP_INTERVAL] 

Downloads movie data with ids as filenames to the output folder. Fetches movies with ids [STARTID...ENDID] inclusively'''

api_key = None
base_url = 'http://api.themoviedb.org/2.1/Movie.getInfo/en/json/%(api_key)s/%(movie_id)d'
interval_sec=1.1
dest_dir = 'out'

def main():
    global api_key, interval_sec, dest_dir 

    if len(argv) < 4 :
        print usage % argv[0]
        exit(0)
    
    api_key = argv[1]

    try:
        start = int(argv[2])
        end = int(argv[3])
        start = min(start,end)
        end = max(start,end);

        if len(argv) > 5:
            interval_sec = float(argv[5])
    except:
        print 'invalid numeric parameters'
        exit(1)

    if len(argv) > 4:
        dest_dir = argv[4]

    if os.path.exists(dest_dir) == False:
        try:
            os.mkdir(dest_dir)
            print 'Directory %s is created.' % dest_dir
        except Exception as err:
            print 'Error occurred: %s' % err
            exit(2)
    print 'Destination directory is \'%s\''% dest_dir


    print 'Starting download %d...%d' % (start, end)
    for movie_id in range(start,end+1):
        result = download_save(movie_id)
        if result:
            print '#%d: OK' % movie_id
        sleep(interval_sec)


def download_save(movie_id):
    try:
        url = prepare_url(movie_id)

        file_name = url.split('/')[-1]
        local = open(os.path.join(dest_dir, file_name),'w+')

        web = urlopen(url)
        local.write(web.read())
        web.close()
        local.close()

        return True
    except Exception as err:
        print '#%d: ERROR: %s' % (movie_id, err)
        return False
        

def prepare_url(movie_id):
    global base_url
    return base_url % {"api_key":api_key, "movie_id":movie_id}

if __name__ == '__main__':
    main()

