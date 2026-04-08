import os
import glob
import subprocess
import shutil
import re
from pypdf import PdfReader
import difflib

def get_project_titles():
    projects_dir = "projects"
    titles = {}
    
    if not os.path.exists(projects_dir):
        print(f"Error: {projects_dir} directory not found.")
        return titles

    for project_name in os.listdir(projects_dir):
        project_path = os.path.join(projects_dir, project_name)
        tex_file = os.path.join(project_path, "questionnaire.tex")
        
        if os.path.exists(tex_file):
            with open(tex_file, "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(r'\\title\{([^}]+)\}', content)
                if match:
                    titles[project_name] = match.group(1).strip()
                    
    return titles

def extract_pdf_title(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        first_page = reader.pages[0]
        text = first_page.extract_text()
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            return " ".join(lines[:3])
    except Exception as e:
        print(f"    Failed to read PDF text: {e}")
    return ""

def main():
    titles = get_project_titles()
    if not titles:
        print("No project titles found. Exiting.")
        return
        
    print("Found Projects and Titles:")
    for proj, title in titles.items():
        print(f"  {proj}: {title}")

    base_dest_dir = "sortedSurveys"
    for project_name in titles.keys():
        dest_folder = os.path.join(base_dest_dir, f"{project_name}")
        os.makedirs(dest_folder, exist_ok=True)
        print(f"Created/Verified folder: {dest_folder}/")
        
    unscanned_dir = "newSurveys"
    if not os.path.exists(unscanned_dir):
        print(f"\n{unscanned_dir}/ directory not found. No images to process.")
        return
        
    print("\nProcessing images in 'newSurveys/' ...")
    valid_extensions = ('.png', '.jpg', '.jpeg', '.tiff')
    
    for filename in os.listdir(unscanned_dir):
        if not filename.lower().endswith(valid_extensions):
            continue
            
        img_path = os.path.join(unscanned_dir, filename)
        base_name = os.path.splitext(filename)[0]
        temp_pdf_base = os.path.join(unscanned_dir, f"{base_name}_temp")
        out_pdf_path = f"{temp_pdf_base}.pdf"
        
        print(f"\n- Converting: {filename} to searchable PDF...")

        try:
            subprocess.run(["tesseract", img_path, temp_pdf_base, "pdf"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"    Tesseract failed for {filename}: {e}")
            continue
            

        extracted_text = extract_pdf_title(out_pdf_path)
        print(f"    Extracted top text: '{extracted_text[:60]}...'")
        

        best_match = None
        best_ratio = 0.0
        
        for proj, title in titles.items():
       
            sm = difflib.SequenceMatcher(None, title.lower(), extracted_text.lower())
 
            ratio = max([difflib.SequenceMatcher(None, title.lower(), extracted_text[i:i+len(title)].lower()).ratio() 
                         for i in range(max(1, len(extracted_text) - len(title) + 1))])
            
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = proj

        if best_match and best_ratio > 0.6:  
            print(f"    -> MATCHED to project '{best_match}' (Confidence: {best_ratio:.2f})")
            _, ext = os.path.splitext(filename)
            final_dest = os.path.join(base_dest_dir, f"{best_match}", f"{base_name}{ext}")
            shutil.move(img_path, final_dest)
            
            if os.path.exists(out_pdf_path):
                os.remove(out_pdf_path)
                
            print(f"    -> Moved image to {final_dest} and removed temp PDF")
        else:
            if os.path.exists(out_pdf_path):
                os.remove(out_pdf_path)
            print(f"    -> NO MATCH FOUND (Best was {best_match} at {best_ratio:.2f}). Leaving image in newSurveys/")

if __name__ == "__main__":
    main()