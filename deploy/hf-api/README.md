---
title: Getaround Pricing API
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

> Deployment repository of the Hugging Face Space
> [sam-bot/get-around-api](https://huggingface.co/spaces/sam-bot/get-around-api).
> Source, tests and CI live in [tryph0n/getarround](https://github.com/tryph0n/getarround).
> This repository is a copy made with `make stage-api`: do not edit here.

# Getaround Pricing API

API for predicting optimal rental prices for cars.

## Endpoints

- `POST /predict` - Predict rental prices
- `GET /health` - Health check
- `GET /docs` - API documentation (Swagger UI)

## Usage

```bash
curl -X POST https://sam-bot-get-around-api.hf.space/predict \
  -H "Content-Type: application/json" \
  -d '{"cars": [{"model_key": "Peugeot", "mileage": 50000, "engine_power": 120, "fuel": "diesel", "paint_color": "black", "car_type": "sedan", "private_parking_available": true, "has_gps": true, "has_air_conditioning": true, "automatic_car": false, "has_getaround_connect": false, "has_speed_regulator": true, "winter_tires": false}]}'
```

## Deployment

Built and uploaded with `make deploy-api` from the source repository.

## Data

The model is trained on data provided by the Jedha training course (Getaround case study).
The provider states no licence. The data is not covered by the code licence.
