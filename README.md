<p align="center">
  <h1 align="center">⚛️ ATOMIC · VISION</h1>
  <p align="center">
    <strong>AI-Powered Book Page Analyzer</strong><br/>
    Upload a photo of any book page → get instant AI insights, quotes, summaries & vocabulary.
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini 2.5 Flash"/>
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
    <img src="https://img.shields.io/badge/Tesseract-OCR-blue?style=for-the-badge" alt="Tesseract OCR"/>
    <img src="https://img.shields.io/badge/OpenCV-27338e?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV"/>
  </p>
</p>

---

## ✨ What is Atomic Vision?

**Atomic Vision** is an AI-powered web application that analyzes book page images using **Google Gemini 2.5 Flash Vision AI**. Simply snap a photo of any book page, upload it, and get rich, structured insights — all in seconds.

### 🔍 What It Extracts

| Feature | Description |
|---------|-------------|
| 📖 **Title & Author** | Automatically identifies the book title and author from the page |
| 💬 **Best Quote** | Picks the most insightful or memorable sentence from the page |
| 📝 **3-Point Summary** | Generates three concise key takeaways from the content |
| 🧠 **Context Explanation** | Explains the page's broader significance and theme |
| 📚 **Difficult Words** | Lists advanced vocabulary with definitions and difficulty scores |
| 🔤 **Raw OCR Text** | Displays the raw extracted text via Tesseract OCR |

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| **AI Engine** | Google Gemini 2.5 Flash (Vision API) |
| **Backend** | Python · FastAPI · Uvicorn |
| **Image Processing** | OpenCV · Pillow · NumPy |
| **OCR** | Tesseract OCR (via pytesseract) |
| **Frontend** | Vanilla HTML · CSS · JavaScript |
| **Fonts** | Space Grotesk · Space Mono |

---

## 📁 Project Structure

```
atomic-vision/
├── backend/
│   └── main.py              # FastAPI server, Gemini Vision integration, image preprocessing
├── frontend/
│   ├── index.html            # Main HTML page
│   ├── styles.css            # Dark/Light theme styling
│   └── app.js                # Drag-drop upload, API calls, result rendering
├── requirements.txt          # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Tesseract OCR** — [Download for Windows](https://github.com/UB-Mannheim/tesseract/wiki)
- A **Google Gemini API Key** — [Get one here](https://ai.google.dev/)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/atomic-vision.git
cd atomic-vision
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Your Gemini API Key

Open `backend/main.py` and replace the API key on **line 35**:

```python
GEMINI_API_KEY = "your-gemini-api-key-here"
```

### 5. Run the Application

```bash
python backend/main.py
```

The server will start at **`http://127.0.0.1:8000`**

### 6. Open the App

Navigate to:

```
http://127.0.0.1:8000/static/index.html
```

---

## 🖥️ How to Use

1. **Upload** — Drag & drop a book page image (or click to browse)
2. **Wait** — Gemini Vision AI analyzes the image in seconds
3. **Explore** — View the title, author, best quote, summary, context, and difficult words in the results panel

---

## 🌗 Features

- **Dark / Light Theme** — Toggle with the `◐` button in the top bar
- **Drag & Drop Upload** — Intuitive image upload experience
- **Responsive Layout** — Works on desktop and tablet screens
- **Real-time Analysis** — Instant results powered by Gemini 2.5 Flash
- **Image Preprocessing** — Automatic upscaling, sharpening, and binarization for optimal AI analysis

---

## ⚙️ Configuration

| Setting | Location | Default |
|---------|----------|---------|
| Debug mode | `backend/main.py` → `DEBUG` | `True` |
| Gemini model | `backend/main.py` → `GEMINI_MODEL` | `gemini-2.5-flash` |
| Server host | `backend/main.py` → `uvicorn.run()` | `127.0.0.1:8000` |
| Tesseract path | `backend/main.py` → `TESSERACT_PATHS` | Auto-detected |

When `DEBUG = True`, preprocessed images and raw Gemini responses are saved to the `./temp/` folder for inspection.

---

## 📦 Dependencies

```
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
opencv-python==4.8.1.78
pytesseract==0.3.10
pillow==10.1.0
numpy<2
pydantic>=2.0
google-genai>=1.0.0
```

---

## 🛣️ Roadmap

- [ ] Multi-page analysis (batch upload)
- [ ] PDF support
- [ ] Reading history & bookmarking
- [ ] Export analysis as PDF / Markdown
- [ ] Cloud deployment (Docker + Railway / Vercel)

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ and Gemini AI
</p>
