#! /bin/sh

### BEGIN INIT INFO
# Provides:          station.py
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
### END INIT INFO

# If you want a command to always run, put it here
cd /home/pi/weather/

# Carry out specific functions when asked to by the system
case "$1" in
  start)
    echo "Starting station.py"
    pipenv run python station.py run &
    echo "Started"
    ;;
  stop)
    echo "Stopping station.py"
    pkill -f /home/pi/weather/station.py
    echo "Stopped"
    ;;
  report)
    pipenv run python station.py report
    ;;
  report-temperature)
    pipenv run python station.py report-temperature
    ;;
  report-humidity)
    pipenv run python station.py report-humidity
    ;;
  *)
    echo "Usage: /etc/init.d/station.sh {start|stop|report|report-humidity|report-temperature}"
    exit 1
    ;;
esac

exit 0
