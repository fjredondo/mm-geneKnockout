#!/bin/bash
#
#SBATCH -p hpc-bio-ampere
#SBATCH --chdir=/home/alumno24
#SBATCH -J sb_mm_24
#SBATCH --output=./sbatch_output/%u-%j.out
#SBATCH --error=./sbatch_output/%u-%j.err
#SBATCH --mail-type=NONE #END/START/NONE
#SBATCH --mail-user=MAIL@um.es
#SBATCH --cpus-per-task=4
#SBATCH --time=00:30:00


# @author: fjredondo
# @description: Conversiones en modelos para mieloma multiple

# execution Operations
var=$(date +'%Y/%m/%d %r')
echo "Job start at $var"

module load cplex/12.10

file_name=${SLURM_JOB_USER}-${SLURM_JOB_ID}

echo std_output: $file_name.out
echo err_output: $file_name.err

# declare -a dir_model=('./models/mm/')

declare -a dir_model=('./models/generic/' './models/mm/' './models/tissue/')


for i in "${dir_model[@]}"
do

echo ${i}data


rm -rf ${i}data
rm -rf ${i}gcs

if [ ! -d ${i}data ]
then
mkdir ${i}data
fi

if [ ! -d ${i}gcs ]
then
mkdir ${i}gcs
fi



echo "Converting to binary data ..."

for filepath in ${i}*.*
do

if [ -f $filepath ]
then

	filename=$(basename "$filepath")
	filename="${i}data/${filename%.*}.dat"

	echo Processing ${filepath} to ${filename} ...
	python3.6 modelToBinary.py $filepath $filename &
	echo

fi


done
time wait

echo "Converting data to gcs"

for filepath in ${i}data/*.dat
do

if [ -f $filepath ]
then
	filename=$(basename "$filepath")
	filename="${i}gcs/${filename%.*}.gcs"

	echo Processing ${filepath} to ${filename} ...
	python3.6 gMCSForBiomass.py $filepath $filename &

fi


done
time wait


done

echo Processing gKnockoutTargets.py ...
python3.6 gKnockoutTargets.py


module unload cplex/12.10

var=$(date +'%Y/%m/%d %r')
echo "Job has ended at $var"

