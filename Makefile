.PHONY: paper-images check-paper-images

paper-images:
	python3 scripts/convert-paper-images.py

check-paper-images:
	python3 scripts/convert-paper-images.py --check
