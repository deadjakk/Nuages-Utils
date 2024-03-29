#!/bin/bash
echo "running kali pre-installation actions..."
sudo apt update -y
sudo apt install -y npm 
wget http://http.us.debian.org/debian/pool/main/c/curl/libcurl3_7.52.1-5+deb9u9_amd64.deb
sudo dpkg -x libcurl3*.deb /tmp/
sudo cp /tmp/usr/lib/x86_64-linux-gnu/libcurl.so.3 /usr/lib

git clone https://github.com/p3nt4/Nuages/
wget https://raw.githubusercontent.com/deadjakk/Nuages-Utils/master/testnuages.py
cd Nuages

echo "installing mongodb"
wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-debian92-4.2.0.tgz
tar zxvf *.tgz
cd mongo*/
sudo cp bin/* /usr/bin
echo "mongodb installed"
sudo mkdir /var/log/mongodb
sudo mkdir /data/db -p
sudo touch /var/log/mongodb/mongod.log
sudo env LD_PRELOAD=/usr/lib/libcurl.so.3 mongod --dbpath /data/db --logpath /var/log/mongodb/mongod.log &
echo "mongod should be started on 27017"

cd ../Server
export NODE_PATH=`pwd`/node_modules/
sudo npm install feathers-cli
sudo npm install fsevents
printf "\n\nInstalling local npm dependencies\n";
npm install serve-favicon
npm install winston
npm install compression
npm install helmet
npm install

if [ $? -eq 0 ]; then
    echo "Done!"
else
    echo "FAILED to install npm dependencies !"
    exit 1
fi
sudo bash setup.sh
sed s/\"localhost\"/\"0.0.0.0\"/g config/*.json -i
cat > runnit.sh <<EOF
#!/bin/bash
sudo env LD_PRELOAD=/usr/lib/libcurl.so.3 mongod --dbpath /data/db --logpath /var/log/mongodb/mongod.log &
export NODE_ENV=production
node src/
EOF
cp -r ../Clients/Nuages_WebCli/ public/
echo "to start, use runnit.sh in the `pwd`/Nuages/Server directory "
echo "you can connect to the server via http://`curl -s ifconfig.me`:3030/Nuages_WebCli"
echo "test the server using testnuages.py -i `curl -s ifconfig.me` "

