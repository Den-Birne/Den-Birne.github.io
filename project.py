import csv, argparse, pandas, re


def main():
    index = locator(get_file())
    print(f"The specified value resides at the index {index}")


def get_file():
    parser = argparse.ArgumentParser(
        description="Performs filtering of CSV files with specified columns for concrete values which are homogeneous"
    )
    parser.add_argument(
        "--filename",
        "-f",
        required=True,
        help="Specifies filename of a CSV file which is intended to be processed",
        type=str,
    )
    parser.add_argument(
        "--column",
        "-c",
        required=True,
        help="Specifies column of a CSV file whereto the searched value belongs",
        type=str,
    )
    parser.add_argument(
        "--value",
        "-v",
        required=True,
        help="Specifies the value which is the intended result",
        type=str,
    )
    parser.add_argument(
        "--type",
        "-t",
        choices=["int", "float", "str"],
        default="str",
        help="Type of the data in the column",
    )
    arguments = parser.parse_args()
    if not re.search(r".*(\.xlsx|\.csv)", arguments.filename, re.IGNORECASE):
        raise ValueError('Filename must have an extension ".xlsx" or ".csv"')
    return (arguments.filename, arguments.column, arguments.type, arguments.value)


def Fibonacci_numbers_generator(min_n):

    # Define the first two Fibonacci numbers
    fib = [0, 1]
    while fib[-1] < min_n:

        # If the last Fibonacci number is less than the length of the list, then procede appending the next Fibonacci number
        fib.append(fib[-1] + fib[-2])
    return fib


def locator(file_properties):

    # Retreive the data from the vector arguments, typed by the user
    filename, column, data_type, value = file_properties

    # Implementation of convesion the file extension if it is an Excel file
    if filename.endswith(".xlsx"):
        df = pandas.read_excel(filename)
        csv_filename = re.sub(r"\.xlsx$", ".csv", filename, re.IGNORECASE)
        df.to_csv(csv_filename, index=False)
        filename = csv_filename

    with open(filename, newline="", encoding="utf-8") as file:
        reader = list(csv.DictReader(file))  # Convert to list once

    # Convert column to proper type
    if data_type == "int":
        indexed_values = [(idx, int(row[column])) for idx, row in enumerate(reader)]
        target = int(value)
    elif data_type == "float":
        indexed_values = [(idx, float(row[column])) for idx, row in enumerate(reader)]
        target = float(value)
    else:
        indexed_values = [(idx, row[column]) for idx, row in enumerate(reader)]
        target = value

    # Sort values while keeping original indices
    indexed_values.sort(key=lambda x: x[1])
    original_indices, values = map(list, zip(*indexed_values))
    n = len(values)

    # Fibonacci search
    fib = Fibonacci_numbers_generator(n)
    k = len(fib) - 1
    offset = 0  # Start from the first element

    while k > 0:
        i = min(offset + fib[k - 2] - 1, n - 1)  # Subtract 1 to align indexing
        if values[i] == target:
            return original_indices[i]
        elif values[i] < target:
            offset = i + 1  # Move offset past eliminated section
            k -= 2
        else:
            k -= 1

    # Final check if remaining element matches
    if offset < n and values[offset] == target:
        return original_indices[offset]

    raise ValueError("Value does not exist within the provided CSV file")


if __name__ == "__main__":
    main()
