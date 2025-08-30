#!/bin/bash

# Setup script for Hugo with PaperMod theme
set -euo pipefail

echo "Setting up Hugo with PaperMod theme..."

# Check if Hugo is installed
if ! command -v hugo &> /dev/null; then
    echo "Hugo is not installed. Please install Hugo first."
    echo "Visit: https://gohugo.io/installation/"
    exit 1
fi

# Create Hugo site structure
mkdir -p content posts docs static layouts archetypes assets

# Copy Hugo configuration
cp configs/hugo.toml hugo.toml

# Initialize git repository if not exists
if [ ! -d .git ]; then
    git init
    echo "Initialized git repository"
fi

# Create .gitignore for Hugo
cat > .gitignore << EOF
# Hugo
public/
resources/
.hugo_build.lock

# OS
.DS_Store
Thumbs.db

# Editor
.vscode/
.idea/
*.swp
*.swo

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# Build artifacts
dist/
build/
*.egg-info/
EOF

# Create README for the Hugo site
cat > README_HUGO.md << 'EOF'
# Hugo Wiki Site

This is a Hugo site generated from your Obsidian vault using the PaperMod theme.

## Quick Start

1. **Install Hugo** (if not already installed):
   ```bash
   # macOS
   brew install hugo
   
   # Ubuntu/Debian
   sudo apt-get install hugo
   
   # Windows
   choco install hugo
   ```

2. **Install PaperMod theme**:
   ```bash
   git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/hugo-papermod
   ```

3. **Run the development server**:
   ```bash
   hugo server -D
   ```

4. **Build for production**:
   ```bash
   hugo
   ```

## Directory Structure

- `content/` - Your converted Obsidian notes
- `static/` - Static assets (images, files, etc.)
- `layouts/` - Custom layouts (if needed)
- `archetypes/` - Content templates
- `assets/` - Source assets for processing

## Theme Configuration

The site uses the PaperMod theme with the following features enabled:

- ✅ Table of Contents
- ✅ Code highlighting
- ✅ Search functionality
- ✅ Reading time
- ✅ Word count
- ✅ Social sharing
- ✅ Responsive design

## Customization

1. Edit `hugo.toml` to customize site settings
2. Add custom CSS in `assets/css/`
3. Modify layouts in `layouts/`
4. Add custom shortcodes in `layouts/shortcodes/`

## Deployment

### Netlify
1. Connect your repository to Netlify
2. Set build command: `hugo`
3. Set publish directory: `public`

### GitHub Pages
1. Enable GitHub Pages in repository settings
2. Set source to GitHub Actions
3. Use the provided workflow in `.github/workflows/hugo.yml`

### Vercel
1. Import your repository to Vercel
2. Set build command: `hugo`
3. Set output directory: `public`

## Troubleshooting

- **Theme not found**: Run `git submodule update --init --recursive`
- **Build errors**: Check Hugo version compatibility
- **Missing content**: Ensure conversion was successful

## Support

For issues with:
- **Hugo**: https://gohugo.io/support/
- **PaperMod theme**: https://github.com/adityatelange/hugo-PaperMod
- **Conversion tool**: Check the main project documentation
EOF

# Create GitHub Actions workflow for deployment
mkdir -p .github/workflows

cat > .github/workflows/hugo.yml << 'EOF'
name: Deploy Hugo site to Pages

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

defaults:
  run:
    shell: bash

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          submodules: recursive
          fetch-depth: 0
      
      - name: Setup Pages
        id: pages
        uses: actions/configure-pages@v4
      
      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: 'latest'
          extended: true
      
      - name: Build with Hugo
        env:
          HUGO_ENVIRONMENT: production
          HUGO_ENV: production
        run: |
          hugo \
            --gc \
            --minify \
            --baseURL "${{ steps.pages.outputs.base_url }}/"
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./public

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
EOF

# Create Netlify configuration
cat > netlify.toml << 'EOF'
[build]
  publish = "public"
  command = "hugo"

[build.environment]
  HUGO_VERSION = "0.120.0"
  HUGO_ENV = "production"
  HUGO_ENABLEGITINFO = "true"

[[headers]]
  for = "/assets/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"

[[redirects]]
  from = "/admin/*"
  to = "/admin/index.html"
  status = 200

[[redirects]]
  from = "/*"
  to = "/404.html"
  status = 404
EOF

echo "Hugo setup completed!"
echo ""
echo "Next steps:"
echo "1. Install PaperMod theme: git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/hugo-papermod"
echo "2. Run the converter: python -m obsidian_to_hugo convert --obsidian-vault /path/to/vault"
echo "3. Start Hugo server: hugo server -D"
echo ""
echo "See README_HUGO.md for more details."