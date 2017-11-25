#!/bin/bash

echo $1, $2, $3, $4

#check $1
list="p00 p01 p02 p03 p04 p05 p06 p07 p08 p09 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20"

if ! [[ $list =~ (^| )$1($| ) ]]; then
  echo "error: participant_id [$1] does not exist"
  echo "Usage: ./startStudy.sh <participant_id> <experimenter_name> <study_phase> <record_option>"
  echo "./startStudy.sh p000 sam experiment record"
  exit
fi

#check $2
list="sam huili mike safinah"
if ! [[ $list =~ (^| )$2($| ) ]]; then
  echo "error: experimenter [$2] does not exist"
  echo "Usage: ./startStudy.sh <participant_id> <experimenter_name> <study_phase> <record_option>"
  echo "./startStudy.sh p01 sam experiment record"
  exit
fi

#check $3
list="practice experiment posttest"
if ! [[ $list =~ (^| )$3($| ) ]]; then
  echo "error: study phase [$3] does not exist"
  echo "Usage: ./startStudy.sh <participant_id> <experimenter_name> <study_phase> <record_option>"
  echo "./startStudy.sh p01 sam experiment record"
  exit
fi

#check $4
list="record no-record"
if ! [[ $list =~ (^| )$4($| ) ]]; then
  echo "error: record option [$4] does not exist"
  echo "Usage: ./startStudy.sh <participant_id> <experimenter_name> <study_phase> <record_option>"
  echo "./startStudy.sh p01 sam experiment record"
  exit
fi

mkdir -p log
mkdir -p rosbag


gnome-terminal --geometry 40x120+0+0 --title ">>>iSpy Game Study MAIN<<<" -e "./scripts/run_ispy.sh $1 $2"

if [ $4 = 'record' ]; then
  ./scripts/rosbag_record.sh $1 $2 $3
fi