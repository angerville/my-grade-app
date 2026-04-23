import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import pdfplumber
import pandas as pd
import fitz  # PyMuPDF

class SchoolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("교행용 화표 자동 대조기")
        self.root.geometry("500x600")

        # 1. 기안문/엑셀 업로드 칸
        self.label1 = tk.Label(root, text="1. 기안문(PDF) 또는 엑셀을 드래그하세요", pady=20, bg="lightgray")
        self.label1.pack(fill="x", padx=10, pady=10)
        self.label1.drop_target_register(DND_FILES)
        self.label1.dnd_bind('<<Drop>>', self.drop_draft)

        # 3. 화표 PDF 일괄 업로드 칸
        self.label2 = tk.Label(root, text="3. 화표(영수증) PDF들을 드래그하세요", pady=20, bg="lightblue")
        self.label2.pack(fill="x", padx=10, pady=10)
        self.label2.drop_target_register(DND_FILES)
        self.label2.dnd_bind('<<Drop>>', self.drop_receipts)
        
        self.btn_run = tk.Button(root, text="실행 및 PDF 병합", command=self.process_files)
        self.btn_run.pack(pady=20)

    def drop_draft(self, event):
        # 파일 경로를 받아 처리하는 로직 (PDF/Excel 구분)
        print(f"기안문 로드: {event.data}")

    def drop_receipts(self, event):
        # 여러 화표 파일 경로를 리스트로 저장
        print(f"화표 로드: {event.data}")

    def process_files(self):
        # 2번: 텍스트 추출 및 표 만들기
        # 4번: 중국어 OCR 비교 대조
        # 5번: PDF 병합 (컬러/흑백) 및 표 삽입
        pass

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = SchoolApp(root)
    root.mainloop()