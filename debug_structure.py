#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug script to check PPT structure"""

import sys
sys.path.insert(0, 'src')

from translate_pptx._pptx import extract_text_from_slides

# Extract text from the test file
texts = extract_text_from_slides("test.pptx")

print("="*60)
print("EXTRACTED STRUCTURE:")
print(f"Total slides: {len(texts)}")
for i, slide in enumerate(texts):
    print(f"\nSlide {i}: {len(slide)} shapes")
    for j, shape in enumerate(slide):
        if isinstance(shape, list):
            print(f"  Shape {j}: list with {len(shape)} runs")
            for k, run in enumerate(shape):  # Show ALL runs
                # Show repr to see escape characters like \n
                print(f"    Run {k}: {repr(run)}")
        else:
            if len(shape) > 80:
                print(f"  Shape {j}: string - '{shape[:80]}...'")
            else:
                print(f"  Shape {j}: string - '{shape}'")
print("="*60)
