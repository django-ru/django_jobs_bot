deps:
	pip-compile requirements.in --rebuild --no-annotate
	pip-compile requirements-dev.in --rebuild --no-annotate
