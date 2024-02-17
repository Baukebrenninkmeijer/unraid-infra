import sys
from pathlib import Path

sys.path.insert(0, (Path(__file__).parents[1] / "dags").as_posix())
print(sys.path)

import airflow_assessment

if __name__ == "__main__":
    print(sys.path)
    print("Hello, World!")
