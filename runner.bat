:: runner.bat 3b1b 1_BFS\main.py BFS
:: runner.bat 1_BFS\main.py BFS
:: -pql flags for low quality render
:: -p --high_quality flags for high quality render

@echo off

if %1==3b1b (
	echo "doing 3b1b"
	cd ..\manim-3b1b
	python -m manim ..\m_examples\%2 %3 -pql
	cd ..\m_examples
) else (
	echo "doing community version"
	manim %1 %2 -p --high_quality
)