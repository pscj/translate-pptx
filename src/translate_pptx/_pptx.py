from typing import List
from pptx.util import Pt

def get_english_font_size(chinese_size_pt: float) -> float:
    """Map Chinese font size to optimal English font size for visual balance.
    
    Chinese characters are denser and more complex, so English text typically
    needs to be slightly larger to achieve similar visual weight.
    """
    # Mapping table based on common PPT font sizes
    # Chinese -> English (slightly larger for readability)
    size_map = {
        8: 9,
        9: 10,
        10: 11,
        11: 12,
        12: 13,
        14: 14,   # Keep same for body text
        16: 16,   # Keep same for subtitles
        18: 18,   # Keep same for titles
        20: 20,
        22: 22,
        24: 24,
        28: 28,
        32: 32,
        36: 36,
        44: 44,
    }
    
    # Find closest match
    if chinese_size_pt in size_map:
        return size_map[chinese_size_pt]
    
    # For sizes not in map, use proportional adjustment
    # Small text (< 12pt): +1pt
    # Medium text (12-18pt): same
    # Large text (> 18pt): same
    if chinese_size_pt < 12:
        return chinese_size_pt + 1
    else:
        return chinese_size_pt

def extract_text_from_slides(pptx_path: str) -> List[List[List[str]]]:
    """Extract text from a PowerPoint presentation file and return it as a list of lists of strings."""
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE

    def is_chart_shape(shape):
        """Check if a shape is part of a chart or diagram."""
        # Check if it's a chart type
        if shape.shape_type == MSO_SHAPE_TYPE.CHART:
            return True
        # Check if it's a group (diagrams are often groups)
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            return True
        # Check if shape name suggests it's part of a chart/diagram
        if hasattr(shape, 'name'):
            name_lower = shape.name.lower()
            if any(keyword in name_lower for keyword in ['chart', 'diagram', 'smartart']):
                return True
        return False

    def extract_shape_text(shape, use_run_mode=False):
        """Extract text from a single shape, handling different shape types."""
        shape_data = []
        
        # Handle tables
        if shape.shape_type == MSO_SHAPE_TYPE.TABLE:
            for row in shape.table.rows:
                for cell in row.cells:
                    if hasattr(cell, "text_frame"):
                        for paragraph in cell.text_frame.paragraphs:
                            # Combine all runs in a paragraph into one text
                            para_text = ''.join([run.text for run in paragraph.runs])
                            if para_text:  # Only add non-empty paragraphs
                                shape_data.append(para_text)
            return shape_data if shape_data else None
        
        # Handle grouped shapes
        elif shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            for sub_shape in shape.shapes:
                sub_data = extract_shape_text(sub_shape, use_run_mode)
                if sub_data:
                    shape_data.extend(sub_data)
            return shape_data if shape_data else None
        
        # Handle shapes with text_frame (text boxes, titles, etc.)
        elif hasattr(shape, "text_frame"):
            if use_run_mode:
                # For charts: extract each run separately
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        if run.text:  # Only add non-empty runs
                            shape_data.append(run.text)
            else:
                # For normal text: combine runs in a paragraph
                for paragraph in shape.text_frame.paragraphs:
                    para_text = ''.join([run.text for run in paragraph.runs])
                    if para_text:  # Only add non-empty paragraphs
                        shape_data.append(para_text)
            return shape_data if shape_data else None
        
        # Handle shapes with simple text attribute
        elif hasattr(shape, "text"):
            text = shape.text.strip()
            return text if text else None
        
        return None

    prs = Presentation(pptx_path)
    all_texts = []

    for slide in prs.slides:
        slide_texts = []
        for shape in slide.shapes:
            # Use run mode for charts, paragraph mode for others
            use_run_mode = is_chart_shape(shape)
            extracted = extract_shape_text(shape, use_run_mode)
            if extracted is not None:
                slide_texts.append(extracted)
        all_texts.append(slide_texts)

    return all_texts


