@echo off
chcp 65001 >nul
cd C:\Projects\TextVision
call .venv\Scripts\activate
cd PO_Vision
python OCR_shut_down.py