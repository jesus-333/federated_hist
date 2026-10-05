# Brief introduction

This is a repository focused on Federated Learning applied to biological data, developed for the Clinnova Project.
The primary goal of this repository is to build a Python package that enables data scientists, researchers, and similar professionals to easily implement federated learning workflows.

The main structure of the repository is as follows:
```txt
├── data/                  # Contains some small datasets for testing and examples
├── examples/              # Contains example scripts demonstrating how to use the package
├── llm_wiki/              # Contains the wiki and documentation for the package
└── src/                   # Contains the source code of the package
```
You can ignore all other folders. They are artefacts of the development process and are not relevant to the main functionality of the package.

Inside the `src/` folder, there is a `README.md` file that provides a detailed description of the package, its purpose, and how to use it. 
It is still work in progress, but it is a good starting point for understanding the package's functionality and how to get started with it.

# Instructions

Analyze the repository and create a wiki page that provides a comprehensive overview of the package, its purpose, and how to use it. 
The wiki must be created inside the folder `llm_wiki`.
Its primary purpose is to provide you with a detailed description of the repository, so that you don't have to analyze it all from scratch every time you implement something new.


The wiki should have the following structure :
```txt
├── llm_wiki/              
    ├── 0_wiki_index.md                 
    ├── 0_wiki_quickstart.md
    ├── coding_style_instructions_ENG.md
    ├── examples/
    ├── instructions/
    └── modules/                   
```

A brief description of each file/folder is as follows:
- `0_wiki_index.md`: This file serves as the main index for the wiki, providing an overview of the package and links to other relevant sections.
- `0_wiki_quickstart.md`: This file provides a quick start guide for the package. It includes its purpose, main structure etc
- `coding_style_instructions_ENG.md`: This file contains coding style instructions for the package, ensuring consistency and readability in the codebase. You cannot change this file.
- `examples/`: This folder contains a brief description of the examples provided in the `examples/` folder of the repository.
- `instructions/`: This folder contains additional instructions regarding task that you may need to perform while working with the package. It is not meant to be modified or referenced in detail in the wiki. Just specify that it exists, its purpose and that can be ignored.
- `modules/`: This folder is the main focus of the wiki. It contains a detailed description of each module in the package, including its purpose, functionality, and usage examples. For each module there should be a quickstart guide that provide an overview of the module and serve as a starting point/index. Then for each python file in the module, there should be a separate markdown file that provides a detailed description of the file, its purpose, and how to use it.


Proceed in this way :
1. Analyze the repository and its structure. You could start from the `src/README.md` file and then proceed with the source code.
2. Create the `0_wiki_quickstart.md` file, providing a quick start guide for the package, including its purpose, main structure, and how to get started with it.
3. Create the `0_wiki_index.md` file, providing an overview of the package and links to other relevant sections.
4. Create the `modules/` folder and for each module in the package, with all the necessary files and descriptions as specified above.
5. Create the `examples/` folder and provide a brief description of the examples provided in the `examples/` folder of the repository.

A small note on the `src/README.md` file. 
I'm responsible for that file, and you CANNOT CHANGE or MODIFY it (expect for typos, grammatical errors, and formatting issues). 
It is not meant to be a detailed description of the package (for this, there is the wiki).
It's meant to explain the main "philosophy" behind the package, the reason behind some design choices and give a general overview/vibe (with some extra details about Flower/federated learning)

If something it is not clear reagarding the instructions, please just let me know.
