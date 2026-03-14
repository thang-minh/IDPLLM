import fitz

print(f"PyMuPDF version being tested: {fitz.__doc__}")
print(f"Path to fitz module: {fitz.__file__}")

attributes_to_check = [
    "PDF_ENCRYPT_NONE",
    "PDF_PERM_PRINT",
    "PDF_PERM_COPY",
    "PDF_PERM_MODIFY",
    "PDF_PERM_ANNOTATE",
    "PDF_PERM_FILL_FORM", # Đây là thuộc tính gây lỗi
    "PDF_PERM_ACCESSIBILITY",
    "PDF_PERM_ASSEMBLE",
    "PDF_PERM_PRINT_HQ"
]

all_attributes_exist = True
for attr_name in attributes_to_check:
    if hasattr(fitz, attr_name):
        print(f"Attribute '{attr_name}' exists in fitz.")
    else:
        print(f"!!!!!!!!!!!!!!!!!!!! ATTRIBUTE '{attr_name}' DOES NOT EXIST in fitz. !!!!!!!!!!!!!!!!!!!!")
        all_attributes_exist = False

if all_attributes_exist:
    print("\nAll checked permission attributes seem to exist in this PyMuPDF version.")
    # Thử truy cập trực tiếp
    try:
        perm_value = fitz.PDF_PERM_FILL_FORM
        print(f"Successfully accessed fitz.PDF_PERM_FILL_FORM, value: {perm_value}")
    except AttributeError as e:
        print(f"ERROR accessing fitz.PDF_PERM_FILL_FORM directly: {e}")
else:
    print("\nOne or more permission attributes are missing. This indicates an issue with the PyMuPDF version or installation.")