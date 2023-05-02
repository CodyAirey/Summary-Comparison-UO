eval "$(conda shell.bash hook)"


files=("compare_books.py" "compare_sections.py" "compare_sections_to_books.py")
datasets=("fixed" "adjusted")

function run_comparisons {
  python_file="$1"
  dataset="$2"

  conda activate bert2
  python $python_file -m bertscore -s all -d $dataset -o bertscore
  conda deactivate
  
  }

for d in "${datasets[@]}"
do
    for f in "${files[@]}"
    do
        run_comparisons "$f" "$d"
    done
done