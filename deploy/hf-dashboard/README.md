---
title: Getaround Delay Analysis Dashboard
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
license: mit
---

> Deployment repository of the Hugging Face Space
> [sam-bot/get-around-dashboard](https://huggingface.co/spaces/sam-bot/get-around-dashboard).
> Source, tests and CI live in [tryph0n/getarround](https://github.com/tryph0n/getarround).
> This repository is a copy made with `make stage-dashboard`: do not edit here.

# Getaround Delay Analysis Dashboard

Interactive dashboard to help Product Managers decide on minimum delay threshold between car rentals.

## Features

- Delay analysis visualizations
- Impact on next driver analysis
- Interactive threshold simulator
- Revenue impact estimation
- Pricing prediction via API integration

## Key Questions Answered

1. What share of revenue would be affected by the feature?
2. How many rentals would be affected by threshold and scope?
3. How often are drivers late for the next check-in?
4. How many problematic cases will the threshold solve?

## Deployment

Built and uploaded with `make deploy-dashboard` from the source repository.

## Data

Data provided by the Jedha training course (Getaround case study). The provider states no licence. The data files are not covered by the code licence.
