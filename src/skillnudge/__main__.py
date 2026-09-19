"""Module entry point for the SkillNudge development CLIs."""

import sys

from .experiment_runner import main as experiment_main
from .phase1 import main


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "experiment":
        raise SystemExit(experiment_main(sys.argv[2:]))
    raise SystemExit(main())
