from core import Core

core = Core('sample.wav')
core.generate_source_positions()
core.generate_distances()
core.prepare()
core.generate_signals()
core.draw_plot()
