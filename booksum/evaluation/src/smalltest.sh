eval "$(conda shell.bash hook)"

conda activate moverscore
python compare_sections.py -m moverscore -s all -d fixed -o moverscoresmall
conda deactivate