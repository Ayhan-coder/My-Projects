from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os

# Create PDF
pdf_filename = "homework1.pdf"
doc = SimpleDocTemplate(pdf_filename, pagesize=letter,
                        rightMargin=0.75*inch, leftMargin=0.75*inch,
                        topMargin=0.75*inch, bottomMargin=0.75*inch)

# Container for PDF elements
elements = []

# Define styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.black,
    spaceAfter=30,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=16,
    textColor=colors.black,
    spaceAfter=12,
    spaceBefore=12,
    fontName='Helvetica-Bold'
)

subheading_style = ParagraphStyle(
    'CustomSubHeading',
    parent=styles['Heading3'],
    fontSize=13,
    textColor=colors.black,
    spaceAfter=10,
    spaceBefore=10,
    fontName='Helvetica-Bold'
)

normal_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=11,
    alignment=TA_JUSTIFY,
    spaceAfter=8
)

# ========== TITLE PAGE ==========
elements.append(Spacer(1, 1.5*inch))
elements.append(Paragraph("CMPE 362 - Homework 1", title_style))
elements.append(Paragraph("Simple Audio Analysis", title_style))

elements.append(Spacer(1, 0.8*inch))
elements.append(Paragraph("Student Name: <b>[FILL IN YOUR NAME]</b>", normal_style))
elements.append(Spacer(1, 0.3*inch))
elements.append(Paragraph("Student ID: <b>[FILL IN YOUR ID]</b>", normal_style))
elements.append(Spacer(1, 1*inch))
elements.append(Paragraph("Spring 2026", normal_style))
elements.append(Spacer(1, 0.3*inch))
elements.append(Paragraph("Department of Computer Engineering<br/>Bogazici University", normal_style))

elements.append(PageBreak())

# ========== SPECTROGRAMS SECTION ==========
elements.append(Paragraph("Spectrograms", heading_style))
elements.append(Spacer(1, 0.2*inch))

# Low Pitch Spectrogram
elements.append(Paragraph("Low Pitch - Spectrogram", subheading_style))
if os.path.exists("low_pitch_spectrogram.png"):
    img = Image("low_pitch_spectrogram.png", width=6.5*inch, height=4.5*inch)
    elements.append(img)
    elements.append(Paragraph("<i>Figure 1: Spectrogram of low_pitch.wav showing the frequency content over time. Identify the dominant red horizontal line to determine the fundamental frequency.</i>", 
                             ParagraphStyle('figcaption', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, textColor=colors.grey)))
elements.append(PageBreak())

# High Pitch Spectrogram
elements.append(Paragraph("High Pitch - Spectrogram", subheading_style))
if os.path.exists("high_pitch_spectrogram.png"):
    img = Image("high_pitch_spectrogram.png", width=6.5*inch, height=4.5*inch)
    elements.append(img)
    elements.append(Paragraph("<i>Figure 2: Spectrogram of high_pitch.wav showing the frequency content over time. The bright red band indicates the fundamental frequency.</i>", 
                             ParagraphStyle('figcaption', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, textColor=colors.grey)))
elements.append(PageBreak())

# Whistle Spectrogram
elements.append(Paragraph("Whistle - Spectrogram", subheading_style))
if os.path.exists("whistle_spectrogram.png"):
    img = Image("whistle_spectrogram.png", width=6.5*inch, height=4.5*inch)
    elements.append(img)
    elements.append(Paragraph("<i>Figure 3: Spectrogram of whistle.wav showing a narrow, clean frequency band characteristic of a whistle sound.</i>", 
                             ParagraphStyle('figcaption', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, textColor=colors.grey)))
elements.append(PageBreak())

# Complex Spectrogram
elements.append(Paragraph("Complex Melody - Spectrogram", subheading_style))
if os.path.exists("complex_spectrogram.png"):
    img = Image("complex_spectrogram.png", width=6.5*inch, height=4.5*inch)
    elements.append(img)
    elements.append(Paragraph("<i>Figure 4: Spectrogram of complex.wav showing the melody structure with multiple notes and their harmonic content.</i>", 
                             ParagraphStyle('figcaption', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, textColor=colors.grey)))
