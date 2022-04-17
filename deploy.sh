#!/bin/bash

set -u
set -e

ssh ubuntu@54.252.220.59 << EOF
cd ~/codequest
sudo docker-compose down
sudo rm -rf *
EOF

rsync -azP --exclude-from='deploy_exclude.txt' . ubuntu@54.252.220.59:~/codequest

ssh ubuntu@54.252.220.59 << EOF
cd ~/codequest
sudo docker-compose up --detach
EOF
