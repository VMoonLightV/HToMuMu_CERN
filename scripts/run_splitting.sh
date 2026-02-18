echo "---------------- Splitting on ggH tuples ---------------- "
python3 scripts/split_tuples.py signal ggH
python3 scripts/split_tuples.py data ggH

echo "---------------- Splitting on VBF tuples ---------------- "
python3 scripts/split_tuples.py signal VBF
python3 scripts/split_tuples.py data VBF