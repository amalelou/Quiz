from flask import Flask, render_template, request, redirect, url_for
import speech_recognition as sr
import os
from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
from google.oauth2 import service_account
from googleapiclient.discovery import build
import openai
import os

print(os.chdir('path/to/credentials'))


openai.api_key = "sk-***********************************"
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/forms', 'https://www.googleapis.com/auth/drive'])
app = Flask(__name__)
app.debug = True 
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    # Access the uploaded audio file
    audio_file = request.files['audio_file']

    # Save the audio file to a temporary location
    audio_file.save('temp.wav')

    # Perform audio transcription
    r = sr.Recognizer()
    with sr.AudioFile('temp.wav') as source:
        audio = r.record(source)
        transcription = r.recognize_google(audio)

    # Remove the temporary audio file
    os.remove('temp.wav')

    # Return the transcription result
    return redirect(url_for('generate_form', transcription=transcription))
@app.route('/generate', methods=['POST', 'GET'])
def generate_form():
    transcription = request.args.get('transcription')
    print(transcription)
    NEW_FORM = {
        "info": {
            "title": transcription,
        }
    }
    service = build('forms', 'v1', credentials=credentials)
    form = service.forms().create(
        body=NEW_FORM 
    ).execute()
    
    for i in range(10):
        input_text = "Generate a multiple-choice question about: {}, with the options: A: , B: , C: , D: ".format(transcription)

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=input_text,
            max_tokens=100,
            temperature=0.7,
            n=1,
            stop=None,
        )

        question = response['choices'][0].text.strip()
        parts = question.split('\n')
        print("Parts:", parts)
        

        if len(parts) >= 5:

            NEW_QUESTION = {
                "requests": [{
                    "createItem": {
                        "item": {
                            "title": parts[0],
                            "questionItem": {
                                "question": {
                                    "required": True,
                                    "choiceQuestion": {
                                        "type": "RADIO",
                                        "options": [
                                            {"value": parts[1]},
                                            {"value": parts[2]},
                                            {"value": parts[3]},
                                            {"value": parts[4]}
                                        ],
                                        "shuffle": True
                                        }
                                    }
                                },
                            },
                        "location": {
                        "index": 0
                        }
                    }
                }]
            }
            print("NEW_QUESTION:", NEW_QUESTION)
            question_setting = service.forms().batchUpdate(formId = form['formId'], body = NEW_QUESTION).execute()
            get_result = service.forms().get(formId=form["formId"]).execute()
        
    return render_template('login.html', output = get_result['responderUri'], transcription=transcription)
if __name__ == '__main__':
    app.run()