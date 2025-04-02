sl = '''resp = {"product": "bike", "brand": "Adrenex", "style": "mountain", "quality": "mid-range", "features": ["disc brakes", "front suspension", "aluminum frame"]}'''
sl = sl.replace("\n", "").replace("  ", "")
sl = sl.replace(',"', ', "')
sl = sl.replace('": "', '** - ')
sl = sl.replace(', "', '\n**')
sl = sl.replace('{"', '**')
sl = sl.replace('"', '')
sl = sl.replace('[', '')
sl = sl.replace(']', '')
sl = sl.replace('}', '')
sl = sl.replace(': ', '** - ')













print(sl)