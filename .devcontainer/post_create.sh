#!/bin/bash
set -e

WORKSPACE_DIR="/workspace"

echo "========================================================"
echo "  DevContainer Post-Create Setup"
echo "========================================================"

# Install frontend dependencies
if [ -d "$WORKSPACE_DIR/frontend" ]; then
  echo ""
  echo "=============== Installing frontend dependencies ==============="
  cd "$WORKSPACE_DIR/frontend"
  npm install
else
  echo ""
  echo "No frontend directory found, skipping frontend setup"
fi

# Install backend dependencies and set up database
if [ -d "$WORKSPACE_DIR/backend" ]; then
  echo ""
  echo "=============== Installing backend dependencies ================"
  cd "$WORKSPACE_DIR/backend"

  if [ -f "pyproject.toml" ]; then
    pip install -e ".[dev]"
  elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
  else
    echo "No pyproject.toml or requirements.txt found, skipping backend setup"
  fi

  # Wait for SQL Server to be ready
  echo ""
  echo "==================== Setting up database ======================="
  echo "Waiting for SQL Server to be ready..."

  for i in {1..30}; do
    if /opt/mssql-tools18/bin/sqlcmd -S db -U sa -P SenateDev2026! -C -Q "SELECT 1" > /dev/null 2>&1; then
      echo "SQL Server is ready!"
      break
    fi
    echo "Waiting for SQL Server... ($i/30)"
    sleep 1
  done

  # Create databases
  if [ -d "script" ]; then
    echo "Creating databases..."
    python -m script.create_db && echo "Development database created successfully" || echo "Warning: Database creation failed. You may need to run this manually."
    python -m script.create_test_db && echo "Test database created successfully" || echo "Warning: Test database creation failed. You may need to run this manually."
  fi
else
  echo ""
  echo "No backend directory found, skipping backend setup"
fi

# Install pre-commit hooks
if [ -f "$WORKSPACE_DIR/.pre-commit-config.yaml" ]; then
  echo ""
  echo "================== Installing pre-commit hooks ================="
  cd "$WORKSPACE_DIR"
  pre-commit install
  pre-commit install-hooks
else
  echo ""
  echo "No .pre-commit-config.yaml found, skipping pre-commit setup"
fi

echo ""
echo "========================================================"
echo "  Setup Complete!"
echo "========================================================"
