# Streamlit app for the NYC Taxi Fare Prediction 
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    # App title and description
    st.title("NYC Green Taxi Fare Predictor")
    st.write("This app predicts the total fare amount for NYC green taxi rides based on a Multiple Linear Regression model")
    
    # Try to load the model
    try:
        with open('nyc_taxi_fare_rf_model.pkl', 'rb') as f:
            model = pickle.load(f)
        model_loaded = True
        st.success("Model loaded successfully!")
    except:
        st.warning("Model file not found. Using simplified calculation instead.")
        model_loaded = False

    # Sidebar for inputs
    st.sidebar.header("Ride Information")

    # Collecting user inputs
    trip_distance = st.sidebar.slider("Trip Distance (miles)", 0.1, 30.0, 2.5)
    passenger_count = st.sidebar.slider("Number of Passengers", 1, 6, 1)
    trip_duration = st.sidebar.slider("Trip Duration (minutes)", 1, 120, 15)

    # Payment Type
    payment_options = {
        "Credit Card": 1, 
        "Cash": 2,
        "No Charge": 3, 
        "Dispute": 4,
        "Unknown": 5
    }
    payment_type = st.sidebar.selectbox("Payment Type", list(payment_options.keys()))
    payment_type_value = payment_options[payment_type]

    # Trip Type
    trip_type_options = ["Street-hail", "Dispatch"]
    trip_type = st.sidebar.selectbox("Trip Type", trip_type_options)
    trip_type_value = 1 if trip_type == "Street-hail" else 2

    # Day of the week
    weekday_options = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday = st.sidebar.selectbox("Day of the Week", weekday_options)

    # Hour of the day
    hour = st.sidebar.slider("Hour of the Day (24h)", 0, 23, 12)

    # Additional charges
    st.sidebar.subheader("Additional Charges")
    fare_amount = st.sidebar.slider("Base Fare Amount ($)", 2.5, 20.0, 2.5)
    extra = st.sidebar.slider("Extra Charges ($)", 0.0, 5.0, 0.0)
    mta_tax = st.sidebar.slider("MTA Tax ($)", 0.0, 1.0, 0.5)
    tip_amount = st.sidebar.slider("Tip Amount ($)", 0.0, 20.0, 0.0)
    tolls_amount = st.sidebar.slider("Tolls Amount ($)", 0.0, 20.0, 0.0)
    improvement_surcharge = st.sidebar.slider("Improvement Surcharge ($)", 0.0, 1.0, 0.3)
    congestion_surcharge = st.sidebar.slider("Congestion Surcharge ($)", 0.0, 3.0, 2.5)

    # Main panel
    st.header("Prediction")

    # Prediction logic
    if model_loaded:
        input_data = {
            'trip_distance': trip_distance,
            'fare_amount': fare_amount,
            'extra': extra,
            'mta_tax': mta_tax,
            'tip_amount': tip_amount,
            'tolls_amount': tolls_amount,
            'improvement_surcharge': improvement_surcharge,
            'congestion_surcharge': congestion_surcharge,
            'trip_duration': trip_duration,
            'passenger_count': passenger_count,
            'payment_type_2': 1 if payment_type_value == 2 else 0,
            'payment_type_3': 1 if payment_type_value == 3 else 0,
            'payment_type_4': 1 if payment_type_value == 4 else 0,
            'payment_type_5': 1 if payment_type_value == 5 else 0,
            'trip_type_2': 1 if trip_type_value == 2 else 0,
            'weekday_Monday': 1 if weekday == 'Monday' else 0,
            'weekday_Saturday': 1 if weekday == 'Saturday' else 0,
            'weekday_Sunday': 1 if weekday == 'Sunday' else 0,
            'weekday_Thursday': 1 if weekday == 'Thursday' else 0,
            'weekday_Tuesday': 1 if weekday == 'Tuesday' else 0,
            'weekday_Wednesday': 1 if weekday == 'Wednesday' else 0,
            f'hour_{hour}': 1
        }

        input_df = pd.DataFrame([input_data])

        try:
            predicted_fare = model.predict(input_df)[0]
            st.subheader(f"Predicted Total Fare: ${predicted_fare:.2f}")
        except Exception as e:
            st.error(f"Error making prediction: {e}")
            model_loaded = False

    if not model_loaded:
        base_fare = fare_amount
        per_mile_rate = 2.50
        per_minute_rate = 0.35
        estimated_fare = base_fare + (trip_distance * per_mile_rate) + (trip_duration * per_minute_rate)
        estimated_fare += extra + mta_tax + tip_amount + tolls_amount + improvement_surcharge + congestion_surcharge
        st.subheader(f"Estimated Total Fare: ${estimated_fare:.2f}")

    # Explanation section
    st.header("Fare Breakdown")
    breakdown = {
        "Base Fare": f"${fare_amount:.2f}",
        "Distance Charge (estimated)": f"${trip_distance * 2.50:.2f}",
        "Time Charge (estimated)": f"${trip_duration * 0.35:.2f}",
        "Extra": f"${extra:.2f}",
        "MTA Tax": f"${mta_tax:.2f}",
        "Tip": f"${tip_amount:.2f}",
        "Tolls": f"${tolls_amount:.2f}",
        "Improvement Surcharge": f"${improvement_surcharge:.2f}",
        "Congestion Surcharge": f"${congestion_surcharge:.2f}"
    }
    for item, value in breakdown.items():
        st.write(f"{item}: {value}")

    # Data visualization section
    st.header("Data Visualization")
    tab1, tab2, tab3 = st.tabs(["Fare by Distance", "Fare by Time", "Payment Types"])

    with tab1:
        st.subheader("Relationship between Trip Distance and Fare")
        distances = np.linspace(0, 30, 100)
        fares = [fare_amount + d * 2.5 for d in distances]
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(distances, fares)
        ax.scatter([trip_distance], [fare_amount + trip_distance * 2.5], color='red', s=100)
        ax.set_xlabel('Trip Distance (miles)')
        ax.set_ylabel('Fare Amount ($)')
        ax.set_title('Fare vs Distance')
        ax.grid(True)
        st.pyplot(fig)

    with tab2:
        st.subheader("Fare by Time of Day")
        hours = list(range(24))
        hourly_fares = [15 + 5 * np.sin((h - 8) * np.pi / 12) for h in hours]
        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(hours, hourly_fares)
        bars[hour].set_color('red')
        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Average Fare ($)')
        ax.set_title('Average Fare by Hour of Day')
        ax.set_xticks(hours)
        st.pyplot(fig)

    with tab3:
        st.subheader("Payments by Type")
        payment_labels = list(payment_options.keys())
        payment_counts = [40, 30, 5, 3, 2]
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(payment_counts, labels=payment_labels, autopct='%1.1f%%', startangle=90)
        ax.set_title('Payment Type Distribution')
        ax.axis('equal')
        st.pyplot(fig)

    # Tips and information
    st.header("Tips for Taxi Users")
    tips = [
        "The base fare for NYC green taxis is $2.50.",
        "MTA tax of $0.50 is added to all rides.",
        "Trips between 4 PM and 8 PM on weekdays (excluding holidays) include a $1.00 rush hour surcharge.",
        "There is a NYS congestion surcharge of $2.50 for trips that start, end or pass through Manhattan below 96th Street.",
        "Always ask for a receipt as proof of your trip.",
        "You can pay with credit card, cash, or via a mobile app."
    ]
    for tip in tips:
        st.markdown(f"• {tip}")

    # Disclaimer
    st.info("Note: This is a simplified model for demonstration purposes. A real model would use a trained machine learning algorithm based on historical data.")

    # Map visualization
    st.header("NYC Taxi Zone Map")
    st.write("This visualization shows the taxi zones in New York City.")
    # Placeholder for map code

if __name__ == "__main__":
    main()
