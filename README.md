# Elementary Graph Algorithms
This repository keeps the codes to generate videos in my "[Elementary Graph Algorithms](https://www.youtube.com/playlist?list=PLWkTpUb3t-2zqd2t4j47Wbw1GsxuQKmdX)" playlist.
My main goal is playing with the Manim animation engine. 
As a byproduct, I try to gain a deeper insight into basic graph algorithms by exploring their different variations.

## Installation
You need the Manim engine (community edition) to run the codes. 
Please refer to installation instructions at the [Manim GitHub repository](https://github.com/ManimCommunity/manim/). 
If you have Anaconda, you can create a new environment, open a terminal inside it and run the following command:
```
conda install -c conda-forge manim
```
You need to install LaTeX separately. 

## Usage
First, clone the repository with the following command:
```
git clone git@github.com:mahdidolati/elementary-graph-algorithms.git
```
Then, you can use the following template to run a specific example:
```
.\runner.bat .\path\to\python\file.py ClassName
```
Currently, following examples are available and have been tested with Manim Community v0.17.2:
```
.\runner.bat .\bfs\bfs_1.py Bfs
.\runner.bat .\bfs\bfs_2.py Bfs
.\runner.bat .\dfs\dfs_1.py Dfs
.\runner.bat .\dfs\dfs_2.py Dfs
.\runner.bat .\dfs\dfs_3.py Dfs
```

You should change the `runner.bat` file to select the video quality.
* `-ql`: Low quality
* `--high-quality`: High quality

## License & copyright
&copy; Mahdi Dolati

Licensed under the [MIT License](LICENSE).