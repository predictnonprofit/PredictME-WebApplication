from weasyprint import HTML



def create_invoice_pdf():
    invoice_pdf = HTML(filename="predictme.html").write_pdf("predictme.pdf")

    return invoice_pdf