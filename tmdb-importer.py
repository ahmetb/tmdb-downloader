#!/usr/bin/python

# Author: Ahmet Alp Balkan <ahmetalpbalkan at gmail.com>
# http://ollaa.com

import os
from sys import argv, exit
import json
import datetime

try:
    from pymongo import Connection
except ImportError:
    print '''pymongo is not installed on your system: 
    execute command "easy_install pymongo" or refer to 
    http://api.mongodb.org/python/current/installation.html'''
    exit(1)

usage = '''Usage:   %s SRCDIR MONGO_DB MONGO_COLLECTION [MONGO_HOST [MONGO_PORT
            [MONGO_USER [MONGO_PASSWORD]]]]

(Dependencies: pymongo)

SRCDIR should have files containing JSON data for TMDb movies. Each file 
should contain only movie or error message.

Input files will be processed (often reduced) and then saved to the mongodb,
however that can be customized.'''

MOVIE_ITEM_TYPE = 1

srcdir, mongo_db, mongo_collection = None, None, None
mongo_host, mongo_port, mongo_user, mongo_pass = 'localhost', 27017, None, None

# lazy loading db instances
connection, db, collection = None, None, None

def main():
    global srcdir, mongo_db, mongo_collection
    global mongo_host, mongo_port, mongo_user, mongo_pass
    if len(argv) < 4:
        print usage % argv[0]
        exit(0)

    srcdir = os.path.abspath(argv[1])
    mongo_db = argv[2];
    mongo_collection = argv[3]
    
    if os.path.exists(srcdir) == False:
        print 'Error: %s doesn\'t exists or unreachable.' % srcdir
        exit(1)

    if not mongo_db or not mongo_collection:
        print 'Error: MONGO_DB and MONGO_COLLECTION are required.'
        exit(1);

    if len(argv) > 4:
        mongo_host = argv[4]

    if len(argv) > 5:
        try:
            mongo_port = int(argv[5])
        except:
            print 'Error: Port number should be numeric.'
            exit(1)
    
    if len(argv) > 6:
        mongo_user = argv[6]
    if len(argv) > 7:
        mongo_pass = argv[7]
    

    process_dir(srcdir)
    dispose()

def process_dir(directory):
    ls = os.listdir(directory)
    for f in ls:
        path = os.path.join(directory, f)
        if os.path.isfile(path):
            process_file(path)

def process_file(path):
    contents = None

    try:
        f = open(path, 'r')
        contents = f.read()
        f.close()
    except IOError as e:
        print 'IOError occurred: %s' % e
        exit(1)

    process_file_content(contents, path)

def process_file_content(content, filename):
    '''Process json content, ignore errors, save to db.'''
    movie = prepare_from_json(content,filename)

    if movie != None:
        save_movie(movie)


def prepare_from_json(json_str, filename):
    '''Prepare a movie dict from given json str, may return None'''
    try:
        try:
            obj = json.loads(json_str);
            if type(obj) is list:
                obj = obj[0]

            if type(obj) in [unicode, str]:
                #print 'File %s is not json object.' % filename
                return

            if obj['movie_type'] != 'movie':
                return

            # our movie object
            movie = {
                    'type' : obj['movie_type'], #should be movie
                    'tmdb_id': obj['id'],
                    'popularity' : obj['popularity'],
                    }

            name_keys = ['original_name', 'name', 'alternative_name']
            names = []
            
            for name_key in name_keys:
                if name_key in obj and not obj[name_key] in names:
                    name = obj[name_key]
                    if name != None:
                        names.append(obj[name_key])

            movie['names'] = names;

            if 'released' in obj: movie['released'] = obj['released']
            if 'rating' in obj: movie['rating'] = obj['rating']
            if 'imdb_id' in obj: movie['imdb_id'] = obj['imdb_id']
            if 'genres' in obj and obj['genres'] != []:
                names = []
                for genre in obj['genres']:
                    names.append(genre['name'])
                movie['genres'] = names

            if 'cast' in obj and obj['cast'] != []:
                names = []
                for cast in obj['cast'][:3]:
                    names.append(cast['name'])
                movie['cast'] = names

            if 'posters' in obj and obj['posters'] != []:
                urls = []
                for pic in obj['posters']:
                    img = pic['image']
                    if 'type' in img:
                        if img['type'] == 'poster' and \
                           img['size'] in ['thumb', 'mid', 'original'] and \
                           len(urls) < 3: # only one poster set
                            # here we trust that imgs will come in sorted order
                            urls.append(img['url'])
                    movie['pictures'] = urls

            return movie
                
        except KeyError as err:
            print 'JSON error in file %s: %s' % (filename, err)
            return

    except ValueError as err:
        print 'Parse error: %s' % err
        exit(1)

def save_movie(movie):
    global connection, db, collection
    global mongo_db, mongo_collection, mongo_user, mongo_pass
    '''Itemizes given movie and persists.'''

    item = {
            'type' : MOVIE_ITEM_TYPE,
            'created' : datetime.datetime.utcnow(),
            'features' : movie
            }

    try:
        if not connection or not db or not collection:
            try:
                connection = Connection(mongo_host, mongo_port)
                db = connection[mongo_db]
                if mongo_user or mongo_pass:
                    db.authenticate(mongo_user, mongo_pass)
                collection = db[mongo_collection]

            except Exception as err:
                print 'DB error establishing connection: %s' % err
                exit(3)

        existing = collection.find_one({"features.tmdb_id": \
                movie['tmdb_id']})
        
        if existing:
            print 'Movie %d already found, updating.' % movie['tmdb_id']
            existing['features'] = movie
            collection.save(existing) 
        else:
            print 'Movie %d is created.' % movie['tmdb_id']
            collection.save(item)


    except Exception as err:
        print 'DB Error: %s' % err

def dispose():
    if connection:
        connection.close()

if __name__ == '__main__':
    main()
