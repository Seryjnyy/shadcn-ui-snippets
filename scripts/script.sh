#!/bin/bash


SHADCN_UI_REPO_DIR="../shadcn-ui-repo"
REPO_URL="https://github.com/shadcn-ui/ui.git"

# Clone the repository if it doesn't exist
if [ ! -d "$SHADCN_UI_REPO_DIR" ]; then
    echo "Cloning repository..."
#    git clone --depth 1 --no-checkout https://github.com/shadcn-ui/ui.git shadcn-ui-repo
    git clone --depth 1 --no-checkout "$REPO_URL" "$SHADCN_UI_REPO_DIR"
    cd "$SHADCN_UI_REPO_DIR"
    git sparse-checkout init
    echo "/apps/www/content/docs/components/*" > .git/info/sparse-checkout
    git checkout main
    cd - || exit
else
    echo "Repository exists. Pulling latest changes..."
    cd "$SHADCN_UI_REPO_DIR" || exit
    git pull
    cd - || exit
fi

echo "shadcn/ui repository is up to date."