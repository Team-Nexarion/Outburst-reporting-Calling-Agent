from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
import pandas as pd
import datetime

app = Flask(__name__)
CSV_FILE = 'glacial_reports.csv'

# Helper to get the full URL dynamically
def get_base_url():
    # This ensures the agent knows its own address
    return request.host_url.rstrip('/')

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    response = VoiceResponse()
    # Use the full URL for the 'action'
    gather = Gather(num_digits=3, action=f"{get_base_url()}/handle-location")
    gather.say("Welcome to the Glacial Monitoring System. Please enter your 3-digit location code.")
    response.append(gather)
    return str(response)

@app.route("/handle-location", methods=['GET', 'POST'])
def handle_location():
    location_id = request.values.get('Digits')
    response = VoiceResponse()
    
    # Passing location to the next step
    gather = Gather(num_digits=1, action=f"{get_base_url()}/handle-condition?loc={location_id}")
    gather.say("Thank you. Press 1 for Flooding, 2 for Ice Fall, or 3 for Lake Expansion.")
    response.append(gather)
    return str(response)

@app.route("/handle-condition", methods=['GET', 'POST'])
def handle_condition():
    loc = request.args.get('loc')
    cond = request.values.get('Digits')
    response = VoiceResponse()
    
    gather = Gather(num_digits=1, action=f"{get_base_url()}/store-data?loc={loc}&cond={cond}")
    gather.say("Finally, enter severity level. Press 1 for Low, 2 for Medium, or 3 for Critical.")
    response.append(gather)
    return str(response)

@app.route("/store-data", methods=['GET', 'POST'])
def store_data():
    loc = request.args.get('loc')
    cond = request.args.get('cond')
    sev = request.values.get('Digits')
    
    # Append data to CSV
    new_row = pd.DataFrame([[datetime.datetime.now(), loc, cond, sev]])
    new_row.to_csv(CSV_FILE, mode='a', header=False, index=False)

    response = VoiceResponse()
    response.say("Report recorded successfully. Stay safe. Goodbye.")
    return str(response)

if __name__ == "__main__":
    app.run(port=5000)