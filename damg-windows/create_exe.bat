del *.exe
pyinstaller -F src\dam_collect.py
pyinstaller -F src\dam_high_frequency.py
pyinstaller -F src\run_single.py
pyinstaller -F src\run_series.py
pyinstaller -F src\run_stable.py
nsis\makensis.exe damg.nsi
del *.spec
rmdir /s/q build
rmdir /s/q dist
rmdir /s/q src\__pycache__