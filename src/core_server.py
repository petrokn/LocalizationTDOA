from flask import Flask, request, jsonify
from src.logic.core import Core
from multiprocessing import freeze_support

app = Flask(__name__)


@app.route("/get_position")
def get_position():
    """http://localhost:5000/get_position?filename=test&mic_amount=37 ..."""
    filename = request.args.get('filename', '', str)
    mic_amount = request.args.get('mic_amount', 0, int)
    trials = request.args.get('trials', 0, int)
    proc_number = request.args.get('proc_number', 0, int)
    core = Core(filename, mic_amount=mic_amount, trials=trials, proc_number=proc_number)
    core.generate_source_positions()
    core.generate_distances()
    core.prepare()
    core.generate_signals()
    return jsonify(est_x=float(core.estimated_positions[0][0]), est_y=float(core.estimated_positions[0][1]),
                   est_z=float(core.estimated_positions[0][2]), true_x=float(core.true_positions[0][0]),
                   true_y=float(core.true_positions[0][1]), true_z=float(core.true_positions[0][2]))

if __name__ == "__main__":
    freeze_support()
    app.run(host='0.0.0.0')
