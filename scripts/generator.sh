#!/bin/bash

foods=( burger burrito lobster beer )

cd ../code
for food in ${foods[@]}
do
    python process_reviews.py $food 0 199 --save_results ../static/test_data/sample_data.json
done
cd ../scripts