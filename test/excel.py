import pandas as pd

# Define dummy data
data = [
    ["ABC Pvt Ltd", "private ltd", "05-10-2020", "John Doe", "CEO", 9876543210, 9876543211, "abc@example.com", "IT Services", "active", "pan", "abc123", "pass123", "Verified", "c:/Users/Abhiraj Das/Documents/book66.xlsx", "c:/Users/Abhiraj Das/Documents/book66.xlsx", "c:/Users/Abhiraj Das/Documents/book66.xlsx"],
    ["XYZ LLP", "llp", "08-15-2019", "Jane Smith", "Manager", 7894561230, 7894561231, "xyz@example.com", "Finance", "active", "tan", "xyz456", "pass456", "Urgent", "c:/Users/Abhiraj Das/Documents/1212.xlsx", "c:/Users/Abhiraj Das/Documents/book66.xlsx", "c:/Users/Abhiraj Das/Documents/book66.xlsx"],
    ["LMN Trust", "trust", "11-20-2018", "Robert Brown", "Director", 8547123690, 8547123691, "lmn@example.com", "Education", "inactive", "msme", "lmn789", "pass789", "Pending", "c:/Users/Abhiraj Das/Documents/book66.xlsx", "c:/Users/Abhiraj Das/Documents/book66.xlsx", "c:/Users/Abhiraj Das/Documents/book66.xlsx"],
    ["PQR HUF", "huf", "02-05-2021", "Alice Green", "Founder", 9638527410, 9638527411, "pqr@example.com", "Consulting", "active", "pf", "pqr123", "pass123", "Approved", "c:/Users/Abhiraj Das/Documents/book66.xlsx", "c:/Users/Abhiraj Das/Documents/book66.xlsx", "c:/Users/Abhiraj Das/Documents/book66.xlsx"],
    ["EFG OPC", "opc", "07-30-2017", "Michael Scott", "MD", 7418529630, 7418529631, "efg@example.com", "Marketing", "inactive", "esic", "efg456", "pass456", "Rejected", "c:/Users/Abhiraj Das/Documents/book66.xlsx", "c:/Users/Abhiraj Das/Documents/book66.xlsx", "c:/Users/Abhiraj Das/Documents/book66.xlsx"]
]

# Define column names
columns = ["client_name", "entity_type", "date_of_incorporation", "contact_person", "designation", "contact_no_1", "contact_no_2", "email", "business_detail", "status", "document_type", "login", "password", "remark", "file1", "file2", "file3"]

# Create DataFrame
df = pd.DataFrame(data, columns=columns)

# Save to Excel
df.to_excel("dummy_data.xlsx", index=False)
print("Excel file created: dummy_data.xlsx")
