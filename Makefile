SHELL=/bin/bash

Default: GenerateTree ViewTree

GenerateTree:
	source $(CONDA_PREFIX)/etc/profile.d/conda.sh && \
	conda activate NeptunesPride && \
	python src/LocalTree.py && \
	conda deactivate
	@sleep 1

ViewTree:
	xdg-open data/LatestMap.png >/dev/null &