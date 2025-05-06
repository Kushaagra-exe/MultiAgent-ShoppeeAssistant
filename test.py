import json

# The input string in JSON format
string = '{ "product": "t-shirt", "brand": "Nike", "style": "Graphic T-Shirt", "quality": "High", "features": ["Crew Neck", "Short Sleeves", "Floral Design", "Logo Print"] }'

# Parse the string to a dictionary
data = json.loads(string)

# Function to format the dictionary to Markdown dynamically
def format_to_markdown(data):
    markdown = ""
    
    # Loop through the dictionary and format each key-value pair
    for key, value in data.items():
        if isinstance(value, list):  # If the value is a list (e.g., 'features')
            markdown += f"**{key.capitalize()}**:\n"
            for item in value:
                markdown += f"- {item}\n"
        else:  # If it's a single value
            markdown += f"**{key.capitalize()}**: {value}\n"
    
    return markdown

formatted_markdown = format_to_markdown(data)
print(formatted_markdown)
