




def print_result_table (output, data, header,table_title):

    # pad data rows to match header by appending empty strings
    # to end of individual rows

    rows = []
    for row in data:
        if len(row) < len(header):
            row = row + [""] * (len(header) - len(row))
        rows.append(row)
    

    output.print_table(
        table_data = rows,
        title=table_title,
        columns=header,
        last_line_style='color:red;',
    )