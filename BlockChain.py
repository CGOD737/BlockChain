import hashlib
import time
import requests


from flask import Flask, jsonify, request
from urllib.parse import urlparse

##Begininng of Block class
class Block:

	def __init__(self, index, proof_no, prev_hash, data, timestamp=None):
		self.index = index
		self.proof_no = proof_no
		self.prev_hash = prev_hash
		self.data = data
		self.timestamp = timestamp or time.time()

	@property
	def calc_hash(self):

		block_of_string = "{}{}{}{}{}".format(self.index, self.proof_no, self.prev_hash, self.data, self.timestamp)

		return hashlib.sha256(block_of_string.encode()).hexdigest()

	def __repr__(self):
		return "{} - {} - {} - {} - {}".format(self.index, self.proof_no, self.prev_hash, self.data, self.timestamp)

##Begininng of Block Chain class
class BlockChain:

	def __init__(self):
		self.chain = []
		self.current_data = []
		self.nodes = set()
		self.construct_genesis()

	##Constructs the initial block
	def construct_genesis(self):
		self.construct_block(proof_no=0, prev_hash = 0)
	
	##Creates a New Block in the Chain
	def construct_block(self, proof_no, prev_hash):
		block = Block(index = len(self.chain), proof_no = proof_no, prev_hash = prev_hash, data = self.current_data)
		self.current_data = []

		self.chain.append(block)
		return block

	##checks validity of the chain to prevent tampering
	@staticmethod
	def check_validity(self, chain):

		prev_block = chain[0]
		current_index = 1

		while current_index < len(chain):

			block = chain[current_index]

			if prev_block.index + 1 != block.index:
				return False

			elif prev_block.calc_hash != block.prev_hash:
				return False

			elif  not BlockChain.verifying_proof(block.proof_no, prev_block.proof_no):
				return False

			elif block.timestamp <= prev_block.timestamp:
				return False

			last_block = block
			current_index += 1

		return True

	#Creates the data for the Transaction
	def new_data(self, sender, recipient, quantity):
		self.current_data.append({'sender': sender, 'recipient' : recipient, 'quantity' : quantity})
		return self.latest_block.index + 1

	# Algorithm which is the goal to find a number p' such that hash(pp') contains leading 4 zeros
	# Where p is the previous proof, and p' is the new proof.
	@staticmethod
	def proof_of_work(last_proof):
	    proof_no = 0
	    while BlockChain.verifying_proof(proof_no, last_proof) is False:
	        proof_no += 1

	    return proof_no

	def verifying_proof(last_proof, proof):
		
		guess = f'{last_proof}{proof}'.encode()
		guess_hash = hashlib.sha256(guess).hexdigest()
		return guess_hash[:4] == "0000"   

	@property
	def latest_block(self):
		return self.chain[-1]

	def block_mining(self, details_miner):

		self.new_data(sender='0', reciever = details_miner, quantity = 1)

		last_block = self.latest_block

		last_proof_no = last_block.proof_no
		proof_no = self.proof_of_work(last_proof_no)

		last_hash = last_block.calc_hash
		block = self.construct_block(proof_no, last_hash)

		return vars(block)

	def create_node(self, address):
		parsed_url = urlparse(address)
		self.nodes.add(parsed_url.netloc)
		return True

	#Static Method to return the Block Object
	@staticmethod
	def obtain_block_object(block_data):
		return Block( block_data['index'], block_data['proof_no'], block_data['prev_hash'], block_data['data'], timestamp=block_data['timestamp'])

	#Solves Conflicts by replacing our chain with the longest one in the network.
	#returns True if chain was replaced false otherwise.
	def resolve_conflict(self):

		neighbors = self.nodes
		new_chain = None

		max = len(self.chain)

		#grab and verify the chain from all nodes in the network
		for node in neighbors:
			response = requests.get(f'http://{node}/chain')

			if response.status_code == 200:
				length = response.json()['length']
				chain = response.json()['chain']

				if length > max and self.check_validity(self, chain):
					max_length = length
					new_chain = chain

		#Replace the chain if we discovered a new chain that is longer than ours and is also valid.
		if new_chain:
			self.chain = new_chain
			return True

		return False

