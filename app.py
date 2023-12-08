# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit.logger import get_logger
import openai
import time


LOGGER = get_logger(__name__)


st.set_page_config(layout="wide", initial_sidebar_state="collapsed")



# Set your OpenAI Assistant ID here
assistant_id = 'asst_lTBM6xP6R035vIYpDLldY0Uc'


# Initialize the OpenAI client (ensure to set your API key in the sidebar within the app)
client = openai
client.api_key = "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"
# Initialize session state variables for file IDs and chat control

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

#A dictionary to track each chat's history:
if "chats" not in st.session_state:
    st.session_state.chats = {}



def home_page():
    st.title("MonkeyDonky veelgestelde vragen assistent")
    st.write("Stel hier jouw vraag en ik probeer jou zo goed mogelijk te helpen :)")


    # button to start the chat session

    st.session_state.start_chat = True
    # create a thread once and store its id in session state
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id





    # initialize the model and messages list if not already in session state
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-3.5-turbo-1106"
    if "messages" not in st.session_state.keys(): # Initialize the chat messages history
        st.session_state.messages = [
        {"role": "assistant", "content": "Hoe kan ik jou helpen?"}
    ]

    # display existing messages in the chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # chat input for the user
    if prompt := st.chat_input("type hier jouw vraag?"):
        # add user message to the state and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # add the user's message to the existing thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        with st.spinner('openai is generating a response...'):
            run = client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=assistant_id,
                instructions=""
            )




            # poll for the run to complete and retrieve the assistant's messages
            while run.status != 'completed':
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )

            # retrieve messages added by the assistant
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )

            # process and display assistant messages
            assistant_messages_for_run = [
                message for message in messages
                if message.run_id == run.id and message.role == "assistant"
            ]
            for message in assistant_messages_for_run:
                full_response = message.content[0].text.value
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                with st.chat_message("assistant"):
                    st.markdown(full_response, unsafe_allow_html=True)



        if st.button('clear chat'):
            clear_chat()
            st.experimental_rerun()  # optional: rerender the page to reflect changes


def main():
    home_page()

def clear_chat():
    st.session_state.messages = []




if __name__ == '__main__':
    main()


