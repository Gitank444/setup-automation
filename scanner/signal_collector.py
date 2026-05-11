import shutil
from models import ToolEvidence


def collect_python_signal():

    command_exists = shutil.which("python") is not None

    evidence = ToolEvidence(
        tool="python",
        command_exists=command_exists,
        pip_installed=False,
        conda_installed=False,
        path_found=command_exists,
        errors=[]
    )

    return evidence
