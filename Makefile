.PHONY: up down dev seed eval test clean reset-demo

## Start all services (hackathon demo mode)
up:
	docker compose -f infrastructure/docker-compose.yml up -d
	@echo "\n✅ MeetMind running:"
	@echo "   Frontend:  http://localhost:3000"
	@echo "   API Docs:  http://localhost:8000/docs"
	@echo "   Flower:    http://localhost:5555"
	@echo "   Neo4j:     http://localhost:7474"

## Stop all services
down:
	docker compose -f infrastructure/docker-compose.yml down

## Run migrations
migrate:
	docker compose -f infrastructure/docker-compose.yml exec backend alembic upgrade head

## Seed demo data (run before hackathon presentation)
seed:
	docker compose -f infrastructure/docker-compose.yml exec backend python scripts/seed_demo_data.py

## Generate additional test transcripts
gen-transcripts:
	docker compose -f infrastructure/docker-compose.yml exec backend python scripts/generate_test_transcripts.py

## Run evaluation suite
eval:
	docker compose -f infrastructure/docker-compose.yml exec backend python tests/eval/evaluate.py

## Run backend unit tests
test:
	cd backend && pytest tests/unit -v

## Full demo reset (wipe + re-seed)
reset-demo: down
	docker volume rm meetmind_postgres_data meetmind_redis_data || true
	$(MAKE) up
	sleep 5
	$(MAKE) migrate
	$(MAKE) seed
	@echo "\n🎯 Demo environment ready!"

## Clean all Docker resources
clean:
	docker compose -f infrastructure/docker-compose.yml down -v --remove-orphans

## View logs
logs:
	docker compose -f infrastructure/docker-compose.yml logs -f

## Backend shell
shell:
	docker compose -f infrastructure/docker-compose.yml exec backend bash
