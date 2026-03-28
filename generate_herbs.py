import json
import os
import re

def generate_herb_pages():
    # Load herbs data
    with open('herbcraft/herbs.json', 'r') as f:
        herbs = json.load(f)
    
    # Load template
    with open('herbcraft/herb-template.html', 'r') as f:
        template = f.read()

    # Ensure herbs directory exists
    os.makedirs('herbs', exist_ok=True)

    for herb in herbs:
        filename = f"herbcraft/herbs/{herb['id']}.html"
        
        # Simple replacement logic for the template
        content = template.replace('[Herb Name]', herb['name'])
        content = content.replace('[Scientific Name]', herb.get('scientific', ''))
        
        # Inject Overview
        overview_html = f"<h2>Overview</h2>\n<p>{herb.get('overview', '')}</p>"
        content = re.sub(r'<h2>Overview</h2>.*?<h2>Traditional Uses</h2>', f"{overview_html}\n\n<h2>Traditional Uses</h2>", content, flags=re.DOTALL)
        
        # Inject Traditional Uses
        trad_html = f"<h2>Traditional Uses</h2>\n<p>{herb.get('traditional', '')}</p>"
        content = re.sub(r'<h2>Traditional Uses</h2>.*?<h2>Active Compounds</h2>', f"{trad_html}\n\n<h2>Active Compounds</h2>", content, flags=re.DOTALL)

        # Inject Active Compounds
        active_html = f"<h2>Active Compounds</h2>\n<p>{herb.get('active_compounds', '')}</p>"
        content = re.sub(r'<h2>Active Compounds</h2>.*?<h2>Potential Benefits</h2>', f"{active_html}\n\n<h2>Potential Benefits</h2>", content, flags=re.DOTALL)

        # Inject Benefits
        benefits_html = f"<h2>Potential Benefits</h2>\n<p>{herb.get('benefits', '')}</p>"
        content = re.sub(r'<h2>Potential Benefits</h2>.*?<h2>Safety & Side Effects</h2>', f"{benefits_html}\n\n<h2>Safety & Side Effects</h2>", content, flags=re.DOTALL)

        # Inject Safety
        safety_html = f"<h2>Safety & Side Effects</h2>\n<p>{herb.get('safety_info', '')}</p>"
        content = re.sub(r'<h2>Safety & Side Effects</h2>.*?<div class="when-to-see-doctor">', f"{safety_html}\n\n<div class=\"when-to-see-doctor\">", content, flags=re.DOTALL)

        # Inject References (Simple list)
        ref_list = herb.get('references', [])
        ref_html = ""
        for i, ref in enumerate(ref_list):
            ref_html += f'<li id="ref-{i+1}">{ref}</li>\n'
        
        content = re.sub(r'<ol class="references-list">.*?</ol>', f'<ol class="references-list">\n{ref_html}</ol>', content, flags=re.DOTALL)

        # Write file
        with open(filename, 'w') as f:
            f.write(content)
        print(f"Generated {filename}")

if __name__ == "__main__":
    generate_herb_pages()
