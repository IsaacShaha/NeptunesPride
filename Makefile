# As of Jan. 24th 9:10PM, Hellfire Renaissance owes me $165.

SHELL=/bin/bash
GAME_NUMBER=5583056940040192
GAME_API=qdnLtw

Default: GenerateTree ViewTree

GenerateTree:
	source $(CONDA_PREFIX)/etc/profile.d/conda.sh && \
	conda activate NeptunesPride && \
	python src/LocalTree.py $(GAME_NUMBER) $(GAME_API) && \
	conda deactivate
	@sleep 1

ViewTree:
	xdg-open data/LatestMap.png >/dev/null &