elements.append(PageBreak())

# ========== AUTOCORRELATION SECTION ==========
elements.append(Paragraph("Autocorrelation Analysis", heading_style))
elements.append(Spacer(1, 0.2*inch))

# Low Pitch Autocorrelation
elements.append(Paragraph("Low Pitch - Autocorrelation", subheading_style))
if os.path.exists("low_pitch_autocorr.png"):
    img = Image("low_pitch_autocorr.png", width=6.5*inch, height=3.5*inch)
    elements.append(img)
    elements.append(Paragraph("<i>Figure 5: Autocorrelation of low_pitch.wav. The first peak after the center indicates the period of the fundamental frequency. Use: f = 1/T where T is the lag at the first peak.</i>", 
                             ParagraphStyle('figcaption', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, textColor=colors.grey)))
elements.append(PageBreak())

# High Pitch Autocorrelation
elements.append(Paragraph("High Pitch - Autocorrelation", subheading_style))
if os.path.exists("high_pitch_autocorr.png"):
    img = Image("high_pitch_autocorr.png", width=6.5*inch, height=3.5*inch)
    elements.append(img)
    elements.append(Paragraph("<i>Figure 6: Autocorrelation of high_pitch.wav showing the periodicity. The spacing of peaks reveals the fundamental frequency period.</i>", 
                             ParagraphStyle('figcaption', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, textColor=colors.grey)))
elements.append(PageBreak())

# Whistle Autocorrelation
elements.append(Paragraph("Whistle - Autocorrelation", subheading_style))
if os.path.exists("whistle_autocorr.png"):
    img = Image("whistle_autocorr.png", width=6.5*inch, height=3.5*inch)
    elements.append(img)
    elements.append(Paragraph("<i>Figure 7: Autocorrelation of whistle.wav. The clear, distinct peaks indicate a strong, pure tone with a well-defined fundamental frequency.</i>", 
                             ParagraphStyle('figcaption', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, textColor=colors.grey)))
elements.append(PageBreak())

# Complex Autocorrelation
elements.append(Paragraph("Complex Melody - Autocorrelation", subheading_style))
if os.path.exists("complex_autocorr.png"):
    img = Image("complex_autocorr.png", width=6.5*inch, height=3.5*inch)
    elements.append(img)
    elements.append(Paragraph("<i>Figure 8: Autocorrelation of complex.wav showing multiple pitch components from the melody sequence.</i>", 
                             ParagraphStyle('figcaption', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, textColor=colors.grey)))
elements.append(PageBreak())

# ========== FUNDAMENTAL FREQUENCY ANALYSIS ==========
elements.append(Paragraph("Fundamental Frequency Analysis", heading_style))
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph("From visual inspection of the spectrograms and autocorrelation plots, the fundamental frequencies have been identified as follows:", normal_style))
elements.append(Spacer(1, 0.3*inch))

elements.append(Paragraph("Low Pitch Audio", subheading_style))
elements.append(Paragraph("<b>From Spectrogram:</b><br/>The dominant red horizontal band is located at approximately <b>[FILL IN Hz]</b><br/>This corresponds to note: <b>[FILL IN note name]</b><br/><br/><b>From Autocorrelation:</b><br/>The first peak occurs at a lag of approximately <b>[FILL IN ms/s]</b><br/>Fundamental frequency: f = 1/T = <b>[FILL IN Hz]</b>", normal_style))
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph("High Pitch Audio", subheading_style))
elements.append(Paragraph("<b>From Spectrogram:</b><br/>The dominant red band is at approximately <b>[FILL IN Hz]</b><br/>This corresponds to note: <b>[FILL IN note name]</b><br/><br/><b>From Autocorrelation:</b><br/>The first peak occurs at a lag of approximately <b>[FILL IN ms/s]</b><br/>Fundamental frequency: f = 1/T = <b>[FILL IN Hz]</b>", normal_style))
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph("Whistle Audio", subheading_style))
elements.append(Paragraph("<b>From Spectrogram:</b><br/>The narrow, clean band is at approximately <b>[FILL IN Hz]</b><br/>This corresponds to note: <b>[FILL IN note name]</b><br/><br/><b>From Autocorrelation:</b><br/>The first peak occurs at a lag of approximately <b>[FILL IN ms/s]</b><br/>Fundamental frequency: f = 1/T = <b>[FILL IN Hz]</b>", normal_style))
elements.append(PageBreak())

