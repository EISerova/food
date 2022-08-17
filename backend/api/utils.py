from django.http import FileResponse
from fpdf import FPDF

# я не горжусь этим решением, оно временное, не хватило времени.


def generate_pdf(ingredients_in_cart):

    HEADER = "Продукт                                                                                 Количество"
    pdf = FPDF("P", "mm", "A4")
    pdf.add_page()
    pdf.add_font("DejaVu", "", "fonts/DejaVuSansCondensed.ttf", uni=True)
    pdf.set_font("DejaVu", "", 24)
    pdf.cell(40, 10, "Список покупок:", 0, 1)
    pdf.cell(40, 10, "", 0, 1)

    pdf.set_font("DejaVu", "", 12)
    pdf.cell(200, 8, HEADER, 0, 1)
    pdf.line(10, 30, 200, 30)
    pdf.line(10, 38, 200, 38)
    line_height = pdf.font_size * 2
    col_width = pdf.epw / 3

    for line in ingredients_in_cart:
        pdf.cell(col_width, line_height, line["ingredient__name"])
        pdf.cell(
            col_width,
            line_height,
            f'{line["amount"]}',
            align="R",
        )
        pdf.cell(col_width, line_height, line["ingredient__measurement_unit"], "L")
        pdf.ln(line_height)

    pdf.output("shopping_list.pdf", "F")
    return FileResponse(
        open("shopping_list.pdf", "rb"),
        as_attachment=True,
        content_type="application/pdf",
    )
