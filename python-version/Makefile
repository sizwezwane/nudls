
.PHONY: run test install clean

install:
	pip install -r requirements.txt

run:
	.venv/bin/uvicorn app.main:app --reload

test:
	TESTING=1 .venv/bin/pytest tests/

clean:
	rm -rf .venv
	rm -rf __pycache__
	rm -rf .pytest_cache
