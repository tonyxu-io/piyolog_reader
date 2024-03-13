import piyolog_reader


log_pathes = ["./logs/aaron-piyolog-2023.txt", "./logs/aaron-piyolog-2024.txt"]
dfs = piyolog_reader.read_texts(log_pathes)
print(dfs)
