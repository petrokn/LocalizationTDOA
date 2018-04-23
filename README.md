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

# Launch of simple console runner
```sh
$ cd src/base_sample/
$ python console_runner.py -m 5 -p 2 -t 2 -f "../samples/sample.wav"
```

# Launch of server runner

Choose desired configuration in server_config.json and run

```sh
$ cd src
$ python server_runner.py
```