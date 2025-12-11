# main.py
import streamlit as st
from voice import listen, speak, speak_eng
from outdoor_nav import get_outdoor_route
from indoor_nav import get_indoor_route
from poi_search import search_poi
from object_detection import ObjectDetector
from tracker import NavigatorTracker
from gps_simulator import GPSSimulator
import time
import re

st.set_page_config(page_title="Blind Navigation Assistant", layout="wide")

# ------------------- SESSION STATE -------------------
if "detector" not in st.session_state:
    st.session_state.detector = ObjectDetector()
if "tracker" not in st.session_state:
    st.session_state.tracker = None

# ------------------- UI -------------------
st.title("🦮 Blind Navigation Assistant")
st.write("App for voice navigation assistance.")
mode = st.radio("Choose mode:", ["Outdoor (street)", "Indoor (shopping mall)"])

FAKE_GPS = (43.238949, 76.889709)  # starting point for simulation

# ------------------- MAIN VOICE INPUT -------------------
if st.button("🎤 Where are you going?"):
    try:
        speak("I'm listening to you. Where do you want to go?")
        user_text = listen()
        st.write("You said:", user_text)

        # ---- POI SEARCH ----
        poi = search_poi(user_text)
        if not poi:
            speak("Sorry, I didn't find this place.")
            st.stop()
        st.write("Found:", poi)

        # ---- ROUTE BUILDING ----
        if mode == "Outdoor (street)":
            speak(f"Building path to {poi['name']}")
            lat0, lon0 = FAKE_GPS
            route = get_outdoor_route(lat0, lon0, poi["lat"], poi["lon"], mode="walking")
            steps = route["routes"][0]["legs"][0]["steps"]
        else:
            speak(f"Building path to {poi['name']}")
            route = get_indoor_route(poi)
            steps = route["steps"]

        st.json(route)
        speak("Listen to instructions.")

        # ------------------- START OBJECT DETECTOR -------------------
        detector = st.session_state.detector
        detector.start()
        speak("Object detection is turned on.")

        # ------------------- LIVE OBJECT FEED -------------------
        st.write("### Live object detection feed:")
        frame_placeholder = st.empty()
        start_time = time.time()
        while time.time() - start_time < 5:
            if detector.last_frame is not None:
                frame_placeholder.image(detector.last_frame, channels="BGR")
            time.sleep(0.03)

        # ------------------- START TRACKER -------------------
        tracker = NavigatorTracker(steps)
        if st.session_state.tracker:
            st.session_state.tracker.stop()
        st.session_state.tracker = tracker
        tracker.start()

        # ------------------- SIMULATED GPS -------------------
        route_coords = [
                # Start moving normally
                (43.2389, 76.8897),
                (43.23895, 76.8896),
                (43.2390, 76.8895),
                (43.2391, 76.8893),
                (43.2392, 76.8891),

                # Slight deviation to the left (off-route)
                (43.23925, 76.8890),
                (43.2393, 76.8889),

                # Back on track
                (43.2394, 76.8882),
                (43.2395, 76.8880),

                # Standing still to trigger stop detection
                (43.2395, 76.8880),
                (43.2395, 76.8880),
                (43.2395, 76.8880),

                # Resume moving to next step
                (43.2396, 76.8878),
                (43.2397, 76.8875),
                (43.2398, 76.8870),
                (43.2399, 76.8867),
                (43.2400, 76.8865),

                # Small back-and-forth to check repeated instructions
                (43.23995, 76.8866),
                (43.2400, 76.8865),
                (43.23998, 76.88655),
                (43.2400, 76.8865),

                # Standing still to trigger stop detection
                (43.2395, 76.8880),
                (43.2395, 76.8880),
                (43.2395, 76.8880),
                (43.2395, 76.8880),
                (43.2395, 76.8880),
                (43.2395, 76.8880),
                (43.2395, 76.8880),
                (43.2395, 76.8880),
                (43.2395, 76.8880),
                (43.2395, 76.8880),
                (43.2395, 76.8880),
                (43.2395, 76.8880),
                (43.2395, 76.8880),
                (43.2395, 76.8880),
                (43.2395, 76.8880)
            ]

        gps_sim = GPSSimulator(route_coords, interval=3)
        for lat, lon in gps_sim.start():
            st.session_state["gps_data"] = f"{lat},{lon}"
            st.write("Simulated GPS:", lat, lon)

            if st.session_state.tracker:
                st.session_state.tracker.update_position(lat, lon)

                # Check if user is standing still
                if getattr(tracker, "_stopped", False):
                    speak_eng("It seems you are standing still for a long time. Do you want to stop the navigation?")

                    user_answer = listen()
                    st.write("You said:", user_answer)

                    if "yes" in user_answer.lower():
                        speak_eng("Navigation stopped.")
                        tracker.stop()
                        break
                    else:
                        speak_eng("Continuing navigation.")
                        tracker._stopped = False


    except Exception as e:
        try:
            speak_eng("Sorry, something is wrong.")
        except:
            pass
        st.error(f"Error: {e}")
