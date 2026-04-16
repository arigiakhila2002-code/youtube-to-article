import yt_dlp
import whisper
from openai import OpenAI
import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def download_audio(youtube_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'output/audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    return "output/audio.mp3"


def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]


def generate_article(transcript):
    paragraphs = transcript.split(". ")

    article = "Artificial Intelligence - Explained\n\n"

    for p in paragraphs:
        if len(p.strip()) > 0:
            article += p.strip() + ".\n\n"

    return article


from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch

def save_pdf(text):
    doc = SimpleDocTemplate("output/article.pdf")

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="TitleStyle",
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        name="HeadingStyle",
        fontSize=16,
        leading=20,
        spaceBefore=15,
        spaceAfter=10,
    )

    body_style = ParagraphStyle(
        name="BodyStyle",
        fontSize=11,
        leading=16,
        spaceAfter=10,
    )

    story = []

    # Title Page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("Artificial Intelligence", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Generated from YouTube Video", styles["Normal"]))
    story.append(PageBreak())

    # Content
    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        if not line:
            story.append(Spacer(1, 10))
            continue

        if line.lower() in ["introduction", "applications of ai", "types of ai"]:
            story.append(Paragraph(f"<b>{line}</b>", heading_style))
        else:
            story.append(Paragraph(line, body_style))

    doc.build(story)


if __name__ == "__main__":
    url = input("Enter YouTube URL: ")

    print("Downloading...")
    audio_path = download_audio(url)

    print("Transcribing...")
    transcript = transcribe_audio(audio_path)

    print("Generating article...")
    article = generate_article(transcript)

    print("Saving PDF...")
    save_pdf(article)

    print("Done! Check output/article.pdf")