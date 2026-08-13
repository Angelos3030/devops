# Research Summary — theme-refs-gh-api

**Objective:** From each GitHub API search result set, identify repositories that are REAL LOCAL BUSINESS website templates (restaurant, taverna, cafe, bakery, plumber, electrician, HVAC, cleaning, construction, mechanic, dentist, clinic, salon, barber, gym, hotel, accountant, real estate, pet services, photography, local retail). For each promising repo report: full_name, html_url, stars, license spdx_id EXACTLY as given (null means UNKNOWN — treat as reject-until-verified), vertical, and whether the description suggests a distinctive information architecture rather than a generic one-page landing. REJECT: SaaS dashboards, admin panels, AI/startup landing pages, developer portfolios, tutorial/course projects, and anything whose license field is null or non-permissive.
**Generated:** 2026-08-13T04:49:09.722247+00:00
**Models:** Pass 1 = deepseek-v4-flash | Pass 2 = deepseek-v4-pro
**Tokens:** in=13,027 out=4,427 (~$0.0132 USD)
**Sources analyzed:** 8  |  **Deep-analysed:** 1  |  **Rejected:** 6  |  **Pending (over budget):** 0

## Findings (deep-analysed)

- **PictureElement/grecko** — REJECT — Real local business template for restaurants with MIT license; includes responsive design, SEO optimization, and Cloudinary image management, but it uses a standard Bootstrap layout that is not genuinely different in information architecture or vertical-specific conversion pattern.

## Rejected (sample)

- YaninaTrekhleb/restaurant-website — License null; generic restaurant landing page.
- vijaythapa333/web-design-course-restaurant — License null; tutorial/course project.
- cosmicjs/nextjs-restaurant-website-cms — License null; CMS starter not simple local template.
- marynganga/Restaurant-Website-Template — MIT but school project, not production template.
- shovoalways/restaurant-elementor-template — License null; WordPress tutorial project.
- codewithshabbir/Restoran — License unknown; cannot verify permissive use.