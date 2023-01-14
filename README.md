# Redis DB Analyzer

## Summary
Tool for scanning an entire key set in a Redis DB

## Features
- Scans all keys in a DB, categorizes them by data type, and provides memory stats per data type.
## Prerequisites
- Python
## Installation
1. Clone this repo.

2. Install Python requirements (either in a virtual env or global)
```bash
pip install -r requirements.txt
```
## Usage
### Options
- --url. Redis connection string.  Default = redis://localhost:6379
- --batchsize. Number of keys to be scanned per scan cycle.  Default = 1000.
- --nsynth. Number synthetic objects to be created in the Redis DB.  Default = 0.
### Execution
```bash
python3 analyzer.py --url redis://default:redis@localhost:12000 --nsynth 1000000 --batchsize 10000
```
### Output

Generated Keys: {'hash': 333677, 'ReJSON-RL': 332290, 'string': 334033}

Fetched 1000000 keys

|       |       hash |   ReJSON-RL |       string |
|:------|-----------:|------------:|-------------:|
| count | 333677     |  332290     | 334033       |
| mean  |    179.595 |     182.858 |     68.5162  |
| std   |     60.395 |      71.677 |      5.76625 |
| min   |     78     |      56     |     51       |
| 25%   |    127     |     121     |     64       |
| 50%   |    179     |     182     |     69       |
| 75%   |    230     |     243     |     74       |
| max   |    337     |     364     |     78       |