# Deploy του landing site (web/) στο Cloudflare Pages.
# Προϋπόθεση: npm εγκατεστημένο + Cloudflare account.
#
#   pwsh scripts/deploy-landing.ps1
#
# Πρώτη φορά θα ανοίξει browser για login στο Cloudflare (wrangler login).

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$web  = Join-Path $root "web"

Write-Host "Deploying $web -> Cloudflare Pages (project: vitrina)..." -ForegroundColor Cyan

# wrangler μέσω npx (δεν χρειάζεται global install)
npx --yes wrangler@latest pages deploy $web --project-name vitrina --commit-dirty=true

Write-Host "`nΈτοιμο. Το site βγαίνει στο https://vitrina.pages.dev" -ForegroundColor Green
Write-Host "Μετά: Cloudflare Dashboard -> Pages -> vitrina -> Custom domains -> getvitrina.gr" -ForegroundColor Yellow
