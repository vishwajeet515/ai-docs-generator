# AI Documentation Generator

Automatically generate 5 professional business documents for any organization by scraping their website using AI.

## Documents Generated
1. **Company Profile**
2. **Frequently Asked Questions (FAQ)**
3. **Services Overview**
4. **Success Stories & Proof Points**
5. **Objection Responses** (for sales teams)

## Setup

### Prerequisites
- Python 3.9+
- A free [Groq API key](https://console.groq.com)

### Local Development

1. **Clone the repo:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
   cd YOUR_REPO
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your Groq API key** to `.streamlit/secrets.toml`:
   ```toml
   GROQ_API_KEY = "your-groq-api-key-here"
   ```

4. **Run the app:**
   ```bash
   streamlit run app.py
   ```

---

## Deploy to Streamlit Community Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your GitHub repo.
3. In the deployment settings, click **"Advanced settings"** → **"Secrets"** and add:
   ```
   GROQ_API_KEY = "your-groq-api-key-here"
   ```
4. Click **Deploy!** — share the public URL with your team.
