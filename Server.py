#Flask Server Written to host BlockChain

import requests
from flask import Flask, jsonify, request
import BlockChain
from urllib.parse import urlparse
from uuid import uuid4

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-','')

#Instantiate the object
blockchain = BlockChain.BlockChain()

#Mining Sequences
@app.route('/mine', methods=['GET'])
def mine():
	print(blockchain.chain)
	last_block = blockchain.latest_block
	last_proof_no = last_block.proof_no
	proof_no = blockchain.proof_of_work(last_proof_no)

	blockchain.new_data(
	    sender = "0",  #it implies that this node has created a new block
	    recipient = node_identifier,  #let's send some coins
	    quantity = 1,  #creating a new block (or identifying the proof number) is awarded with 1
	)

	print("Mined 1 Block of Gooch Coin")

	last_hash = last_block.calc_hash
	block = blockchain.construct_block(proof_no, last_hash)

	#create a message response to send back to the user
	response = {
   	    'message': "New Block Forged",
        'index': block['index'],
        'data': block['data'],
        'proof': block['proof_no'],
        'previous_hash': block['prev_hash'],
    }
	return jsonify(response), 200

@app.route('/transaction/new', methods=['POST'])

def new_data():
	values = request.get_json()
	required = ['sender' , 'recipient', 'quantity']
	if not all(k in values for k in required):
		return 'Missing values', 400

	index = blockchain.new_data(values['sender'], values['recipient'], values['quantity'])

	response = {'message': f'Transaction will be added to Block {index}'}

	return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
	response = { 'chain': blockchain.chain, 'length': len(blockchain.chain),}
	return jsonify(response), 200


#App portion to register individual Nodes
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
	values = request.get_json()

	nodes = values.get('nodes')
	if nodes is None:
		return "Error: Please supply a valid list of nodes", 400

	for node in nodes:
		blockchain.register_node(node)

	response = { 'message': 'New nodes have been added', 'total_nodes' : list(blockchain.nodes),}

	return jsonify(response), 201

#App portion to resolve any conflicts
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)