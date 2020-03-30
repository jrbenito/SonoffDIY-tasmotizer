#!/usr/bin/env python3
# encoding: utf-8
"""
fake-registration-server.py
Created by nano on 2018-11-22.
Copyright (c) 2018 VTRUST. All rights reserved.
"""

import tornado.web
import tornado.locks
from tornado.options import define, options, parse_command_line

define("port", default=80, help="run on the given port", type=int)
define("addr", default="192.168.254.1", help="run on the given ip", type=str)
define("debug", default=True, help="run in debug mode")

import os
import signal

def exit_cleanly(signal, frame):
	print("Received SIGINT, exiting...")
	exit(0)

signal.signal(signal.SIGINT, exit_cleanly)

from base64 import b64encode
import hashlib
import hmac
import binascii

from time import time
timestamp = lambda : int(time())

class FilesHandler(tornado.web.StaticFileHandler):
	def parse_url_path(self, url_path):
		if not url_path or url_path.endswith('/'):
			url_path = url_path + str('index.html')
		return url_path

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.write("You are connected to vtrust-flash")


def main():
	parse_command_line()
	app = tornado.web.Application(
		[
			(r"/", MainHandler),
			('/files/(.*)', FilesHandler, {'path': str('../files/')}),
			(r".*", tornado.web.RedirectHandler, {"url": "http://" + options.addr + "/", "permanent": False}),
		],
		debug=options.debug,
	)
	try:
		app.listen(options.port, options.addr)
		print("Listening on " + options.addr + ":" + str(options.port))
		tornado.ioloop.IOLoop.current().start()
	except OSError as err:
		print("Could not start server on port " + str(options.port))
		if err.errno == 98: # EADDRINUSE
			print("Close the process on this port and try again")
		else:
			print(err)


if __name__ == "__main__":
	main()
