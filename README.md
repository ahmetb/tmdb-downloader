Introduction
============
This project is described for downloading data from TMDb database and saving it to the MongoDB. Both parts can be used independently. Saving feature is specifically designed for ollaa.com project, see `tmdb-importer.py` for details.

Usage
=====

Example to an update scenario:

    ./tmdb-downloader.py #ApiKey# 80000 90000 out 0.5

then

    ./tmdb-importer out dbName collName localhost 27017 myUser myPass

new records will be created, old records will be updated.

Credits
=======
Ahmet Alp Balkan <ahmetalpbalkan at gmail.com>

Licence
=======
This work is licensed under [Apache License version 2.0](http://www.apache.org/licenses/LICENSE-2.0.html).
