import streamlit as st 
import json
import logging
import os
import sys
import time
from pathlib import Path
 
import requests

st.title("Text to speech Avatar using Streamlit")

#st.markdown('## Key Metrics')

logging.basicConfig(stream=sys.stdout, level=logging.INFO,  # set to logging.DEBUG for verbose output
        format="[%(asctime)s] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p %Z")
logger = logging.getLogger(__name__)
 
# Your Speech resource key and region
# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
 
SUBSCRIPTION_KEY = os.getenv("SUBSCRIPTION_KEY", '381744472c174221b178ad4e561a4c60')
SERVICE_REGION = os.getenv("SERVICE_REGION", "westus2")
 
NAME = "Simple avatar synthesis"
DESCRIPTION = "Simple avatar synthesis description"
 
# The service host suffix.
SERVICE_HOST = "customvoice.api.speech.microsoft.com"

#changes
def clear_submit():
    st.session_state["submit"] = False

def submit_synthesis(query,avatar,voice):
    url = f'https://{SERVICE_REGION}.{SERVICE_HOST}/api/texttospeech/3.1-preview1/batchsynthesis/talkingavatar'
    header = {
        'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY,
        'Content-Type': 'application/json'
    }
 
    payload = {
        'displayName': NAME,
        'description': DESCRIPTION,
        "textType": "PlainText",
        'synthesisConfig': {
            "voice": voice,
        },
        # Replace with your custom voice name and deployment ID if you want to use custom voice.
        # Multiple voices are supported, the mixture of custom voices and platform voices is allowed.
        # Invalid voice name or deployment ID will be rejected.
        'customVoices': {
            # "YOUR_CUSTOM_VOICE_NAME": "YOUR_CUSTOM_VOICE_ID"
        },
        "inputs": [
            {
                "text": query,
            },
        ],        "properties": {
            "customized": False, # set to True if you want to use customized avatar
            "talkingAvatarCharacter": avatar,  # talking avatar character
            "talkingAvatarStyle": "graceful-sitting",  # talking avatar style, required for prebuilt avatar, optional for custom avatar
            "videoFormat": "mp4",  # mp4 or webm, webm is required for transparent background
            "videoCodec": "vp9",  # hevc, h264 or vp9, vp9 is required for transparent background; default is hevc
            "subtitleType": "soft_embedded",
            "backgroundColor": "transparent",
        }
    }
    response = requests.post(url, json.dumps(payload), headers=header)
    st.info('All good 1')
    #if response.status_code < 400:
    #    logger.info('Batch avatar synthesis job submitted successfully')
    #    logger.info(f'Job ID: {response.json()["id"]}')
    return response.json()["id"]
    #else:
    #    logger.error(f'Failed to submit batch avatar synthesis job: {response.text}')
 
if __name__ == '__main__':
    query = st.text_area("Type a sentence ", value= "Hi, I'm a virtual assistant created by Microsoft.", on_change=clear_submit)
    
    col1, col2= st.columns(2)
    
    with col1:
        avatar = st.radio('Select an avatar character:', key="visibility", options=["lisa"],)
    
    with col2:
        voice = st.selectbox('Select voice:', ('en-US-JennyNeural', 'en-US-GuyNeural', 'en-US-AriaNeural', 'en-US-DavisNeural', 'en-US-AmberNeural', 'en-US-AndrewNeural', 'en-US-AshleyNeural', 'en-US-BrandonNeural','en-US-BrianNeural', 'en-US-ChristopherNeural','en-US-CoraNeural','en-US-ElizabethNeural','en-US-EmmaNeural','en-US-EricNeural','en-US-JacobNeural','en-US-JaneNeural','en-US-JasonNeural','en-US-MichelleNeural','en-US-MonicaNeural'),)
    
    generate = st.button('Generate video')
    
    if generate or st.session_state.get("submit"):
        if not query:
            st.error("Please enter a statement!")
        else:
            st.session_state["submit"] = True
            
            job_id = submit_synthesis(query,avatar,voice)
            st.info('All good 2')
            if job_id is not None:
                timeout = time.time() +120 #set a timeout of 2 minutes
                while time.time() < timeout:
                    st.info('All good 3')
                    url = f'https://{SERVICE_REGION}.{SERVICE_HOST}/api/texttospeech/3.1-preview1/batchsynthesis/talkingavatar/{job_id}' 
                    header = {'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY}
                    response = requests.get(url, headers=header)
                    if response.status_code < 400:
                        st.info('All good 4')
                        logger.debug('Get batch synthesis job successfully')
                        logger.debug(response.json())
                        if response.json()['status'] == 'Succeeded':
                            logger.info(f'Batch synthesis job succeeded, download URL: {response.json()["outputs"]["result"]}')
                            st.info(f'Batch synthesis job succeeded, download URL: {response.json()["outputs"]["result"]}')
                            url1 = response.json()["outputs"]["result"]
                    else:
                        st.error(f'Failed to get batch synthesis job: {response.text}')
                    
                    
                    status = response.json()['status']

                    st.info('All good 5')
                    if status == 'Succeeded':
                        #logger.info('batch avatar synthesis job succeeded')
                        st.info('All good 6')
                        st.video(url1,format="mp4")
                        break
                    elif status == 'Failed':
                        st.error('Batch avatar synthesis job failed')
                        break
                    else:
                        st.info('All good 7')
                        st.info(f'batch avatar synthesis job is still running, status [{status}]')
                        time.sleep(10)
                else:
                    st.error('Timeout: Batch avatar synthesis job took too long')
