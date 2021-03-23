# MAGDA

*MAGDA* is a Python library intended for assembling a stream-like architecture of an application following functional programming principles, by using predefined interfaces and classes. *MAGDA* stands for Modular and Asynchronous Graphs with Directed and Acyclic edges, and is the backbone of the library. The library works best when the code can be split into independent operations with clearly defined input and outputs. The main idea is to use *MAGDA* to process code in a sequential flow. Think of this as nodes with input/output as edges in directed graphs.

*MAGDA* supports following operations:
- building an application pipeline from a configuration file and from code,
- asynchronous and synchronous processing,
- dividing modules into groups for asynchronous pipeline,
- aggregation of partial results.

*MAGDA* can be applied almost anywhere, but is especially well-suited for BigData parallel processing and ML pipelines intended for carrying out multiple, repeatable experiments.

| Read the documentation on the [Github Wiki](https://github.com/NeuroSYS-pl/magda/wiki). |
| :---: |

## Installation

###### pip
```
pip install magda
```

###### From the repository
```bash
pip install https://github.com/NeuroSYS-pl/magda/archive/main.zip
```

## License
[Apache-2.0 License](LICENSE)
