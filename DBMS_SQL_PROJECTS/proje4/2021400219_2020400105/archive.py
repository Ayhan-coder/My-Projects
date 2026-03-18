"""
Dune Archive System - A Simple Database Management System
CMPE 321 Project 4

This program is a simple database system. It can create types (tables), add records, search for records, and delete records. It saves data in files and keeps a log of all actions. The system uses pages to store records and supports basic data types: integer and string.
"""

import os
import sys
import time
import struct
import json
from typing import Dict, List, Any, Optional, Tuple

class DuneArchiveSystem:
    """
    This class manages the Dune Archive System. It can create types, add, search, and delete records.
    It saves type information in a catalog file and keeps data in separate files for each type.
    """
    def __init__(self):
        self.page_size = 4096  # bytes
        self.max_records_per_page = 10
        self.max_fields_per_type = 6
        self.max_type_name_length = 12
        self.max_field_name_length = 20
        self.max_string_field_length = 50  # Define max string length
        
        # System catalog to store type definitions
        self.catalog = {}
        self.catalog_file = "system_catalog.json"
        self.log_file = "log.csv"
        self.output_file = "output.txt"
        
        # Load existing catalog if it exists
        self.load_catalog()
        
        # Initialize log file if it doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write("")  # Create empty log file

    def load_catalog(self):
        """
        Load the system catalog from a file.
        The catalog keeps information about all types (tables) in the system.
        """
        if os.path.exists(self.catalog_file):
            try:
                with open(self.catalog_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        self.catalog = json.loads(content)
                    else:
                        self.catalog = {}
            except (json.JSONDecodeError, FileNotFoundError, PermissionError):
                self.catalog = {}
            except Exception:
                self.catalog = {}

    def save_catalog(self):
        """
        Save the system catalog to a file.
        This makes sure type information is not lost when the program closes.
        """
        try:
            with open(self.catalog_file, 'w', encoding='utf-8') as f:
                json.dump(self.catalog, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save catalog: {e}")

    def log_operation(self, operation: str, status: str):
        """
        Write an operation and its status (success or failure) to the log file.
        This helps to keep track of what happened in the system.
        """
        try:
            timestamp = int(time.time())
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"{timestamp}, {operation}, {status}\n")
        except Exception as e:
            print(f"Warning: Could not write to log: {e}")

    def calculate_record_size(self, field_types: List[str]) -> int:
        """
        Calculate the size of a record in bytes.
        The size depends on the types of fields (int or string).
        """
        size = 1  # 1 byte for validity flag
        for field_type in field_types:
            if field_type == 'int':
                size += 4  # 4 bytes for integer
            elif field_type == 'str':
                size += self.max_string_field_length  # Fixed size for strings
        return size

    def create_type(self, type_name: str, num_fields: int, primary_key_order: int, 
                   field_definitions: List[Tuple[str, str]]) -> bool:
        """
        Create a new type (table) in the system.
        type_name: The name of the type.
        num_fields: How many fields the type has.
        primary_key_order: Which field is the primary key (1-based).
        field_definitions: List of (field_name, field_type) pairs.
        Returns True if successful, False otherwise.
        """
        try:
            # Validate input
            if len(type_name) > self.max_type_name_length:
                return False
            
            if type_name in self.catalog:
                return False  # Type already exists
            if not type_name.isalnum():
                return False

            # Check field name contains at least one letter
            if not any(c.isalpha() for c in type_name):
                return False
            
            if num_fields > self.max_fields_per_type:
                return False
            
            if primary_key_order < 1 or primary_key_order > num_fields:
                return False
            
            # Validate field definitions
            field_names = []
            field_types = []
            for field_name, field_type in field_definitions:
                if len(field_name) > self.max_field_name_length:
                    return False
                if not field_name.isalnum():
                    return False
                if not any(c.isalpha() for c in field_name):
                    return False
                if field_type not in ['int', 'str']:
                    return False
                
                field_names.append(field_name)
                field_types.append(field_type)
            
            # Store type definition in catalog
            self.catalog[type_name] = {
                'num_fields': num_fields,
                'primary_key_order': primary_key_order,
                'field_names': field_names,
                'field_types': field_types,
                'record_size': self.calculate_record_size(field_types),
                'next_page_id': 0
            }
            
            self.save_catalog()
            
            # Create data file for this type
            data_file = f"{type_name}.dat"
            if not os.path.exists(data_file):
                with open(data_file, 'wb') as f:
                    pass  # Create empty data file
            
            return True
            
        except Exception as e:
            print(f"Error creating type: {e}")
            return False

    def pack_record(self, type_name: str, values: List[Any]) -> bytes:
        """
        Convert a record's values into binary format for storage.
        Returns the packed bytes.
        """
        try:
            if type_name not in self.catalog:
                return b''
                
            type_def = self.catalog[type_name]
            field_types = type_def['field_types']
            
            if len(values) != len(field_types):
                return b''
            
            # Start with validity flag (1 = valid)
            packed_data = struct.pack('B', 1)
            
            for i, (value, field_type) in enumerate(zip(values, field_types)):
                if field_type == 'int':
                    try:
                        int_val = int(value)
                        packed_data += struct.pack('i', int_val)
                    except (ValueError, TypeError):
                        return b''
                elif field_type == 'str':
                    # Handle string encoding more safely
                    try:
                        str_value = str(value) if value is not None else ""
                        # Truncate if too long
                        if len(str_value) > self.max_string_field_length:
                            str_value = str_value[:self.max_string_field_length]
                        # Encode to bytes first, then pad
                        str_bytes = str_value.encode('utf-8', errors='replace')
                        if len(str_bytes) > self.max_string_field_length:
                            str_bytes = str_bytes[:self.max_string_field_length]
                        str_bytes = str_bytes.ljust(self.max_string_field_length, b'\0')
                        packed_data += str_bytes
                    except Exception:
                        # If encoding fails, use empty string
                        empty_bytes = b'\0' * self.max_string_field_length
                        packed_data += empty_bytes
            
            return packed_data
        except Exception as e:
            print(f"Error packing record: {e}")
            return b''

    def unpack_record(self, type_name: str, packed_data: bytes) -> Optional[List[Any]]:
        """
        Convert binary data back into a list of values for a record.
        Returns the list of values, or None if there is a problem.
        """
        try:
            if len(packed_data) == 0 or type_name not in self.catalog:
                return None
                
            type_def = self.catalog[type_name]
            field_types = type_def['field_types']
            
            # Calculate expected size
            expected_size = self.calculate_record_size(field_types)
            if len(packed_data) < expected_size:
                return None
            
            offset = 0
            
            # Check validity flag
            validity = struct.unpack_from('B', packed_data, offset)[0]
            if validity == 0:  # Invalid record
                return None
            offset += 1
            
            values = []
            for field_type in field_types:
                if field_type == 'int':
                    if offset + 4 > len(packed_data):
                        return None
                    value = struct.unpack_from('i', packed_data, offset)[0]
                    values.append(value)
                    offset += 4
                elif field_type == 'str':
                    if offset + self.max_string_field_length > len(packed_data):
                        return None
                    str_bytes = packed_data[offset:offset + self.max_string_field_length]
                    try:
                        # Decode and strip null bytes
                        value = str_bytes.decode('utf-8', errors='replace').rstrip('\0')
                    except Exception:
                        value = ""
                    values.append(value)
                    offset += self.max_string_field_length
            
            return values
            
        except Exception as e:
            print(f"Error unpacking record: {e}")
            return None

    def find_record_in_page(self, type_name: str, page_data: bytes, primary_key_value: Any) -> Optional[Tuple[int, List[Any]]]:
        """
        Search for a record with a given primary key in a page.
        Returns the slot number and values if found, or None if not found.
        """
        try:
            if len(page_data) < 2 or type_name not in self.catalog:
                return None
                
            type_def = self.catalog[type_name]
            record_size = type_def['record_size']
            primary_key_index = type_def['primary_key_order'] - 1
            
            if primary_key_index < 0 or primary_key_index >= type_def['num_fields']:
                return None
            
            # Read bitmap (2 bytes for 10 records)
            try:
                bitmap = struct.unpack('H', page_data[:2])[0]
            except struct.error:
                return None
            
            offset = 2  # Start after bitmap
            
            for slot in range(self.max_records_per_page):
                # Check if slot is occupied
                if bitmap & (1 << slot):
                    if offset + record_size > len(page_data):
                        break
                    record_data = page_data[offset:offset + record_size]
                    values = self.unpack_record(type_name, record_data)
                    
                    if values and len(values) > primary_key_index:
                        # More careful comparison
                        record_pk = values[primary_key_index]
                        # Handle both string and int comparisons
                        if self.values_equal(record_pk, primary_key_value):
                            return slot, values
                
                offset += record_size
            
            return None
        except Exception as e:
            print(f"Error finding record in page: {e}")
            return None

    def values_equal(self, val1: Any, val2: Any) -> bool:
        """
        Check if two values are equal, even if their types are different.
        Returns True if they are equal, False otherwise.
        """
        try:
            # If both are same type, direct comparison
            if type(val1) == type(val2):
                return val1 == val2
            
            # Convert both to strings and compare (handles int/str mismatches)
            str1 = str(val1).strip() if val1 is not None else ""
            str2 = str(val2).strip() if val2 is not None else ""
            
            return str1 == str2
        except Exception:
            return False

    def load_page(self, type_name: str, page_id: int) -> Optional[bytes]:
        """
        Load a page from the data file for a type.
        Returns the page data as bytes, or None if not found.
        """
        try:
            data_file = f"{type_name}.dat"
            if not os.path.exists(data_file):
                return None
            
            with open(data_file, 'rb') as f:
                f.seek(page_id * self.page_size)
                page_data = f.read(self.page_size)
                
                if len(page_data) == 0:
                    return None
                
                # Pad page if it's not full size
                if len(page_data) < self.page_size:
                    page_data += b'\0' * (self.page_size - len(page_data))
                
                return page_data
        except Exception as e:
            print(f"Error loading page: {e}")
            return None

    def save_page(self, type_name: str, page_id: int, page_data: bytes):
        """
        Save a page to the data file for a type.
        Makes sure the page is the correct size.
        """
        try:
            data_file = f"{type_name}.dat"
            
            # Ensure page_data is correct size
            if len(page_data) < self.page_size:
                page_data = page_data + b'\0' * (self.page_size - len(page_data))
            elif len(page_data) > self.page_size:
                page_data = page_data[:self.page_size]
            
            # Ensure file exists and is large enough
            required_size = (page_id + 1) * self.page_size
            
            with open(data_file, 'r+b' if os.path.exists(data_file) else 'wb') as f:
                # Extend file if necessary
                f.seek(0, 2)  # Seek to end
                current_size = f.tell()
                if current_size < required_size:
                    f.write(b'\0' * (required_size - current_size))
                
                f.seek(page_id * self.page_size)
                f.write(page_data)
        except Exception as e:
            print(f"Error saving page: {e}")

    def create_record(self, type_name: str, values: List[Any]) -> bool:
        """
        Add a new record to a type (table).
        values: The values for the record fields.
        Returns True if successful, False otherwise.
        """
        try:
            if type_name not in self.catalog:
                return False
            
            type_def = self.catalog[type_name]
            
            # Validate number of values
            if len(values) != type_def['num_fields']:
                return False
            
            primary_key_index = type_def['primary_key_order'] - 1
            if primary_key_index >= len(values) or primary_key_index < 0:
                return False
                
            primary_key_value = values[primary_key_index]
            
            # Check if record with this primary key already exists
            if self.search_record(type_name, primary_key_value) is not None:
                return False
            
            # Validate input types and string constraints
            for i, (value, field_type) in enumerate(zip(values, type_def['field_types'])):
                if field_type == 'int':
                    if not isinstance(value, int):
                        return False
                elif field_type == 'str':
                    if not isinstance(value, str):
                        return False
                    # String must be alphanumeric and contain at least one letter
                    if not value.isalnum():
                        return False
                else:
                    # Unknown type
                    return False
            
            # Calculate how many records can actually fit in a page
            header_size = 2  # 2 bytes for bitmap
            available_space = self.page_size - header_size
            max_records_in_page = min(self.max_records_per_page, available_space // type_def['record_size'])
            
            if max_records_in_page <= 0:
                return False
            
            # Find a page with free space or create new page
            page_id = 0
            max_pages = 100
            
            while page_id < max_pages:
                page_data = self.load_page(type_name, page_id)
                if page_data is None:
                    # Create new page
                    page_data = bytearray(self.page_size)
                    # Initialize bitmap to 0
                    struct.pack_into('H', page_data, 0, 0)
                else:
                    page_data = bytearray(page_data)
                
                # Check for free slot
                try:
                    bitmap = struct.unpack_from('H', page_data, 0)[0]
                except struct.error:
                    bitmap = 0
                    struct.pack_into('H', page_data, 0, bitmap)
                
                free_slot = None
                for slot in range(max_records_in_page):
                    if not (bitmap & (1 << slot)):
                        free_slot = slot
                        break
                
                if free_slot is not None:
                    # Add record to this page
                    record_data = self.pack_record(type_name, values)
                    if not record_data:
                        return False
                        
                    record_offset = 2 + free_slot * type_def['record_size']  # 2 bytes for bitmap
                    
                    # Check bounds
                    if record_offset + len(record_data) > self.page_size:
                        page_id += 1
                        continue
                    
                    # Update bitmap
                    bitmap |= (1 << free_slot)
                    struct.pack_into('H', page_data, 0, bitmap)
                    
                    # Write record data
                    page_data[record_offset:record_offset + len(record_data)] = record_data
                    
                    # Save page
                    self.save_page(type_name, page_id, bytes(page_data))
                    return True
                
                page_id += 1
            
            return False
            
        except Exception as e:
            print(f"Error creating record: {e}")
            return False

    def search_record(self, type_name: str, primary_key_value: Any) -> Optional[List[Any]]:
        """
        Search for a record by its primary key value.
        Returns the list of values if found, or None if not found.
        """
        try:
            if type_name not in self.catalog:
                return None
            
            data_file = f"{type_name}.dat"
            if not os.path.exists(data_file):
                return None
            
            # Get file size to determine how many pages exist
            file_size = os.path.getsize(data_file)
            if file_size == 0:
                return None
            
            num_pages = (file_size + self.page_size - 1) // self.page_size
            
            # Search through existing pages only
            for page_id in range(num_pages):
                page_data = self.load_page(type_name, page_id)
                if page_data is None:
                    continue
                
                result = self.find_record_in_page(type_name, page_data, primary_key_value)
                if result is not None:
                    slot, values = result
                    return values
            
            return None
            
        except Exception as e:
            print(f"Error searching record: {e}")
            return None

    def delete_record(self, type_name: str, primary_key_value: Any) -> bool:
        """
        Delete a record from a type (table) by its primary key value.
        Returns True if successful, False otherwise.
        """
        try:
            if type_name not in self.catalog:
                return False
            
            data_file = f"{type_name}.dat"
            if not os.path.exists(data_file):
                return False
            
            # Get file size to determine how many pages exist
            file_size = os.path.getsize(data_file)
            if file_size == 0:
                return False
            
            num_pages = (file_size + self.page_size - 1) // self.page_size
            
            # Search through existing pages only
            for page_id in range(num_pages):
                page_data = self.load_page(type_name, page_id)
                if page_data is None:
                    continue
                
                result = self.find_record_in_page(type_name, page_data, primary_key_value)
                if result is not None:
                    slot, values = result
                    
                    # Mark slot as free in bitmap
                    page_data = bytearray(page_data)
                    bitmap = struct.unpack_from('H', page_data, 0)[0]
                    bitmap &= ~(1 << slot)  # Clear the bit for this slot
                    struct.pack_into('H', page_data, 0, bitmap)
                    
                    # Mark record as invalid
                    type_def = self.catalog[type_name]
                    record_offset = 2 + slot * type_def['record_size']
                    if record_offset < len(page_data):
                        struct.pack_into('B', page_data, record_offset, 0)  # Set validity flag to 0
                    
                    # Save page
                    self.save_page(type_name, page_id, bytes(page_data))
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error deleting record: {e}")
            return False

    def process_command(self, command: str):
        """
        Read and process a single command from the input.
        Supports create type, create record, search record, and delete record commands.
        """
        if not command or not command.strip():
            return
            
        parts = command.strip().split()
        if not parts:
            return
        
        try:
            if parts[0] == "create" and len(parts) > 1 and parts[1] == "type":
                # create type <type-name> <number-of-fields> <primary-key-order> <field1-name> <field1-type> ...
                if len(parts) < 5:
                    self.log_operation(command, "failure")
                    return
                
                try:
                    type_name = parts[2]
                    num_fields = int(parts[3])
                    primary_key_order = int(parts[4])
                except (ValueError, IndexError):
                    self.log_operation(command, "failure")
                    return
                
                # Validate we have enough parts for all field definitions
                if len(parts) < 5 + num_fields * 2:
                    self.log_operation(command, "failure")
                    return
                
                field_definitions = []
                try:
                    for i in range(num_fields):
                        field_name = parts[5 + i * 2]
                        field_type = parts[6 + i * 2]
                        field_definitions.append((field_name, field_type))
                except IndexError:
                    self.log_operation(command, "failure")
                    return
                
                success = self.create_type(type_name, num_fields, primary_key_order, field_definitions)
                status = "success" if success else "failure"
                self.log_operation(command, status)
            
            elif parts[0] == "create" and len(parts) > 1 and parts[1] == "record":
                # create record <type-name> <field1-value> <field2-value> ...
                if len(parts) < 4:  # Need at least: create record type_name value
                    self.log_operation(command, "failure")
                    return
                    
                type_name = parts[2]
                values = parts[3:]
                
                # Convert values to appropriate types
                if type_name in self.catalog:
                    type_def = self.catalog[type_name]
                    if len(values) != type_def['num_fields']:
                        self.log_operation(command, "failure")
                        return
                        
                    converted_values = []
                    for i, (value, field_type) in enumerate(zip(values, type_def['field_types'])):
                        try:
                            if field_type == 'int':
                                converted_values.append(int(value))
                            else:
                                converted_values.append(str(value))
                        except (ValueError, TypeError):
                            self.log_operation(command, "failure")
                            return
                    values = converted_values
                else:
                    self.log_operation(command, "failure")
                    return
                
                success = self.create_record(type_name, values)
                status = "success" if success else "failure"
                self.log_operation(command, status)
            
            elif parts[0] == "search" and len(parts) > 1 and parts[1] == "record":
                # search record <type-name> <primary-key>
                if len(parts) < 4:
                    self.log_operation(command, "failure")
                    return
                    
                type_name = parts[2]
                primary_key_str = parts[3]
                
                # Convert primary key to appropriate type
                if type_name in self.catalog:
                    type_def = self.catalog[type_name]
                    primary_key_index = type_def['primary_key_order'] - 1
                    
                    if primary_key_index < 0 or primary_key_index >= len(type_def['field_types']):
                        self.log_operation(command, "failure")
                        return
                    
                    primary_key_type = type_def['field_types'][primary_key_index]
                    
                    try:
                        if primary_key_type == 'int':
                            primary_key_value = int(primary_key_str)
                        else:
                            primary_key_value = str(primary_key_str)
                    except (ValueError, TypeError):
                        self.log_operation(command, "failure")
                        return
                    
                    result = self.search_record(type_name, primary_key_value)
                    if result is not None:
                        # Output to file - make sure we write immediately and flush
                        try:
                            with open(self.output_file, 'a', encoding='utf-8') as f:
                                output_line = ' '.join(str(val) for val in result)
                                f.write(output_line + '\n')
                                f.flush()  # Ensure data is written immediately
                            status = "success"
                            print(f"Search found: {result}")  # Debug output
                        except Exception as e:
                            print(f"Error writing output: {e}")
                            status = "failure"
                    else:
                        status = "failure"
                        print(f"Search failed for {type_name} with key {primary_key_value}")  # Debug output
                else:
                    status = "failure"
                    print(f"Type {type_name} not found in catalog")  # Debug output
                
                self.log_operation(command, status)
            
            elif parts[0] == "delete" and len(parts) > 1 and parts[1] == "record":
                # delete record <type-name> <primary-key>
                if len(parts) < 4:
                    self.log_operation(command, "failure")
                    return
                    
                type_name = parts[2]
                primary_key_str = parts[3]
                
                # Convert primary key to appropriate type
                if type_name in self.catalog:
                    type_def = self.catalog[type_name]
                    primary_key_index = type_def['primary_key_order'] - 1
                    
                    if primary_key_index < 0 or primary_key_index >= len(type_def['field_types']):
                        self.log_operation(command, "failure")
                        return
                    
                    primary_key_type = type_def['field_types'][primary_key_index]
                    
                    try:
                        if primary_key_type == 'int':
                            primary_key_value = int(primary_key_str)
                        else:
                            primary_key_value = str(primary_key_str)
                    except (ValueError, TypeError):
                        self.log_operation(command, "failure")
                        return
                    
                    success = self.delete_record(type_name, primary_key_value)
                    status = "success" if success else "failure"
                else:
                    status = "failure"
                
                self.log_operation(command, status)
            else:
                self.log_operation(command, "failure")
        
        except Exception as e:
            print(f"Error processing command '{command}': {e}")
            import traceback
            traceback.print_exc()  # More detailed error info
            self.log_operation(command, "failure")

    def run(self, input_file_path: str):
        """
        Run the database system using commands from an input file.
        Each command is processed one by one.
        """
        try:
            # Clear output file at start
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write("")  # Clear the file
        except Exception as e:
            print(f"Warning: Could not clear output file: {e}")
        
        # Process input file
        try:
            with open(input_file_path, 'r', encoding='utf-8') as f:
                commands = f.readlines()
                
            print(f"Processing {len(commands)} commands...")
            
            for line_num, line in enumerate(commands, 1):
                line = line.strip()
                if line:
                    print(f"Processing command {line_num}: {line}")
                    try:
                        self.process_command(line)
                    except Exception as e:
                        print(f"Error processing line {line_num}: {e}")
                        import traceback
                        traceback.print_exc()
                        self.log_operation(line, "failure")
                        
        except FileNotFoundError:
            print(f"Input file not found: {input_file_path}")
        except PermissionError:
            print(f"Permission denied reading file: {input_file_path}")
        except Exception as e:
            print(f"Error reading input file: {e}")
            import traceback
            traceback.print_exc()

def main():
    """
    This is the main function. It checks the command line arguments and starts the Dune Archive System.
    The program expects one argument: the path to the input file with commands.
    """
    if len(sys.argv) != 2:
        print("Usage: python3 archive.py <input_file_path>")
        sys.exit(1)
    
    input_file_path = sys.argv[1]
    db_system = DuneArchiveSystem()
    db_system.run(input_file_path)

if __name__ == "__main__":
    main()