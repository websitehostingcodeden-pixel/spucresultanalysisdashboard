import pandas as pd
import io


def read_excel(file):
    """
    Read Excel file and extract SCIENCE and COMMERCE sheets
    
    Args:
        file: Django UploadedFile object
        
    Returns:
        pd.DataFrame with combined data from both sheets with 'stream' column
        
    Raises:
        Exception: If sheets are missing or file is invalid
    """
    try:
        # Read the file into memory
        file_content = file.read()
        excel_file = io.BytesIO(file_content)
        
        # Load Excel file
        xls = pd.ExcelFile(excel_file)
        
        # Check for required sheets
        required_sheets = ["SCIENCE", "COMMERCE"]
        
        for sheet in required_sheets:
            if sheet not in xls.sheet_names:
                raise ValueError(f"Missing required sheet: {sheet}")
        
        # Read both sheets
        df_science = pd.read_excel(xls, "SCIENCE")
        df_commerce = pd.read_excel(xls, "COMMERCE")
        
        # Add stream column
        df_science["stream"] = "SCIENCE"
        df_commerce["stream"] = "COMMERCE"
        
        # Combine dataframes
        df = pd.concat([df_science, df_commerce], ignore_index=True)
        
        return df
        
    except Exception as e:
        raise Exception(f"Excel read failed: {str(e)}")
