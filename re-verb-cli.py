import os
import argparse
import sys

def generate_context(root_path, output_file="project_context.xml"):
    """
    Generates a high-reasoning XML context file for LLMs.
    Respects common ignore patterns and skips binaries.
    """
    junk_patterns = {
        '.git', 'node_modules', '.next', 'dist', 'build', '.cache',
        'vendor', '.venv', 'venv', '__pycache__', '.upm', '.replit',
        '.DS_Store'
    }
    
    binary_extensions = {
        '.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.zip', '.tar', '.gz',
        '.exe', '.bin', '.dll', '.so', '.dylib', '.woff', '.woff2', '.ttf', 
        '.eot', '.mp4', '.mp3', '.wav', '.flac', '.avi', '.mov', '.webm', '.map'
    }

    print(f"🚀 RE-VERB: Scanning {root_path}...")
    
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write("<project_context>\n")
        
        for root, dirs, files in os.walk(root_path):
            # Prune junk directories in-place
            dirs[:] = [d for d in dirs if d not in junk_patterns]
            
            for file in files:
                if any(file.endswith(ext) for ext in binary_extensions):
                    continue
                
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, root_path)
                
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    out.write("  <file>\n")
                    out.write(f"    <path>{rel_path}</path>\n")
                    out.write("    <content>\n")
                    out.write(content)
                    out.write("\n    </content>\n")
                    out.write("  </file>\n")
                except Exception as e:
                    print(f"⚠️ Skipping {rel_path}: {e}")

        out.write("</project_context>\n")
    
    print(f"✅ Success! Context saved to: {os.path.abspath(output_file)}")
    print("📋 Copy the contents of this file into Claude/GPT to begin.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RE-VERB CLI Pro - The LLM Context Cloner")
    parser.add_argument("path", nargs="?", default=".", help="Path to the project root (default: current dir)")
    parser.add_argument("-o", "--output", default="project_context.xml", help="Output filename")
    
    args = parser.parse_args()
    generate_context(args.path, args.output)
