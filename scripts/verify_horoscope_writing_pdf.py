"""Verify generation of the 6-page traditional Tamil horoscope booklet and inspect pages."""

import sys
from pathlib import Path
from datetime import date, time
from io import BytesIO
from pypdf import PdfReader

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.services.horoscope_writing import (
    calculate_traditional_horoscope_writing_data,
    TraditionalHoroscopePdfGenerator,
)


def main():
    print("=== Testing Traditional Tamil Horoscope Booklet Generation ===")
    
    # Ad-hoc birth input for verification
    b_date = date(1993, 7, 24)
    b_time = time(10, 15, 30)
    lat = 13.0827
    lon = 80.2707

    calc_data = calculate_traditional_horoscope_writing_data(
        birth_date=b_date,
        birth_time=b_time,
        latitude=lat,
        longitude=lon,
        timezone_str="Asia/Kolkata",
        person_name="சுந்தரேசன் (Sundaresan)",
        gender="male",
        panchanga_system="thirukanitha",
        entrance_direction_basis="rasi",
    )

    print(f"Native Name: {calc_data['person_details']['name']}")
    print(f"Tamil Year/Month/Date: {calc_data['page1_birth_details']['tamil_year_month_date']}")
    print(f"Weekday: {calc_data['page1_birth_details']['weekday']}")
    print(f"Nakshatra & Pada: {calc_data['page1_birth_details']['birth_nakshatra']}")
    print(f"Udayadhi Nazhigai: {calc_data['page1_birth_details']['udayadhi_nazhigai']}")
    print(f"Ahas (Daylight): {calc_data['page1_birth_details']['ahas']}")
    print(f"Vara Yoga: {calc_data['page1_birth_details']['vara_yoga']}")
    print(f"Dasa Lord & Balance: {calc_data['page3_udumaka_dasa']['dasa_lord']} -> {calc_data['page3_udumaka_dasa']['dasa_iruppu']}")
    print(f"Birth Pakshi: {calc_data['page5_padupakshi']['uyir_pakshi']}")
    print(f"Archana Direction: {calc_data['page6_archana_slip']['entrance_direction']}")

    # Generate PDF
    generator = TraditionalHoroscopePdfGenerator(calc_data)
    pdf_bytes = generator.generate()

    output_pdf_path = Path(__file__).resolve().parent.parent / "sample_traditional_tamil_horoscope_6pages.pdf"
    output_pdf_path.write_bytes(pdf_bytes)
    print(f"Saved PDF to: {output_pdf_path} ({len(pdf_bytes)} bytes)")

    # Inspect with pypdf
    reader = PdfReader(BytesIO(pdf_bytes))
    page_count = len(reader.pages)
    print(f"Total Pages in PDF: {page_count}")
    assert page_count == 6, f"Expected 6 pages, got {page_count}"

    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        print(f"Page {i} characters extracted: {len(text)}")
        assert len(text) > 50, f"Page {i} appears blank or unpopulated!"

    print("=== Verification Successful! Exactly 6 pages with non-empty content generated. ===")


if __name__ == "__main__":
    main()
