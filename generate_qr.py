import qrcode
import sys
import os

def generate_qr(url, output_path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    print(f"QR code saved to {output_path}")

if __name__ == "__main__":
    # Generate Looker Studio QR code
    looker_url = "https://lookerstudio.google.com/reporting/XXXX"
    looker_output = "docs/assets/qr/looker_template_qr.png"
    generate_qr(looker_url, looker_output)
    
    # Generate Google Sheets QR code
    sheets_url = "https://docs.google.com/spreadsheets/d/XXXX"
    sheets_output = "docs/assets/qr/sheets_template_qr.png"
    generate_qr(sheets_url, sheets_output)
