from fpdf import FPDF
from django.http import FileResponse


def generate_pdf(ingredients_in_cart):

    pdf = FPDF("P", "mm", "A4")
    pdf.add_page()
    pdf.add_font("DejaVu", "", "fonts/DejaVuSansCondensed.ttf", uni=True)
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(40, 10, "Список покупок:", 0, 1)
    pdf.cell(40, 10, "", 0, 1)
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(
        200,
        8,
        f"{'Продукт'.ljust(30)} {'Количество'.rjust(30)}",
        0,
        1,
    )
    pdf.line(10, 30, 150, 30)
    pdf.line(10, 38, 150, 38)
    for line in ingredients_in_cart:
        pdf.cell(
            200,
            8,
            f"{line['ingredient__name'].ljust(30)} {line['amount']} {line['ingredient__measurement_unit'].rjust(20)}",
            0,
            1,
        )
    pdf.output("test.pdf", "F")
    return FileResponse(
        open("test.pdf", "rb"), as_attachment=True, content_type="application/pdf"
    )
