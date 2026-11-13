PY ?= python3

.PHONY: test orders billing tools web contract check run

# Everything CI runs.
test: orders billing tools web

orders:
	cd services/orders && $(PY) -m pytest -q

billing:
	cd services/billing && $(PY) -m pytest -q

tools:
	$(PY) -m pytest -q tools

web:
	cd services/web && npm ci --silent && npm run -s gen:check && npm run -s typecheck && npm run -s test

# Writes the contract from the service and the types of the web client from the contract.
contract:
	$(PY) tools/contract.py export
	cd services/web && npm run -s gen

# The contract is what the service serves, and every consumer reads fields it has.
check:
	$(PY) tools/contract.py snapshot
	$(PY) tools/contract.py consumers

# The orders service on http://127.0.0.1:8000, with the interactive API page at /docs.
run:
	cd services/orders && $(PY) -m uvicorn --factory orders.app:create_app --reload
