@echo off
call "%USERPROFILE%\anaconda3\Scripts\activate.bat" carburants
cd /d C:\Users\Alexy\Documents\Projects\projet-carburants-fr
python src\download_data.py
python src\clean_data.py
python src\append_history.py