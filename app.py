import streamlit as st
import os
import shutil
import tempfile
from urllib.parse import urlparse
from generate_docs import extract_text_from_url, generate_content, save_to_docx

st.set_page_config(page_title="AI Docs Generator", page_icon="📄", layout="centered")

st.title("📄 AI Documentation Generator")
st.markdown("Generate 5 professional business documents for any organization — instantly using AI.")

# Load Groq API key from Streamlit secrets (works both locally and on Streamlit Cloud)
groq_api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
if not groq_api_key:
    st.error("⚠️ GROQ_API_KEY is not configured. Please add it in `.streamlit/secrets.toml` (locally) or Streamlit Cloud Secrets settings.")
    st.stop()

url_input = st.text_input("🌐 Enter Organization Website URL:", placeholder="https://nmpartnership.com/")

if st.button("🚀 Generate Documents", type="primary"):
    if not url_input.strip():
        st.error("Please enter a valid URL.")
    else:
        try:
            raw_url = url_input.strip()
            if not raw_url.startswith("http"):
                raw_url = "https://" + raw_url
            domain = urlparse(raw_url).netloc.replace("www.", "")
            safe_domain_name = domain.split('.')[0]
            if not safe_domain_name:
                st.error("Could not parse a valid domain name from the URL.")
                st.stop()
        except Exception as e:
            st.error(f"Invalid URL: {e}")
            st.stop()

        # Use a temp directory to store generated docs (works safely on Streamlit Cloud)
        tmp_dir = tempfile.mkdtemp()
        org_folder = os.path.join(tmp_dir, safe_domain_name)
        os.makedirs(org_folder)

        progress_bar = st.progress(0)
        status_text = st.empty()

        # Step 1: Scrape
        status_text.text(f"🔍 Scraping text from {raw_url}...")
        context = extract_text_from_url(raw_url)
        progress_bar.progress(10)

        if not context:
            st.error(f"Failed to extract text from {raw_url}. Please check the URL and try again.")
            st.stop()

        titles = {
            'profile': "Company Profile",
            'faq': "Frequently Asked Questions",
            'services': "Services Overview",
            'success_stories': "Success Stories and Proof Points",
            'objection_responses': "Objection Responses"
        }

        # Step 2: Generate each document
        completed = 0
        for key, title in titles.items():
            status_text.text(f"✍️ Generating: {title}...")
            generated_text = generate_content(key, context, api_key=groq_api_key)
            save_to_docx(generated_text, org_folder, key, title)
            completed += 1
            progress_bar.progress(10 + int((completed / len(titles)) * 90))

        status_text.text("✅ All documents generated!")

        # Step 3: Create ZIP
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