# ========== COMPARISON ==========
elements.append(Paragraph("Comparison: Spectrogram vs Autocorrelation Methods", heading_style))
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph("Method Comparison", subheading_style))
elements.append(Paragraph("<b>Spectrogram Method</b>", normal_style))
elements.append(Paragraph("<b>Advantages:</b><br/>" +
                         "• Visually shows frequency content over time<br/>" +
                         "• Easy to identify obvious peaks<br/>" +
                         "• Shows harmonic structure<br/>" +
                         "• Good for single-pitch sustained notes<br/><br/>" +
                         "<b>Challenges:</b><br/>" +
                         "• Harmonic content can be confusing<br/>" +
                         "• Requires careful visual inspection<br/>" +
                         "• Resolution depends on window parameters", normal_style))

elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph("<b>Autocorrelation Method</b>", normal_style))
elements.append(Paragraph("<b>Advantages:</b><br/>" +
                         "• Based on signal periodicity (more robust)<br/>" +
                         "• Less affected by harmonics<br/>" +
                         "• Quantitative (measurable lag values)<br/><br/>" +
                         "<b>Challenges:</b><br/>" +
                         "• Requires careful lag measurement<br/>" +
                         "• Can be noisy with weak signals<br/>" +
                         "• Interpretation requires understanding of periodicity", normal_style))

elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph("Results Summary", subheading_style))

# Create comparison table
table_data = [
    ["Audio", "Spectrogram (Hz)", "Autocorr (Hz)", "Difference"],
    ["Low Pitch", "[FILL IN]", "[FILL IN]", "[FILL IN]"],
    ["High Pitch", "[FILL IN]", "[FILL IN]", "[FILL IN]"],
    ["Whistle", "[FILL IN]", "[FILL IN]", "[FILL IN]"]
]

table = Table(table_data, colWidths=[1.3*inch, 1.5*inch, 1.5*inch, 1.2*inch])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 11),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))
elements.append(table)

elements.append(Spacer(1, 0.3*inch))
elements.append(Paragraph("<b>Observations and Comments:</b><br/><br/>[FILL IN YOUR COMPARISON ANALYSIS - 2-3 paragraphs describing the agreement or differences between the two methods, and any insights about the accuracy and reliability of each approach]", normal_style))

elements.append(PageBreak())

# ========== COMPLEX SIGNAL ANALYSIS ==========
elements.append(Paragraph("Complex Signal Analysis", heading_style))
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph("Fundamental Frequency of Complex Signals", subheading_style))

elements.append(Paragraph("<b>What does fundamental frequency mean for complex.wav?</b><br/><br/>" +
                         "The complex.wav file contains a melody consisting of a sequence of discrete musical notes. Unlike the previous single-note recordings, this signal is fundamentally different:<br/><br/>" +
                         "<b>Single Notes vs Melody:</b> The previous audio files contained sustained notes with one fundamental frequency. Complex.wav switches between different notes over time.<br/><br/>" +
                         "<b>Time-Varying Pitch:</b> The fundamental frequency changes as the melody progresses, making a single fundamental frequency value meaningless.<br/><br/>" +
                         "<b>Interpretation:</b> For complex.wav, we cannot define 'the' fundamental frequency. Instead, we must identify:<br/>" +
                         "• The <b>fundamental frequency of each note</b> in the sequence<br/>" +
                         "• The <b>timing/duration</b> of each note<br/>" +
                         "• The <b>sequence</b> of notes that compose the melody", normal_style))

