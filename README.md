# LocalizationTDOA

TDOA localization done with Python.

Based on: 
    https://github.com/StevenJL/tdoa_localization

#  Requirements
- Python 3.14
- Python libs (see `requirements.txt`):
  - numpy
  - scipy (also reads the WAV files, so no libsndfile is needed)
  - matplotlib

Plots open in matplotlib's native window on macOS and Windows. On Linux, install
Tk for your Python (e.g. `python3-tk`) or pick another interactive backend.

# Setup

```sh
$ python3.14 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

# Launch of simple console runner

Run from the repository root:

```sh
$ python -m src.base_sample.console_runner -m 5 -p 2 -t 2 -f samples/sample.wav
```

# Launch of server runner

Choose desired configuration in `src/server_config.json` (the `audio` path is
relative to that file) and run from the repository root:

```sh
$ python -m src.server_runner
```
