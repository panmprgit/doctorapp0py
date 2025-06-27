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

The interface now ships with a polished look using a global Qt Style Sheet.
A theme toggle allows switching between **dark** and **light** modes from the
sidebar. Tables, forms and dialogs scale nicely with window size, and icons are
used throughout the navigation buttons.

![Dashboard Screenshot](docs/screenshot.png)

