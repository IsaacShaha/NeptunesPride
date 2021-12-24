SHELL=/bin/bash

Default: GenerateTree ViewTree

GenerateTree:
	source $(CONDA_PREFIX)/etc/profile.d/conda.sh && \
	conda activate NeptunesPride && \
	python src/LocalTree.py && \
	conda deactivate

ViewTree:
	xdg-open data/LatestMap.png >/dev/null &