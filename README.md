# piyolog_reader
A library for reading piyolog text files

## install 
```bash
pip3 install git+https://github.com/shu65/piyolog_reader.git
```

## how to read piyolog text
```
log_pathes = [
  "./piyolog/【ぴよログ】2022年12月.txt",
  "./piyolog/【ぴよログ】2022年11月.txt"
]
dfs = piyolog_reader.read_texts(log_pathes)
```
