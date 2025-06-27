# Doctor Application

## Requirements

- Python 3.10+
- [PySide6](https://pypi.org/project/PySide6/)

Install dependencies using the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```

Alternatively, run the setup script to create a virtual environment and
install everything automatically:

```bash
./setup.sh
```

## Running

```bash
python main.py
```

The application will create a local `data.db` SQLite database on first run.

## UI Improvements

The interface now features a modern dark theme and a sidebar layout with
responsive tables. Therapy entries automatically resize so you no longer need
to manually expand the tab when editing customers.

