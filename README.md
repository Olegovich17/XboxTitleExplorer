<div align="center">

<img width="443" height="442" alt="logo" src="https://github.com/user-attachments/assets/9804409a-9d1a-4b30-9b87-343e92b1b92f" />

# Xbox Title Explorer
## Names over HEX. Speed over Windows Explorer.

</div>

Helps you scan game folders and copy selected titles to external drives using TeraCopy. Features automatic title name fetching via API


## Features

- Scan Xbox title folders (Hdd1:\Content\0000000000000000)
- Fetch title information from online API ([dbox API](https://dbox.tools/api/docs))
- Batch title info caching
- [TeraCopy](https://codesector.com/downloads) integration for copying files
- Multi-language support (English, Russian)
- Dark theme UI

## Requirements

- Python 3.10+
- Windows
- TeraCopy (for copy functionality)

## Installation

```bash
pip install PyQt6
```

## Usage

Run the application:
```bash
python main.py
```

Or use the launcher:
```bash
run.bat
```

### Building EXE

Run the build script:
```bash
build.bat
```

The executable will be created in the `dist` folder.

## Configuration

Configuration is stored in `config.ini`:
- Language selection
- TeraCopy path and flags

## License

MIT
