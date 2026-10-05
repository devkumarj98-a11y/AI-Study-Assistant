import streamlit as st
import streamlit.components.v1 as components
from pypdf import PdfReader
from google import genai



client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)



st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚"
)

st.title("AI Study Assistant")
st.write("Upload your study PDF and ask questions from it.")



pdf_file = st.file_uploader(
    "Choose a PDF file",
    type="pdf"
)


if pdf_file:

    st.success("PDF uploaded successfully!")

    
    reader = PdfReader(pdf_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"


    
    st.subheader("PDF Content")

    if text.strip():
        st.write(text[:3000])
    else:
        st.warning("No readable text was found in this PDF.")


    
    st.subheader("Ask a Question")

    question = st.text_input(
        "Enter your question:"
    )


    if question:

        with st.spinner("AI is thinking..."):

            
            prompt = f"""
You are an AI Study Assistant.

Answer the student's question using ONLY the information
available in the PDF content given below.

If the answer is not present in the PDF, say:

"Sorry, this information is not available in the uploaded PDF."

Explain the answer in simple language suitable for a college student.

PDF CONTENT:
{text}

STUDENT QUESTION:
{question}
"""

            try:

                
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt
                )

                answer = response.text.strip()

                st.subheader("Answer")
                st.write(answer)


                
                diagram_prompt = f"""
You are helping a college student understand a concept.

Question:
{question}

Answer:
{answer}

Decide whether a diagram or flowchart would help explain
this concept.

If a diagram is not useful, reply exactly:

NO_DIAGRAM

If a diagram is useful, create a simple Mermaid flowchart.

Rules:
- Use flowchart TD.
- Keep it simple.
- Use short labels.
- Use only simple English text inside nodes.
- Do not use special characters inside node text.
- Return only Mermaid code.
- Do not use markdown code fences.

Example format:

flowchart TD
    A[Start] --> B[First Step]
    B --> C[Second Step]
    C --> D[Result]
"""


                # Generate diagram
                diagram_response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=diagram_prompt
                )

                diagram = diagram_response.text.strip()


                # Show diagram
                if diagram != "NO_DIAGRAM":

                    diagram = diagram.replace(
                        "```mermaid",
                        ""
                    )

                    diagram = diagram.replace(
                        "```",
                        ""
                    )

                    diagram = diagram.strip()

                    st.subheader("Diagram")


                    # Display Mermaid diagram
                    html = f"""
                    <!DOCTYPE html>
                    <html>

                    <head>
                        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>

                        <script>
                            mermaid.initialize({{
                                startOnLoad: true,
                                theme: "default"
                            }});
                        </script>
                    </head>

                    <body>

                        <div class="mermaid">
                        {diagram}
                        </div>

                    </body>

                    </html>
                    """

                    components.html(
                        html,
                        height=450,
                        scrolling=True
                    )


            except Exception as e:

                st.error("Something went wrong.")
                st.write(e)