#!/usr/bin/env bash
# Vercel build for the existing dashboard project: keep serving the repository root as a static
# site (copied into public/) and add the Ngecas app under /ngecas/.
set -euo pipefail
rm -rf public && mkdir public
for f in * .[!.]*; do
  case "$f" in app|public|node_modules|api|.git|.gitignore|.vercel|vercel.json|build.sh|.claude) ;;
    *) cp -r "$f" public/ ;;
  esac
done
cd app && npm ci --no-audit --no-fund && npm run build:root
