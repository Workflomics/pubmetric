# Workflomics Publication Metric

This code is currently under development.


## Overview

pubmetric is a library for benchmarking workflows based on the co-citation network connectivity of the publications describing the tools making up the workflow.


## Usage

First start Cytoscape, then open your notebook environment and run the code.


## Dependencies

Python packages listed in the `pyproject.toml` file. You can install them using the following command: 

```bash
    poetry install
```

If you're setting up the project for development and need the test dependencies, you can include them by running:

```bash
    poetry install --with dev
```

Cytoscape software, which can be downloaded from [https://cytoscape.org/](https://cytoscape.org/). Please make sure Cytoscape is open and running when executing the code.


## License

This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). 
