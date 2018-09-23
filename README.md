# My PI Projects

All projects are provisioned by Ansible.

Before installation of any project make sure that you've 
provisioned your PI with common modules:

    ./setup_pi.sh  
    
# Projects

1. [Weather station](weather-station): primitive home weather 
station on DH11

    Measures temperature and humidity and stores them in sqlite
    database + to GCP StackDriver
    
2. [Weather station display](weather-station-display): 
8 segment 4 digit display

    Display which uses [weather station](weather-station) API 
    to display temperature, humidity and current time
    
3. [Power button](power-button): button to power up/down PI, with on-off 
indicator