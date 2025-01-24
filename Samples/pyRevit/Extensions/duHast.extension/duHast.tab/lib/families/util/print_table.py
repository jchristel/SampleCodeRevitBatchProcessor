




def print_result_table (output, data, header,table_title):

    # pad data rows to match header by appending empty strings
    # to end of individual rows

    # set a max row value to display
    max_row_number = 100

    # safety check
    if len(header) == 0:
        print("Header is empty. Cannot print table")
        return
    
    rows = []
    print("Data contains {} rows.".format(len(data)))
    for row in data:
        if len(row) < len(header):
            # pad row with empty strings
            row = row + [""] * (len(header) - len(row))
        rows.append(row)
    
    if (len(rows) > max_row_number):
        print("Table has too many rows to display. Printing only first {} rows".format(max_row_number))
        rows = rows[:max_row_number]
    
    #print( "Printing table with {} rows and {} columns".format(len(rows), len(header)))
    
    #return
    output.print_table(
        table_data = rows,
        title=table_title,
        columns=header,
        last_line_style='color:red;',
    )