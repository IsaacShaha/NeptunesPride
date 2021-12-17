SHELL=/bin/bash

Default: GenerateTree ViewTree

GenerateTree:
	source ~/anaconda3/etc/profile.d/conda.sh && \
	conda activate NeptunesPride && \
	python LocalTree.py && \
	conda deactivate

ViewTree:
	xdg-open LatestMap.png >/dev/null &