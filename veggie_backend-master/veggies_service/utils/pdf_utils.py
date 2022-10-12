from flask import make_response
from fpdf import FPDF, HTMLMixin


class MyFPDF(FPDF, HTMLMixin):
    pass


def get_pdf():
    data = [['Name', 'Phone No', 'Total Pending']]
    # data.extend(get_data_for_bishi(req_data))
    html1 = '<H1 align="center">Members list</H1><table border="1" align="center" width="100%"><thead><tr>    <th width="25%">name</th>    <th width="20%">mobile no</th>    <th width="55%">pending amount</th>    </tr></thead><tbody>'
    html2 = '</tbody></table>'
    data = ['dada', 'daa', 'dasdasda']
    # data = get_data_for_bishi(req_data)
    for x in data:
        html1 += "<tr><td>" + x[0] + "</td><td>" + x[1] + "</td><td>" + x[2] + "</td></tr>"
    html = html1 + html2
    pdf = MyFPDF()

    pdf.add_page()
    pdf.write_html(html)

    pdf.add_page()
    pdf.write_html(html)

    # pdf.cell(200, 10, txt="Members Pending Amount!", ln=1, align="C")
    # col_width = pdf.w / 3.3
    # row_height = 8
    # for row in data:
    #     for item in row:
    #         pdf.cell(col_width, row_height * spacing,
    #                  txt=item, border=1)
    #     pdf.ln(row_height * spacing)
    response = make_response(pdf.output(name='members.pdf', dest='S'))
    response.headers.set('Content-Disposition', 'attachment', filename='members.pdf')
    response.headers.set('Content-Type', 'application/pdf')
    return response
