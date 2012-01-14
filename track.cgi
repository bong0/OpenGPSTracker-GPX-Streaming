#!/bin/bash
# OpenGPSTracker Streaming Query Processor
# Author: bongo 2012
# Thanks to @schiermi for the clever query processing code
# 
# Sample query: track.cgi?debug=1&lat=27.78684600&lon=14.6376800&tid=42&alt=20.6999969482422&acc=5.0&spd=1.75&bear=236.7&tim=1326480108000
#                                                                                                                         ^ in fact, this value never gets as accurate as s
####### USER CONSTANTS #######
HOME=/home/${USER}
TRACKDIR=$HOME/tracks
GPSBABEL_BIN=$(which gpsbabel)
DEBUG=0
##############################
printf "Content-Type: text/plain\n\n"

if test -z $GPSBABEL_BIN; then
  echo "[-] FATAL: Could not find gpsbabel! Are you sure it's installed and in PATH?"
  exit 1
fi 

ucsv_header="" #specifies the field order
ucsv_data="" #the actual csv data
printf "Content-Type: text/plain\n\n"

for param in ${QUERY_STRING//&/ } #loop through query replacing & with SPC
do
  case $param in
    lat=*)
      lat=${param##*=} #extract value by cutting key 
      lat=${lat//[^0-9\.]/} #strip invalid characters
      if test -n $lat; then
        ucsv_header=${ucsv_header}"Latitude,"
        ucsv_data=${ucsv_data}${lat}","
      fi
      if [[ $DEBUG -eq 1 ]]; then echo "Latitude: ${lat}"; fi
    ;;
    lon=*)
      lon=${param##*=}
      lon=${lon//[^0-9\.]/} #strip invalid characters
      if test -n $lon; then
        ucsv_header=${ucsv_header}"Longitude,"
        ucsv_data=${ucsv_data}${lon}","
      fi
      if [[ $DEBUG -eq 1 ]]; then echo "Longitude: ${lon}"; fi
    ;;
    tid=*)
      tid=${param##*=}
      tid=${tid//[^0-9]/} #strip invalid characters
      #trackid is only used to set the trackname, therefore it isn't included in the waypoint data (ucsv)
      if [[ $DEBUG -eq 1 ]]; then echo "TrackId: ${tid}"; fi
    ;;
    alt=*)
      alt=${param##*=}
      alt=${alt//[^0-9\.]/} #strip invalid characters
      if test -n $alt; then
        ucsv_header=${ucsv_header}"Altitude,"
        ucsv_data=${ucsv_data}${alt}","
      fi
      if [[ $DEBUG -eq 1 ]]; then echo "Altitude: ${alt}"; fi
    ;;
    acc=*)
      acc=${param##*=}
      acc=${acc//[^0-9\.]/} #strip invalid characters
      if test -n $acc; then
        ucsv_header=${ucsv_header}"pdop,"
        ucsv_data=${ucsv_data}${acc}","
      fi
      if [[ $DEBUG -eq 1 ]]; then echo "Accuracy: ${acc}"; fi
    ;;
    spd=*)
      spd=${param##*=}
      spd=${spd//[^0-9\.]/} #strip invalid characters
      if test -n $spd; then
        ucsv_header=${ucsv_header}"Speed,"
        ucsv_data=${ucsv_data}${spd}","
      fi
      if [[ $DEBUG -eq 1 ]]; then echo "Speed: ${spd}"; fi
    ;;
    bear=*)
      bear==${param##*=}
      bear=${bear//[^0-9\.]/} #strip invalid characters
      if test -n $bear; then
        ucsv_header=${ucsv_header}"Heading,"
        ucsv_data=${ucsv_data}${bear}","
      fi
      if [[ $DEBUG -eq 1 ]]; then echo "Bearing (Heading of Compass): ${bear}"; fi
    ;;
    tim=*)
      tim=${param##*=}
      tim=${tim//[^0-9]/} #strip invalid characters
      tim=${tim%000} #strip the three trailing zeroes
      tim=$(date -d "@${tim}" "+%H:%M:%S") #convert time to hh:mm:ss
      if test -n $tim; then
        ucsv_header=${ucsv_header}"Time,"
        ucsv_data=${ucsv_data}${tim}","
      fi
      if [[ $DEBUG -eq 1 ]]; then echo "Time: ${tim}"; fi
    ;;
    debug=1)
      DEBUG=1
      echo "debugging enabled"
    ;;
  esac
done

#generate date
date=$(date "+%Y/%m/%d")
ucsv_header=${ucsv_header}"Date"
ucsv_data=${ucsv_data}${date}

if $( test -z $lat || test -z $lon ); then
  if [[ $DEBUG -eq 1 ]]; then
    echo "Error, you haven't supplied at least one of _mandatory_ arguments Longitude and Latitude!";
  else
    echo "Error"
  fi
  exit 1
fi
  
if [[ $DEBUG -eq 1 ]]; then printf "UCSV Header: ${ucsv_header}\nUCSV Data: ${ucsv_data}\n"; fi

if [ ! -f $TRACKDIR/${tid}.gpx ]; then
  if [[ $DEBUG -eq 1 ]]; then echo "creating new file..."; fi
  printf ${ucsv_header}"\n"${ucsv_data} | $GPSBABEL_BIN -t -i unicsv,format=y -f - -x track,merge,title=$tid -o gpx -F "${TRACKDIR}/${tid}.gpx" 2>&1 #>/dev/null
  chmod og= ${TRACKDIR}/${tid}.gpx
else
  if [[ $DEBUG -eq 1 ]]; then echo "appending..."; fi
  printf ${ucsv_header}"\n"${ucsv_data} | $GPSBABEL_BIN -t -i gpx -f "${TRACKDIR}/${tid}.gpx" -i unicsv,format=y -f - -x track,merge,title=$tid -o gpx -F "${TRACKDIR}/${tid}.gpx" 2>&1 #>/dev/null
fi

# printf "\n"
if [[ $DEBUG -eq 1 ]];
 then
  echo "wrote waypoint to file";
 else
  echo "OK"
fi
