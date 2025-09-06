# Fibonacci CSV search engine

A laconic and consistent search engine, designed to process files with either `.csv` or `.xlsx` extension, applying FIbonacci search technique

## Content
- [Installation](#installation)
- [Features and Configuration](#features_and_configuration)
- [Usage](#usage)
- [Examples](#examples)

# Installation
```bash
git clone https://hithub.com/Den-Birne/Den-Birne.github.io
```


# Features and Configuration
## Functionality

The program conprises three fundamental functions which are interconnected, thus dividing the procedure into sequencial operations, supplemented by third-party libraries in order to simplify the development process and add advanced features.

### get_file()

The function serves as an extractor of the input information via the **Command Line Interface vector argument** accompanied by **flags** with the purpose of organization of position-independent arguments with the possibility of accessing detailed explanation using --help menu and visualiazion of the instuction.
This stage specifies the user requirements and performs initial data validation.
The function does not expect argument, returns a tuple of arguments that were specified by the user after each of the flags applying [argparse](https://docs.python.org/3/library/argparse.html#module-argparse) library:
- `filename`: the name of the file which the user intends to process, it is additionally validated with a pattern, implemeted using the library [re](https://docs.python.org/3/library/re.html), specifically, the `.search()` method, regarding case-insesitivity
- `column`: the name of the column which contains the sought value
- `type`: the type of data which is contained within the specified column, if the user does not specifies thi argument, it receives the default type `str`
- `value`: the value being sought.
> An example of the CLI argument configuration:
```bash
parser.add_argument(
    '--type',
    '-t',
    choices=['int', 'float', 'str'],
    default='str'
    help-'Type of the data in the column'
)
```

> Note: the `filename` parameter must also contain the path if the file has not been places within the same repository as the instaled package

### Fibonacci_numbers_generator()

The function expects as an argument `int`, which is supposed to be the length of the processed column which includes the concretized value. It applies the traditional Fibonacci sequence, incuding initialization of the first, although, disputet, two numbers (which in our context are to be `0` and `1`, considering that the indexation is preferably commenced from `0`). The fundamental idea is implemented by looping through the previously intialized list of values, appending a value, which per se represents a sum of two preceding elements of the array until the last one exeeds the configured length of the dictionary. Eventually, it returns a list containing [Fibonacci sequence](https://en.wikipedia.org/wiki/Fibonacci_sequence), which is required to delineate the boundaries, within which the search is performed.

### locator()

As the name implies, the function's purpose is to locate the value, nay, determine the index pointing unto it. Intially, function unpacks the data retreived by the `get_file()` function, which is subsequently verifies whether the file requires conevrsion, which is relatively simple, due to the fact that prefered file extension `csv` is a core element of more sofisticated file editors, such as *Microsoft Excel*.

Function calls the integrated method `open` to access the previously specified `.csv` file, applying a powerful Dictionary Reader - `DictReader`, considering that we would like to narrow the diapason of the processed data, without heeding the trivial matter.

One the important nuances is that we are supposed to compose a distinct values and correlated indices which ought to be temporarily stored for further perocessing. The code below demonstrates composition of two separate lists: `original_indices` and `values`:
```bash
if data_type == 'type':
    indexed_values = [(idx, type(row[column])) for idx, row in enumerate(reader]
    target = float
    elif ...
        ...

indexed_values.sort(key=lambda x: x[1])
original_indices, values = map(list, zip(*indexed_values))
```
Where:
- 'type' implies one of three configured types `['int','float', 'str']`.
- `lambda` is a succinct method of expression a parameter, which expects a function, that in this case will not be called again.
- `map()` applies the functions `list()` and `zip()` to iterated unpacked values of the list `indexed_values`

> Note: the last condition does not require str() function, since the function 'DictReader' returns each row with the values interpreted as strings.

Finally, the function implements the search mechanism using our pre-configures set of Fobinacci numbers.
```bash
fib = Fibonacci_number_generator(n)
k = len(fib)
offset = 0

while k > 0:
i = min(offset + fib[k - 2] - 1, n - 1)
```
This section of the process intialize the scope of the search during every iteration by selecting the smallest arbitrary index.
```bash
if values[i] == target # verifies whether the value within the same index suits
    return original_indices[i]
elif values[i] < target:
    offset = i + 1 # Move offset past eliminated section
    k -= 2
else:
    k -= 1
```
Here the determination of the relative location of the sought value is being executed based on the previously sorted in descending order list

In the end, we should verify whether the last object of the dictionary matches our target if the loop does not succeed. if even this last operation does not return `True`, the program will immediately terminate, raising a ValueError, because the `.csv` file does not contain the sought value
```bash
if offset < n and values[offset] == target:
    return original_indices[offset]

raise ValueError(...)
```
If planned to include the file as an external module, specify that it should be executed without calling the `main()` function:
```bash
if __name__ == '__main__':
    main()
```

# Usage

The program accepts arguments via CLI, you could review all the necessary description by entering --help without any further arguments

> Note: before inserting a file, please verify that the data encaplsulated are sortable, namely they are homogeneous and can be compared based on their ASCII code.

# Examples

the input below

`python project.py --file ~/filename.csv --column NameOfColumn --type float --value 80.05`

Is a relevant example of the input information and should extract the index of the value `80.05` within the column `NameOfColumn` if it is indeed there:

`The specified value resides at the index resulting_index`
