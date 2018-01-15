from core import Core

core = Core('../samples/sample.wav', 5, 1, 2)
core.generate_source_positions()
core.generate_distances()
core.prepare()
core.generate_signals()
core.draw_plot()
