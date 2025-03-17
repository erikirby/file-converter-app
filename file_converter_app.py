import os
import sys
import csv
import zipfile
import xml.etree.ElementTree as ET
import re
import streamlit as st
import time

def extract_text_from_docx(filepath):
    """Extract text from a .docx file"""
    text = ""
    try:
        # .docx files are zip archives
        with zipfile.ZipFile(filepath) as document:
            # The document content is in word/document.xml
            with document.open('word/document.xml') as content:
                # Parse the XML
                tree = ET.parse(content)
                root = tree.getroot()
                
                # Extract all text elements (this is a simplified approach)
                # The XML namespace in .docx files can be complex
                namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                for paragraph in root.findall('.//w:p', namespaces):
                    for text_element in paragraph.findall('.//w:t', namespaces):
                        if text_element.text:
                            text += text_element.text + " "
                    text += "\n"
    except Exception as e:
        text = f"[Error extracting text from {os.path.basename(filepath)}: {str(e)}]"
    
    return text

def extract_text_from_xlsx(filepath):
    """Extract text from a .xlsx file (simplified, just gets shared strings)"""
    text = ""
    try:
        # .xlsx files are zip archives
        with zipfile.ZipFile(filepath) as document:
            # Try to extract data from sheets
            sheet_files = [f for f in document.namelist() if f.startswith('xl/worksheets/sheet')]
            
            # Simple approach: just extract the shared strings
            if 'xl/sharedStrings.xml' in document.namelist():
                with document.open('xl/sharedStrings.xml') as content:
                    tree = ET.parse(content)
                    root = tree.getroot()
                    
                    # Extract all text elements
                    for string_item in root.findall('.//{*}t'):
                        if string_item.text:
                            text += string_item.text + "\n"
    except Exception as e:
        text = f"[Error extracting text from {os.path.basename(filepath)}: {str(e)}]"
    
    return text

def extract_text_from_pptx(filepath):
    """Extract text from a .pptx file"""
    text = ""
    try:
        # .pptx files are zip archives
        with zipfile.ZipFile(filepath) as presentation:
            # Get a list of all slides
            slides = [f for f in presentation.namelist() if f.startswith('ppt/slides/slide')]
            slides.sort()
            
            # Process each slide
            for slide in slides:
                text += f"--- Slide {slides.index(slide) + 1} ---\n"
                
                with presentation.open(slide) as content:
                    tree = ET.parse(content)
                    root = tree.getroot()
                    
                    # Extract text elements (simplified)
                    for text_element in root.findall('.//{*}t'):
                        if text_element.text:
                            text += text_element.text + "\n"
                
                text += "\n"
    except Exception as e:
        text = f"[Error extracting text from {os.path.basename(filepath)}: {str(e)}]"
    
    return text

def extract_text_from_csv(filepath):
    """Extract text from a .csv file"""
    text = ""
    try:
        with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                text += " | ".join(row) + "\n"
    except Exception as e:
        try:
            # Try again with Latin-1 encoding if UTF-8 fails
            with open(filepath, 'r', newline='', encoding='latin-1') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    text += " | ".join(row) + "\n"
        except Exception as e2:
            text = f"[Error extracting text from {os.path.basename(filepath)}: {str(e2)}]"
    
    return text

