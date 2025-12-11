# Smart Coupon Recommendation System

![CI](https://github.com/Kanak1009/Smart-Coupon-Recommendation/actions/workflows/python-ci.yml/badge.svg)


A rule-based coupon recommendation engine in **Python** that analyzes a shopping cart and suggests the best coupon to maximize savings. The system loads product and coupon datasets, checks coupon eligibility (dates, categories, min cart value, active status), computes savings for each coupon, and recommends the most optimal discount. Includes a comma-separated CLI, modular architecture, realistic datasets, and unit tests with GitHub Actions CI.

---

## Features
- Load product and coupon data from CSV files (`data/`).
- Rule-based eligibility checks:
  - active / inactive coupons
  - date range (start / end)
  - minimum cart value
  - category-specific applicability (e.g., ELECTRONICS, GROCERY)
- Supports two discount types:
  - `PERCENT` (with a cap)
  - `FLAT`
- Calculates applicable amount, savings, and final total for each coupon.
- CLI (comma-separated input) for quick interactive usage.
- Unit tests using `pytest` and CI on GitHub Actions.

---
