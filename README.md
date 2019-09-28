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

## installnuageskali.sh
Like the title implies, installs the Nuages C2 server on a base kali image
will try to keep this updated with the current kali stage however for 
the time being this is for my current dev environment. 
However may aid individuals in installing Nuages on their within their own environment
Has some redundancies but is currently working at the time of this writing
<br>
simply run the script as root 
