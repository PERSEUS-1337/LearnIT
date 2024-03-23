import streamlit as st
import main
import os


st.set_page_config(page_title="LearnIT Demo App", page_icon="📚", layout="wide")


def gui_options():
    global chunk_size, chunk_overlap, uploaded_file, loader_choice, llm_choice
    uploaded_file = st.file_uploader("Choose a file")

    # if uploaded_file is not None:
    #     file_path = os.path.basename(uploaded_file.name)

    col1, col2 = st.columns(2)
    with col1:
        chunk_size = int(
            st.number_input("Enter Chunk Size", step=250, min_value=500, value=500)
        )

    with col2:
        chunk_overlap = int(
            st.number_input("Enter Chunk Overlap", step=50, min_value=100)
        )

    loader_options = ["PyPDFLoader", "PyPDFium2Loader", "TextLoader"]
    loader_choice = st.selectbox(
        "Pick a loader to use (pdf or text, for prototyping)",
        options=loader_options,
        index=None,
        placeholder="Select...",
    )
    llm_options = ["gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613", "gpt-4-0613"]
    llm_choice = st.selectbox(
        "Pick OpenAI LLM to use (for prototyping)",
        options=llm_options,
        placeholder="Select...",
    )

    # return uploaded_file, chunk_size, chunk_overlap, loader_choice, llm_choice


def gui_summary(chunks, model):
    # Create a progress bar
    progress_bar = st.progress(0)

    total_chunks = len(chunks)
    for i, chunk in enumerate(chunks):
        # Update the progress bar
        progress_bar.progress((i + 1) / total_chunks)

        chunk.metadata["index"] = i
        col_original, col_processed, col_details = st.columns([2, 2, 1])
        result = main.llm_process(chunk, model)
        original_count = len(chunk.page_content)
        new_count = len(result)

        # Calculate the difference
        difference = new_count - original_count

        # Calculate the percentage
        percentage = (difference / original_count) * 100

        with col_original:
            st.caption(f"{i+1}: {chunk.page_content}\n")
            # st.caption(f"Character Count: {len(chunk.page_content)}")

        with col_processed:
            st.markdown(result)

        with col_details:
            # Display the original and new character counts
            st.metric(label="Original Character Count", value=f"{original_count} chars")
            st.metric(label="Original Character Count", value=f"{new_count} chars")

            # Display the percentage
            st.metric(
                label="Character Count Reduction",
                value=f"{percentage:.2f}%",
                delta=difference,
                delta_color="inverse",
            )

        st.divider()


def main_gui():
    st.header(
        "LearnIT: AI-Powered Learning Companion in Education Setting using Text Segmentation and Contextual Condensing"
    )
    st.write("Presented By: Aron Resty B. Ramillano and Reginald Neil Recario")
    st.caption(
        "This application aims to provide a proof of concept for the following:\n"
        "- Optimized Reading via Text Segmentation and Context Condensing\n"
        "- Proper QnA via RAG for response fidelity\n"
    )

    col1, col2 = st.columns([1, 3])

    with col1:
        gui_options()

    try:
        with col2:
            tab1, tab2, tab3 = st.tabs(
                [
                    "Raw Generated Chunks from Text",
                    "Condensed Text",
                    "Contextual Inquiry via RAG",
                ]
            )

            with tab1:
                st.header("Raw Chunks")
                if not (uploaded_file and loader_choice and llm_choice):
                    st.caption(
                        "Nothing written here yet! Make sure to upload a file first and select the proper settings"
                    )
                else:
                    file_path = os.path.basename(uploaded_file.name)
                    # global text_chunks
                    text_chunks = main.process_document(
                        file_path, chunk_size, chunk_overlap, loader_choice
                    )

                    st.text(
                        f"Chunk Size (Character Count):{chunk_size} | Chunk Overlap: {chunk_overlap}"
                    )

                    for i, chunk in enumerate(text_chunks):
                        chunk_col1, chunk_col2 = st.columns([3, 1])
                        chunk.metadata["index"] = i
                        chunk_col1.write(f"{i+1}: {chunk.page_content}\n")
                        chunk_col2.metric(
                            label=f"Character Count",
                            value=f"{len(chunk.page_content)} chars",
                        )
                        st.divider()
                        # st.metric(label="Original Character Count", value=f"{new_count} chars")

            with tab2:
                st.header("Text Segmentation and Contextual Condensing")
                if not (uploaded_file and loader_choice and llm_choice):
                    st.caption(
                        "Nothing written here yet! Make sure to upload a file first and select the proper settings"
                    )
                else:
                    proc_sum_btn = st.button("Produce Summaries!")
                    if proc_sum_btn:
                        with st.spinner("Generating Chunks"):
                            gui_summary(text_chunks, llm_choice)

            with tab3:
                st.header("Contextual Inquiry via Retrieval Augmented Generation (RAG)")
                if not (uploaded_file and loader_choice and llm_choice):
                    st.caption(
                        "Nothing written here yet! Make sure to upload a file first and select the proper settings"
                    )
                else:
                    qa_chain = main.qa_chain_setup(
                        text_chunks, llm_choice, uploaded_file.name
                    )
                    query = st.text_input("What's your question?")
                    if query:
                        with st.spinner("Looking through the database..."):
                            response = main.llm_qa_response(qa_chain, query)
                            process_llm_response(response, "PDF")
    except Exception as e:
        col2.error("An error occurred: {}".format(e))


def process_llm_response(llm_response, type):
    st.subheader("Answer:")
    st.write(f"{llm_response['result']}")
    if type == "PDF":
        st.subheader("Sources:")
        # for source in llm_response["source_documents"]:
        pages = [source.metadata["page"] for source in llm_response["source_documents"]]

        indices = [
            source.metadata["index"] for source in llm_response["source_documents"]
        ]

        st.text(f"Pages: {pages}\nIndices: {indices}")


if __name__ == "__main__":
    main_gui()

# For Chat Based Implementation
# Discontinued because of complexity

# openai.api_key = st.secrets["OPENAI_API_KEY"]
#
# if "openai_model" not in st.session_state:
#     st.session_state["openai_model"] = "gpt-3.5-turbo"
#
# # Initilize Chat History
# if "messages" not in st.session_state:
#     st.session_state.messages = []
#
# # Display Chat Messages from History on App Rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])
#
# # React to User Input
# if prompt := st.chat_input("What is up?"):
#     # Display user message in chat message container
#     with st.chat_message("user"):
#         st.markdown(prompt)
#
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})
#
#     # Display assistant response in chat message container
#     with st.chat_message("assistant", avatar="😈"):
#         message_placeholder = st.empty()
#         full_response = ""
#
#         for response in openai.ChatCompletion.create(
#             model=st.session_state["openai_model"],
#             messages=[
#                 {"role": m["role"], "content": m["content"]}
#                 for m in st.session_state.messages
#             ],
#             stream=True,
#         ):
#             full_response += response.choices[0].delta.get("content", "")
#             message_placeholder.markdown(full_response + "| ")
#         message_placeholder.markdown(full_response)
#
#     # Add assistant response to chat history
#     st.session_state.messages.append(({"role": "assistant", "content": full_response}))
#     print(st.session_state.messages)