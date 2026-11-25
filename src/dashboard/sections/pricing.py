"""Section 6: pricing prediction through the ML API."""

import logging

import httpx
import streamlit as st

logger = logging.getLogger(__name__)


def render(api_url: str) -> None:
    """Render the pricing form and call the prediction API on submit.

    Args:
        api_url: Base URL of the pricing API.
    """
    st.header("6. Pricing Prediction")
    st.markdown(
        "Use the form below to estimate the daily rental price "
        "for a car based on its features."
    )

    st.info(
        "Model: GradientBoosting | Test RMSE: 16.14 EUR | R2: 0.762\n"
        "Selected as best among 3 models (Linear Regression, Random Forest, "
        "Gradient Boosting) via RandomizedSearchCV (5-fold CV, optimizing RMSE). "
        "Baseline (mean predictor): 33.56 RMSE."
    )

    st.markdown(f"API Documentation: [{api_url}/docs]({api_url}/docs)")

    with st.form("prediction_form"):
        # Row 1 - Main characteristics
        r1c1, r1c2, r1c3 = st.columns(3)

        with r1c1:
            model_key = st.selectbox(
                "Brand",
                options=[
                    "Alfa Romeo",
                    "Audi",
                    "BMW",
                    "Citroen",
                    "Ferrari",
                    "Fiat",
                    "Ford",
                    "Honda",
                    "KIA",
                    "Lamborghini",
                    "Lexus",
                    "Maserati",
                    "Mazda",
                    "Mercedes",
                    "Mini",
                    "Mitsubishi",
                    "Nissan",
                    "Opel",
                    "PGO",
                    "Peugeot",
                    "Porsche",
                    "Renault",
                    "SEAT",
                    "Subaru",
                    "Suzuki",
                    "Toyota",
                    "Volkswagen",
                    "Yamaha",
                ],
                index=19,  # Peugeot
            )

        with r1c2:
            fuel = st.selectbox(
                "Fuel",
                options=[
                    "diesel",
                    "petrol",
                    "hybrid_petrol",
                    "electro",
                ],
                index=0,
            )

        with r1c3:
            car_type = st.selectbox(
                "Car Type",
                options=[
                    "sedan",
                    "hatchback",
                    "suv",
                    "van",
                    "estate",
                    "convertible",
                    "coupe",
                    "subcompact",
                ],
                index=0,
            )

        # Row 2 - Specifications
        r2c1, r2c2, r2c3 = st.columns(3)

        with r2c1:
            mileage = st.number_input(
                "Mileage (km)",
                min_value=0,
                max_value=500_000,
                value=100_000,
                step=5_000,
            )

        with r2c2:
            engine_power = st.number_input(
                "Engine Power (hp)",
                min_value=10,
                max_value=500,
                value=120,
                step=10,
            )

        with r2c3:
            paint_color = st.selectbox(
                "Paint Color",
                options=[
                    "black",
                    "white",
                    "grey",
                    "silver",
                    "blue",
                    "red",
                    "beige",
                    "brown",
                    "green",
                    "orange",
                ],
                index=0,
            )

        # Row 3 - Equipment
        st.markdown("**Equipment**")
        r3c1, r3c2, r3c3, r3c4 = st.columns(4)

        with r3c1:
            private_parking = st.checkbox("Private parking", value=False)
            has_gps = st.checkbox("GPS", value=False)

        with r3c2:
            has_ac = st.checkbox("Air conditioning", value=True)
            automatic = st.checkbox("Automatic transmission", value=False)

        with r3c3:
            has_connect = st.checkbox("Getaround Connect", value=False)
            has_regulator = st.checkbox("Speed regulator", value=False)

        with r3c4:
            winter_tires = st.checkbox("Winter tires", value=False)

        submitted = st.form_submit_button("Predict Price")

    if submitted:
        payload = {
            "cars": [
                {
                    "model_key": model_key,
                    "mileage": mileage,
                    "engine_power": engine_power,
                    "fuel": fuel,
                    "paint_color": paint_color,
                    "car_type": car_type,
                    "private_parking_available": private_parking,
                    "has_gps": has_gps,
                    "has_air_conditioning": has_ac,
                    "automatic_car": automatic,
                    "has_getaround_connect": has_connect,
                    "has_speed_regulator": has_regulator,
                    "winter_tires": winter_tires,
                }
            ]
        }

        try:
            response = httpx.post(
                f"{api_url}/predict",
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
            result = response.json()
            price = result["prediction"][0]
            st.success(f"Estimated daily rental price: {price} EUR/day")
        except httpx.ConnectError:
            st.error(
                f"Cannot connect to API at {api_url}. Ensure the API server is running."
            )
        except httpx.HTTPStatusError as exc:
            st.error(
                f"API error (HTTP {exc.response.status_code}): {exc.response.text}"
            )
        except Exception as exc:
            logger.exception("Prediction request failed")
            st.error(f"Prediction failed: {exc}")