def extract_text_from_txt(filepath):
    """Extract text from plain text file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        try:
            # Try again with Latin-1 encoding
            with open(filepath, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            return f"[Error extracting text from {os.path.basename(filepath)}: {str(e)}]"

def process_files(directory_path, output_file, progress_callback=None):
    """Process all files in the given directory and extract text"""
    
    # Define which file extensions to process
    supported_extensions = {
        '.docx': extract_text_from_docx,
        '.xlsx': extract_text_from_xlsx,
        '.pptx': extract_text_from_pptx,
        '.csv': extract_text_from_csv,
        '.txt': extract_text_from_txt,
    }
    
    # Find all files
    all_files = []
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            if file_ext in supported_extensions:
                all_files.append((file_path, file_ext))
    
    # Process each file
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for i, (file_path, file_ext) in enumerate(all_files):
            try:
                file_name = os.path.basename(file_path)
                
                # Update progress
                if progress_callback:
                    progress_callback((i + 1) / len(all_files))
                
                # Write file header
                out_file.write(f"\n\n==== BEGIN FILE: {file_name} ====\n\n")
                
                # Extract text based on file type
                extract_function = supported_extensions[file_ext]
                text_content = extract_function(file_path)
                out_file.write(text_content)
                
                # Write file footer
                out_file.write(f"\n\n==== END FILE: {file_name} ====\n\n")
                
            except Exception as e:
                st.error(f"Error processing {file_path}: {str(e)}")
    
    return len(all_files)

def main():
    st.set_page_config(
        page_title="File to Text Converter",
        page_icon="📄",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    
    # Custom CSS to make it prettier
    st.markdown("""
        <style>
        .main {
            background-color: #f5f7ff;
            border-radius: 10px;
            padding: 20px;
        }
        .stButton>button {
            background-color: #4f8bf9;
            color: white;
            border-radius: 5px;
            padding: 10px 15px;
            font-weight: bold;
        }
        h1 {
            color: #1f3d7a;
        }
        .footer {
            margin-top: 50px;
            text-align: center;
            color: #888;
            font-size: 12px;
        }
        .stProgress > div > div > div > div {
            background-color: #4f8bf9;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("📄 File to Text Converter")
    st.subheader("Convert your documents to a single text file for AI training")
    
    # File selection section
    st.markdown("### 1. Select your files folder")
    
    directory_path = st.text_input("Folder containing your files:", 
                                  placeholder="e.g., /Users/username/Documents/MyFiles")
    
    # Check if directory exists
    if directory_path and not os.path.isdir(directory_path):
        st.warning("⚠️ This directory doesn't exist. Please enter a valid folder path.")
    
    # Output file section
    st.markdown("### 2. Choose output file location")
    output_file = st.text_input("Output file path:", 
                              value=os.path.join(os.path.expanduser("~"), "Desktop", "all_content.txt") if directory_path else "",
                              placeholder="e.g., /Users/username/Desktop/all_content.txt")
    
    # File types section
    st.markdown("### 3. Supported File Types")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("- Microsoft Word (.docx)")
        st.markdown("- Microsoft Excel (.xlsx)")
        st.markdown("- Microsoft PowerPoint (.pptx)")
    with col2:
        st.markdown("- CSV files (.csv)")
        st.markdown("- Text files (.txt)")
    
    # Process button
    if st.button("Convert Files 🚀"):
        if not directory_path or not os.path.isdir(directory_path):
            st.error("Please select a valid folder first!")
            return
        
        if not output_file:
            st.error("Please specify an output file!")
            return
        
        # Create a placeholder for the status
        status_text = st.empty()
        status_text.text("Scanning for files...")
        
        # Create a progress bar
        progress_bar = st.progress(0)
        
        # Start time
        start_time = time.time()
        
        # Process the files
        try:
            file_count = process_files(directory_path, output_file, progress_bar.progress)
            
            # End time
            end_time = time.time()
            
            # Calculate file size
            file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
            
            # Success message
            st.success(f"✅ Conversion complete! Processed {file_count} files in {end_time - start_time:.1f} seconds.")
            
            # Output file details
            st.info(f"📊 Output file: {output_file}")
            st.info(f"📊 File size: {file_size_mb:.2f} MB")
            
            # Add a download button
            with open(output_file, "rb") as file:
                st.download_button(
                    label="Download Text File",
                    data=file,
                    file_name=os.path.basename(output_file),
                    mime="text/plain"
                )
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    # Footer
    st.markdown("""
        <div class="footer">
            File to Text Converter - Made with ❤️ using Streamlit
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()