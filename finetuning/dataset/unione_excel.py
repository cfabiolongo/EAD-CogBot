import pandas as pd

# Leggi i due file Excel
file1 = './snippet_train.xlsx'
file2 = './train_refined.xlsx'

df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

# Fonda i DataFrame
merged_df = pd.concat([df1, df2], ignore_index=True)

# Salva il DataFrame fuso in un nuovo file Excel
merged_file = './train_refined2.xlsx'
merged_df.to_excel(merged_file, index=False)

print("Fusione completata. Il file è stato salvato come:", merged_file)
