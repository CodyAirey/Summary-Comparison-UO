eval "$(conda shell.bash hook)"


files=("compare_books.py" "compare_sections.py" "compare_sections_to_books.py")
datasets=("fixed" "adjusted")

function run_comparisons {
  python_file="$1"
  dataset="$2"
  
  conda activate rouge
  python $python_file -m rouge-1n -s all -d $dataset -o rouge-1nsmall
  python $python_file -m rouge-2n -s all -d $dataset -o rouge-2nsmall
  python $python_file -m rouge-l -s all -d $dataset -o rouge-lsmall
  conda deactivate
  
  conda activate bleu
  python $python_file -m bleu -s all -d $dataset -o bleusmall
  conda deactivate
  
  conda activate chrf
  python $python_file -m chrf -s all -d $dataset -o chrfsmall
  conda deactivate
  
  conda activate meteor
  python $python_file -m meteor -s all -d $dataset -o meteorsmall
  conda deactivate
  
#   conda activate moverscore
#   python $python_file -m moverscore -s all -d $dataset -o moverscoresmall
#   conda deactivate
  
#   conda activate bert
#   python $python_file -m bert -s all -d $dataset -o bertsmall
#   python $python_file -m bertscore -s all -d $dataset -o bertscoresmall
#   conda deactivate
  
#   conda activate bart
#   python $python_file -m bartscore -s all -d $dataset -o bartscoresmall
#   conda deactivate
}

for d in "${datasets[@]}"
do
    for f in "${files[@]}"
    do
        run_comparisons "$f" "$d"
    done
done