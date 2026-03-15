# Altrun Utils [中文](README.md)

A utility for merging and compressing Altrun shortcut list configuration files.

## Features

- **Single File Deduplication**: Deduplicate and compress a single configuration file
- **Configuration Merging**: Merge two Altrun shortcut configuration files
- **Conflict Handling**: Automatically handle conflicts for shortcuts with the same name
- **Duplicate Compression**: Merge entries with the same path, intelligently combine keywords
- **Auto Backup**: Automatically backup input files with .ori1/.ori2 suffix
- **GB2312 Encoding Support**: Correctly read and write GB2312 encoded configuration files

## Usage

```bash
python altrunMerger.py <config_file1> [config_file2]
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `config_file1` | Path to the first configuration file (required) |
| `config_file2` | Path to the second configuration file (optional) |

Output file is fixed to `ShortCutList.txt`

### Examples

**Single file deduplication**
```bash
python altrunMerger.py ShortCutList.txt
```

**Two files merge**
```bash
python altrunMerger.py ShortCutList_local.txt ShortCutList_hw.txt
```

## How It Works

1. **Parse Configs**: Read GB2312 encoded configuration files
2. **Merge by Key**: Merge using field 3 (shortcut name) as the key
3. **Handle Conflicts**: Auto-append suffixes `_0`, `_1`, etc. for name conflicts
4. **Compress by Path**: Merge entries with the same path (field 5), intelligently combine keywords
5. **Auto Backup**: Rename input files with `.ori1`, `.ori2` suffixes

## Configuration File Format

Configuration files use `|` as field delimiter, example:

```
field1 | field2 | shortcut_name | keywords | path | ...
```

## Requirements

- Python 3.x

## License

MIT License