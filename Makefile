all:
	jupyter nbconvert --to script alice.ipynb
	mv alice.py lscealice.py
