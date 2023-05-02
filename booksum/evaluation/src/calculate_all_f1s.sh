eval "$(conda shell.bash hook)"


files=("compare_books.py" "compare_sections.py" "compare_sections_to_books.py")
datasets=("fixed" "adjusted")

function run_comparisons {
  python_file="$1"
  dataset="$2"
  
  conda activate rouge
  python $python_file -m rouge-1n -s all -d $dataset -o rouge-1n
  python $python_file -m rouge-2n -s all -d $dataset -o rouge-2n
  python $python_file -m rouge-l -s all -d $dataset -o rouge-l
  conda deactivate
  
  conda activate bleu
  python $python_file -m bleu -s all -d $dataset -o bleu
  conda deactivate
  
  conda activate chrf
  python $python_file -m chrf -s all -d $dataset -o chrf
  conda deactivate
  
  conda activate meteor
  python $python_file -m meteor -s all -d $dataset -o meteor
  conda deactivate

  conda activate bart
  python $python_file -m bartscore -s all -d $dataset -o bartscore
  conda deactivate

  conda activate bert
  python $python_file -m bert -s all -d $dataset -o bert
  python $python_file -m bertscore -s all -d $dataset -o bertscore
  conda deactivate

  # conda deactivate
  # conda activate moverscore
  # python $python_file -m moverscore -s all -d $dataset -o moverscore
  
}

for d in "${datasets[@]}"
do
    for f in "${files[@]}"
    do
        run_comparisons "$f" "$d"
    done
done