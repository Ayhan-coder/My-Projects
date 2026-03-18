# Dune Archive System

A simple database system built with Python to store and manage information about the Dune universe.

## What is this project?

This project creates a basic database system from scratch. It can store different types of data (like houses, characters, etc.) and lets you add, find, and delete records. Everything is saved in files so your data stays even after closing the program.

## Features

- Create different data types (like tables in a database)
- Add new records with different information
- Search for records using a key value
- Delete records you don't need
- All operations are logged with timestamps
- Data is saved in binary files for better performance
- Comprehensive error handling without system crashes
- Strict data validation for consistency

## How to use

### Step 1: Run the program
```bash
python archive.py input.txt
```

### Step 2: Write commands in input.txt

#### Create a new type (table)
```
create type house 6 1 name str origin str leader str militarystrength int wealth int spiceproduction int
```
This creates a type called "house" with 6 fields. The first field (name) is the primary key.

#### Add a record
```
create record house Atreides Caladan Duke 8000 5000 150
```
This adds a new house record with the given values.

#### Search for a record
```
search record house Atreides
```
This finds the house with name "Atreides".

#### Delete a record
```
delete record house Atreides
```
This removes the house with name "Atreides".

## Command format

### Create Type
```
create type <name> <number-of-fields> <primary-key-position> <field1-name> <field1-type> <field2-name> <field2-type> ...
```

### Create Record
```
create record <type-name> <value1> <value2> <value3> ...
```

### Search Record
```
search record <type-name> <primary-key-value>
```

### Delete Record
```
delete record <type-name> <primary-key-value>
```

## Data types

- **int**: Numbers (like 123, 4567)
- **str**: Text (like "Atreides", "Caladan")

## Example

Here's a complete example:

**input.txt:**
```
create type house 3 1 name str planet str power int
create record house Atreides Caladan 8000
create record house Harkonnen GiediPrime 12000
search record house Atreides
delete record house Harkonnen
search record house Harkonnen
```

**What happens:**
1. Creates a "house" type with 3 fields
2. Adds two house records
3. Finds Atreides (success)
4. Deletes Harkonnen (success)
5. Tries to find Harkonnen (fails - already deleted)

## Output files

The program creates these files:

- **output.txt**: Results from search commands
- **log.csv**: List of all operations with success/failure status
- **system_catalog.json**: Information about your data types
- **[type-name].dat**: Binary files with your actual data

## Rules and limits

- **Type names**: Maximum 12 characters, alphanumeric only, must contain at least one letter
- **Field names**: Maximum 20 characters, alphanumeric only, must contain at least one letter
- **String values**: Maximum 50 characters, alphanumeric only
- **Fields per type**: Maximum 6 fields
- **Data types**: Only int and str supported
- **Primary key**: Must be unique (no duplicates)
- **File size**: Maximum 100 pages per type (400KB limit)

## Validation Rules

**Important:** The system enforces strict validation:
- All names (types, fields) must be alphanumeric characters only (a-z, A-Z, 0-9)
- No special characters (including underscores) are allowed
- All names must contain at least one letter
- String field values must also be alphanumeric only

## Error handling

The system handles these problems gracefully:
- Trying to create a type that already exists
- Adding records with duplicate primary keys
- Searching for records that don't exist
- Deleting records that don't exist
- Wrong command format
- Invalid data types
- Non-alphanumeric characters in names or string values

All errors are logged but won't crash the program. The system provides debug output to help identify issues.

## Requirements

- Python 3.6 or newer
- No external libraries needed
- Works on Windows, Mac, and Linux

## How it works

The system uses a simple but effective approach:
- Data is stored in 4KB pages (like book pages)
- Each page can hold up to 10 records
- Records have a fixed size for better performance
- Binary format saves space and loads faster
- Each data type gets its own file
- Maximum 100 pages per file (400KB limit)

This makes the system fast for small to medium amounts of data.

## Debug Output

When running the program, you'll see debug messages like:
```
Processing 11 commands...
Processing command 1: create type house...
Processing command 2: create record house...
Search found: ['Atreides', 'Caladan', 'Duke', 8000, 5000, 150]
```

This helps you track what the system is doing and identify any issues.

## Troubleshooting

**Problem: "File not found" error**
- Make sure input.txt exists in the same folder

**Problem: No results in output.txt**
- Check if your search commands use existing record names
- Look at log.csv to see which operations failed

**Problem: Commands not working**
- Make sure your command format matches the examples exactly
- Check for typos in type names and field names
- Ensure all names use only alphanumeric characters (no underscores or special characters)

**Problem: Validation errors**
- Check that all type names, field names, and string values contain only letters and numbers
- Make sure all names contain at least one letter
- Verify field names don't use underscores (use "militarystrength" not "military_strength")

## Project info

This is a school project for CMPE 321 (Database Systems) course. It shows how databases work at a basic level without using existing database software.

**Authors:** Ali Ayhan Gunder (2021400219) & Bora Depecik (2020400105)