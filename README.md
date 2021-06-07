# BlockChain

## Instructions

#### Dependencies
(Flask, hashlib, time, request, jsonify, urllib.parse, uuid, pipenv)

#### Running Instructions
  
  * In the directory you downloaded the repository, run the command "pipenv run python server.py -p [port_number]"
  * Using Postman, copy and paste the url into the top box
  * Add the following commands to the end of the url to test
      *   /mine : mines one block of the chain [GET] 
      *   /new/transaction : requires the format of {"sender" : "sender_address , "recipient" : "recipient_address", "quantity": number of blocks } [POST]
      *   /nodes/register : requires the format of { node: "address } [POST]
  
  
