
import time
import streamlit as st
from openai import OpenAI






# --- Main App ---
st.title("Inferencing with vLLM and Google TPUs")



# Set OpenAI API key from Streamlit secrets
client = OpenAI(base_url="http://35.200.86.219:8000/v1", api_key='no-key')

st.markdown('<style>' + open('styles.css').read() + '</style>', unsafe_allow_html=True)

#Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "Qwen/Qwen2.5-32B"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Generating..."):
            def get_streamed_completion(completion_generator):
                start = time.time()
                tokcount = 0
                first_token_time = 0
                for chunk in completion_generator:
                    if tokcount == 0:
                        first_token_time = time.time()
                    tokcount += 1
                    if len(chunk.choices):
                        yield chunk.choices[0].delta.content
                
                end = time.time()
                ttft = first_token_time - start if first_token_time > 0 else 0
                tok_per_sec = tokcount / (end - start) if end > start else 0
                st.sidebar.metric("Time to First Token", f"{ttft:.2f}s")
                st.sidebar.metric("Average Tokens per second", f"{tok_per_sec:.2f}")

            try:
                response = st.write_stream(
                    get_streamed_completion(
                        client.chat.completions.create(
                            model=st.session_state["openai_model"],
                            messages=[
                             {"role": m["role"], "content": m["content"]}
                             for m in st.session_state.messages
                            ],
                            stream=True,
                            stream_options={"include_usage": True}
                            )
                        )
                    )
            except Exception as e:
                response = st.error(f"Error: {e}")
                print(e)

    st.session_state.messages.append({"role": "assistant", "content": response})


