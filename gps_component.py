import streamlit as st
import streamlit.components.v1 as components

def get_gps():
    gps_html = """
    <script>
    function sendPosition(position) {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;
        const data = lat + "," + lon;

        const streamlitEvent = new CustomEvent("streamlit:componentEvent", {
            detail: {data: data}
        });
        window.parent.document.dispatchEvent(streamlitEvent);
    }

    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(sendPosition, function(error){
                const streamlitEvent = new CustomEvent("streamlit:componentEvent", {
                    detail: {data: "error"}
                });
                window.parent.document.dispatchEvent(streamlitEvent);
            });
        } else {
            const streamlitEvent = new CustomEvent("streamlit:componentEvent", {
                detail: {data: "error"}
            });
            window.parent.document.dispatchEvent(streamlitEvent);
        }
    }

    getLocation();
    </script>
    """
    components.html(gps_html, height=0)
