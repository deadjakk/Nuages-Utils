# Nuages-Jakk
Custom handler for the https://github.com/p3nt4/Nuages/ C2 server 
A work in progress but as of now allows a very simple layer over the web API to allow for simpler input
to be translated into the desired Nuages protocol as so as to prevent having to implememnt/use web libraries in implants

## Documentation
This will be added at a later date
<br>
Type edit the Handler.py file to set configurations then run the Handler with:
```
python Handler.py 
```

## testnuages.py
Allows you to register an implant to test the server after installing the server
<br>
Example command:
```
python testnuages.py -i 127.0.0.1 -p 3090
```
