import matplotlib.pyplot as plt
import pandas as pd
import json
import threading
import queue
import time
from datetime import datetime
import paho.mqtt.client as mqtt

# Queue to safely pass data between threads
update_queue = queue.Queue()

# Callback for when a message is received
def on_message(client, userdata, msg):
    try:
        # Decode the payload
        payload = str(msg.payload.decode("utf-8"))
        print(f"Received message: {payload}")
        # Add the data to the queue
        update_queue.put((datetime.now(), payload))
    except Exception as e:
        print(f"Error processing message: {e}")

# Function to process queue and update the plot
def update_plot():
    data = []

    # Initialize the plot
    plt.ion()
    plt.figure()
    plt.show()

    while True:
        # Process all items in the queue
        while not update_queue.empty():
            timestamp, sensor_data = update_queue.get()
            data.append((timestamp, sensor_data))
            if len(data) > 100:  # Keep only the last 100 points
                data.pop(0)

        # Update the plot
        if data:
            df = pd.DataFrame(data, columns=["timestamp", "sensor_data"])
            # Parse the sensor data JSON
            df["temperature"] = df["sensor_data"].apply(lambda x: json.loads(x)["temperature"])
            df["humidity"] = df["sensor_data"].apply(lambda x: json.loads(x)["humidity"])
            plt.clf()  # Clear the current figure
            plt.plot(df["timestamp"], df["temperature"], label="Temperature")
            plt.plot(df["timestamp"], df["humidity"], label="Humidity")
            plt.legend()
            plt.draw()  # Redraw the figure
            plt.pause(0.1)  # Pause to refresh the display

        time.sleep(0.5)  # Sleep for a short time to avoid busy-waiting

# MQTT client setup
client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1884)  # Update port if needed
client.subscribe("sensor/data")

# Start the MQTT client in a separate thread
threading.Thread(target=client.loop_forever, daemon=True).start()

# Start the plot update loop in the main thread
update_plot()
