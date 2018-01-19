# LocalizationTDOA

TDOA localization done with Python.

Based on: 
    https://github.com/StevenJL/tdoa_localization

#  Requirements
### System bin/libs:
- Python 2.7
- libsndfile-devel
- tkinter
### Python libs:
- numpy
- scipy
- matplotlib
- scikits.audiolab

# Launch
```sh
$ cd src
$ python console.py -m 5 -p 2 -t 2 -f "../samples/sample.wav"
```