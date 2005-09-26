# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
NanoHiveUtils.py

$Id$

History:

'''
__author__ = "Brian"

# Version 2

import socket


class NH_Connection:
	"A sockets connection to a Nano-Hive instance."
	
	
	def connect(self, hostIP, port, serverTimeout, clientTimeout):
		"""
		Connects to the specified N-H instance.
		
		Parameters:
			hostIP
				The IP address of the N-H host
			port
				The port listened to by the SocketsControl plugin of the N-H host
			serverTimeout
				A float specifying how long, in seconds, to give when reading
				from, and writing to, N-H
			clientTimeout
				A float specifying the timeout period of the SocketsControl
				plugin of the N-H host. Not implemented yet, but this will
				keep the N-H connection alive with "ping" commands
				
		Returns:
			success indicator
				A one if the N-H instance was successfully connected to, or a
				zero if an error occurred and connection failed
			error message
				If connection failed, describes the problem
		"""
		try:
			self.connectionHandle = \
				socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.connectionHandle.connect((hostIP, port))
			self.connectionHandle.settimeout(serverTimeout)
			
		except socket.error, errorMessage:
			return 0, errorMessage
			
		return 1, ""
		
		
	def close(self):
		"""
		Closes the connection to the N-H instance.
		"""
		self.connectionHandle.close()
		
		
	def sendCommand(self, command):
		"""
		Sends a command to the N-H instance and returns the response.
		
		Parameters:
			command
				The command to send to the N-H instance
				
		Returns:
			success indicator
				A one if the command was successfully sent and a response was
				received
			response or error message
				If all was successful, the encoded N-H instance response, or a
				description of the error if unsuccessful. The encoded response
				can be decoded with the
				Nano-Hive/data/local/en_resultCodes.txt file
		"""
			
		# Send command
		success = 1
		try:
			self.connectionHandle.send(command)

		except socket.error, errorMessage:
			success = 0
		
		# Read response length
		if success:
			try:
				responseLengthChars = self.connectionHandle.recv(4)
				
			except socket.error, errorMessage:
				success = 0
				
		if success:
			responseLength = ord(responseLengthChars[0])
			responseLength |= ord(responseLengthChars[1]) << 8
			responseLength |= ord(responseLengthChars[2]) << 16
			responseLength |= ord(responseLengthChars[3]) << 24;

			# Read response
			try:
				response = self.connectionHandle.recv(responseLength)

			except socket.error, errorMessage:
				success = 0

		if success:
			return 1, response
			
		else:
			return 0, errorMessage