import pandas as pd

# Sample JSON data (list of dictionaries)
json_data = [
    {"Name": "Alice", "Age": 30, "City": "New York"},
    {"Name": "Bob", "Age": 25, "City": "Los Angeles"},
    {"Name": "Charlie", "Age": 35, "City": "Chicago"}
]

# Create a Pandas DataFrame
df = pd.DataFrame(json_data)

# Export DataFrame to Excel
df.to_excel("output.xlsx", index=False, engine='openpyxl')

print("JSON data exported to output.xlsx")