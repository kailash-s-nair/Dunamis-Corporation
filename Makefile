PYTHON = python3 -m
CHECK_PIP = ensurepip
INSTALL_REQUIREMENTS = pip install -r requirements.txt
RUN_FRONTEND = frontendgui

setup: requirements.txt
	$(PYTHON) $(CHECK_PIP)
	$(PYTHON) $(INSTALL_REQUIREMENTS)
run: Frontend, backend
	$(PYTHON) $(RUN_FRONTEND)