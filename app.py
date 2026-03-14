import streamlit as st
import os
import shutil
import tempfile
from urllib.parse import urlparse
from generate_docs import (
    extract_text_from_url,
    extract_text_from_pptx,
    extract_text_from_pdf,
    generate_content,
    save_to_docx
)

st.set_page_config(page_title="AI Docs Generator", page_icon="📄", layout="centered")

st.title("📄 AI Documentation Generator")
st.markdown("Generate 5 professional business documents for any organization — using AI powered by the company website and/or an uploaded presentation.")

# Load Groq API key from Streamlit secrets (works both locally and on Streamlit Cloud)
try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except (KeyError, FileNotFoundError):
    groq_api_key = os.environ.get("GROQ_API_KEY", "")

if not groq_api_key:
    st.error("⚠️ GROQ_API_KEY is not configured. Please add it in `.streamlit/secrets.toml` (locally) or Streamlit Cloud Secrets settings.")
    st.stop()

# --- Inputs ---
url_input = st.text_input("🌐 Organization Website URL (optional):", placeholder="https://nmpartnership.com/")
uploaded_file = st.file_uploader(
    "📎 Upload a PPT or PDF (optional):",
    type=["pptx", "pdf"],
    help="Upload a company presentation or document to supplement the website content."
)

st.caption("💡 You can provide a URL, a file, or both — the AI will combine all available information.")

if st.button("🚀 Generate Documents", type="primary"):

    if not url_input.strip() and uploaded_file is None:
        st.error("Please provide at least a URL or upload a file.")
        st.stop()

    # Parse organization name
    safe_domain_name = "organization"
    if url_input.strip():
        try:
            raw_url = url_input.strip()
            if not raw_url.startswith("http"):
                raw_url = "https://" + raw_url
            domain = urlparse(raw_url).netloc.replace("www.", "")
            name = domain.split('.')[0]
            if name:
                safe_domain_name = name
        except Exception:
            pass
    elif uploaded_file:
        # Use filename without extension as org name
        safe_domain_name = os.path.splitext(uploaded_file.name)[0].replace(" ", "_").lower()

    tmp_dir = tempfile.mkdtemp()
    org_folder = os.path.join(tmp_dir, safe_domain_name)
    os.makedirs(org_folder)

    progress_bar = st.progress(0)
    status_text = st.empty()
    combined_context = ""

    # Step 1: Scrape website (if URL provided)
    if url_input.strip():
        status_text.text(f"🔍 Scraping text from {url_input.strip()}...")
        web_text = extract_text_from_url(url_input.strip())
        if web_text:
            combined_context += "=== FROM WEBSITE ===\n" + web_text
        else:
            st.warning(f"⚠️ Could not extract text from the URL. Using uploaded file only.")

    progress_bar.progress(15)

    # Step 2: Extract text from uploaded file (if provided)
    if uploaded_file is not None:
        status_text.text(f"📂 Reading uploaded file: {uploaded_file.name}...")
        file_bytes = uploaded_file.read()
        if uploaded_file.name.endswith(".pptx"):
            file_text = extract_text_from_pptx(file_bytes)
        else:
            file_text = extract_text_from_pdf(file_bytes)

        if file_text:
            combined_context += "\n\n=== FROM UPLOADED FILE ===\n" + file_text
        else:
            st.warning(f"⚠️ Could not extract text from the uploaded file.")

    progress_bar.progress(25)

    if not combined_context.strip():
        st.error("No content could be extracted from the provided URL or file. Please try again with a different source.")
        st.stop()

    titles = {
        'profile': "Company Profile",
        'faq': "Frequently Asked Questions",
        'services': "Services Overview",
        'success_stories': "Success Stories and Proof Points",
        'objection_responses': "Objection Responses"
    }

    # Step 3: Generate each document
    completed = 0
    for key, title in titles.items():
        status_text.text(f"✍️ Generating: {title}...")
        generated_text = generate_content(key, combined_context, api_key=groq_api_key)
        save_to_docx(generated_text, org_folder, key, title)
        completed += 1
        progress_bar.progress(25 + int((completed / len(titles)) * 75))

    status_text.text("✅ All documents generated!")

    # Step 4: Create ZIP
    zip_path = os.path.join(tmp_dir, f"{safe_domain_name}_docs")
    shutil.make_archive(zip_path, 'zip', org_folder)
    zip_file = zip_path + ".zip"

    st.success(f"✅ 5 documents generated for **{safe_domain_name}**!")
    st.balloons()

    with open(zip_file, "rb") as fp:
        st.download_button(
            label="📥 Download All Documents (ZIP)",
            data=fp,
            file_name=f"{safe_domain_name}_docs.zip",
            mime="application/zip",
            type="primary"
        )

st.markdown("---")
st.caption("Powered by Groq AI (Llama 3.3) • Built with Streamlit")