elements.append(Spacer(1, 0.3*inch))

# Extracted notes table
elements.append(Paragraph("Notes Extracted from complex.wav", subheading_style))

notes_data = [
    ["Note#", "Freq (Hz)", "Duration (s)", "Note"],
    ["1", "375", "0.811", "A4"],
    ["2", "117", "1.067", "C#2"],
    ["3", "281", "0.597", "E3"],
    ["4", "188", "0.139", "A3"],
    ["5", "375", "0.224", "A4"],
    ["6", "281", "0.192", "E3"],
    ["7", "117", "0.267", "C#2"],
    ["8", "188", "0.235", "A3"],
    ["9", "117", "0.107", "C#2"],
    ["10", "375", "0.213", "A4"],
    ["11", "188", "0.181", "A3"],
    ["12", "117", "0.192", "C#2"],
    ["13", "188", "0.395", "A3"]
]

notes_table = Table(notes_data, colWidths=[0.8*inch, 1*inch, 1.2*inch, 0.8*inch])
notes_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))
elements.append(notes_table)

elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph("[FILL IN YOUR ANALYSIS - 1-2 paragraphs discussing what this melody might represent, any patterns you notice, and whether the extracted notes match the original melody]", normal_style))

elements.append(PageBreak())

# ========== RECREATION ANALYSIS ==========
elements.append(Paragraph("Complex Melody Recreation", subheading_style))
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph("Using the extracted notes, a synthetic melody was recreated using pure sinusoids. The figure below shows a side-by-side comparison of the original and recreated spectrograms.", normal_style))

elements.append(Spacer(1, 0.2*inch))
if os.path.exists("complex_comparison.png"):
    img = Image("complex_comparison.png", width=6.5*inch, height=3.5*inch)
    elements.append(img)
    elements.append(Paragraph("<i>Figure 9: Side-by-side comparison of original complex.wav (left) and recreated complex_recreate.wav (right) spectrograms.</i>", 
                             ParagraphStyle('figcaption', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, textColor=colors.grey)))

elements.append(Spacer(1, 0.3*inch))
elements.append(Paragraph("Melody Recreation Results", subheading_style))

elements.append(Paragraph("<b>How notes were selected:</b><br/><br/>" +
                         "[FILL IN YOUR EXPLANATION - Describe the method used to extract frequencies from the spectrogram, any challenges encountered, and how decisions were made about note boundaries and frequencies]", normal_style))

elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph("<b>Comparison between original and recreated:</b>", normal_style))

elements.append(Paragraph("<b>Similarities:</b><br/>" +
                         "• [FILL IN] - The fundamental frequencies match the original<br/>" +
                         "• [FILL IN] - The timing follows the original melody<br/>" +
                         "• [FILL IN] - Any other observations about agreement<br/><br/>" +
                         "<b>Differences:</b><br/>" +
                         "• <b>Pure sinusoids:</b> The recreated version uses perfect sine waves, while the original contains natural harmonics and timbre variations<br/>" +
                         "• <b>Missing transients:</b> Attack and decay envelopes are not captured<br/>" +
                         "• [FILL IN] - Any other differences observed", normal_style))

elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph("<b>Quality Assessment:</b><br/><br/>" +
                         "[FILL IN YOUR COMMENTS - 2-3 sentences comparing how similar the recreated melody sounds to the original, and what this tells us about the importance of harmonics and timbre in how we perceive voices]", normal_style))

# Build PDF
doc.build(elements)
print(f"\n✓ PDF created successfully: {pdf_filename}")
print(f"File location: {os.path.abspath(pdf_filename)}")
