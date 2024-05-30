import pandas as pd

def print_excel_contents(excel_file):
    try:
        excel_data = pd.read_excel(excel_file, engine='openpyxl')
    except Exception as e:
        print(f"Error reading the Excel file: {e}")
        return

    print(excel_data)

if __name__ == "__main__":
    print_excel_contents('DNS_Request_Form.xlsx')
