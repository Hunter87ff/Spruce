pip install --upgrade pip
pip install uv
uv sync

MAX_RUNS=2
while [ $MAX_RUNS -gt 0 ]; do
    uv run src/main.py
    sleep 5
    ((MAX_RUNS--))
done
