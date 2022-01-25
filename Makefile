SHELL=/bin/bash
# GAME_NUMBER=5583056940040192
# GAME_API=qdnLtw

Default: GenerateTree ViewTree

GenerateTree:
	source $(CONDA_PREFIX)/etc/profile.d/conda.sh && \
	conda activate NeptunesPride && \
	python src/LocalTree.py & \
	conda deactivate
	@sleep 1

ViewTree:
	xdg-open data/LatestMap.png >/dev/null &
