# Primitive display for weather station

Manual used:
- https://raspi.tv/2015/how-to-drive-a-7-segment-display-directly-on-raspberry-pi-in-python

# Pins

3461AS Pins-to-GPIO mapping:

- 1 -> 17 : Segment - Bottom left
- 2 -> 27 : Segment - Bottom
- 3 -> 22 : Segment - Dot
- 4 -> 10 : Segment - Bottom right 
- 5 -> 9  : Segment - Middle
- 6 -> 11 : Digit - 4
- 7 -> 18 : Segment - Top right
- 8 -> 23 : Digit - 3
- 9 -> 24 : Digit - 2
- 10 -> 25 : Segment - Top
- 11 -> 8 : Segment - Top left
- 12 -> 7 : Digit - 1

All Segments reqiure resistors. I've used 330 Ohm. Less is also fine.

# Deploy

    ansible-playbook -i ../infrastructure/ansible/pi install.yml
    
# Possible further improvements

1. Button to switch display modes