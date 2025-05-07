from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
import os

# Create a PDF document
doc = SimpleDocTemplate(
    "docs/client_deck.pdf",
    pagesize=letter,
    rightMargin=72, leftMargin=72,
    topMargin=72, bottomMargin=72
)

# Define styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'Title',
    parent=styles['Title'],
    fontSize=24,
    textColor=colors.HexColor('#0F62FE'),
    alignment=TA_CENTER,
    spaceAfter=20
)
heading_style = ParagraphStyle(
    'Heading',
    parent=styles['Heading1'],
    fontSize=18,
    textColor=colors.HexColor('#0F62FE'),
    spaceAfter=12
)
normal_style = ParagraphStyle(
    'Normal',
    parent=styles['Normal'],
    fontSize=12,
    textColor=colors.HexColor('#222222'),
    spaceAfter=10
)
bullet_style = ParagraphStyle(
    'Bullet',
    parent=styles['Normal'],
    fontSize=12,
    textColor=colors.HexColor('#222222'),
    leftIndent=20,
    spaceAfter=6
)
footer_style = ParagraphStyle(
    'Footer',
    parent=styles['Normal'],
    fontSize=8,
    textColor=colors.gray,
    alignment=TA_CENTER
)

# Create content for each slide
slides = []

# Slide 1: Title & client logo placeholder
slides.append([
    Paragraph("Klaviyo Reporting Solution", title_style),
    Paragraph("Automated Email Marketing Analytics", heading_style),
    Spacer(1, 0.5*inch),
    Paragraph("[Client Logo Placeholder]", normal_style),
    Spacer(1, 0.5*inch),
    Paragraph("Confidential – For <i>Client Name</i> review only", footer_style)
])

# Slide 2: Pain points / "Why manual Klaviyo reporting hurts"
slides.append([
    Paragraph("Why Manual Klaviyo Reporting Hurts", heading_style),
    Spacer(1, 0.2*inch),
    Paragraph("• <b>Time-consuming:</b> 5-8 hours per week spent on manual exports", bullet_style),
    Paragraph("• <b>Error-prone:</b> Copy-paste mistakes lead to incorrect decisions", bullet_style),
    Paragraph("• <b>Inconsistent:</b> Different team members use different metrics", bullet_style),
    Paragraph("• <b>Limited visibility:</b> No real-time access to performance data", bullet_style),
    Paragraph("• <b>Difficult collaboration:</b> Siloed reports not easily shared", bullet_style),
    Paragraph("• <b>No historical trends:</b> Point-in-time snapshots miss patterns", bullet_style),
    Spacer(1, 0.5*inch),
    Paragraph("Confidential – For <i>Client Name</i> review only", footer_style)
])

# Slide 3: Architecture graphic
slides.append([
    Paragraph("Automated Pipeline Architecture", heading_style),
    Spacer(1, 0.2*inch),
    Paragraph("Klaviyo → Fivetran → BigQuery → Looker Studio", normal_style),
    Spacer(1, 0.2*inch),
    Paragraph("[Architecture Diagram Placeholder]", normal_style),
    Spacer(1, 0.2*inch),
    Paragraph("• <b>Automated:</b> Scheduled syncs keep data fresh", bullet_style),
    Paragraph("• <b>Reliable:</b> Enterprise-grade data pipeline", bullet_style),
    Paragraph("• <b>Secure:</b> Compliant with data privacy regulations", bullet_style),
    Paragraph("• <b>Scalable:</b> Handles growing data volumes", bullet_style),
    Spacer(1, 0.5*inch),
    Paragraph("Confidential – For <i>Client Name</i> review only", footer_style)
])

# Slide 4: Screenshot of Looker dashboard
slides.append([
    Paragraph("Interactive Dashboard", heading_style),
    Spacer(1, 0.2*inch),
    Paragraph("[Dashboard Screenshot Placeholder]", normal_style),
    Spacer(1, 0.2*inch),
    Paragraph("• <b>Real-time metrics:</b> Opens, clicks, revenue, conversions", bullet_style),
    Paragraph("• <b>Campaign comparison:</b> Identify top performers", bullet_style),
    Paragraph("• <b>Trend analysis:</b> Track performance over time", bullet_style),
    Paragraph("• <b>Customizable:</b> Filter by date, campaign, segment", bullet_style),
    Spacer(1, 0.5*inch),
    Paragraph("Confidential – For <i>Client Name</i> review only", footer_style)
])

# Slide 5: Value/ROI bullets + sample upsell pricing
slides.append([
    Paragraph("Value & ROI", heading_style),
    Spacer(1, 0.2*inch),
    Paragraph("• <b>Time savings:</b> 75% reduction in reporting time", bullet_style),
    Paragraph("• <b>Improved accuracy:</b> Eliminate manual errors", bullet_style),
    Paragraph("• <b>Better decisions:</b> Data-driven campaign optimization", bullet_style),
    Paragraph("• <b>Team alignment:</b> Single source of truth", bullet_style),
    Spacer(1, 0.3*inch),
    Paragraph("<b>Pricing Options</b>", heading_style),
    Paragraph("• <b>Basic:</b> $X/month - Dashboard only", bullet_style),
    Paragraph("• <b>Standard:</b> $Y/month - Dashboard + Google Sheets export", bullet_style),
    Paragraph("• <b>Premium:</b> $Z/month - Custom metrics + email alerts", bullet_style),
    Spacer(1, 0.5*inch),
    Paragraph("Confidential – For <i>Client Name</i> review only", footer_style)
])

# Slide 6: Next steps + QR codes + contact info
slides.append([
    Paragraph("Next Steps & Resources", heading_style),
    Spacer(1, 0.2*inch),
    Paragraph("• <b>Technical assessment:</b> 1-2 days", bullet_style),
    Paragraph("• <b>Setup & configuration:</b> 3-5 days", bullet_style),
    Paragraph("• <b>Testing & validation:</b> 1-2 days", bullet_style),
    Paragraph("• <b>Training & handoff:</b> 1 day", bullet_style),
    Spacer(1, 0.3*inch),
    Paragraph("<b>Resources</b>", heading_style),
    Paragraph("• Looker Studio Template: [QR Code Placeholder]", bullet_style),
    Paragraph("• Google Sheets Template: [QR Code Placeholder]", bullet_style),
    Spacer(1, 0.2*inch),
    Paragraph("<b>Contact:</b> your.consultant@example.com | (555) 123-4567", normal_style),
    Spacer(1, 0.5*inch),
    Paragraph("Confidential – For <i>Client Name</i> review only", footer_style)
])

# Build the document with all slides
story = []
for i, slide in enumerate(slides):
    if i > 0:  # Add page break after each slide except the last one
        story.append(Spacer(1, 0.5*inch))  # Add some space at the bottom of the page
        story.append(Paragraph("<pagebreak/>", styles['Normal']))  # Add page break
    story.extend(slide)

# Build the PDF
doc.build(story)

print("Slide deck created at docs/client_deck.pdf")
