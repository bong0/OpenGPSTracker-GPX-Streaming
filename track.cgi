#!/bin/bash
# OpenGPSTracker Streaming Query Processor
# Author: bongo 2012
# Thanks to @schiermi for the clever query processing code
# 
# Sample query: track.cgi?debug=1&lat=27.78684600&lon=14.6376800&tid=42&alt=20.6999969482422&acc=5.0&spd=1.75&bear=236.7&tim=1326480108000
#                                                                                                                         ^ in fact, this value never gets as accurate as ms
####### USER CONSTANTS #######
HOME=/home/${USER}
TRACKDIR=$HOME/tracks
GPSBABEL_BIN=$HOME/.toast/armed/bin/gpsbabel
DEBUG=0
##############################
printf "Content-Type: text/plain\n\n"

for param in ${QUERY_STRING//&/ } #loop through query replacing & with SPC
do
  case $param in
    lat=*)
      lat=${param##*=} #extract value by cutting key 
      if [[ $DEBUG -eq 1 ]]; then echo "Latitude: ${lat}"; fi
    ;;
    lon=*)
      lon=${param##*=}
      if [[ $DEBUG -eq 1 ]]; then echo "Longitude: ${lon}"; fi
    ;;
    tid=*)
      tid=${param##*=}
      if [[ $DEBUG -eq 1 ]]; then echo "TrackId: ${tid}"; fi
    ;;
    alt=*)
      alt=${param##*=}
      if [[ $DEBUG -eq 1 ]]; then echo "Altitude: ${alt}"; fi
    ;;
    acc=*)
      acc=${param##*=}
      if [[ $DEBUG -eq 1 ]]; then echo "Accuracy: ${acc}"; fi
    ;;
    spd=*)
      spd=${param##*=}
      if [[ $DEBUG -eq 1 ]]; then echo "Speed: ${spd}"; fi
    ;;
    bear=*)
      bear==${param##*=}
      if [[ $DEBUG -eq 1 ]]; then echo "Bearing: ${bear}"; fi
    ;;
    tim=*)
      tim=${param##*=}
      if [[ $DEBUG -eq 1 ]]; then echo "Time: ${tim}"; fi
    ;;
    debug=1)
      DEBUG=1
      echo "debugging enabled"
    ;;
  esac
done

if [ ! -f $TRACKDIR/${tid}.gpx ]; then
  if [[ $DEBUG -eq 1 ]]; then echo "creating new file..."; fi
  printf "$lat","$lon" | $GPSBABEL_BIN -t -i csv -f - -x track,merge,title=$tid -o gpx -F "${TRACKDIR}/${tid}.gpx" #2>&1 >/dev/null
  chmod og= ${TRACKDIR}/${tid}.gpx
else
  if [[ $DEBUG -eq 1 ]]; then echo "appending..."; fi
  printf "$lat","$lon" | $GPSBABEL_BIN -t -i gpx -f "${TRACKDIR}/${tid}.gpx" -i csv -f - -o gpx -F "${TRACKDIR}/${tid}.gpx" #1>/dev/null #2>&1
fi

# printf "\n"
if [[ $DEBUG -eq 1 ]];
 then
  echo "wrote waypoint to file";
 else
  echo "OK"
fi
