import pandas as pd

json_file_path = "/Users/janchristel/Documents/GitHub/SampleCodeRevitBatchProcessor/test/Data/Jupyter/VT_Overrides.json"
df = pd.read_json(json_file_path)

parquet_output_path = "/Users/janchristel/Documents/GitHub/SampleCodeRevitBatchProcessor/test/Data/Jupyter/VT_Overrides.parquet"
df.to_parquet(parquet_output_path, engine="fastparquet")


import pandas as pd

#parquet_file_path = "path_to_your_parquet_file.parquet"
df = pd.read_parquet(parquet_output_path)

# You can now work with the DataFrame 'df'
print(df.head())  # Display the first few rows of the DataFrame