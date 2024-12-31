#!/bin/bash

# Set the energy meter's constant here
CONST=2500

parse_packet() {
  packet=""
  capturing=""
  count=0
  
  while read line
  do
    count=$[count + 1]
    if [ "$capturing" ]; then
      if [[ $line =~ ^[0-9a-fA-F]{2}\ [0-9a-fA-F] ]]; then
        packet="$packet $line"
      else
        #echo RAW: $packet
        cnt=0
        dcnt=0
        bl=0
        bt=0
        bc=0
        np=""
        mp=""

        DTYPE=0

        for i in $packet; do
            if [[ "$cnt" -eq "13" ]]; then
              tl=`echo "ibase=16; $i"|bc`
              #echo TL $tl
            fi
            if [[ "$cnt" -gt "13" ]]; then
              np+=$i
              if [[ "$bl" -eq "0" ]]; then
                if [[ "$DTYPE" -eq "130" ]]; then # iNode Energy Meter identification
                  #echo DTYPE

                  #CONST
                  HEX=`echo $mp | awk '{ print $12$11 }'`
                  DEC=`echo "ibase=16; $HEX"|bc`
                  #CONST=2500
                  #echo CONST $CONST

                  #WATTS
                  HEX=`echo $mp | awk '{ print $6$5 }'`
                  DEC=`echo "ibase=16; $HEX"|bc`
                  #echo MINUTE POWER $DEC
                  CALC=`echo $DEC $CONST | awk '{ kw=($1/$2*60*1000); printf"%0.0f\n",  kw  }'`

                  #IMPULSES
                  HEXIM=`echo $mp  | awk '{ print $10$9$8$7 }'`
                  #echo TOTAL POWER $HEXIM
                  DECIM=`echo "ibase=16; $HEXIM"|bc`
                  #echo TOTAL POWER $DECIM
                  CALCIM=`echo $DECIM $CONST | awk '{ kWh=($1/$2); printf"%0.3f\n", kWh  }'`
                
                  # Returning data: $DECIM - total number of impulses, $DEC - number of impulses from last 1 minute
                  echo "$DECIM $DEC" 
                  
                  exit 0
                  
                  DTYPE=0
                fi

                if [[ "$dcnt" -lt "$tl" ]]; then
                  bl=`echo "ibase=16; $i"|bc`
                  bcnt=0
                  #echo BL $bl
                  mp=$i" "
                fi
              else
                if [[ "$bcnt" -eq "0" ]]; then
                  bc=`echo "ibase=16; $i"|bc`
                  #echo BC $bc
                fi
                if [[ "$bc" -eq "255" ]]; then
                  if [[ "$bcnt" -eq "2" ]]; then
                    DTYPE=`echo "ibase=16; $i"|bc`

                    #echo DTYPE $DTYPE
                  fi
                fi

                bcnt=$bcnt+1

                bl=$bl-1

                mp+=$i" "
              fi
              dcnt=$dcnt+1
            fi
            cnt=$cnt+1
        done

        capturing=""
        packet=""
      fi
    fi

    if [ ! "$capturing" ]; then
      if [[ $line =~ ^\> ]]; then
        packet=`echo $line | sed 's/^>.\(.*$\)/\1/'`
        capturing=1
      fi
    fi
  done
}

start_bluetooth_scanning() {
  hcitool lescan --duplicates --passive 1>/dev/null
}

if [ "$1" == "parse" ]; then
  parse_packet
else
  start_bluetooth_scanning &
  sleep 2  # Adjust the sleep duration as needed to allow time for scanning to start

  if [ "$(pidof hcitool)" ]; then
    hcidump --raw | ./"$0" parse "$1"
  fi
fi


