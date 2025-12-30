import subprocess

SKETCH_DIR = "workspace/sketch"
BOARD = "arduino:avr:uno"

def compile_sketch():
    result = subprocess.run(
        [
            "arduino-cli",
            "compile",
            "--fqbn",
            BOARD,
            SKETCH_DIR
        ],
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout + result.stderr
