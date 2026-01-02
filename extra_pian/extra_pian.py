import os
import re
from bs4 import BeautifulSoup
import json

def extract_pian_info(directory_path):
    # Dictionary to store results: Filename -> List of {'id': pian_id, 'name': venue_name}
    result_dict = {}

    # Iterate over all files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".html") or filename.endswith(".htm"):
            file_path = os.path.join(directory_path, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                soup = BeautifulSoup(content, 'html.parser')
                
                # Find all elements with 'pian' attribute
                tags = soup.find_all(attrs={"pian": True})
                
                pian_list = []
                for tag in tags:
                    pian_id = tag['pian']
                    
                    # Try to find the name
                    # Strategy 1: Look for <p> inside <div class="imageTitle">
                    name = "Unknown"
                    title_div = tag.find("div", class_="imageTitle")
                    if title_div:
                        p_tag = title_div.find("p")
                        if p_tag:
                            name = p_tag.get_text(strip=True)
                    
                    # Strategy 2: If Strategy 1 fails, check 'title' attribute of the tag
                    if name == "Unknown" or not name:
                        title_attr = tag.get('title', '')
                        if '-' in title_attr:
                            name = title_attr.split('-')[-1]
                        elif title_attr:
                            name = title_attr
                            
                    pian_list.append({'id': pian_id, 'name': name})
                
                # Store in result dict, removing extension from filename for key
                key_name = os.path.splitext(filename)[0].replace('&nbsp;', ' ')
                result_dict[key_name] = pian_list
                
                print(f"File {filename} processed, found {len(pian_list)} items.")

            except Exception as e:
                print(f"Error reading {filename}: {e}")

    return result_dict

if __name__ == "__main__":
    HTML_FOLDER = '.' 
    
    info_map = extract_pian_info(HTML_FOLDER)

    print("\n" + "="*30)
    print("Extraction Result (Python Dict Format):")
    print("="*30)
    
    # Print as a formatted Python dictionary
    print("PIAN_INFO_MAP = {")
    for venue, items in info_map.items():
        print(f"    '{venue}': [")
        for item in items:
            print(f"        {{'id': '{item['id']}', 'name': '{item['name']}'}},")
        print("    ],")
    print("}")