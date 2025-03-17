import os
import csv
import zipfile
import xml.etree.ElementTree as ET
import re
import streamlit as st
import time
import io

def extract_text_from_docx(file_content):
    """Extract text from a .docx file content"""
    text = ""
    try:
        # Create a BytesIO object from the file content
        bytes_io = io.BytesIO(file_content)
        
        # Open as a zip file
        with zipfile.ZipFile(bytes_io) as document:
            # The document content is in word/document.xml
            with document.open('word/document.xml') as content:
                # Parse the XML
                tree = ET.parse(content)
                root = tree.getroot()
                
                # Extract all text elements
                namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                for paragraph in root.findall('.//w:p', namespaces):
                    for text_element in paragraph.findall('.//w:t', namespaces):
                        if text_element.text:
                            text += text_element.text + " "
                    text += "\n"
    except Exception as e:
        text = f"[Error extracting text: {str(e)}]"
    
    return text

def extract_text_from_xlsx(file_content):
    """Extract text from a .xlsx file content"""
    text = ""
    try:
        # Create a BytesIO object from the file content
        bytes_io = io.BytesIO(file_content)
        
        # Open as a zip file
        with zipfile.ZipFile(bytes_io) as document:
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
        text = f"[Error extracting text: {str(e)}]"
    
    return text

def extract_text_from_pptx(file_content):
    """Extract text from a .pptx file content"""
    text = ""
    try:
        # Create a BytesIO object from the file content
        bytes_io = io.BytesIO(file_content)
        
        # Open as a zip file
        with zipfile.ZipFile(bytes_io) as presentation:
            # Get a list of all slides
            slides = [f for f in presentation.namelist() if f.startswith('ppt/slides/slide')]
            slides.sort()
            
            # Process each slide
            for i, slide in enumerate(slides):
                text += f"--- Slide {i + 1} ---\n"
                
                with presentation.open(slide) as content:
                    tree = ET.parse(content)
                    root = tree.getroot()
                    
                    # Extract text elements
                    for text_element in root.findall('.//{*}t'):
                        if text_element.text:
                            text += text_element.text + "\n"
                
                text += "\n"
    except Exception as e:
        text = f"[Error extracting text: {str(e)}]"
    
    return text

def extract_text_from_csv(file_content):
    """Extract text from a .csv file content"""
    text = ""
    try:
        # Create a StringIO object from the file content
        content_str = file_content.decode('utf-8')
        
        # Use csv reader to parse the content
        reader = csv.reader(content_str.splitlines())
        for row in reader:
            text += " | ".join(row) + "\n"
    except UnicodeDecodeError:
        try:
            # Try again with Latin-1 encoding
            content_str = file_content.decode('latin-1')
            reader = csv.reader(content_str.splitlines())
            for row in reader:
                text += " | ".join(row) + "\n"
        except Exception as e:
            text = f"[Error extracting text: {str(e)}]"
    except Exception as e:
        text = f"[Error extracting text: {str(e)}]"
    
    return text

def extract_text_from_txt(file_content):
    """Extract text from plain text content"""
    try:
        return file_content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            # Try again with Latin-1 encoding
            return file_content.decode('latin-1')
        except Exception as e:
            return f"[Error extracting text: {str(e)}]"

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
    
    # File upload section
    st.markdown("### 1. Upload your files")
    
    uploaded_files = st.file_uploader("Select files to convert", 
                                      accept_multiple_files=True,
                                      type=["docx", "xlsx", "pptx", "csv", "txt"])
    
    # File types section
    st.markdown("### 2. Supported File Types")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("- Microsoft Word (.docx)")
        st.markdown("- Microsoft Excel (.xlsx)")
        st.markdown("- Microsoft PowerPoint (.pptx)")
    with col2:
        st.markdown("- CSV files (.csv)")
        st.markdown("- Text files (.txt)")
    
    # Process button
    if st.button("Convert Files 🚀") and uploaded_files:
        # Create a placeholder for the status
        status_text = st.empty()
        status_text.text("Starting conversion process...")
        
        # Create a progress bar
        progress_bar = st.progress(0)
        
        # Start time
        start_time = time.time()
        
        # Combined text from all files
        all_text = ""
        
        # Process each uploaded file
        try:
            for i, uploaded_file in enumerate(uploaded_files):
                file_name = uploaded_file.name
                file_extension = os.path.splitext(file_name)[1].lower()
                
                # Update progress
                progress_bar.progress((i + 1) / len(uploaded_files))
                status_text.text(f"Processing {file_name}...")
                
                # Read file content
                file_content = uploaded_file.read()
                
                # Add file header
                all_text += f"\n\n==== BEGIN FILE: {file_name} ====\n\n"
                
                # Extract text based on file extension
                if file_extension == '.docx':
                    text_content = extract_text_from_docx(file_content)
                elif file_extension == '.xlsx':
                    text_content = extract_text_from_xlsx(file_content)
                elif file_extension == '.pptx':
                    text_content = extract_text_from_pptx(file_content)
                elif file_extension == '.csv':
                    text_content = extract_text_from_csv(file_content)
                elif file_extension == '.txt':
                    text_content = extract_text_from_txt(file_content)
                else:
                    text_content = f"[Unsupported file type: {file_extension}]"
                
                all_text += text_content
                
                # Add file footer
                all_text += f"\n\n==== END FILE: {file_name} ====\n\n"
            
            # End time
            end_time = time.time()
            
            # Success message
            status_text.empty()
            st.success(f"✅ Conversion complete! Processed {len(uploaded_files)} files in {end_time - start_time:.1f} seconds.")
            
            # Output file details
            text_size_kb = len(all_text) / 1024
            st.info(f"📊 Text size: {text_size_kb:.2f} KB")
            
            # Add a download button
            st.download_button(
                label="Download Text File",
                data=all_text,
                file_name="all_content.txt",
                mime="text/plain"
            )
            
            # Preview section
            with st.expander("Preview content"):
                preview_length = min(5000, len(all_text))
                st.text_area("Content preview (first 5000 characters)", all_text[:preview_length], height=300)
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    elif st.button("Convert Files 🚀") and not uploaded_files:
        st.warning("Please upload files first!")
    
    # Footer
    st.markdown("""
        <div class="footer">
            File to Text Converter - Made with ❤️ using Streamlit
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