def replace_text_in_slides(pptx_path: str, new_texts: List[List[List[str]]], output_path: str, target_language: str = "English"):
    """Replace text in a PowerPoint presentation file with new text."""
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    from pptx.enum.shapes import PP_PLACEHOLDER

    def is_title_shape(shape):
        """Check if a shape is a title placeholder."""
        try:
            if hasattr(shape, 'placeholder_format'):
                placeholder_type = shape.placeholder_format.type
                # Title, center title, or subtitle
                return placeholder_type in [PP_PLACEHOLDER.TITLE, 
                                           PP_PLACEHOLDER.CENTER_TITLE, 
                                           PP_PLACEHOLDER.SUBTITLE]
        except:
            pass
        return False

    def is_chart_shape(shape):
        """Check if a shape is part of a chart or diagram."""
        # Check if it's a chart type
        if shape.shape_type == MSO_SHAPE_TYPE.CHART:
            return True
        # Check if it's a group (diagrams are often groups)
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            return True
        # Check if shape name suggests it's part of a chart/diagram
        if hasattr(shape, 'name'):
            name_lower = shape.name.lower()
            if any(keyword in name_lower for keyword in ['chart', 'diagram', 'smartart']):
                return True
        return False

    def replace_shape_text(shape, text_data, is_title=False, use_run_mode=False):
        """Replace text in a single shape, handling different shape types."""
        para_index = 0
        run_index = 0
        
        # Handle tables
        if shape.shape_type == MSO_SHAPE_TYPE.TABLE:
            for row in shape.table.rows:
                for cell in row.cells:
                    if hasattr(cell, "text_frame"):
                        for paragraph in cell.text_frame.paragraphs:
                            if para_index < len(text_data):
                                # Get original paragraph text
                                original_text = ''.join([run.text for run in paragraph.runs])
                                if original_text:
                                    translated = translate(original_text, text_data[para_index])
                                    # Get original font size BEFORE clearing runs
                                    original_size = None
                                    if target_language.lower() == "english":
                                        for run in paragraph.runs:
                                            if run.font.size:
                                                original_size = run.font.size.pt
                                                break
                                    
                                    # Clear all runs to avoid format expansion
                                    while paragraph.runs:
                                        paragraph._element.remove(paragraph.runs[0]._r)
                                    
                                    # Add new run with translated text (no formatting)
                                    new_run = paragraph.add_run()
                                    new_run.text = translated
                                    
                                    # Adjust font size for English based on Chinese size
                                    if target_language.lower() == "english":
                                        if original_size:
                                            new_run.font.size = Pt(get_english_font_size(original_size))
                                        else:
                                            # Default to 11pt if no size found
                                            new_run.font.size = Pt(11)
                                    para_index += 1
        
        # Handle grouped shapes
        elif shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            for sub_shape in shape.shapes:
                if use_run_mode:
                    # Pass remaining data and get back the number of items consumed
                    consumed = replace_shape_text(sub_shape, text_data[run_index:], is_title, use_run_mode)
                    run_index += consumed
                else:
                    consumed = replace_shape_text(sub_shape, text_data[para_index:], is_title, use_run_mode)
                    para_index += consumed
        
        # Handle shapes with text_frame
        elif hasattr(shape, "text_frame"):
            if use_run_mode:
                # For charts: replace each run individually
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        # Only replace non-empty runs (matching extraction logic)
                        if run.text and run_index < len(text_data):
                            run.text = translate(run.text, text_data[run_index])
                            run_index += 1
            else:
                # For normal text: replace by paragraph
                for paragraph in shape.text_frame.paragraphs:
                    if para_index < len(text_data):
                        # Get original paragraph text
                        original_text = ''.join([run.text for run in paragraph.runs])
                        if original_text:
                            translated = translate(original_text, text_data[para_index])
                            # Get original font size BEFORE clearing runs
                            original_size = None
                            if target_language.lower() == "english":
                                for run in paragraph.runs:
                                    if run.font.size:
                                        original_size = run.font.size.pt
                                        break
                            
                            # Clear all runs to avoid format expansion
                            while paragraph.runs:
                                paragraph._element.remove(paragraph.runs[0]._r)
                            
                            # Add new run with translated text (no formatting)
                            new_run = paragraph.add_run()
                            new_run.text = translated
                            
                            # Adjust font size for English based on Chinese size
                            if target_language.lower() == "english":
                                if original_size:
                                    new_run.font.size = Pt(get_english_font_size(original_size))
                                else:
                                    # Default to 11pt if no size found
                                    new_run.font.size = Pt(11)
                            para_index += 1
        
        # Handle shapes with simple text attribute
        elif hasattr(shape, "text"):
            if isinstance(text_data, str):
                shape.text = translate(shape.text, text_data)
            elif para_index < len(text_data):
                shape.text = translate(shape.text, text_data[para_index])
        
        return run_index if use_run_mode else para_index

    prs = Presentation(pptx_path)

    for slide, slide_texts in zip(prs.slides, new_texts):
        shape_index = 0
        for shape in slide.shapes:
            # Check if this shape has extractable text (same logic as extraction)
            has_text = False
            if shape.shape_type == MSO_SHAPE_TYPE.TABLE:
                has_text = True
            elif shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                has_text = True
            elif hasattr(shape, "text_frame"):
                # Check if there's any non-empty paragraph
                for paragraph in shape.text_frame.paragraphs:
                    para_text = ''.join([run.text for run in paragraph.runs])
                    if para_text:
                        has_text = True
                        break
            elif hasattr(shape, "text"):
                if shape.text.strip():
                    has_text = True
            
            # Only replace text in shapes that have text
            if has_text and shape_index < len(slide_texts):
                is_title = is_title_shape(shape)
                use_run_mode = is_chart_shape(shape)
                replace_shape_text(shape, slide_texts[shape_index], is_title, use_run_mode)
                shape_index += 1

    prs.save(output_path)

def translate(old_text, new_text):
    if old_text != new_text:
        print(f"Translating '{old_text}' to '{new_text}'")
    return new_text