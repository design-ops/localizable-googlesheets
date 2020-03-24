import csv
from os import path
from localisation.utils import create_file

def build_localisations(csv_locations):
    """
    Received a set of csv files and pivots the csv into a dictionary where the first item in the column is the key and the 
    rest are put in an array as the value
    """
    # Open each of the files
    # Build the dictionaries by column
    localisations = []
    for csv_location in csv_locations:
        with open(csv_location) as csvfile:
            reader = csv.DictReader(csvfile)
            locs = {}
            for key in reader.fieldnames:
                locs[key] = []
            for row in reader:
                for key in reader.fieldnames:
                    locs[key].append(row[key])

            localisations.append(locs)
    return localisations


def build_csv(localisations, plurals, localisation_filename, plurals_filename, output_dir):
    """
    Receives a pair of dictionaries in the following form:
    {
     'key': ['', 'test.example', '', '', 'test.dynamic.one', 'test.dynamic.two', '', '', 'test.plural', 'test.plural.and.singular', '',
        '', 'example.icecream.toppings.title', 'example.icecream.sauces.title', 'example.icecream.saucesAndToppings.title'],
     'en': ['', 'A test example of a localized string', '', '', 'One argument: ${arg}', 'Two arguments: ${arg1} and ${arg2}', '', '',
        '${x} in the plural', '${my_value}: ${y} in the plural and ${z}', '', '', 'You have ${ice_cream_toppings} on your ice cream',
        'You have ${ice_cream_sauces} on your ice cream', 'You have ${ice_cream_toppings} and ${ice_cream_sauces} on your ice cream'],
     'pt': ['', 'Examplo duma string localizada', '', '', 'Um argumento: ${arg}', 'Dois argumentos: ${arg1} e ${arg2}', '', '', '${x} no plural',
        '${my_value}: ${y} no plural e ${z}', '', '', 'Tienes ${ice_cream_toppings} en tu helado', 'Tienes ${ice_cream_sauces} en tu helado',
        'Tienes ${ice_cream_toppings} y ${ice_cream_sauces} en tu helado']
    }
    {
     'VARIABLE': ['${ice_cream_toppings}', '${ice_cream_sauces}', '${ice_cream_toppings}', '${ice_cream_sauces}', '${x}', '${x}', '${y}', '${y}'],
     'LANG': ['en', 'en', 'pt', 'pt', 'en', 'pt\n', 'en', 'pt\n'],
     'ZERO': ['no toppings', 'no sauces', 'cero toppings', 'cero salsas', 'zero values', 'cero', 'zero values', 'cero'],
     'ONE': ['one topping', 'one sauce', 'un topping', 'una salsa', 'one value', 'uno', 'one value', 'uno'],
     'TWO': ['', '', '', '', 'two values', 'dos', 'two values', 'dos'],
     'FEW': ['', '', '', '', 'few values', 'pocos', 'few values', 'pocos'],
     'MANY': ['', '', '', '', 'many values', 'muchos', 'many values', 'muchos'],
     'OTHER': ['${ice_cream_toppings} toppings', '${ice_cream_sauces} sauces', '${ice_cream_toppings} toppings', '${ice_cream_sauces} salsas',
        'other values', 'otro', 'other values', 'otro']
    }
    Translates them to rows in a csv and saves that to a file.
    """
    localisation_columns = [[key] + values for key, values in localisations.items()]
    localisation_file = _write_csv_file(output_dir, localisation_filename, localisation_columns)

    plurals_columns = [[key] + values for key, values in plurals.items()]
    plurals_file = _write_csv_file(output_dir, plurals_filename, plurals_columns)

    return [localisation_file, plurals_file]


def _write_csv_file(output_dir, filename, columns):
    csvfile = create_file(output_dir, filename)
    writer = csv.writer(csvfile)

    for index in range(0, len(columns[0])):
        row = []
        for column in columns:
            row.append(column[index])
        writer.writerow(row)

    csvfile.close()
    return path.realpath(path.join(output_dir, filename))