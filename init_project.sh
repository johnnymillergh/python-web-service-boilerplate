#!/bin/bash

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Python Web Service Boilerplate Project Initialization ===${NC}"
echo

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR"

# Check if we're in the right directory
if [[ ! -d "src/python_web_service_boilerplate" ]]; then
    echo -e "${RED}Error: This script must be run from the project root directory.${NC}"
    echo -e "${RED}Expected to find 'src/python_web_service_boilerplate' directory.${NC}"
    exit 1
fi

# Prompt for new project name
NEW_PROJECT_NAME="$1"
if [[ -z "$NEW_PROJECT_NAME" ]]; then
    echo -e "${YELLOW}Please enter your desired project name (use snake_case, e.g., 'my_awesome_project'):${NC}"
    read -p "Project name: " NEW_PROJECT_NAME
fi

# Validate project name
if [[ -z "$NEW_PROJECT_NAME" ]]; then
    echo -e "${RED}Error: Project name cannot be empty.${NC}"
    exit 1
fi

# Check if name contains only valid characters (letters, numbers, underscores)
if [[ ! "$NEW_PROJECT_NAME" =~ ^[a-zA-Z][a-zA-Z0-9_]*$ ]]; then
    echo -e "${RED}Error: Project name must start with a letter and contain only letters, numbers, and underscores.${NC}"
    exit 1
fi

echo
echo -e "${BLUE}Initializing project with name: ${GREEN}$NEW_PROJECT_NAME${NC}"
echo

# Function to replace text in files
replace_in_files() {
    local old_text="$1"
    local new_text="$2"
    local file_pattern="$3"

    echo -e "${YELLOW}Updating $file_pattern files...${NC}"

    # Use find to locate files and sed to replace text
    find . -name "$file_pattern" -type f -not -path "./.*" -not -path "./build/*" -not -path "./__pycache__/*" -not -path "./data/*" | xargs sed -i "s/$old_text/$new_text/g"
}

# Step 1: Update Python files
echo -e "${BLUE}Step 1: Updating Python import statements...${NC}"
replace_in_files "python_web_service_boilerplate" "$NEW_PROJECT_NAME" "*.py"

# Step 2: Update configuration files
echo -e "${BLUE}Step 2: Updating configuration files...${NC}"

# Update pyproject.toml
if [[ -f "pyproject.toml" ]]; then
    echo -e "${YELLOW}Updating pyproject.toml...${NC}"
    sed -i "s/python-web-service-boilerplate/$NEW_PROJECT_NAME/g" pyproject.toml
    sed -i "s/python_web_service_boilerplate/$NEW_PROJECT_NAME/g" pyproject.toml
fi

# Update docker-compose.yml
if [[ -f "docker-compose.yml" ]]; then
    echo -e "${YELLOW}Updating docker-compose.yml...${NC}"
    sed -i "s/python_web_service_boilerplate/$NEW_PROJECT_NAME/g" docker-compose.yml
fi

# Update alembic.ini
if [[ -f "alembic.ini" ]]; then
    echo -e "${YELLOW}Updating alembic.ini...${NC}"
    sed -i "s/python_web_service_boilerplate/$NEW_PROJECT_NAME/g" alembic.ini
fi

# Step 3: Rename directories
echo -e "${BLUE}Step 3: Renaming directories...${NC}"

# Rename source directory
if [[ -d "src/python_web_service_boilerplate" ]]; then
    echo -e "${YELLOW}Renaming src/python_web_service_boilerplate to src/$NEW_PROJECT_NAME...${NC}"
    mv "src/python_web_service_boilerplate" "src/$NEW_PROJECT_NAME"
fi

# Rename test directory
if [[ -d "tests/test_python_web_service_boilerplate" ]]; then
    echo -e "${YELLOW}Renaming tests/test_python_web_service_boilerplate to tests/test_$NEW_PROJECT_NAME...${NC}"
    mv "tests/test_python_web_service_boilerplate" "tests/test_$NEW_PROJECT_NAME"
fi

# Step 4: Clean up cache directories
echo -e "${BLUE}Step 4: Cleaning up cache directories...${NC}"
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -type f -delete 2>/dev/null || true

# Step 5: Update any remaining references
echo -e "${BLUE}Step 5: Final cleanup...${NC}"

# Check for any remaining references and report them
REMAINING_REFS=$(grep -r "python_web_service_boilerplate" . --exclude-dir=.git --exclude-dir=build --exclude-dir=__pycache__ --exclude="*.log" --exclude="init_project.*" 2>/dev/null || true)

if [[ -n "$REMAINING_REFS" ]]; then
    echo -e "${YELLOW}Warning: Found remaining references to 'python_web_service_boilerplate':${NC}"
    echo "$REMAINING_REFS"
    echo -e "${YELLOW}You may need to update these manually.${NC}"
fi

echo
echo -e "${GREEN}✅ Project initialization completed successfully!${NC}"
echo -e "${GREEN}Your project is now named: $NEW_PROJECT_NAME${NC}"
echo
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. Review and commit your changes"
echo -e "2. Update the README.md file with your project details"
echo -e "3. Run: ${YELLOW}poetry install${NC} to install dependencies"
echo -e "4. Run: ${YELLOW}poetry run python -m $NEW_PROJECT_NAME${NC} to start the application"
echo
