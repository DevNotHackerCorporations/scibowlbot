build:
	docker build -t scibowlbot:1.0.0 .
run:
	docker compose up -d scibowlbot
restart:
	docker compose restart scibowlbot
refresh:
	git pull && $(MAKE) build && $(MAKE) restart
