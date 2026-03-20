.PHONY: help install install-dev install-scraper test test-cov lint format clean update-data update-data-de update-data-at update-data-be update-data-nl update-data-fr-es update-data-lu run-example check

# ─── Variables ──────────────────────────────────────────────────────────────────
PYTHON    := uv run python
PYTEST    := uv run pytest
SCRIPTS   := scripts

# ─── Default ────────────────────────────────────────────────────────────────────
help: ## Show this help message
	@echo ""
	@echo "  IBAN Tools — Makefile Commands"
	@echo "  ══════════════════════════════════════════════════════"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ─── Installation ──────────────────────────────────────────────────────────────
install: ## Install project dependencies
	uv sync

install-dev: ## Install project with dev dependencies (pytest)
	uv sync --all-extras

install-scraper: ## Install scraper dependencies (requests, beautifulsoup4, openpyxl)
	uv sync --extra scraper

# ─── Testing ───────────────────────────────────────────────────────────────────
test: ## Run all tests
	$(PYTEST) tests/ -v

test-cov: ## Run all tests with coverage report
	$(PYTEST) tests/ -v --cov=iban_tools --cov-report=term-missing

test-fast: ## Run tests without verbose output
	$(PYTEST) tests/ -q

# ─── Code Quality ──────────────────────────────────────────────────────────────
check: ## Run tests and verify everything works
	@echo "Running full test suite..."
	$(PYTEST) tests/ -v
	@echo ""
	@echo "✅ All checks passed!"

# ─── BIC Data Update ──────────────────────────────────────────────────────────
update-data: install-scraper ## Update ALL BIC datasets from external sources
	@echo "Updating all BIC data..."
	$(PYTHON) $(SCRIPTS)/update_all.py

update-data-de: install-scraper ## Update German (DE) BIC data from Bundesbank
	$(PYTHON) $(SCRIPTS)/scrape_de.py

update-data-at: install-scraper ## Update Austrian (AT) BIC data from OeNB
	$(PYTHON) $(SCRIPTS)/scrape_at.py

update-data-be: install-scraper ## Update Belgian (BE) BIC data from NBB
	$(PYTHON) $(SCRIPTS)/scrape_be.py

update-data-nl: install-scraper ## Update Dutch (NL) BIC data from Betaalvereniging
	$(PYTHON) $(SCRIPTS)/scrape_nl.py

update-data-fr-es: install-scraper ## Update French (FR) & Spanish (ES) BIC data from ECB
	$(PYTHON) $(SCRIPTS)/scrape_fr_es.py

update-data-lu: install-scraper ## Update Luxembourg (LU) BIC data from ABBL
	$(PYTHON) $(SCRIPTS)/scrape_lu.py

# ─── Utility ───────────────────────────────────────────────────────────────────
run-example: ## Run a quick demo of all functions
	@$(PYTHON) -c "\
	from iban_tools import *; \
	print('=== IBAN Tools Demo ==='); \
	print(); \
	iban = generate_mock_iban('DE'); \
	print(f'Generated DE IBAN : {iban}'); \
	print(f'Valid             : {validate_iban(iban)}'); \
	print(f'Formatted         : {format_iban(iban)}'); \
	print(f'Sanitized         : {sanitize_iban(format_iban(iban))}'); \
	print(); \
	p = parse_iban('DE89370400440532013000'); \
	print(f'Parsed DE89...    : {p}'); \
	print(); \
	bic = iban_to_bic('DE89370400440532013000'); \
	print(f'BIC for DE89...   : {bic}'); \
	print(); \
	text = 'Pay to DE89370400440532013000 or TR330006100519786457841326'; \
	found = extract_ibans_from_text(text); \
	print(f'Extracted IBANs   : {found}'); \
	print(); \
	stats = get_bic_data_stats(); \
	print(f'BIC data stats    : {stats}'); \
	print(); \
	print('✅ All functions working!'); \
	"

version: ## Show current version
	@$(PYTHON) -c "from iban_tools import __version__; print(f'iban-tools v{__version__}')"

clean: ## Remove build artifacts and caches
	rm -rf dist/ build/ *.egg-info
	rm -rf .pytest_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "🧹 Cleaned!"

tree: ## Show project structure
	@find . -not -path './.git/*' -not -path './.venv/*' -not -path './__pycache__/*' -not -name '.DS_Store' | head -60
