# Sample PMT Import Data

- match.csv: 1 row per match (metadata)
- pmt_game.csv: 2 team rows + 10 player rows per match

Run:
python manage.py import_pmt data/match.csv data/pmt_game.csv