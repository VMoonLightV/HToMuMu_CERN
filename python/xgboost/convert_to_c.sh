
mkdir -p models/cpp


for model in \
mumu_vs_bkg

do
	python raw_to_cpp.py --xgb_dump=models/model_${model}.txt --num_classes=1 --func_name=${model}
	mv ${model}.h models/cpp/
done
