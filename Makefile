.PHONY: install install-deps install-node-deps install-python-deps setup-env validate-mermaid test clean

# Install all dependencies
install: install-python install-node setup-env
	@echo "✅ All dependencies installed successfully!"

# Alias for install
install-deps: install

# Install Python dependencies using uv
install-python:
	@echo "📦 Installing Python dependencies..."
	@command -v uv >/dev/null 2>&1 || { echo "❌ uv is not installed. Please install it first: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	uv sync
	@echo "✅ Python dependencies installed"

# Install Node.js dependencies (Mermaid CLI)
install-node:
	@echo "📦 Installing Mermaid CLI..."
	@command -v npm >/dev/null 2>&1 || { echo "❌ npm is not installed. Please install Node.js first"; exit 1; }
	npm install -g @mermaid-js/mermaid-cli
	@echo "✅ Mermaid CLI installed"

# Set up environment file
setup-env:
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file from .env.example..."; \
		cp .env.example .env; \
		echo "⚠️  Please edit .env and add your API keys"; \
	else \
		echo "✅ .env file already exists"; \
	fi

# Run mermaid validation test
validate-mermaid:
	@echo "🧪 Running mermaid validation test..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Run 'make setup-env' first and add your API keys"; \
		exit 1; \
	fi
	uv run test_pydantic.py

# Run all tests
test: validate-mermaid
	@echo "✅ All tests completed"

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	rm -rf .venv
	@echo "✅ Cleaned up virtual environment"

# Check if all dependencies are installed
check-deps:
	@echo "🔍 Checking dependencies..."
	@command -v uv >/dev/null 2>&1 || { echo "❌ uv not found"; exit 1; }
	@command -v npm >/dev/null 2>&1 || { echo "❌ npm not found"; exit 1; }
	@command -v mmdc >/dev/null 2>&1 || { echo "❌ mermaid-cli not found"; exit 1; }
	@[ -f .env ] || { echo "❌ .env file not found"; exit 1; }
	@echo "✅ All dependencies are installed"
