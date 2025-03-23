# Define variables
SERVER_FILE = server.js
NODE = node
NPM = npm
BROWSER = start http://localhost:3000

# Install dependencies
install:
	$(NPM) install express mysql2 cors

# Run the server
run:
	$(NODE) $(SERVER_FILE)

# Open in browser
open:
	$(BROWSER)

# Start everything (install, run, open)
start: install run open
