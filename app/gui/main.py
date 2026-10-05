import os
import json
import sys
import webbrowser
import threading
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, simpledialog, ttk
from pathlib import Path

from PIL import Image, ImageOps, ImageTk

APP_VERSION = "V.3.0"
UNITS_TO_INCH = {"px": None, "mm": 1 / 25.4, "cm": 1 / 2.54, "m": 100 / 2.54, "inch": 1, "feet": 12}
DPI_PRESETS = ["72", "96", "100", "150", "200", "300", "Custom"]
UPSCALE_STEPS = {"2x": 2, "4x": 4, "8x": 8}
EN = {
    "เตรียมภาพความละเอียดสูงสำหรับงานป้าย": "Prepare high-resolution images for signage",
    "แปะไว้เผื่ออยากเลี้ยงกาแฟ": "Buy me a coffee if you like",
    "เลือกไฟล์ต้นฉบับ…": "Choose source file…", "เปรียบเทียบภาพ": "Compare images",
    "พอดีหน้าต่าง": "Fit", "ลากภาพเพื่อเลื่อน • เลื่อนล้อเมาส์เพื่อซูมทั้งสองภาพ": "Drag to pan • Scroll to zoom both images",
    "ภาพต้นฉบับ": "Original image", "ผลลัพธ์ AI": "AI result", "ยังไม่ได้เลือกภาพ": "No image selected",
    "จะแสดงตัวอย่างเมื่อประมวลผลเสร็จ": "Preview will appear after processing", "ขนาดงานพิมพ์": "Print size",
    "ล็อกอัตราส่วนภาพ": "Lock aspect ratio", "ขนาดส่งออก:": "Output size:", "AI Upscale": "AI Upscale",
    "Device": "Device", "อุปกรณ์ที่เลือก:": "Selected device:", "เริ่มปรับภาพ": "ENHANCE IMAGE",
    "กรอก Width และ Height เป็นค่าบวก": "Enter positive Width and Height values",
    "เลือกภาพแล้ว — ปรับขนาดงานพิมพ์และตั้งค่าได้": "Image selected — set print size and options",
    "กำลังประมวลผลด้วย Real-ESRGAN…": "Processing with Real-ESRGAN…",
    "เสร็จเรียบร้อย — บันทึกไฟล์ PNG แล้ว": "Done — PNG file saved", "เกิดข้อผิดพลาด": "An error occurred",
    "พร้อมใช้งาน — เลือกภาพเพื่อเริ่ม": "Ready — choose an image to begin",
    "ภาษา": "Language", "ตรวจไม่พบ GPU ที่รองรับ": "No compatible GPU detected",
    "ไม่พบ DirectML GPU หรือยังไม่ได้ติดตั้งส่วนเสริมทดลอง": "No DirectML GPU found or the experimental add-on is not installed",
    "กำหนดขนาดงานพิมพ์": "Set print dimensions", "ขยายด้วย AI Upscale": "Upscale with AI",
    "กำลังสร้างตัวอย่าง AI…": "Generating AI preview…", "กำลังเติมขอบภาพด้วย AI…": "AI is expanding the image canvas…",
    "วิธีปรับภาพ": "Resize method", "ยืดภาพ": "Stretch", "รักษาสัดส่วน": "Preserve proportions", "เติมขอบด้วย AI": "AI expand edges",
    "การปรับขนาดภาพ": "Image resizing", "ฟื้นฟูหน้าตาคน": "Face Recovery",
    "เปิดใช้งาน": "Enable", "โหมดนี้จะกำหนดขนาดพิกเซลปลายทางตามขนาดพิมพ์และ DPI": "Output pixels follow print dimensions and DPI",
    "โหมดนี้จะเพิ่มพิกเซลตามตัวคูณ AI Upscale": "Output pixels follow the AI Upscale factor",
    "ขนาดส่งออกตามโหมดที่เลือก": "Output size for selected mode",
    "AI Upscale จะกำหนดจำนวนพิกเซลที่เพิ่มขึ้น": "AI Upscale sets how many pixels are added",
    "เลือกภาพเพื่อดูขนาดส่งออก": "Choose an image to see output dimensions",
    "ขนาดพิกเซลจะคำนวณจาก Width, Height และ DPI": "Pixel dimensions are calculated from width, height, and DPI",
    "กรุณาเลือกภาพก่อนครับ": "Please choose an image first.", "ขนาดใหญ่เกินไป": "Image is too large",
    "ขนาดด้านใดด้านหนึ่งเกิน 30,000 px กรุณาลดขนาดหรือ DPI": "A side exceeds 30,000 px. Reduce the size or DPI.",
    "ขนาดไม่ถูกต้อง": "Invalid dimensions", "กรุณากรอก Width และ Height ให้ถูกต้อง": "Enter valid Width and Height values.",
    "เปิดภาพไม่สำเร็จ": "Could not open image", "ประมวลผลสำเร็จ": "Processing complete",
    "ไฟล์:": "File:", "ARM AI ERROR": "ARM AI ERROR", "ระบุ DPI ที่ต้องการ:": "Enter the desired DPI:",
    "รายการไฟล์ต้นฉบับ": "Source files", "เลือกทั้งหมด": "Select all", "ยกเลิกทั้งหมด": "Deselect all",
    "ต้นฉบับ": "Original", "ผลลัพธ์ตามค่าปัจจุบัน": "Output at current settings", "ลบออกจากรายการ": "Remove from list",
    "ต้องเลือกอย่างน้อยหนึ่งไฟล์": "Select at least one file", "กำลังประมวลผลไฟล์": "Processing file",
    "ไฟล์ที่เลือกเสร็จแล้ว": "Selected files complete", "ยืนยันลบ": "Remove image", "ต้องการลบไฟล์นี้ออกจากรายการหรือไม่?": "Remove this image from the list?",
    "ภาพย่อ": "Preview", "ชื่อไฟล์": "File name", "ขนาดต้นฉบับ": "Original size", "ขนาดหลัง Enhance": "Output size",
    "Face Recovery": "Face Recovery", "เลือกใบหน้า…": "Choose faces…", "กำลังตรวจหาใบหน้า…": "Detecting faces…",
    "ไม่พบใบหน้าในภาพนี้": "No faces were detected in this image", "เลือกใบหน้าที่ต้องการกู้คืน": "Select faces to restore",
    "เลือกทั้งหมด": "Select all", "ยกเลิกทั้งหมด": "Deselect all", "นำไปใช้": "Apply", "ยกเลิก": "Cancel",
    "ใบหน้า": "Faces", "ยังไม่ได้วิเคราะห์": "not analyzed", "ตรวจพบ": "detected", "เลือกไว้": "selected",
    "ต้องวิเคราะห์แต่ละภาพก่อน": "Analyze faces for each checked image first",
    "หยุด": "Stop", "หยุดทั้งหมด": "Stop all", "หยุดแล้ว": "Stopped",
    "กำลังหยุด…": "Stopping…", "ยกเลิกแล้ว": "Cancelled",
}

ZH = {
    "เตรียมภาพความละเอียดสูงสำหรับงานป้าย": "为广告牌制作高分辨率图像",
    "แปะไว้เผื่ออยากเลี้ยงกาแฟ": "如果您喜欢这个程序，欢迎请我喝杯咖啡",
    "เลือกไฟล์ต้นฉบับ…": "选择源图像…", "เปรียบเทียบภาพ": "图像对比", "พอดีหน้าต่าง": "适合窗口",
    "ลากภาพเพื่อเลื่อน • เลื่อนล้อเมาส์เพื่อซูมทั้งสองภาพ": "拖动图像以平移 • 滚动鼠标滚轮以同步缩放",
    "ภาพต้นฉบับ": "原始图像", "ผลลัพธ์ AI": "AI 结果", "ยังไม่ได้เลือกภาพ": "尚未选择图像",
    "จะแสดงตัวอย่างเมื่อประมวลผลเสร็จ": "处理完成后显示预览", "ขนาดงานพิมพ์": "打印尺寸",
    "ล็อกอัตราส่วนภาพ": "锁定宽高比", "ขนาดส่งออก:": "输出尺寸：", "AI Upscale": "AI 放大",
    "Device": "设备", "อุปกรณ์ที่เลือก:": "已选设备：", "เริ่มปรับภาพ": "开始增强",
    "กรอก Width และ Height เป็นค่าบวก": "请输入大于零的宽度和高度",
    "เลือกภาพแล้ว — ปรับขนาดงานพิมพ์และตั้งค่าได้": "已选择图像 — 可设置打印尺寸和选项",
    "กำลังประมวลผลด้วย Real-ESRGAN…": "正在使用 Real-ESRGAN 处理…", "เสร็จเรียบร้อย — บันทึกไฟล์ PNG แล้ว": "完成 — PNG 文件已保存",
    "เกิดข้อผิดพลาด": "发生错误", "พร้อมใช้งาน — เลือกภาพเพื่อเริ่ม": "准备就绪 — 请选择图像开始",
    "ภาษา": "语言", "ตรวจไม่พบ GPU ที่รองรับ": "未检测到兼容的 GPU",
    "ไม่พบ DirectML GPU หรือยังไม่ได้ติดตั้งส่วนเสริมทดลอง": "未找到 DirectML GPU，或尚未安装实验性组件",
    "กำหนดขนาดงานพิมพ์": "设置打印尺寸", "ขยายด้วย AI Upscale": "使用 AI 放大",
    "กำลังสร้างตัวอย่าง AI…": "正在生成 AI 预览…", "กำลังเติมขอบภาพด้วย AI…": "正在使用 AI 扩展图像边缘…",
    "วิธีปรับภาพ": "缩放方式", "ยืดภาพ": "拉伸图像", "รักษาสัดส่วน": "保持比例", "เติมขอบด้วย AI": "使用 AI 扩展边缘",
    "การปรับขนาดภาพ": "图像缩放", "ฟื้นฟูหน้าตาคน": "人脸修复", "เปิดใช้งาน": "启用",
    "ขนาดส่งออกตามโหมดที่เลือก": "当前模式的输出尺寸", "AI Upscale จะกำหนดจำนวนพิกเซลที่เพิ่มขึ้น": "AI 放大倍率决定输出像素数量",
    "เลือกภาพเพื่อดูขนาดส่งออก": "请选择图像以查看输出尺寸", "ขนาดพิกเซลจะคำนวณจาก Width, Height และ DPI": "像素尺寸根据宽度、高度和 DPI 计算",
    "กรุณาเลือกภาพก่อนครับ": "请先选择图像。", "ขนาดใหญ่เกินไป": "图像尺寸过大",
    "ขนาดด้านใดด้านหนึ่งเกิน 30,000 px กรุณาลดขนาดหรือ DPI": "任一边超过 30,000 像素，请减小尺寸或 DPI。",
    "ขนาดไม่ถูกต้อง": "尺寸无效", "กรุณากรอก Width และ Height ให้ถูกต้อง": "请输入有效的宽度和高度。",
    "เปิดภาพไม่สำเร็จ": "无法打开图像", "ประมวลผลสำเร็จ": "处理完成", "ไฟล์:": "文件：",
    "ระบุ DPI ที่ต้องการ:": "请输入所需 DPI：", "รายการไฟล์ต้นฉบับ": "源文件列表", "เลือกทั้งหมด": "全选",
    "ยกเลิกทั้งหมด": "全部取消", "ต้นฉบับ": "原始图像", "ผลลัพธ์ตามค่าปัจจุบัน": "按当前设置输出",
    "ลบออกจากรายการ": "从列表中移除", "ต้องเลือกอย่างน้อยหนึ่งไฟล์": "请至少选择一个文件", "กำลังประมวลผลไฟล์": "正在处理文件",
    "ไฟล์ที่เลือกเสร็จแล้ว": "已完成文件", "ยืนยันลบ": "确认移除图像", "ต้องการลบไฟล์นี้ออกจากรายการหรือไม่?": "确定从列表中移除此图像吗？",
    "ภาพย่อ": "缩略图", "ชื่อไฟล์": "文件名", "ขนาดต้นฉบับ": "原始尺寸", "ขนาดหลัง Enhance": "增强后尺寸",
    "Face Recovery": "人脸修复", "เลือกใบหน้า…": "选择人脸…", "กำลังตรวจหาใบหน้า…": "正在检测人脸…",
    "ไม่พบใบหน้าในภาพนี้": "未在此图像中检测到人脸", "เลือกใบหน้าที่ต้องการกู้คืน": "选择要修复的人脸",
    "นำไปใช้": "应用", "ยกเลิก": "取消", "ใบหน้า": "人脸", "ยังไม่ได้วิเคราะห์": "尚未分析",
    "ตรวจพบ": "已检测", "เลือกไว้": "已选", "ต้องวิเคราะห์แต่ละภาพก่อน": "请先分析每张图像中的人脸",
    "หยุด": "停止", "หยุดทั้งหมด": "全部停止", "หยุดแล้ว": "已停止", "กำลังหยุด…": "正在停止…", "ยกเลิกแล้ว": "已取消",
    "Width": "宽度", "Height": "高度", "หน่วย": "单位", "Custom DPI": "自定义 DPI", "PROMPTPAY": "PromptPay",
    "ภาษา / Language": "语言", "LINE": "LINE", "itsarap": "itsarap", "รายการไฟล์ต้นฉบับ": "源文件列表",
    "เลือกภาพต้นฉบับ (เลือกได้หลายไฟล์)": "选择源图像（可多选）", "Image Files": "图像文件", "All Files": "所有文件",
    "🚀  เริ่มปรับภาพ": "🚀  开始增强", "Custom DPI": "自定义 DPI", "Custom": "自定义",
    "PromptPay — QR": "PromptPay — 二维码", "ARM AI ERROR": "ARM AI 错误",
}

FR = {
    "เตรียมภาพความละเอียดสูงสำหรับงานป้าย": "Préparez des images haute résolution pour l’impression grand format",
    "แปะไว้เผื่ออยากเลี้ยงกาแฟ": "Offrez-moi un café si le programme vous plaît",
    "เลือกไฟล์ต้นฉบับ…": "Choisir les images source…", "เปรียบเทียบภาพ": "Comparer les images", "พอดีหน้าต่าง": "Ajuster",
    "ลากภาพเพื่อเลื่อน • เลื่อนล้อเมาส์เพื่อซูมทั้งสองภาพ": "Faites glisser pour déplacer • Molette pour zoomer les deux images",
    "ภาพต้นฉบับ": "Image originale", "ผลลัพธ์ AI": "Résultat IA", "ยังไม่ได้เลือกภาพ": "Aucune image sélectionnée",
    "จะแสดงตัวอย่างเมื่อประมวลผลเสร็จ": "L’aperçu apparaîtra après le traitement", "ขนาดงานพิมพ์": "Format d’impression",
    "ล็อกอัตราส่วนภาพ": "Verrouiller les proportions", "ขนาดส่งออก:": "Taille de sortie :", "AI Upscale": "Agrandissement IA",
    "Device": "Appareil", "อุปกรณ์ที่เลือก:": "Appareil sélectionné :", "เริ่มปรับภาพ": "AMÉLIORER L’IMAGE",
    "กรอก Width และ Height เป็นค่าบวก": "Saisissez une largeur et une hauteur positives",
    "เลือกภาพแล้ว — ปรับขนาดงานพิมพ์และตั้งค่าได้": "Image sélectionnée — définissez le format d’impression et les options",
    "กำลังประมวลผลด้วย Real-ESRGAN…": "Traitement avec Real-ESRGAN…", "เสร็จเรียบร้อย — บันทึกไฟล์ PNG แล้ว": "Terminé — fichier PNG enregistré",
    "เกิดข้อผิดพลาด": "Une erreur est survenue", "พร้อมใช้งาน — เลือกภาพเพื่อเริ่ม": "Prêt — choisissez une image pour commencer",
    "ภาษา": "Langue", "ตรวจไม่พบ GPU ที่รองรับ": "Aucun GPU compatible détecté",
    "ไม่พบ DirectML GPU หรือยังไม่ได้ติดตั้งส่วนเสริมทดลอง": "Aucun GPU DirectML détecté ou module expérimental absent",
    "กำหนดขนาดงานพิมพ์": "Définir le format d’impression", "ขยายด้วย AI Upscale": "Agrandir avec l’IA",
    "กำลังสร้างตัวอย่าง AI…": "Génération de l’aperçu IA…", "กำลังเติมขอบภาพด้วย AI…": "Extension des bords avec l’IA…",
    "วิธีปรับภาพ": "Méthode de redimensionnement", "ยืดภาพ": "Étirer", "รักษาสัดส่วน": "Conserver les proportions", "เติมขอบด้วย AI": "Étendre avec l’IA",
    "การปรับขนาดภาพ": "Redimensionnement de l’image", "ฟื้นฟูหน้าตาคน": "Restauration des visages", "เปิดใช้งาน": "Activer",
    "ขนาดส่งออกตามโหมดที่เลือก": "Taille de sortie selon le mode", "AI Upscale จะกำหนดจำนวนพิกเซลที่เพิ่มขึ้น": "Le facteur IA définit le nombre de pixels ajoutés",
    "เลือกภาพเพื่อดูขนาดส่งออก": "Choisissez une image pour voir la taille de sortie", "ขนาดพิกเซลจะคำนวณจาก Width, Height และ DPI": "Les dimensions en pixels sont calculées à partir de la largeur, hauteur et du DPI",
    "กรุณาเลือกภาพก่อนครับ": "Veuillez d’abord choisir une image.", "ขนาดใหญ่เกินไป": "Image trop grande",
    "ขนาดด้านใดด้านหนึ่งเกิน 30,000 px กรุณาลดขนาดหรือ DPI": "Un côté dépasse 30 000 px. Réduisez la taille ou le DPI.",
    "ขนาดไม่ถูกต้อง": "Dimensions incorrectes", "กรุณากรอก Width และ Height ให้ถูกต้อง": "Saisissez une largeur et une hauteur valides.",
    "เปิดภาพไม่สำเร็จ": "Impossible d’ouvrir l’image", "ประมวลผลสำเร็จ": "Traitement terminé", "ไฟล์:": "Fichier :",
    "ระบุ DPI ที่ต้องการ:": "Saisissez le DPI souhaité :", "รายการไฟล์ต้นฉบับ": "Liste des fichiers source", "เลือกทั้งหมด": "Tout sélectionner",
    "ยกเลิกทั้งหมด": "Tout désélectionner", "ต้นฉบับ": "Original", "ผลลัพธ์ตามค่าปัจจุบัน": "Résultat selon les paramètres actuels",
    "ลบออกจากรายการ": "Retirer de la liste", "ต้องเลือกอย่างน้อยหนึ่งไฟล์": "Sélectionnez au moins un fichier", "กำลังประมวลผลไฟล์": "Traitement du fichier",
    "ไฟล์ที่เลือกเสร็จแล้ว": "Fichiers terminés", "ยืนยันลบ": "Retirer l’image", "ต้องการลบไฟล์นี้ออกจากรายการหรือไม่?": "Voulez-vous retirer cette image de la liste ?",
    "ภาพย่อ": "Miniature", "ชื่อไฟล์": "Nom du fichier", "ขนาดต้นฉบับ": "Dimensions d’origine", "ขนาดหลัง Enhance": "Dimensions après amélioration",
    "Face Recovery": "Restauration des visages", "เลือกใบหน้า…": "Choisir les visages…", "กำลังตรวจหาใบหน้า…": "Détection des visages…",
    "ไม่พบใบหน้าในภาพนี้": "Aucun visage détecté dans cette image", "เลือกใบหน้าที่ต้องการกู้คืน": "Choisissez les visages à restaurer",
    "นำไปใช้": "Appliquer", "ยกเลิก": "Annuler", "ใบหน้า": "Visages", "ยังไม่ได้วิเคราะห์": "non analysé",
    "ตรวจพบ": "détecté(s)", "เลือกไว้": "sélectionné(s)", "ต้องวิเคราะห์แต่ละภาพก่อน": "Analysez d’abord les visages de chaque image sélectionnée",
    "หยุด": "Arrêter", "หยุดทั้งหมด": "Tout arrêter", "หยุดแล้ว": "Arrêté", "กำลังหยุด…": "Arrêt en cours…", "ยกเลิกแล้ว": "Annulé",
    "Width": "Largeur", "Height": "Hauteur", "หน่วย": "Unité", "Custom DPI": "DPI personnalisé", "PROMPTPAY": "PromptPay",
    "ภาษา / Language": "Langue", "LINE": "LINE", "itsarap": "itsarap",
    "รายการไฟล์ต้นฉบับ": "Liste des fichiers source",
    "เลือกภาพต้นฉบับ (เลือกได้หลายไฟล์)": "Choisir les images source (sélection multiple)", "Image Files": "Fichiers image", "All Files": "Tous les fichiers",
    "🚀  เริ่มปรับภาพ": "🚀  AMÉLIORER L’IMAGE", "Custom DPI": "DPI personnalisé", "Custom": "Personnalisé",
    "PromptPay — QR": "PromptPay — QR", "ARM AI ERROR": "ERREUR ARM AI",
}

TRANSLATIONS = {"en": EN, "zh": ZH, "fr": FR}
LANGUAGE_CHOICES = {
    "th": "ไทย", "en": "English", "zh": "简体中文", "fr": "Français",
}

EN.update({
    "Recent": "Recent", "Clear History": "Clear History", "User Guide": "User Guide",
    "เริ่มใช้งาน": "Get started", "ลากภาพมาวางที่นี่": "Drop images here",
    "ลาก และ วางภาพที่นี่": "Drag and drop images here", "Browse Images": "Browse Images",
    "ภาพย่อ": "Thumbnails", "รายการ": "List", "Click ▶ ": "Click ▶ ",
    "คัดลอกชื่อแล้ว": "Name copied", "กำลังโหลดส่วนประกอบโปรแกรม…": "Loading application components…",
    "กำลังโหลดโมดูล AI…": "Loading AI modules…", "กำลังตรวจสอบอุปกรณ์…": "Checking available devices…",
    "กำลังเตรียมหน้าต่างโปรแกรม…": "Preparing the application window…", "กำลังเปิดโปรแกรม…": "Starting application…",
    "ปิด": "Close", "คู่มือผู้ใช้": "User Guide", "คู่มือ": "Guide",
    "🚀  เริ่มปรับภาพ": "🚀  Start Enhance",
    "1. ลากภาพมาวางหรือกด Browse Images เพื่อเพิ่มภาพ": "1. Drop images here or choose Browse Images to add pictures.",
    "2. เลือกภาพในรายการเพื่อกำหนดค่าของภาพนั้น": "2. Select an image in the list to edit its settings.",
    "3. เลือกกำหนดขนาดงานพิมพ์หรือขยายด้วย AI Upscale": "3. Choose print dimensions or AI Upscale.",
    "4. เลือกฟื้นฟูหน้าตาคนได้ตามต้องการ": "4. Face Recovery is optional.",
    "5. ดูตัวอย่างแล้วกดเริ่มปรับภาพ": "5. Review the preview and click Enhance Image.",
    "ไฟล์ PNG จะบันทึกไว้ข้างไฟล์ต้นฉบับ": "Enhanced PNG files are saved next to the source images.",
})
ZH.update({
    "Recent": "最近使用", "Clear History": "清除记录", "User Guide": "用户指南",
    "เริ่มใช้งาน": "开始使用", "ลากภาพมาวางที่นี่": "将图像拖放到此处",
    "ลาก และ วางภาพที่นี่": "将图像拖放到此处", "Browse Images": "浏览图像",
    "ภาพย่อ": "缩略图", "รายการ": "列表", "Click ▶ ": "点击 ▶ ",
    "คัดลอกชื่อแล้ว": "名称已复制", "กำลังโหลดส่วนประกอบโปรแกรม…": "正在加载应用组件…",
    "กำลังโหลดโมดูล AI…": "正在加载 AI 模块…", "กำลังตรวจสอบอุปกรณ์…": "正在检查可用设备…",
    "กำลังเตรียมหน้าต่างโปรแกรม…": "正在准备应用窗口…", "กำลังเปิดโปรแกรม…": "正在启动应用…",
    "ปิด": "关闭", "คู่มือผู้ใช้": "用户指南", "คู่มือ": "指南",
    "1. ลากภาพมาวางหรือกด Browse Images เพื่อเพิ่มภาพ": "1. 拖放图像或点击“浏览图像”添加图片。",
    "2. เลือกภาพในรายการเพื่อกำหนดค่าของภาพนั้น": "2. 在列表中选择图像并设置该图像的参数。",
    "3. เลือกกำหนดขนาดงานพิมพ์หรือขยายด้วย AI Upscale": "3. 选择打印尺寸或使用 AI 放大。",
    "4. เลือกฟื้นฟูหน้าตาคนได้ตามต้องการ": "4. 可按需启用人脸修复。",
    "5. ดูตัวอย่างแล้วกดเริ่มปรับภาพ": "5. 查看预览后点击“增强图像”。",
    "ไฟล์ PNG จะบันทึกไว้ข้างไฟล์ต้นฉบับ": "增强后的 PNG 文件将保存在源图像旁边。",
})
FR.update({
    "Recent": "Récents", "Clear History": "Effacer l’historique", "User Guide": "Guide utilisateur",
    "เริ่มใช้งาน": "Commencer", "ลากภาพมาวางที่นี่": "Déposez les images ici",
    "ลาก และ วางภาพที่นี่": "Glissez-déposez les images ici", "Browse Images": "Parcourir les images",
    "ภาพย่อ": "Miniatures", "รายการ": "Liste", "Click ▶ ": "Cliquer ▶ ",
    "คัดลอกชื่อแล้ว": "Nom copié", "กำลังโหลดส่วนประกอบโปรแกรม…": "Chargement des composants…",
    "กำลังโหลดโมดูล AI…": "Chargement des modules IA…", "กำลังตรวจสอบอุปกรณ์…": "Vérification des périphériques…",
    "กำลังเตรียมหน้าต่างโปรแกรม…": "Préparation de la fenêtre…", "กำลังเปิดโปรแกรม…": "Démarrage de l’application…",
    "ปิด": "Fermer", "คู่มือผู้ใช้": "Guide utilisateur", "คู่มือ": "Guide",
    "1. ลากภาพมาวางหรือกด Browse Images เพื่อเพิ่มภาพ": "1. Déposez des images ou cliquez sur « Parcourir les images ». ",
    "2. เลือกภาพในรายการเพื่อกำหนดค่าของภาพนั้น": "2. Sélectionnez une image dans la liste pour régler ses paramètres.",
    "3. เลือกกำหนดขนาดงานพิมพ์หรือขยายด้วย AI Upscale": "3. Choisissez les dimensions d’impression ou l’agrandissement IA.",
    "4. เลือกฟื้นฟูหน้าตาคนได้ตามต้องการ": "4. La restauration des visages est facultative.",
    "5. ดูตัวอย่างแล้วกดเริ่มปรับภาพ": "5. Vérifiez l’aperçu puis cliquez sur Améliorer l’image.",
    "ไฟล์ PNG จะบันทึกไว้ข้างไฟล์ต้นฉบับ": "Les PNG améliorés sont enregistrés à côté des images source.",
})


def application_resource_root():
    """Return the root containing bundled assets/models or the source project."""
    if getattr(sys, "frozen", False):
        bundle_root = getattr(sys, "_MEIPASS", None)
        if bundle_root:
            return Path(bundle_root)
    return Path(__file__).resolve().parents[2]


class ArmAIApp:
    def __init__(self, root, engine_manager=None):
        self.root = root
        self.user_data_dir = Path(os.environ.get("APPDATA", str(Path.home()))) / "ArmAI" / "ImageEnhancer"
        self.settings_path = self.user_data_dir / "settings.json"
        self.legacy_settings_path = Path(__file__).resolve().parents[2] / "settings.json"
        self.settings = self._load_settings()
        saved_recent = self.settings.get("recent_files", [])
        if not isinstance(saved_recent, list):
            saved_recent = []
        self._recent_files = [p for p in saved_recent if isinstance(p, str) and os.path.isfile(p)][:20]
        self.language = self.settings.get("language", "th") if self.settings.get("language") in LANGUAGE_CHOICES else "th"
        self._restored_dimensions = bool(self.settings.get("width") and self.settings.get("height"))
        self._settings_after = None
        self._window_save_after = None
        self._static_texts = {}
        self.status_code = "ready"
        root.title(f"ARM AI Image Enhancer — {APP_VERSION}")
        screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
        default_width, default_height = round(screen_width * 0.8), round(screen_height * 0.8)
        saved_width = self.settings.get("window_width")
        saved_height = self.settings.get("window_height")
        try:
            window_width = int(saved_width) if saved_width else default_width
            window_height = int(saved_height) if saved_height else default_height
        except (TypeError, ValueError):
            window_width, window_height = default_width, default_height
        window_width = max(min(900, screen_width), min(window_width, screen_width))
        window_height = max(min(650, screen_height), min(window_height, screen_height))
        saved_x, saved_y = self.settings.get("window_x"), self.settings.get("window_y")
        try:
            window_x, window_y = int(saved_x), int(saved_y)
            if window_x < 0 or window_y < 0 or window_x + window_width > screen_width or window_y + window_height > screen_height:
                raise ValueError
        except (TypeError, ValueError):
            window_x = max(0, (screen_width - window_width) // 2)
            window_y = max(0, (screen_height - window_height) // 2)
        root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
        root.minsize(min(900, screen_width), min(650, screen_height))
        root.tk.call("tk", "scaling", 1.2)
        for font_name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont", "TkCaptionFont"):
            try:
                tkfont.nametofont(font_name).configure(family="Tahoma", size=11)
            except tk.TclError:
                pass
        self.input_file = None
        self.batch_items = []
        self.batch_by_path = {}
        self._cancel_all_event = threading.Event()
        self._active_items = set()
        self._is_processing = False
        self.selected_item = None
        self.engine_manager = engine_manager
        if self.engine_manager is None:
            from app.engine.engine_manager import EngineManager
            self.engine_manager = EngineManager()
        self.device_choices = ["AUTO", "CPU", "GPU"]
        self.directml_available = any(
            device.backend == "DIRECTML" and device.available
            for device in self.engine_manager.device_manager.get_devices()
        )
        if self.directml_available:
            self.device_choices.append("DIRECTML")
        self._updating = False
        self._loading_job_settings = False
        self._preview_after = None
        self._preview_generation = 0
        self.auto_preview_var = tk.BooleanVar(value=bool(self.settings.get("auto_preview", True)))
        self._preview_refs = {}
        self.scale_var = tk.StringVar(value=self.settings.get("scale", "4x") if self.settings.get("scale") in UPSCALE_STEPS else "4x")
        self.output_mode_var = tk.StringVar(value=self.settings.get("output_mode", "print") if self.settings.get("output_mode") in ("print", "upscale") else "print")
        saved_dpi = str(self.settings.get("dpi", "300"))
        if saved_dpi == "Custom":
            saved_dpi = self.t("Custom")
        self.dpi_var = tk.StringVar(value=saved_dpi)
        self.unit_var = tk.StringVar(value=self.settings.get("unit", "cm") if self.settings.get("unit") in UNITS_TO_INCH else "cm")
        self.width_var = tk.StringVar(value=str(self.settings.get("width", "")))
        self.height_var = tk.StringVar(value=str(self.settings.get("height", "")))
        self.resize_mode_var = tk.StringVar(value=self.settings.get("resize_mode", "preserve" if self.settings.get("lock_ratio", True) else "stretch"))
        if self.resize_mode_var.get() not in ("stretch", "preserve", "ai_expand"):
            self.resize_mode_var.set("preserve")
        self.resize_mode_label_var = tk.StringVar()
        saved_device = self.settings.get("device", "AUTO")
        if saved_device not in self.device_choices:
            saved_device = "AUTO"
        self.device_var = tk.StringVar(value=saved_device)
        self.face_recovery_var = tk.BooleanVar(value=bool(self.settings.get("face_recovery", False)))
        self.status_var = tk.StringVar(value=self.t("พร้อมใช้งาน — เลือกภาพเพื่อเริ่ม"))
        self._face_backend = None
        self._face_backend_device = None
        self._face_backend_lock = threading.Lock()
        self._face_analysis_queue = []
        self._auto_start_after_face_analysis = False
        self._face_detection_busy = False

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Blue.Horizontal.TProgressbar", troughcolor="#DCE7F3", background="#2596F3", bordercolor="#B6C9DC", lightcolor="#2596F3", darkcolor="#2596F3")
        style.configure("Title.TLabel", font=("Tahoma", 20, "bold"))
        style.configure("TLabel", font=("Tahoma", 12))
        style.configure("TButton", font=("Tahoma", 11))
        style.configure("TCheckbutton", font=("Tahoma", 11))
        style.configure("TEntry", font=("Tahoma", 12), padding=4)
        style.configure("TCombobox", font=("Tahoma", 12), padding=4)
        style.configure("Section.TLabelframe.Label", font=("Tahoma", 12, "bold"))
        self._build_language_selector(root)
        self._build_header(root)

        # Main workspace: controls stay in a fixed left rail; previews and queue
        # share the larger right-hand area so action buttons cannot be clipped.
        workspace = ttk.Frame(root)
        workspace.pack(fill="both", expand=True, padx=12, pady=(2, 5))
        workspace.columnconfigure(0, weight=0, minsize=330)
        workspace.columnconfigure(1, weight=1)
        workspace.rowconfigure(0, weight=1)
        sidebar = ttk.Frame(workspace, width=330)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        sidebar.grid_propagate(False)
        right = ttk.Frame(workspace)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=3)
        right.rowconfigure(1, weight=2)

        self.select_button = ttk.Button(sidebar, text="เลือกไฟล์ต้นฉบับ…", command=self.select_image)
        self.select_button.pack(fill="x", pady=(0, 6))

        preview_area = ttk.Frame(right)
        preview_area.grid(row=0, column=0, sticky="nsew")
        preview_area.columnconfigure(0, weight=1)
        preview_area.rowconfigure(1, weight=1)
        zoombar = ttk.Frame(preview_area)
        zoombar.grid(row=0, column=0, sticky="ew", pady=(0, 3))
        ttk.Label(zoombar, text="เปรียบเทียบภาพ").pack(side="left", padx=(4, 12))
        ttk.Button(zoombar, text="−", width=4, command=lambda: self._zoom_by(1 / 1.25)).pack(side="left", padx=2)
        ttk.Button(zoombar, text="+", width=4, command=lambda: self._zoom_by(1.25)).pack(side="left", padx=2)
        ttk.Button(zoombar, text="พอดีหน้าต่าง", command=self._fit_previews).pack(side="left", padx=5)
        ttk.Label(zoombar, text="ลากภาพเพื่อเลื่อน • เลื่อนล้อเมาส์เพื่อซูมทั้งสองภาพ").pack(side="left", padx=12)
        self.zoom_label = ttk.Label(zoombar, text="100%")
        self.zoom_label.pack(side="right", padx=8)
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self._preview_pils = {"before": None, "after": None}
        self._preview_photos = {}
        preview = ttk.Frame(preview_area)
        preview.grid(row=1, column=0, sticky="nsew")
        self.before_panel = self._preview_panel(preview, "ภาพต้นฉบับ", 0)
        self.after_panel = self._preview_panel(preview, "ผลลัพธ์ AI", 1)
        self.before_info = ttk.Label(self.before_panel, text="ยังไม่ได้เลือกภาพ", wraplength=420)
        self.before_info.pack(pady=(0, 8))
        self.after_info = ttk.Label(self.after_panel, text="จะแสดงตัวอย่างเมื่อประมวลผลเสร็จ", wraplength=420)
        self.after_info.pack(pady=(0, 8))
        preview_actions = ttk.Frame(preview_area)
        preview_actions.grid(row=2, column=0, sticky="e", pady=(2, 0))
        ttk.Checkbutton(preview_actions, text="Auto Preview", variable=self.auto_preview_var,
                        command=self._preview_mode_changed).pack(side="left", padx=6)
        self.update_preview_button = ttk.Button(preview_actions, text="Update Preview", command=self._request_ai_preview)
        self.update_preview_button.pack(side="left", padx=5)

        controls = ttk.LabelFrame(sidebar, text="ขนาดงานพิมพ์", style="Section.TLabelframe", padding=8)
        controls.pack(fill="x", pady=4)
        self.print_mode_radio = ttk.Radiobutton(controls, text="กำหนดขนาดงานพิมพ์", variable=self.output_mode_var, value="print", command=self._update_output_mode)
        self.print_mode_radio.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 3))
        ttk.Label(controls, text="Width").grid(row=1, column=0, sticky="w", padx=(0, 4), pady=3)
        self.width_entry = ttk.Entry(controls, textvariable=self.width_var, width=9)
        self.width_entry.grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=3)
        ttk.Label(controls, text="Height").grid(row=1, column=2, sticky="w", padx=(0, 4), pady=3)
        self.height_entry = ttk.Entry(controls, textvariable=self.height_var, width=9)
        self.height_entry.grid(row=1, column=3, sticky="ew", pady=3)
        controls.columnconfigure(1, weight=1)
        controls.columnconfigure(3, weight=1)
        ttk.Label(controls, text="หน่วย").grid(row=2, column=0, sticky="w", padx=(0, 4), pady=3)
        unit = ttk.Combobox(controls, textvariable=self.unit_var, values=["px", "mm", "cm", "m", "inch", "feet"], state="readonly", width=8)
        unit.grid(row=2, column=1, sticky="ew", padx=(0, 8), pady=3)
        unit.bind("<<ComboboxSelected>>", self._unit_changed)
        self.resize_mode_label = ttk.Label(controls, text="วิธีปรับภาพ")
        self.resize_mode_label.grid(row=3, column=0, sticky="w", padx=(0, 4), pady=3)
        self._static_texts[self.resize_mode_label] = "วิธีปรับภาพ"
        self.resize_mode_box = ttk.Combobox(controls, textvariable=self.resize_mode_label_var, values=self._resize_mode_labels(), state="readonly")
        self.resize_mode_box.grid(row=3, column=1, columnspan=3, sticky="ew", pady=3)
        self.resize_mode_box.bind("<<ComboboxSelected>>", self._resize_mode_selected)
        self._sync_resize_mode_label()
        ttk.Label(controls, text="DPI").grid(row=4, column=0, sticky="w", padx=(0, 6), pady=(3, 0))
        self.dpi_box = ttk.Combobox(controls, textvariable=self.dpi_var, values=self._dpi_choices(), width=10)
        self.dpi_box.grid(row=4, column=1, sticky="w", pady=(3, 0))
        self.dpi_box.bind("<<ComboboxSelected>>", self._dpi_selected)
        self.dpi_box.bind("<FocusOut>", self._recalculate)
        ttk.Label(controls, text="ขนาดพิกเซลจะคำนวณจาก Width, Height และ DPI", wraplength=285).grid(row=5, column=0, columnspan=4, sticky="w", pady=(4, 0))
        self.print_controls = [(self.width_entry, "normal"), (self.height_entry, "normal"),
                               (unit, "readonly"), (self.resize_mode_box, "readonly")]
        self.width_var.trace_add("write", lambda *_: self._dimension_changed("width"))
        self.height_var.trace_add("write", lambda *_: self._dimension_changed("height"))

        options = ttk.LabelFrame(sidebar, text="การปรับขนาดภาพ", style="Section.TLabelframe", padding=8)
        options.pack(fill="x", pady=4)
        self.upscale_mode_radio = ttk.Radiobutton(options, text="ขยายด้วย AI Upscale", variable=self.output_mode_var, value="upscale", command=self._update_output_mode)
        self.upscale_mode_radio.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 3))
        ttk.Label(options, text="AI Upscale").grid(row=1, column=0, sticky="w", pady=3)
        self.scale_box = ttk.Combobox(options, textvariable=self.scale_var, values=["2x", "4x", "8x"], state="readonly", width=8)
        self.scale_box.grid(row=1, column=1, sticky="ew", padx=4, pady=3)
        ttk.Label(options, text="AI Upscale จะกำหนดจำนวนพิกเซลที่เพิ่มขึ้น", wraplength=285).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 2))
        options.columnconfigure(1, weight=1)

        recovery = ttk.LabelFrame(sidebar, text="ฟื้นฟูหน้าตาคน", style="Section.TLabelframe", padding=8)
        recovery.pack(fill="x", pady=4)
        ttk.Checkbutton(recovery, text="เปิดใช้งาน", variable=self.face_recovery_var).pack(anchor="w", pady=(0, 3))
        self.choose_faces_button = ttk.Button(recovery, text="เลือกใบหน้า…", command=self._choose_faces)
        self.choose_faces_button.pack(fill="x")

        output_panel = ttk.LabelFrame(sidebar, text="ขนาดส่งออกตามโหมดที่เลือก", style="Section.TLabelframe", padding=8)
        output_panel.pack(fill="x", pady=4)
        self.pixel_info = ttk.Label(output_panel, text="—", wraplength=290, justify="left")
        self.pixel_info.grid(row=0, column=0, sticky="ew")
        output_panel.columnconfigure(0, weight=1)

        device_panel = ttk.LabelFrame(sidebar, text="Device", style="Section.TLabelframe", padding=8)
        device_panel.pack(fill="x", pady=4)
        self.device_box = ttk.Combobox(device_panel, textvariable=self.device_var, values=self.device_choices, state="readonly", width=12)
        self.device_box.pack(fill="x", pady=(0, 3))
        self.device_box.bind("<<ComboboxSelected>>", self._update_device_label)
        self.device_label = ttk.Label(device_panel, text="อุปกรณ์ที่เลือก:", wraplength=285)
        self.device_label.pack(fill="x")

        actions = ttk.Frame(sidebar)
        actions.pack(fill="x", pady=5)
        self.stop_all_button = ttk.Button(actions, text="หยุดทั้งหมด", command=self._stop_all, state="disabled")
        self.stop_all_button.pack(side="right", padx=(4, 0), expand=True, fill="x")
        self.enhance_button = ttk.Button(actions, text="🚀  เริ่มปรับภาพ", command=self.start_enhance)
        self.enhance_button.pack(side="left", expand=True, fill="x")
        ttk.Label(sidebar, textvariable=self.status_var, wraplength=310, justify="center").pack(fill="x", pady=(2, 4))

        self._build_batch_list(right)
        self.workspace = workspace
        self.batch_panel.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        self._capture_static_texts(root)
        self._update_device_label()
        self.set_language(self.language)
        self._recalculate()
        for variable in (self.scale_var, self.output_mode_var, self.dpi_var, self.unit_var, self.width_var, self.height_var, self.resize_mode_var, self.device_var, self.face_recovery_var):
            variable.trace_add("write", lambda *_: self._on_setting_change())
        self.scale_var.trace_add("write", lambda *_: self._recalculate())
        self._update_output_mode()
        self._update_preview_button_state()
        self.recent_view = self.settings.get("recent_view", "thumbnails")
        if self.recent_view not in ("thumbnails", "list"):
            self.recent_view = "thumbnails"
        self.set_language(self.language)
        self.root.bind("<Configure>", self._on_window_configure, add="+")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def t(self, text):
        if self.language == "th":
            return text
        return TRANSLATIONS.get(self.language, EN).get(text, EN.get(text, text))

    def _resize_mode_labels(self):
        return [self.t("ยืดภาพ"), self.t("รักษาสัดส่วน"), self.t("เติมขอบด้วย AI")]

    def _sync_resize_mode_label(self):
        key = {"stretch": "ยืดภาพ", "preserve": "รักษาสัดส่วน", "ai_expand": "เติมขอบด้วย AI"}.get(self.resize_mode_var.get(), "รักษาสัดส่วน")
        self.resize_mode_label_var.set(self.t(key))

    def _resize_mode_selected(self, _event=None):
        reverse = {self.t("ยืดภาพ"): "stretch", self.t("รักษาสัดส่วน"): "preserve", self.t("เติมขอบด้วย AI"): "ai_expand"}
        self.resize_mode_var.set(reverse.get(self.resize_mode_label_var.get(), "preserve"))

    def _dpi_choices(self):
        return [*DPI_PRESETS[:-1], self.t("Custom")]

    def _build_language_selector(self, parent):
        bar = ttk.Frame(parent)
        bar.pack(fill="x", padx=18, pady=(4, 0))
        icon_path = application_resource_root() / "assets" / "lang.png"
        try:
            with Image.open(icon_path) as source:
                icon = source.convert("RGBA")
                icon.thumbnail((20, 20), Image.Resampling.LANCZOS)
            self.language_icon = ImageTk.PhotoImage(icon)
            ttk.Label(bar, image=self.language_icon).pack(side="left", padx=(0, 5))
        except (OSError, ValueError):
            ttk.Label(bar, text="🌐").pack(side="left", padx=(0, 5))
        self.language_var = tk.StringVar(value=LANGUAGE_CHOICES[self.language])
        self._language_code_by_label = {label: code for code, label in LANGUAGE_CHOICES.items()}
        self.language_box = ttk.Combobox(bar, textvariable=self.language_var,
                                         values=list(LANGUAGE_CHOICES.values()),
                                         state="readonly", width=13)
        self.language_box.pack(side="left")
        self.language_box.bind("<<ComboboxSelected>>", self._language_selected)

    def _language_selected(self, _event=None):
        code = self._language_code_by_label.get(self.language_var.get())
        if code:
            self.set_language(code)

    def _apply_language_fonts(self):
        family = "Microsoft YaHei UI" if self.language == "zh" else "Tahoma"
        for font_name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont", "TkCaptionFont"):
            try:
                tkfont.nametofont(font_name).configure(family=family, size=11)
            except tk.TclError:
                pass
        style = ttk.Style()
        style.configure("Title.TLabel", font=(family, 20, "bold"))
        style.configure("TLabel", font=(family, 12))
        style.configure("TButton", font=(family, 11))
        style.configure("TCheckbutton", font=(family, 11))
        style.configure("TRadiobutton", font=(family, 11))
        style.configure("TEntry", font=(family, 12), padding=4)
        style.configure("TCombobox", font=(family, 12), padding=4)
        style.configure("Section.TLabelframe.Label", font=(family, 12, "bold"))
        if hasattr(self, "coffee_tagline"):
            self.coffee_tagline.configure(font=(family, 10, "bold"))

    def _load_settings(self):
        for candidate in (self.settings_path, self.legacy_settings_path):
            try:
                with candidate.open("r", encoding="utf-8") as stream:
                    data = json.load(stream)
                if isinstance(data, dict):
                    return data
            except (OSError, json.JSONDecodeError):
                continue
        return {}

    def _schedule_save_settings(self):
        if self._settings_after is not None:
            try:
                self.root.after_cancel(self._settings_after)
            except tk.TclError:
                pass
        self._settings_after = self.root.after(350, self._save_settings)

    def _save_settings(self):
        self._settings_after = None
        self._save_current_job_settings()
        data = {
            "language": self.language, "scale": self.scale_var.get(), "dpi": self.dpi_var.get(),
            "output_mode": self.output_mode_var.get(),
            "unit": self.unit_var.get(), "width": self.width_var.get(), "height": self.height_var.get(),
            "resize_mode": self.resize_mode_var.get(), "lock_ratio": self.resize_mode_var.get() != "stretch", "device": self.device_var.get(),
            "face_recovery": self.face_recovery_var.get(),
            "job_configs": {
                item["normalized"]: self._serializable_job_config(item)
                for item in self.batch_items
            },
            "recent_files": self._recent_files,
            "recent_view": getattr(self, "recent_view", "thumbnails"),
            "auto_preview": self.auto_preview_var.get(),
        }
        try:
            if self.root.state() == "normal":
                geometry = self.root.geometry().split("+")
                dimensions = geometry[0].split("x")
                if len(dimensions) == 2:
                    data["window_width"], data["window_height"] = map(int, dimensions)
                    if len(geometry) >= 3:
                        data["window_x"], data["window_y"] = int(geometry[1]), int(geometry[2])
        except (tk.TclError, ValueError):
            pass
        try:
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.settings_path.with_suffix(".json.tmp")
            temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            os.replace(temporary, self.settings_path)
        except OSError as exc:
            print(f"Could not save settings: {exc}")

    def _on_close(self):
        if self._window_save_after is not None:
            try:
                self.root.after_cancel(self._window_save_after)
            except tk.TclError:
                pass
        self._save_settings()
        self.root.destroy()

    def _on_window_configure(self, event):
        if event.widget is not self.root:
            return
        if self._window_save_after is not None:
            try:
                self.root.after_cancel(self._window_save_after)
            except tk.TclError:
                pass
        self._window_save_after = self.root.after(500, self._save_settings)

    def _build_header(self, parent):
        header_bg = ttk.Style().lookup("TFrame", "background") or parent.cget("background")
        header = ttk.Frame(parent)
        header.pack(fill="x", padx=18, pady=(5, 3))
        header.grid_columnconfigure(1, weight=1)
        self.logo_canvas = tk.Canvas(header, width=300, height=100, bg=header_bg, highlightthickness=0)
        self.logo_canvas.grid(row=0, column=0, sticky="w")
        self._draw_app_logo()

        title = ttk.Frame(header)
        title.grid(row=0, column=1, sticky="n", pady=(18, 0))
        ttk.Label(title, text="ARM AI IMAGE ENHANCER", style="Title.TLabel").pack(pady=(0, 2))
        ttk.Label(title, text="เตรียมภาพความละเอียดสูงสำหรับงานป้าย").pack()

        self._build_coffee_card(header, header_bg)

    def _draw_app_logo(self):
        logo_path = application_resource_root() / "assets" / "app_logo.png"
        if not logo_path.exists():
            return
        with Image.open(logo_path) as source:
            logo = source.convert("RGBA")
            logo.thumbnail((290, 78), Image.Resampling.LANCZOS)
        self.logo_photo = ImageTk.PhotoImage(logo)
        self.logo_canvas.create_image(4, 50, image=self.logo_photo, anchor="w")

    def _build_coffee_card(self, parent, header_bg):
        card = tk.Frame(parent, bg="#E5F2FC", padx=2, pady=2, highlightthickness=0)
        card.grid(row=0, column=2, sticky="e")
        body = tk.Frame(card, bg="#FFFFFF", padx=8, pady=6)
        body.pack()
        body.configure(width=354, height=140)
        body.pack_propagate(False)

        details = tk.Frame(body, bg="#FFFFFF")
        details.pack(side="left", fill="both", expand=True, anchor="w")
        self.coffee_tagline = tk.Label(details, text=self.t("แปะไว้เผื่ออยากเลี้ยงกาแฟ"), bg="#FFFFFF", fg="#174A73",
                                       font=("Tahoma", 10, "bold"), anchor="w")
        self.coffee_tagline.pack(fill="x", pady=(0, 2))
        self._static_texts[self.coffee_tagline] = "แปะไว้เผื่ออยากเลี้ยงกาแฟ"
        tk.Label(details, text="อิสระพงษ์ สิทธิพล", bg="#FFFFFF", fg="#17324D",
                 font=("Tahoma", 11, "bold"), anchor="w").pack(fill="x", pady=(0, 3))

        line_row = tk.Frame(details, bg="#FFFFFF")
        line_row.pack(fill="x", pady=1)
        ttk.Label(line_row, text="Click ▶ ").pack(side="left")
        line_icon = tk.Label(line_row, text="LINE", bg="#06C755", fg="#FFFFFF", padx=5,
                             font=("Tahoma", 8, "bold"), cursor="hand2")
        line_icon.pack(side="left")
        line_icon.bind("<Button-1>", lambda _event: self._open_contact("https://line.me/ti/p/itsarap"))
        line_name = tk.Label(line_row, text="itsarap", bg="#FFFFFF", fg="#36546A",
                             font=("Tahoma", 9), padx=5, cursor="hand2")
        line_name.pack(side="left")
        line_name.bind("<Button-1>", lambda _event: self._copy_contact("itsarap"))

        facebook_row = tk.Frame(details, bg="#FFFFFF")
        facebook_row.pack(fill="x", pady=1)
        ttk.Label(facebook_row, text="Click ▶ ").pack(side="left")
        facebook_icon = tk.Label(facebook_row, text="f", bg="#1877F2", fg="#FFFFFF", width=2,
                                 font=("Tahoma", 9, "bold"), cursor="hand2")
        facebook_icon.pack(side="left")
        facebook_icon.bind("<Button-1>", lambda _event: self._open_contact("https://www.facebook.com/armSPNprint"))
        facebook_name = tk.Label(facebook_row, text="อาม ทราย", bg="#FFFFFF", fg="#36546A",
                                 font=("Tahoma", 9), padx=5, cursor="hand2")
        facebook_name.pack(side="left")
        facebook_name.bind("<Button-1>", lambda _event: self._copy_contact("อาม ทราย"))

        qr_path = application_resource_root() / "assets" / "QR.jpg"
        qr_column = tk.Frame(body, bg="#FFFFFF")
        qr_column.pack(side="right", padx=(7, 0))
        tk.Label(qr_column, text="PROMPTPAY", bg="#EAF4FC", fg="#17528C",
                 font=("Tahoma", 7, "bold"), padx=4).pack(fill="x", pady=(0, 2))
        self.qr_preview = None
        if qr_path.exists():
            with Image.open(qr_path) as source:
                # Crop only the quiet-zone square around the original QR matrix; no modules are redrawn.
                qr = source.convert("RGB").crop((24, 264, 291, 533))
                qr = qr.resize((112, 112), Image.Resampling.NEAREST)
            self.qr_preview = ImageTk.PhotoImage(qr)
            qr_label = tk.Label(qr_column, image=self.qr_preview, bg="#FFFFFF", cursor="hand2", bd=0)
            qr_label.pack()
            qr_label.bind("<Button-1>", self._show_full_qr)
            qr_label.bind("<Enter>", lambda _event: qr_label.configure(cursor="hand2"))
        else:
            tk.Label(qr_column, text="QR missing", bg="#FFFFFF", fg="#A33", font=("Tahoma", 8)).pack()

    def _copy_contact(self, value):
        self.root.clipboard_clear()
        self.root.clipboard_append(value)
        self.root.update_idletasks()

    @staticmethod
    def _open_contact(url):
        webbrowser.open(url)

    def _show_full_qr(self, _event=None):
        qr_path = application_resource_root() / "assets" / "QR.jpg"
        if not qr_path.exists():
            return
        window = tk.Toplevel(self.root)
        window.title(self.t("PromptPay — QR"))
        window.resizable(False, False)
        with Image.open(qr_path) as source:
            image = source.convert("RGB")
        window.qr_photo = ImageTk.PhotoImage(image)
        tk.Label(window, image=window.qr_photo, bd=0).pack(padx=10, pady=10)
        tk.Label(window, text="อิสระพงษ์ สิทธิพล", font=("Tahoma", 12, "bold")).pack(pady=(0, 10))

    def _capture_static_texts(self, parent):
        for child in parent.winfo_children():
            try:
                value = child.cget("text")
                if value:
                    self._static_texts[child] = value
            except tk.TclError:
                pass
            self._capture_static_texts(child)

    def _build_welcome_page(self, parent):
        self.welcome = ttk.Frame(parent, padding=12)
        self.welcome.columnconfigure(0, weight=0, minsize=330)
        self.welcome.columnconfigure(1, weight=1)
        self.welcome.rowconfigure(0, weight=1)
        recent = ttk.LabelFrame(self.welcome, text="Recent", padding=8)
        recent.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        recent.rowconfigure(1, weight=1)
        recent.columnconfigure(0, weight=1)
        self.recent_header = ttk.Frame(recent)
        self.recent_header.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        ttk.Label(self.recent_header, text="Recent").pack(side="left", padx=4)
        self.recent_list_view_button = ttk.Button(self.recent_header, text="☷", width=3,
                                                  command=lambda: self._set_recent_view("list"))
        self.recent_list_view_button.pack(side="right", padx=(3, 0))
        self.recent_thumbnail_view_button = ttk.Button(self.recent_header, text="▦", width=3,
                                                       command=lambda: self._set_recent_view("thumbnails"))
        self.recent_thumbnail_view_button.pack(side="right")

        self.recent_list = tk.Listbox(recent, height=12, selectmode="browse")
        self.recent_list.bind("<Double-Button-1>", self._open_recent_item)

        self.recent_thumb_frame = ttk.Frame(recent)
        self.recent_thumb_frame.columnconfigure(0, weight=1)
        self.recent_thumb_canvas = tk.Canvas(self.recent_thumb_frame, highlightthickness=0, bd=0)
        self.recent_thumb_scroll = ttk.Scrollbar(self.recent_thumb_frame, orient="vertical",
                                                 command=self.recent_thumb_canvas.yview)
        self.recent_thumb_canvas.configure(yscrollcommand=self.recent_thumb_scroll.set)
        self.recent_thumb_canvas.pack(side="left", fill="both", expand=True)
        self.recent_thumb_scroll.pack(side="right", fill="y")
        self.recent_thumb_inner = ttk.Frame(self.recent_thumb_canvas)
        self.recent_thumb_window = self.recent_thumb_canvas.create_window((0, 0), window=self.recent_thumb_inner, anchor="nw")
        self.recent_thumb_inner.bind("<Configure>", lambda _event: self.recent_thumb_canvas.configure(
            scrollregion=self.recent_thumb_canvas.bbox("all")))
        self.recent_thumb_canvas.bind("<Configure>", lambda event: self.recent_thumb_canvas.itemconfigure(
            self.recent_thumb_window, width=event.width))
        self.recent_thumb_canvas.bind("<MouseWheel>", lambda event: self.recent_thumb_canvas.yview_scroll(
            int(-event.delta / 120), "units"))

        ttk.Button(recent, text="Clear History", command=self._clear_recent).grid(row=2, column=0, sticky="ew", pady=(7, 3))
        ttk.Button(recent, text="User Guide", command=self._show_user_guide).grid(row=3, column=0, sticky="ew", pady=3)
        ttk.Button(recent, text="เริ่มใช้งาน", command=self._show_main_page).grid(row=4, column=0, sticky="ew", pady=(3, 0))

        drop = ttk.LabelFrame(self.welcome, text="ลากภาพมาวางที่นี่", padding=24)
        drop.grid(row=0, column=1, sticky="nsew")
        drop.columnconfigure(0, weight=1)
        drop.rowconfigure(0, weight=1)
        self.drop_prompt = ttk.Label(drop, text="ลาก และ วางภาพที่นี่", anchor="center", style="Title.TLabel")
        self.drop_prompt.grid(row=0, column=0, sticky="nsew")
        self.browse_images_button = ttk.Button(drop, text="Browse Images", command=self.select_image)
        self.browse_images_button.grid(row=1, column=0, pady=14)
        self._recent_photo_refs = []
        self._refresh_recent_list()

    def _apply_recent_view(self):
        if not hasattr(self, "recent_list"):
            return
        view = getattr(self, "recent_view", "thumbnails")
        if view == "list":
            self.recent_thumb_frame.grid_forget()
            self.recent_list.grid(row=1, column=0, sticky="nsew")
        else:
            self.recent_list.grid_forget()
            self.recent_thumb_frame.grid(row=1, column=0, sticky="nsew")
        self.recent_list_view_button.state(["pressed"] if view == "list" else ["!pressed"])
        self.recent_thumbnail_view_button.state(["pressed"] if view == "thumbnails" else ["!pressed"])

    def _set_recent_view(self, view):
        if view not in ("list", "thumbnails"):
            return
        self.recent_view = view
        self._apply_recent_view()
        self._schedule_save_settings()

    def _open_recent_path(self, path):
        try:
            item = self._add_batch_item(path)
            self._show_main_page()
            if item:
                self._show_item(item, initialize_size=not self._restored_dimensions)
            else:
                self._show_item(self.batch_by_path[os.path.normcase(os.path.abspath(path))])
        except Exception as exc:
            messagebox.showerror(self.t("เปิดภาพไม่สำเร็จ"), str(exc))

    def _refresh_recent_list(self):
        if not hasattr(self, "recent_list"):
            return
        self._recent_files = [path for path in self._recent_files if os.path.isfile(path)][:20]
        self.recent_list.delete(0, "end")
        for path in self._recent_files:
            self.recent_list.insert("end", path)
        for child in self.recent_thumb_inner.winfo_children():
            child.destroy()
        self._recent_photo_refs.clear()
        for index, path in enumerate(self._recent_files):
            try:
                with Image.open(path) as source:
                    thumbnail = ImageOps.contain(source.convert("RGB"), (120, 88))
                photo = ImageTk.PhotoImage(thumbnail)
            except (OSError, ValueError):
                continue
            self._recent_photo_refs.append(photo)
            card = ttk.Frame(self.recent_thumb_inner, padding=4, relief="groove")
            card.grid(row=index // 2, column=index % 2, sticky="nsew", padx=3, pady=3)
            self.recent_thumb_inner.columnconfigure(index % 2, weight=1)
            image_label = ttk.Label(card, image=photo, cursor="hand2")
            image_label.pack(padx=2, pady=(2, 3))
            name_label = ttk.Label(card, text=Path(path).name, wraplength=130, justify="center", cursor="hand2")
            name_label.pack(fill="x")
            for widget in (card, image_label, name_label):
                widget.bind("<Double-Button-1>", lambda _event, p=path: self._open_recent_path(p))
        self._apply_recent_view()

    def _clear_recent(self):
        self._recent_files.clear()
        self._refresh_recent_list()
        self._schedule_save_settings()

    def _open_recent_item(self, _event=None):
        selection = self.recent_list.curselection()
        if selection:
            self._open_recent_path(self.recent_list.get(selection[0]))

    def _show_main_page(self):
        self.workspace.pack(fill="both", expand=True, padx=12, pady=(2, 5))

    def _show_welcome_page(self):
        self._show_main_page()

    def _show_user_guide(self):
        window = tk.Toplevel(self.root)
        window.title(self.t("คู่มือผู้ใช้"))
        window.geometry("520x360")
        ttk.Label(window, text=self.t("คู่มือ"), font=("Tahoma", 14, "bold")).pack(anchor="w", padx=18, pady=(16, 4))
        guide_text = "\n".join(self.t(line) for line in (
            "1. ลากภาพมาวางหรือกด Browse Images เพื่อเพิ่มภาพ",
            "2. เลือกภาพในรายการเพื่อกำหนดค่าของภาพนั้น",
            "3. เลือกกำหนดขนาดงานพิมพ์หรือขยายด้วย AI Upscale",
            "4. เลือกฟื้นฟูหน้าตาคนได้ตามต้องการ",
            "5. ดูตัวอย่างแล้วกดเริ่มปรับภาพ",
            "ไฟล์ PNG จะบันทึกไว้ข้างไฟล์ต้นฉบับ",
        ))
        body = ttk.Label(window, text=guide_text, justify="left", wraplength=470)
        body.pack(fill="both", expand=True, padx=20, pady=12)
        language = ttk.Combobox(window, values=list(LANGUAGE_CHOICES.values()), state="readonly", width=15)
        language.set(LANGUAGE_CHOICES[self.language])
        language.pack(side="left", padx=16, pady=(0, 14))
        language.bind("<<ComboboxSelected>>", lambda _event: self._set_guide_language(window, language, body))
        ttk.Button(window, text=self.t("ปิด"), command=window.destroy).pack(side="right", padx=16, pady=(0, 14))

    def _set_guide_language(self, window, language_box, body):
        code = {label: key for key, label in LANGUAGE_CHOICES.items()}.get(language_box.get())
        if code not in LANGUAGE_CHOICES:
            return
        lines = (
            "1. ลากภาพมาวางหรือกด Browse Images เพื่อเพิ่มภาพ",
            "2. เลือกภาพในรายการเพื่อกำหนดค่าของภาพนั้น",
            "3. เลือกกำหนดขนาดงานพิมพ์หรือขยายด้วย AI Upscale",
            "4. เลือกฟื้นฟูหน้าตาคนได้ตามต้องการ",
            "5. ดูตัวอย่างแล้วกดเริ่มปรับภาพ",
            "ไฟล์ PNG จะบันทึกไว้ข้างไฟล์ต้นฉบับ",
        )
        body.configure(text="\n".join(TRANSLATIONS.get(code, {}).get(line, EN.get(line, line)) if code != "th" else line for line in lines))
        window.title(TRANSLATIONS.get(code, {}).get("คู่มือผู้ใช้", EN.get("คู่มือผู้ใช้", "User Guide")) if code != "th" else "คู่มือผู้ใช้")

    def _preview_mode_changed(self):
        self._update_preview_button_state()
        self._on_setting_change()
        if self.auto_preview_var.get():
            self._schedule_ai_preview()

    def _enable_native_file_drop(self, _event=None):
        if sys.platform != "win32":
            return
        if self._drop_scan_active:
            return
        self._drop_scan_active = True
        try:
            import ctypes
            from ctypes import wintypes
            user32, shell32 = ctypes.windll.user32, ctypes.windll.shell32
            callback_type = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
            get_proc = user32.GetWindowLongPtrW
            get_proc.restype = ctypes.c_void_p
            get_proc.argtypes = (wintypes.HWND, ctypes.c_int)
            set_proc = user32.SetWindowLongPtrW
            set_proc.restype = ctypes.c_void_p
            set_proc.argtypes = (wintypes.HWND, ctypes.c_int, ctypes.c_void_p)
            user32.CallWindowProcW.argtypes = (ctypes.c_void_p, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
            user32.CallWindowProcW.restype = ctypes.c_ssize_t
            shell32.DragQueryFileW.argtypes = (wintypes.HANDLE, wintypes.UINT, wintypes.LPWSTR, wintypes.UINT)
            shell32.DragQueryFileW.restype = wintypes.UINT
            shell32.DragFinish.argtypes = (wintypes.HANDLE,)
            shell32.DragAcceptFiles.argtypes = (wintypes.HWND, wintypes.BOOL)
            self.root.update_idletasks()
            hwnd = int(self.root.winfo_id())
            if hwnd in self._drop_wndprocs:
                return
            old_proc = get_proc(hwnd, -4)
            if not old_proc:
                raise OSError("Could not read the current window procedure")
            shell32.DragAcceptFiles(hwnd, True)

            def wndproc(window, message, wparam, lparam):
                if message == 0x0233:  # WM_DROPFILES
                    dropped = []
                    try:
                        count = shell32.DragQueryFileW(wparam, 0xFFFFFFFF, None, 0)
                        for index in range(count):
                            length = shell32.DragQueryFileW(wparam, index, None, 0)
                            buffer = ctypes.create_unicode_buffer(length + 1)
                            shell32.DragQueryFileW(wparam, index, buffer, length + 1)
                            dropped.append(buffer.value)
                    except Exception:
                        pass
                    finally:
                        shell32.DragFinish(wparam)
                    try:
                        self.root.after(0, lambda paths=dropped: self._ingest_paths(paths) if paths else None)
                    except tk.TclError:
                        pass
                    return 0
                return user32.CallWindowProcW(old_proc, window, message, wparam, lparam)

            callback = callback_type(wndproc)
            previous = set_proc(hwnd, -4, ctypes.cast(callback, ctypes.c_void_p))
            if previous:
                self._drop_wndprocs[hwnd] = callback
                self._drop_old_procs[hwnd] = old_proc
            else:
                shell32.DragAcceptFiles(hwnd, False)
                raise OSError("Could not install the file-drop handler")
        except Exception:
            # File browsing remains available if native drop support is not
            # available on a particular Windows/Tk build.
            pass
        finally:
            self._drop_scan_active = False

    def _forget_native_drop_target(self, event):
        if sys.platform != "win32":
            return
        if event.widget is not self.root:
            return
        try:
            import ctypes
            from ctypes import wintypes
            hwnd = int(event.widget.winfo_id())
            old_proc = self._drop_old_procs.get(hwnd)
            callback = self._drop_wndprocs.get(hwnd)
            if old_proc is None or callback is None:
                return
            user32 = ctypes.windll.user32
            set_proc = user32.SetWindowLongPtrW
            set_proc.restype = ctypes.c_void_p
            set_proc.argtypes = (wintypes.HWND, ctypes.c_int, ctypes.c_void_p)
            set_proc(hwnd, -4, old_proc)
            ctypes.windll.shell32.DragAcceptFiles(hwnd, False)
            del self._drop_old_procs[hwnd]
            del self._drop_wndprocs[hwnd]
        except Exception:
            pass

    def _update_preview_button_state(self):
        self.update_preview_button.configure(state="disabled" if self.auto_preview_var.get() else "normal")

    def _schedule_ai_preview(self):
        if self._preview_after is not None:
            try:
                self.root.after_cancel(self._preview_after)
            except tk.TclError:
                pass
        self._preview_after = self.root.after(650, self._request_ai_preview)

    def _request_ai_preview(self):
        self._preview_after = None
        item = self.selected_item
        if item is None or self._is_processing:
            return
        self._save_current_job_settings()
        config = self._read_job_config()
        generation = self._preview_generation = self._preview_generation + 1
        self.after_info.configure(text=self.t("กำลังสร้างตัวอย่าง AI…"))
        source = item["path"]
        try:
            with Image.open(source) as image:
                image = image.convert("RGB")
                canvas = self.before_image
                cw, ch = max(canvas.winfo_width(), 2), max(canvas.winfo_height(), 2)
                factor = min(cw / image.width, ch / image.height) * self.zoom
                left = image.width / 2 - (cw / 2 + self.pan_x * cw) / factor
                top = image.height / 2 - (ch / 2 + self.pan_y * ch) / factor
                box = (max(0, int(left)), max(0, int(top)), min(image.width, int(left + cw / factor) + 1), min(image.height, int(top + ch / factor) + 1))
                crop = image.crop(box)
                crop.thumbnail((512, 512), Image.Resampling.LANCZOS)
        except Exception as exc:
            self.after_info.configure(text=f"Preview unavailable: {exc}")
            return
        choice = config.get("device", "AUTO")
        try:
            device = self._engine_device(choice)
        except Exception as exc:
            self.after_info.configure(text=f"Preview unavailable: {exc}")
            return
        threading.Thread(target=self._ai_preview_worker, args=(generation, crop, device), daemon=True).start()

    def _ai_preview_worker(self, generation, crop, device):
        import tempfile
        input_path = output_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as stream:
                input_path = stream.name
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as stream:
                output_path = stream.name
            crop.save(input_path)
            engine = self.engine_manager.create_engine(device)
            engine.enhance(input_path, output_path, scale=2)
            with Image.open(output_path) as enhanced:
                enhanced.load()
                # Downsample the model result to the source-crop footprint so the preview overlays the original framing.
                enhanced = enhanced.convert("RGB").resize(crop.size, Image.Resampling.LANCZOS)
            self.root.after(0, lambda g=generation, image=enhanced.copy(): self._show_ai_preview(g, image))
        except Exception as exc:
            self.root.after(0, lambda g=generation, e=str(exc): self._preview_error(g, e))
        finally:
            for path in (input_path, output_path):
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except OSError:
                        pass

    def _show_ai_preview(self, generation, crop):
        if generation != self._preview_generation or self.selected_item is None:
            return
        # Preview crop is shown in the result pane; keep the current source viewport aligned by fitting its visible crop.
        original = self._preview_pils.get("before")
        if original is None:
            return
        preview = original.copy()
        canvas = self.before_image
        cw, ch = max(canvas.winfo_width(), 2), max(canvas.winfo_height(), 2)
        factor = min(cw / original.width, ch / original.height) * self.zoom
        x0 = max(0, int(original.width / 2 - (cw / 2 + self.pan_x * cw) / factor))
        y0 = max(0, int(original.height / 2 - (ch / 2 + self.pan_y * ch) / factor))
        x1 = min(original.width, x0 + max(1, int(cw / factor)))
        y1 = min(original.height, y0 + max(1, int(ch / factor)))
        if crop.size != (x1 - x0, y1 - y0):
            crop = crop.resize((x1 - x0, y1 - y0), Image.Resampling.LANCZOS)
        preview.paste(crop, (x0, y0))
        # Make the preview reflect the requested output proportions. The real
        # export is resized to these pixel dimensions after the AI pass too.
        try:
            config = self._read_job_config()
            target_w, target_h = self._output_size_for(self.selected_item, config)
            scale = min(1800 / target_w, 1400 / target_h)
            preview_size = (max(1, round(target_w * scale)), max(1, round(target_h * scale)))
            if config.get("resize_mode", "preserve") == "stretch":
                preview = preview.resize(preview_size, Image.Resampling.LANCZOS)
            else:
                fitted = ImageOps.contain(preview, preview_size, method=Image.Resampling.LANCZOS)
                framed = Image.new("RGB", preview_size, "white")
                framed.paste(fitted, ((preview_size[0] - fitted.width) // 2,
                                      (preview_size[1] - fitted.height) // 2))
                preview = framed
        except (ValueError, KeyError, ZeroDivisionError):
            pass
        self._preview_pils["after"] = preview
        self._render_previews()
        self.after_info.configure(text="ตัวอย่าง AI โดยประมาณ • ยังไม่บันทึก")

    def _preview_error(self, generation, error):
        if generation == self._preview_generation:
            self.after_info.configure(text=f"Preview unavailable: {error}")

    def set_language(self, language):
        if language not in LANGUAGE_CHOICES:
            return
        self.language = language
        self.language_var.set(LANGUAGE_CHOICES[language])
        self.dpi_box.configure(values=self._dpi_choices())
        if hasattr(self, "resize_mode_box"):
            self.resize_mode_box.configure(values=self._resize_mode_labels())
            self._sync_resize_mode_label()
        self._apply_language_fonts()
        self.root.title(f"ARM AI Image Enhancer — {APP_VERSION}")
        for widget, source_text in list(self._static_texts.items()):
            try:
                widget.configure(text=self.t(source_text))
            except tk.TclError:
                pass
        self._update_device_label()
        self._recalculate()
        self._refresh_image_labels()
        self._refresh_batch_rows()
        self._set_status(self.status_code)
        self._schedule_save_settings()

    def _set_status(self, code):
        self.status_code = code
        messages = {
            "ready": "พร้อมใช้งาน — เลือกภาพเพื่อเริ่ม",
            "selected": "เลือกภาพแล้ว — ปรับขนาดงานพิมพ์และตั้งค่าได้",
            "working": "กำลังประมวลผลด้วย Real-ESRGAN…",
            "expanding": "กำลังเติมขอบภาพด้วย AI…",
            "done": "เสร็จเรียบร้อย — บันทึกไฟล์ PNG แล้ว",
            "error": "เกิดข้อผิดพลาด",
            "stopping": "กำลังหยุด…",
            "cancelled": "ยกเลิกแล้ว",
        }
        self.status_var.set(self.t(messages[code]))

    def _refresh_image_labels(self):
        if getattr(self, "input_metadata", None):
            name, width, height, image_format = self.input_metadata
            if self.language == "en":
                self.before_info.configure(text=f"{name}\n{width:,} × {height:,} px  •  {image_format}")
            else:
                self.before_info.configure(text=f"{name}\n{width:,} × {height:,} px  •  {image_format}")
        if getattr(self, "output_metadata", None):
            path, width, height, dpi = self.output_metadata
            self.after_info.configure(text=f"{width:,} × {height:,} px  •  {dpi} DPI\n{path}")

    def _engine_device(self, choice):
        if choice == "AUTO":
            return "AUTO"
        if choice == "CPU":
            return "cpu"
        if choice == "DIRECTML":
            gpu = next((d for d in self.engine_manager.device_manager.get_devices() if d.backend == "DIRECTML" and d.available), None)
            if gpu is None:
                raise RuntimeError(self.t("ไม่พบ DirectML GPU หรือยังไม่ได้ติดตั้งส่วนเสริมทดลอง"))
            return gpu.device_id
        gpu = next((d for d in self.engine_manager.device_manager.get_devices() if d.backend in ("CUDA", "DIRECTML") and d.available), None)
        if gpu is None:
            raise RuntimeError(self.t("ตรวจไม่พบ GPU ที่รองรับ"))
        return gpu.device_id

    def _update_device_label(self, _event=None):
        choice = self.device_var.get()
        try:
            target = self._engine_device(choice)
            device = (self.engine_manager.device_manager.get_default_device() if target == "AUTO"
                      else self.engine_manager.device_manager.get_device(target))
            name = device.name if device else self.t("ตรวจไม่พบ GPU ที่รองรับ")
        except Exception as exc:
            name = str(exc)
        self.device_label.configure(text=f"{self.t('อุปกรณ์ที่เลือก:')} {name}")

    def _build_batch_list(self, parent):
        panel = ttk.LabelFrame(parent, text="รายการไฟล์ต้นฉบับ", style="Section.TLabelframe")
        self.batch_panel = panel
        tools = ttk.Frame(panel)
        tools.pack(fill="x", padx=6, pady=(2, 4))
        ttk.Button(tools, text="เลือกทั้งหมด", command=lambda: self._check_all(True)).pack(side="left", padx=3)
        ttk.Button(tools, text="ยกเลิกทั้งหมด", command=lambda: self._check_all(False)).pack(side="left", padx=3)
        headings = ttk.Frame(panel)
        headings.pack(fill="x", padx=8, pady=(0, 2))
        ttk.Label(headings, text="ภาพย่อ", width=11).pack(side="left", padx=(42, 0))
        ttk.Label(headings, text="ชื่อไฟล์", width=30, anchor="w").pack(side="left", padx=4)
        ttk.Label(headings, text="ขนาดต้นฉบับ", width=33, anchor="w").pack(side="left", padx=4)
        ttk.Label(headings, text="ขนาดหลัง Enhance", anchor="w").pack(side="left", padx=8)
        self.batch_canvas = tk.Canvas(panel, height=155, highlightthickness=0)
        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=self.batch_canvas.yview)
        self.batch_canvas.configure(yscrollcommand=scrollbar.set)
        self.batch_canvas.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=(0, 6))
        scrollbar.pack(side="right", fill="y", padx=(0, 6), pady=(0, 6))
        self.batch_inner = ttk.Frame(self.batch_canvas)
        self.batch_window = self.batch_canvas.create_window((0, 0), window=self.batch_inner, anchor="nw")
        self.batch_inner.bind("<Configure>", lambda _event: self.batch_canvas.configure(scrollregion=self.batch_canvas.bbox("all")))
        self.batch_canvas.bind("<Configure>", lambda event: self.batch_canvas.itemconfigure(self.batch_window, width=event.width))
        self.batch_canvas.bind("<MouseWheel>", lambda event: self.batch_canvas.yview_scroll(int(-event.delta / 120), "units"))
        self.resize_mode_var.trace_add("write", lambda *_: self._refresh_batch_rows())
        self.resize_mode_var.trace_add("write", lambda *_: self._recalculate())

    def _check_all(self, checked):
        for item in self.batch_items:
            item["checked"].set(checked)

    def _add_batch_item(self, path):
        normalized = os.path.normcase(os.path.abspath(path))
        if normalized in self.batch_by_path:
            return None
        with Image.open(path) as image:
            width, height = image.size
            thumb = ImageOps.contain(image.convert("RGB"), (64, 48))
            fmt = image.format or "Image"
        saved_config = self.settings.get("job_configs", {}).get(normalized, {})
        if not saved_config and self.selected_item is not None:
            saved_config = self._read_job_config()
        item = {"path": path, "normalized": normalized, "size": (width, height), "format": fmt,
                "thumbnail": ImageTk.PhotoImage(thumb), "checked": tk.BooleanVar(value=True), "output_path": None,
                "cancel_event": threading.Event(), "selected_faces": set(saved_config.get("selected_faces", [])),
                "config": self._default_job_config(saved_config)}
        self._recent_files = [p for p in self._recent_files if os.path.normcase(os.path.abspath(p)) != normalized]
        self._recent_files.insert(0, path)
        self._recent_files = self._recent_files[:20]
        row = ttk.Frame(self.batch_inner, padding=(4, 3), height=50)
        row.pack(fill="x", padx=2, pady=1)
        row.pack_propagate(False)
        separator = ttk.Separator(self.batch_inner, orient="horizontal")
        separator.pack(fill="x", padx=5)
        item["row"] = row
        item["separator"] = separator
        info = ttk.Frame(row)
        info.pack(side="left", fill="both", expand=True)
        actions = ttk.Frame(row)
        actions.pack(side="right", fill="y")
        check = ttk.Checkbutton(info, variable=item["checked"], command=lambda selected=item: self._on_item_checked(selected))
        check.pack(side="left", padx=(3, 8))
        thumb_label = ttk.Label(info, image=item["thumbnail"])
        thumb_label.pack(side="left", padx=(0, 10))
        filename = ttk.Label(info, text=os.path.basename(path), width=17, anchor="w")
        filename.pack(side="left", padx=4)
        original = ttk.Label(info, text=f"{self.t('ต้นฉบับ')}: {width:,} × {height:,} px  •  {fmt}", width=24, anchor="w")
        original.pack(side="left", padx=4)
        face_status = ttk.Label(info, text=f"{self.t('ใบหน้า')}: {self.t('ยังไม่ได้วิเคราะห์')}", width=14, anchor="w")
        face_status.pack(side="left", padx=4)
        output = ttk.Label(info, text="", width=20, anchor="w")
        output.pack(side="left", fill="x", expand=True, padx=8)
        delete = ttk.Button(actions, text="🗑", width=3, command=lambda p=path: self._remove_batch_item(p))
        delete.pack(side="right", padx=(3, 2))
        stop = ttk.Button(actions, text=self.t("หยุด"), width=7,
                          command=lambda selected=item: self._stop_item(selected), state="disabled")
        stop.pack(side="right", padx=2)
        self._static_texts[stop] = "หยุด"
        meter = tk.Canvas(actions, width=112, height=23, background="#DCE7F3", highlightthickness=0, bd=0)
        fill = meter.create_rectangle(0, 0, 0, 23, fill="#2596F3", outline="")
        progress_text = meter.create_text(56, 11, text="0%", fill="#17324D", font=("Tahoma", 9, "bold"))
        meter.pack(side="right", padx=(4, 3), pady=7)
        item["output_label"] = output
        item["face_status"] = face_status
        item["original_label"] = original
        item["filename_label"] = filename
        item["delete_button"] = delete
        item["stop_button"] = stop
        item["progress_canvas"] = meter
        item["progress_fill"] = fill
        item["progress_text"] = progress_text
        self.batch_items.append(item)
        self.batch_by_path[normalized] = item
        self._refresh_recent_list()
        self._schedule_save_settings()
        for widget in (info, thumb_label, filename, original, face_status, output):
            widget.bind("<Button-1>", lambda _event, selected=item: self._show_item(selected))
        return item

    def _set_item_progress(self, item, percent, text=None):
        item["progress_canvas"].coords(item["progress_fill"], 0, 0, max(0, min(100, percent)) * 1.12, 23)
        item["progress_canvas"].itemconfigure(item["progress_text"], text=text or f"{percent}%")

    def _post_item_progress(self, item, percent, text=None):
        self.root.after(0, lambda: self._set_item_progress(item, percent, text))

    def _tile_progress_callback(self, item, start, end):
        last_value = [start]

        def report(percent):
            value = min(end, max(start, start + round((end - start) * percent / 100)))
            if value > last_value[0] or percent >= 100:
                last_value[0] = value
                self._post_item_progress(item, value)

        return report

    def _mark_item_failed(self, item):
        self._set_item_progress(item, 100, "ERR")

    def _stop_item(self, item):
        if self._is_processing and item["normalized"] in self._active_items:
            item["cancel_event"].set()
            item["stop_button"].configure(state="disabled", text=self.t("กำลังหยุด…"))

    def _stop_all(self):
        if not self._is_processing:
            return
        self._cancel_all_event.set()
        self.stop_all_button.configure(state="disabled", text=self.t("กำลังหยุด…"))
        self._set_status("stopping")

    def _is_cancelled(self, item):
        return self._cancel_all_event.is_set() or item["cancel_event"].is_set()

    def _mark_item_cancelled(self, item):
        self._set_item_progress(item, 0, self.t("ยกเลิกแล้ว"))
        if self.selected_item is item:
            self._clear_preview()

    def _on_item_checked(self, item):
        if not item["checked"].get() and self.selected_item is item:
            self._clear_preview()

    def _remove_batch_item(self, path):
        normalized = os.path.normcase(os.path.abspath(path))
        item = self.batch_by_path.pop(normalized, None)
        if not item:
            return
        item["row"].destroy()
        item["separator"].destroy()
        self.batch_items.remove(item)
        if self.selected_item is item:
            self._clear_preview()
        self._refresh_batch_rows()

    def _clear_preview(self):
        self.input_file = None
        self.selected_item = None
        self._preview_pils["before"] = None
        self._preview_pils["after"] = None
        self.input_metadata = None
        self.output_metadata = None
        self.before_info.configure(text=self.t("ยังไม่ได้เลือกภาพ"))
        self.after_info.configure(text=self.t("จะแสดงตัวอย่างเมื่อประมวลผลเสร็จ"))
        self._render_previews()
        self._recalculate()
        self._set_status("ready")

    def _show_item(self, item, initialize_size=False):
        try:
            previous = self.selected_item
            if previous is not None and previous is not item:
                self._save_current_job_settings()
            with Image.open(item["path"]) as image:
                image.load()
                preview = ImageOps.contain(image.convert("RGB"), (1800, 1400))
            self.selected_item = item
            self._apply_job_settings(item)
            self.input_file = item["path"]
            self._ratio = item["size"][0] / item["size"][1]
            self.input_metadata = (os.path.basename(item["path"]), item["size"][0], item["size"][1], item["format"])
            self._preview_pils["before"] = preview
            self._preview_pils["after"] = None
            self._fit_previews()
            self._refresh_image_labels()
            if item.get("output_path") and os.path.isfile(item["output_path"]):
                with Image.open(item["output_path"]) as result:
                    result.load()
                    self._preview_pils["after"] = ImageOps.contain(result.convert("RGB"), (1800, 1400))
                with Image.open(item["output_path"]) as result:
                    result_size = result.size
                self.output_metadata = (item["output_path"], *result_size, item.get("output_dpi", self._dpi()))
                self._refresh_image_labels()
                self._render_previews()
            else:
                self.output_metadata = None
                self.after_info.configure(text=self.t("จะแสดงตัวอย่างเมื่อประมวลผลเสร็จ"))
            if initialize_size:
                self._set_dimensions_from_source()
            self._recalculate()
            self._set_status("selected")
            if self.auto_preview_var.get():
                self._schedule_ai_preview()
        except Exception as exc:
            messagebox.showerror(self.t("เปิดภาพไม่สำเร็จ"), str(exc))

    def _default_job_config(self, saved=None):
        saved = saved or {}
        config = {
            "output_mode": self.settings.get("output_mode", "print"),
            "width": self.settings.get("width", ""),
            "height": self.settings.get("height", ""),
            "unit": self.settings.get("unit", "cm"),
            "dpi": self.settings.get("dpi", "300"),
            "resize_mode": self.settings.get("resize_mode", "preserve" if self.settings.get("lock_ratio", True) else "stretch"),
            "scale": self.settings.get("scale", "4x"),
            "device": self.settings.get("device", "AUTO"),
            "face_recovery": bool(self.settings.get("face_recovery", False)),
            "selected_faces": [],
        }
        config.update({key: value for key, value in saved.items() if key in config})
        if "resize_mode" not in saved and "lock_ratio" in saved:
            config["resize_mode"] = "preserve" if saved["lock_ratio"] else "stretch"
        if config["resize_mode"] not in ("stretch", "preserve", "ai_expand"):
            config["resize_mode"] = "preserve" if config.get("lock_ratio", True) else "stretch"
        if config["output_mode"] not in ("print", "upscale"):
            config["output_mode"] = "print"
        if config["unit"] not in UNITS_TO_INCH:
            config["unit"] = "cm"
        if config["scale"] not in UPSCALE_STEPS:
            config["scale"] = "4x"
        if config["device"] not in self.device_choices:
            config["device"] = "AUTO"
        return config

    def _serializable_job_config(self, item):
        config = dict(item.get("config", {}))
        config["selected_faces"] = sorted(item.get("selected_faces", set()))
        return config

    def _save_current_job_settings(self):
        if self.selected_item is not None and not self._loading_job_settings:
            self.selected_item["config"] = self._read_job_config()

    def _read_job_config(self):
        return {
            "output_mode": self.output_mode_var.get(), "width": self.width_var.get(),
            "height": self.height_var.get(), "unit": self.unit_var.get(),
            "dpi": self.dpi_var.get(), "resize_mode": self.resize_mode_var.get(),
            "lock_ratio": self.resize_mode_var.get() != "stretch",
            "scale": self.scale_var.get(), "device": self.device_var.get(),
            "face_recovery": self.face_recovery_var.get(),
        }

    def _on_setting_change(self):
        if self._loading_job_settings:
            return
        self._save_current_job_settings()
        self._schedule_save_settings()
        if self.auto_preview_var.get():
            self._schedule_ai_preview()

    def _apply_job_settings(self, item):
        config = self._default_job_config(item.get("config"))
        self._loading_job_settings = True
        try:
            self.output_mode_var.set(config["output_mode"])
            self.width_var.set(str(config["width"]))
            self.height_var.set(str(config["height"]))
            self.unit_var.set(config["unit"])
            self.dpi_var.set(str(config["dpi"]))
            self.resize_mode_var.set(config["resize_mode"])
            self._sync_resize_mode_label()
            self.scale_var.set(config["scale"])
            self.device_var.set(config["device"])
            self.face_recovery_var.set(bool(config["face_recovery"]))
        finally:
            self._loading_job_settings = False
        self._update_output_mode()
        self._update_device_label()
        self._refresh_batch_rows()

    def _refresh_batch_rows(self):
        if not hasattr(self, "batch_items"):
            return
        for item in self.batch_items:
            ow, oh = item["size"]
            item["original_label"].configure(text=f"{self.t('ต้นฉบับ')}: {ow:,} × {oh:,} px  •  {item['format']}")
            face_data = item.get("face_data")
            if face_data is None:
                face_text = self.t("ยังไม่ได้วิเคราะห์")
            else:
                total = len(face_data["crops"])
                selected = len(item.get("selected_faces", set()))
                face_text = f"{self.t('เลือกไว้')} {selected}/{total}"
            item["face_status"].configure(text=f"{self.t('ใบหน้า')}: {face_text}")
            item["stop_button"].configure(text=self.t("กำลังหยุด…") if item["cancel_event"].is_set() else self.t("หยุด"))
            try:
                config = self._read_job_config() if item is self.selected_item else item.get("config", {})
                tw, th = self._output_size_for(item, config)
            except (ValueError, KeyError, AttributeError):
                continue
            unit = config.get("unit", "cm")
            if unit == "px":
                shown_w, shown_h = tw, th
            else:
                factor = UNITS_TO_INCH[unit] * self._dpi(config)
                shown_w, shown_h = tw / factor, th / factor
            line = f"{self.t('ผลลัพธ์ตามค่าปัจจุบัน')}: {shown_w:,.2f} × {shown_h:,.2f} {unit} ({tw:,} × {th:,} px)"
            item["output_label"].configure(text=line)

    def _target_box_size(self, config=None):
        config = config or self._read_job_config()
        width, height = float(config.get("width", "")), float(config.get("height", ""))
        if width <= 0 or height <= 0:
            raise ValueError("dimensions")
        if config.get("unit") == "px":
            return max(1, round(width)), max(1, round(height))
        factor = UNITS_TO_INCH[config.get("unit", "cm")] * self._dpi(config)
        return max(1, round(width * factor)), max(1, round(height * factor))

    def _effective_torch_device(self, choice=None):
        selected = self._engine_device(choice or self.device_var.get())
        if selected == "AUTO":
            selected = self.engine_manager.device_manager.get_default_device().device_id
        # GFPGAN/FaceXLib on DirectML is not yet validated. Keep face recovery
        # on CPU while allowing Real-ESRGAN itself to use the DirectML GPU.
        if str(selected).startswith("dml:"):
            return "cpu"
        return selected

    def _load_face_backend(self, device_name):
        with self._face_backend_lock:
            if self._face_backend is not None and self._face_backend_device == device_name:
                return self._face_backend
            import torch
            from basicsr.utils.download_util import load_file_from_url
            from facexlib.utils.face_restoration_helper import FaceRestoreHelper
            from gfpgan.archs.gfpganv1_clean_arch import GFPGANv1Clean

            model_dir = application_resource_root() / "models" / "face"
            model_dir.mkdir(parents=True, exist_ok=True)
            model_path = model_dir / "GFPGANv1.4.pth"
            if not model_path.exists():
                load_file_from_url(
                    url="https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth",
                    model_dir=str(model_dir), progress=False, file_name=model_path.name,
                )
            device = torch.device(device_name)
            network = GFPGANv1Clean(
                out_size=512, num_style_feat=512, channel_multiplier=2,
                decoder_load_path=None, fix_decoder=False, num_mlp=8,
                input_is_latent=True, different_w=True, narrow=1, sft_half=True,
            )
            checkpoint = torch.load(str(model_path), map_location="cpu")
            weights = checkpoint.get("params_ema", checkpoint.get("params", checkpoint))
            network.load_state_dict(weights, strict=True)
            network.eval().to(device)
            helper = FaceRestoreHelper(
                1, face_size=512, crop_ratio=(1, 1), det_model="retinaface_resnet50",
                save_ext="png", use_parse=False, device=device, model_rootpath=str(model_dir),
            )
            self._face_backend = {"network": network, "helper": helper, "torch": torch, "device": device}
            self._face_backend_device = device_name
            return self._face_backend

    def _choose_faces(self):
        item = self.selected_item
        if item is None:
            messagebox.showwarning("ARM AI", self.t("กรุณาเลือกภาพก่อนครับ"))
            return
        if self._face_detection_busy or self._is_processing:
            return
        self._face_detection_busy = True
        self.choose_faces_button.configure(state="disabled")
        self.enhance_button.configure(state="disabled")
        self.status_var.set(self.t("กำลังตรวจหาใบหน้า…"))
        try:
            device_name = self._effective_torch_device()
        except Exception as exc:
            self._face_detection_failed(str(exc))
            return
        threading.Thread(target=self._detect_faces_worker, args=(item, device_name, False), daemon=True).start()

    def _detect_faces_worker(self, item, device_name, auto_start=False):
        try:
            import cv2
            import numpy as np
            backend = self._load_face_backend(device_name)
            with Image.open(item["path"]) as image:
                rgb = np.array(image.convert("RGB"))
            bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            helper = backend["helper"]
            helper.clean_all()
            helper.read_image(bgr)
            helper.get_face_landmarks_5()
            helper.align_warp_face()
            state = {
                "input_img": helper.input_img.copy(),
                "crops": [face.copy() for face in helper.cropped_faces],
                "landmarks": [face.copy() for face in helper.all_landmarks_5],
                "affine": [matrix.copy() for matrix in helper.affine_matrices],
            }
            previews = [Image.fromarray(cv2.cvtColor(face, cv2.COLOR_BGR2RGB)) for face in state["crops"]]
            self.root.after(0, lambda: self._show_face_selector(item, state, previews, auto_start))
        except Exception as exc:
            self.root.after(0, lambda error=str(exc): self._face_detection_failed(error, auto_start))

    def _face_detection_failed(self, error, auto_start=False):
        if auto_start:
            self._face_analysis_queue.clear()
            self._auto_start_after_face_analysis = False
        self._face_detection_busy = False
        self.choose_faces_button.configure(state="normal")
        self.enhance_button.configure(state="normal")
        self._set_status("error")
        messagebox.showerror(self.t("Face Recovery"), error)

    def _show_face_selector(self, item, state, previews, auto_start=False):
        if not auto_start:
            self._face_detection_busy = False
            self.choose_faces_button.configure(state="normal")
            self.enhance_button.configure(state="normal")
            self._set_status("selected")
        item["face_data"] = state
        if not previews:
            item["selected_faces"] = set()
            self._refresh_batch_rows()
            messagebox.showinfo(self.t("Face Recovery"), self.t("ไม่พบใบหน้าในภาพนี้"))
            if auto_start:
                self.root.after(100, self._analyze_next_auto_face)
            return
        old_selection = item.get("selected_faces")
        initial = set(range(len(previews))) if old_selection is None else set(old_selection) & set(range(len(previews)))
        top = tk.Toplevel(self.root)
        top.title(self.t("เลือกใบหน้าที่ต้องการกู้คืน"))
        top.geometry("720x540")
        top.transient(self.root)
        ttk.Label(top, text=f"{os.path.basename(item['path'])} — {self.t('เลือกใบหน้าที่ต้องการกู้คืน')}").pack(pady=10)
        canvas = tk.Canvas(top, highlightthickness=0)
        scrollbar = ttk.Scrollbar(top, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 10))
        grid = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=grid, anchor="nw")
        grid.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        variables = []
        for index, face in enumerate(previews):
            var = tk.BooleanVar(value=index in initial)
            variables.append(var)
            thumb = ImageTk.PhotoImage(ImageOps.contain(face, (150, 150)))
            block = ttk.Frame(grid, padding=8)
            block.grid(row=index // 3, column=index % 3, padx=10, pady=8)
            image_label = ttk.Label(block, image=thumb)
            image_label.image = thumb
            image_label.pack()
            ttk.Checkbutton(block, text=f"{self.t('ใบหน้า')} {index + 1}", variable=var).pack(pady=4)
        buttons = ttk.Frame(top)
        buttons.pack(fill="x", padx=12, pady=10)
        ttk.Button(buttons, text="เลือกทั้งหมด", command=lambda: [var.set(True) for var in variables]).pack(side="left", padx=4)
        ttk.Button(buttons, text="ยกเลิกทั้งหมด", command=lambda: [var.set(False) for var in variables]).pack(side="left", padx=4)

        def apply_selection():
            item["selected_faces"] = {index for index, var in enumerate(variables) if var.get()}
            self._on_setting_change()
            self._refresh_batch_rows()
            top.destroy()
            if auto_start:
                self.root.after(100, self._analyze_next_auto_face)

        def close_selection():
            # Treat the window close button as saving the current choices. This
            # lets users reopen the selector without losing their face selection.
            item["selected_faces"] = {index for index, var in enumerate(variables) if var.get()}
            self._on_setting_change()
            self._refresh_batch_rows()
            top.destroy()
            if auto_start:
                self.root.after(100, self._analyze_next_auto_face)

        def cancel_selection():
            if auto_start:
                item["selected_faces"] = set()
                self._refresh_batch_rows()
            top.destroy()
            if auto_start:
                self.root.after(100, self._analyze_next_auto_face)

        ttk.Button(buttons, text="ยกเลิก", command=cancel_selection).pack(side="right", padx=4)
        ttk.Button(buttons, text="นำไปใช้", command=apply_selection).pack(side="right", padx=4)
        top.protocol("WM_DELETE_WINDOW", close_selection)
        top.grab_set()

    def _analyze_next_auto_face(self):
        if self._face_analysis_queue:
            item = self._face_analysis_queue.pop(0)
            device_name = getattr(self, "_face_device_by_item", {}).get(item["normalized"], self._face_analysis_device)
            analyzed = len(self._face_analysis_total) - len(self._face_analysis_queue)
            self.status_var.set(f"{self.t('กำลังตรวจหาใบหน้า…')} {analyzed} / {len(self._face_analysis_total)}")
            threading.Thread(target=self._detect_faces_worker, args=(item, device_name, True), daemon=True).start()
            return
        should_start = self._auto_start_after_face_analysis
        self._auto_start_after_face_analysis = False
        self._face_detection_busy = False
        self.choose_faces_button.configure(state="normal")
        self.enhance_button.configure(state="normal")
        self._set_status("selected")
        if should_start:
            self.root.after(100, self.start_enhance)

    def _start_auto_face_analysis(self, items, device_name):
        self._face_analysis_total = list(items)
        self._face_analysis_queue = list(items)
        self._face_analysis_device = device_name
        self._auto_start_after_face_analysis = True
        self._face_detection_busy = True
        self.choose_faces_button.configure(state="disabled")
        self.enhance_button.configure(state="disabled")
        self._analyze_next_auto_face()

    def _restore_selected_faces(self, item, output_path, device_name):
        selected = sorted(item.get("selected_faces", set()))
        if not selected:
            return False
        import cv2
        import numpy as np
        from basicsr.utils import img2tensor, tensor2img
        from torchvision.transforms.functional import normalize

        backend = self._load_face_backend(device_name)
        helper = backend["helper"]
        state = item["face_data"]
        helper.clean_all()
        helper.read_image(state["input_img"].copy())
        helper.cropped_faces = [state["crops"][index].copy() for index in selected]
        helper.all_landmarks_5 = [state["landmarks"][index].copy() for index in selected]
        helper.affine_matrices = [state["affine"][index].copy() for index in selected]
        helper.get_inverse_affine()
        network, torch = backend["network"], backend["torch"]
        for crop in helper.cropped_faces:
            face_tensor = img2tensor(crop / 255., bgr2rgb=True, float32=True)
            normalize(face_tensor, (0.5, 0.5, 0.5), (0.5, 0.5, 0.5), inplace=True)
            face_tensor = face_tensor.unsqueeze(0).to(backend["device"])
            with torch.no_grad():
                restored = network(face_tensor, return_rgb=False, weight=0.5)[0]
            restored_face = tensor2img(restored.squeeze(0), rgb2bgr=True, min_max=(-1, 1)).astype(np.uint8)
            helper.add_restored_face(restored_face)
        result_bgr = helper.paste_faces_to_input_image()
        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        Image.fromarray(result_rgb).save(output_path)
        return True

    def _preview_panel(self, parent, title, column):
        panel = ttk.LabelFrame(parent, text=title, style="Section.TLabelframe")
        panel.grid(row=0, column=column, sticky="nsew", padx=5)
        parent.columnconfigure(column, weight=1)
        parent.rowconfigure(0, weight=1)
        canvas = tk.Canvas(panel, background="#292929", highlightthickness=0, cursor="hand2")
        canvas.pack(fill="both", expand=True, padx=8, pady=8)
        if column == 0:
            self.before_image = canvas
            key = "before"
        else:
            self.after_image = canvas
            key = "after"
        canvas.bind("<Configure>", lambda _event: self._render_previews())
        canvas.bind("<ButtonPress-1>", lambda event, k=key: self._pan_start(event, k))
        canvas.bind("<B1-Motion>", lambda event, k=key: self._pan_move(event, k))
        canvas.bind("<MouseWheel>", self._wheel_zoom)
        canvas.bind("<Button-4>", lambda event: self._zoom_by(1.15, event))
        canvas.bind("<Button-5>", lambda event: self._zoom_by(1 / 1.15, event))
        return panel

    def _render_previews(self):
        self._clamp_pan()
        for key, canvas in (("before", getattr(self, "before_image", None)), ("after", getattr(self, "after_image", None))):
            image = self._preview_pils.get(key)
            if canvas is None:
                continue
            if image is None:
                canvas.delete("preview")
                self._preview_photos[key] = None
                continue
            cw, ch = max(canvas.winfo_width(), 2), max(canvas.winfo_height(), 2)
            factor = min(cw / image.width, ch / image.height) * self.zoom
            left = image.width / 2 - (cw / 2 + self.pan_x * cw) / factor
            top = image.height / 2 - (ch / 2 + self.pan_y * ch) / factor
            box = (max(0, int(left)), max(0, int(top)), min(image.width, int(left + cw / factor) + 1), min(image.height, int(top + ch / factor) + 1))
            if box[2] <= box[0] or box[3] <= box[1]:
                canvas.delete("preview")
                continue
            visible = image.crop(box)
            size = (max(1, min(cw, int(visible.width * factor))), max(1, min(ch, int(visible.height * factor))))
            photo = ImageTk.PhotoImage(visible.resize(size, Image.Resampling.LANCZOS))
            self._preview_photos[key] = photo
            canvas.delete("preview")
            x = cw / 2 + self.pan_x * cw - image.width * factor / 2 + box[0] * factor
            y = ch / 2 + self.pan_y * ch - image.height * factor / 2 + box[1] * factor
            canvas.create_image(x, y, image=photo, anchor="nw", tags="preview")
        if hasattr(self, "zoom_label"):
            self.zoom_label.configure(text=f"{round(self.zoom * 100)}%")

    def _clamp_pan(self):
        limits_x, limits_y = [], []
        for key, canvas in (("before", getattr(self, "before_image", None)), ("after", getattr(self, "after_image", None))):
            image = self._preview_pils.get(key)
            if canvas is None or image is None:
                continue
            cw, ch = max(canvas.winfo_width(), 2), max(canvas.winfo_height(), 2)
            fit = min(cw / image.width, ch / image.height)
            limits_x.append(max(0.0, image.width * fit * self.zoom - cw) / (2 * cw))
            limits_y.append(max(0.0, image.height * fit * self.zoom - ch) / (2 * ch))
        if limits_x:
            limit = min(limits_x)
            self.pan_x = min(limit, max(-limit, self.pan_x))
        if limits_y:
            limit = min(limits_y)
            self.pan_y = min(limit, max(-limit, self.pan_y))

    def _zoom_by(self, factor, _event=None):
        self.zoom = min(8.0, max(0.25, self.zoom * factor))
        self._render_previews()
        if self.auto_preview_var.get():
            self._schedule_ai_preview()

    def _wheel_zoom(self, event):
        self._zoom_by(1.15 if event.delta > 0 else 1 / 1.15, event)

    def _fit_previews(self):
        self.zoom, self.pan_x, self.pan_y = 1.0, 0.0, 0.0
        self._render_previews()

    def _pan_start(self, event, key):
        self._pan_origin = (event.x, event.y, key, self.pan_x, self.pan_y)

    def _pan_move(self, event, key):
        if not hasattr(self, "_pan_origin"):
            return
        x0, y0, _origin_key, px, py = self._pan_origin
        canvas = self.before_image if key == "before" else self.after_image
        self.pan_x = px + (event.x - x0) / max(1, canvas.winfo_width())
        self.pan_y = py + (event.y - y0) / max(1, canvas.winfo_height())
        self._render_previews()
        if self.auto_preview_var.get():
            self._schedule_ai_preview()

    def _dpi(self, config=None):
        try:
            value = int((config or {}).get("dpi", self.dpi_var.get()))
            return value if value > 0 else 300
        except (TypeError, ValueError):
            return 300

    def _dimension_changed(self, changed):
        if self._updating or self._loading_job_settings:
            return
        self._recalculate()

    def _unit_changed(self, _event=None):
        if not self.input_file:
            return
        self._set_dimensions_from_source()

    def _dpi_selected(self, _event=None):
        if self.dpi_var.get() == self.t("Custom"):
            value = simpledialog.askinteger(self.t("Custom DPI"), self.t("ระบุ DPI ที่ต้องการ:"), parent=self.root, minvalue=1, maxvalue=2400)
            if value is None:
                self.dpi_var.set("300")
            else:
                self.dpi_var.set(str(value))
        self._recalculate()

    def _set_dimensions_from_source(self):
        with Image.open(self.input_file) as image:
            self._ratio = image.width / image.height
            if self.unit_var.get() == "px":
                width, height = image.size
            else:
                factor = UNITS_TO_INCH[self.unit_var.get()] * self._dpi()
                width, height = image.width / factor, image.height / factor
        self._updating = True
        self.width_var.set(f"{width:.4f}".rstrip("0").rstrip("."))
        self.height_var.set(f"{height:.4f}".rstrip("0").rstrip("."))
        self._updating = False
        self._recalculate()

    def _recalculate(self, _event=None):
        try:
            config = self._read_job_config()
            if self.output_mode_var.get() == "upscale":
                if not self.selected_item:
                    self.pixel_info.configure(text=self.t("เลือกภาพเพื่อดูขนาดส่งออก"))
                    self._refresh_batch_rows()
                    return
                factor = UPSCALE_STEPS[self.scale_var.get()]
                pixels = tuple(max(1, dimension * factor) for dimension in self.selected_item["size"])
                dpi = self._dpi()
                unit = self.unit_var.get()
                if unit == "px":
                    physical = (pixels[0] / dpi * 2.54, pixels[1] / dpi * 2.54)
                    physical_text = f"  •  {physical[0]:,.2f} × {physical[1]:,.2f} cm"
                else:
                    factor_per_inch = UNITS_TO_INCH[unit]
                    physical = (pixels[0] / (dpi * factor_per_inch), pixels[1] / (dpi * factor_per_inch))
                    physical_text = f"  •  {physical[0]:,.2f} × {physical[1]:,.2f} {unit}"
                self.pixel_info.configure(text=f"{pixels[0]:,} × {pixels[1]:,} px{physical_text}  •  {dpi} DPI")
            else:
                width, height = float(self.width_var.get()), float(self.height_var.get())
                if width <= 0 or height <= 0:
                    raise ValueError
                if self.unit_var.get() == "px":
                    pixels = round(width), round(height)
                else:
                    factor = UNITS_TO_INCH[self.unit_var.get()] * self._dpi()
                    pixels = round(width * factor), round(height * factor)
                self.pixel_info.configure(text=f"{pixels[0]:,} × {pixels[1]:,} px  •  DPI {self._dpi()}")
        except (ValueError, KeyError):
            self.pixel_info.configure(text=self.t("กรอก Width และ Height เป็นค่าบวก"))
        self._refresh_batch_rows()
        if hasattr(self, "auto_preview_var") and self.auto_preview_var.get():
            self._schedule_ai_preview()

    def _update_output_mode(self):
        print_enabled = self.output_mode_var.get() == "print"
        for widget, active_state in self.print_controls:
            widget.configure(state=active_state if print_enabled else "disabled")
        self.scale_box.configure(state="disabled" if print_enabled else "readonly")
        self.resize_mode_box.configure(state="readonly" if print_enabled else "disabled")
        self._recalculate()

    def select_image(self):
        title = self.t("เลือกภาพต้นฉบับ (เลือกได้หลายไฟล์)")
        paths = filedialog.askopenfilenames(title=title, filetypes=[(self.t("Image Files"), "*.jpg *.jpeg *.png *.bmp *.tif *.tiff *.webp"), (self.t("All Files"), "*.*")])
        if not paths:
            return
        self._ingest_paths(paths)

    def _ingest_paths(self, paths):
        initialize_size = not self.batch_items and not self._restored_dimensions
        added = []
        for path in paths:
            if not os.path.isfile(path):
                continue
            try:
                item = self._add_batch_item(path)
                if item:
                    added.append(item)
            except Exception as exc:
                messagebox.showerror(self.t("เปิดภาพไม่สำเร็จ"), f"{os.path.basename(path)}\n{exc}")
        if added:
            self._show_main_page()
            self._show_item(added[0], initialize_size=initialize_size)
        elif self.batch_items:
            self._show_item(self.batch_items[0])
        self._refresh_batch_rows()
        if added:
            self._schedule_save_settings()

    def start_enhance(self):
        if self._face_detection_busy:
            return
        selected_items = [item for item in self.batch_items if item["checked"].get()]
        if not selected_items:
            messagebox.showwarning("ARM AI", self.t("ต้องเลือกอย่างน้อยหนึ่งไฟล์"))
            return
        self._save_current_job_settings()
        jobs = []
        missing_face_data = []
        try:
            for item in selected_items:
                config = self._default_job_config(item.get("config"))
                if item is self.selected_item:
                    config = self._read_job_config()
                    item["config"] = config
                target_size = self._output_size_for(item, config)
                if max(target_size) > 30000:
                    messagebox.showerror(self.t("ขนาดใหญ่เกินไป"), self.t("ขนาดด้านใดด้านหนึ่งเกิน 30,000 px กรุณาลดขนาดหรือ DPI"))
                    return
                engine_device = self._engine_device(config["device"])
                if config["output_mode"] == "upscale":
                    scale = UPSCALE_STEPS[config["scale"]]
                elif config.get("resize_mode") == "ai_expand":
                    work_w, work_h = self._ai_canvas_dimensions(item["size"], target_size)
                    scale = self._model_scale_for_dimensions(work_w, work_h, target_size)
                else:
                    scale = self._model_scale_for(item, target_size)
                face_enabled = bool(config["face_recovery"])
                face_device = self._effective_torch_device(config["device"]) if face_enabled else "cpu"
                resize_mode = config.get("resize_mode", "preserve") if config.get("output_mode") == "print" else "preserve"
                jobs.append((item, target_size, scale, self._dpi(config), face_enabled, face_device, engine_device, resize_mode))
                if face_enabled and item.get("face_data") is None:
                    missing_face_data.append(item)
        except (ValueError, KeyError, RuntimeError) as exc:
            messagebox.showwarning(self.t("ขนาดไม่ถูกต้อง"), f"{self.t('กรุณากรอก Width และ Height ให้ถูกต้อง')}\n{exc}")
            return
        if missing_face_data:
            self._face_device_by_item = {job[0]["normalized"]: job[5] for job in jobs}
            self._start_auto_face_analysis(missing_face_data, None)
            return
        self._cancel_all_event.clear()
        self._active_items = {job[0]["normalized"] for job in jobs}
        self._is_processing = True
        for item in selected_items:
            item["cancel_event"].clear()
            self._set_item_progress(item, 0)
            item["stop_button"].configure(state="normal", text=self.t("หยุด"))
        self.enhance_button.configure(state="disabled")
        self.choose_faces_button.configure(state="disabled")
        self.stop_all_button.configure(state="normal", text=self.t("หยุดทั้งหมด"))
        self._set_status("working")
        threading.Thread(target=self._enhance_worker, args=(jobs,), daemon=True).start()

    def _output_size_for(self, item, config=None):
        config = config or (self._read_job_config() if item is self.selected_item else item.get("config", {}))
        if config.get("output_mode", "print") == "upscale":
            factor = UPSCALE_STEPS[config.get("scale", "4x")]
            return item["size"][0] * factor, item["size"][1] * factor
        return self._target_box_size(config)

    @staticmethod
    def _model_scale_for(item, target_size):
        return ArmAIApp._model_scale_for_dimensions(item["size"][0], item["size"][1], target_size)

    @staticmethod
    def _model_scale_for_dimensions(width, height, target_size):
        required = max(target_size[0] / width, target_size[1] / height)
        return 2 if required <= 2 else (4 if required <= 4 else 8)

    @staticmethod
    def _ai_canvas_dimensions(source_size, target_size):
        source_w, source_h = source_size
        target_ratio = target_size[0] / target_size[1]
        source_ratio = source_w / source_h
        if target_ratio > source_ratio:
            canvas_w, canvas_h = max(source_w, round(source_h * target_ratio)), source_h
        else:
            canvas_w, canvas_h = source_w, max(source_h, round(source_w / target_ratio))
        shrink = min(1.0, 2048 / max(canvas_w, canvas_h))
        return max(1, round(canvas_w * shrink)), max(1, round(canvas_h * shrink))

    def _enhance_worker(self, jobs):
        completed, failures, cancelled = [], [], []
        try:
            engines = {}
            for index, (item, target_size, scale, dpi, face_enabled, face_device, device, resize_mode) in enumerate(jobs, start=1):
                if device not in engines:
                    engines[device] = self.engine_manager.create_engine(device)
                engine = engines[device]
                source = item["path"]
                base = os.path.splitext(os.path.basename(source))[0]
                output_file = os.path.join(os.path.dirname(source), f"{base}_ARM_AI_{scale}x.png")
                if self._is_cancelled(item):
                    cancelled.append(os.path.basename(source))
                    self.root.after(0, lambda i=item: self._mark_item_cancelled(i))
                    continue
                self.root.after(0, lambda i=index, n=len(jobs): self.status_var.set(f"{self.t('กำลังประมวลผลไฟล์')} {i}/{n}…"))
                self._post_item_progress(item, 8)
                temporary_files = []
                try:
                    import tempfile
                    fd, final_temp = tempfile.mkstemp(prefix=f"{base}_ARM_AI_{scale}x_final_", suffix=".png", dir=os.path.dirname(source))
                    os.close(fd)
                    os.remove(final_temp)
                    temporary_files.append(final_temp)
                    source_for_engine = source
                    if face_enabled and item.get("selected_faces"):
                        import tempfile
                        fd, face_path = tempfile.mkstemp(prefix=f"{base}_face_recovery_", suffix=".png", dir=os.path.dirname(source))
                        os.close(fd)
                        os.remove(face_path)
                        temporary_files.append(face_path)
                        self._post_item_progress(item, 16)
                        self._restore_selected_faces(item, face_path, face_device)
                        if self._is_cancelled(item):
                            raise InterruptedError("Processing stopped by user")
                        source_for_engine = face_path
                        self._post_item_progress(item, 28)
                    if resize_mode == "ai_expand":
                        import tempfile
                        fd, expanded_path = tempfile.mkstemp(prefix=f"{base}_ARM_AI_expand_", suffix=".png", dir=os.path.dirname(source))
                        os.close(fd)
                        os.remove(expanded_path)
                        temporary_files.append(expanded_path)
                        self.root.after(0, lambda: self._set_status("expanding"))
                        self._post_item_progress(item, 30)
                        self._outpaint_source(source_for_engine, expanded_path, target_size,
                                              cancel_check=lambda i=item: self._is_cancelled(i))
                        source_for_engine = expanded_path
                        self._post_item_progress(item, 34)
                    if scale == 8:
                        import tempfile
                        fd, temp_file = tempfile.mkstemp(prefix=f"{base}_ARM_AI_8x_stage_", suffix=".png", dir=os.path.dirname(source))
                        os.close(fd)
                        os.remove(temp_file)
                        temporary_files.append(temp_file)
                        first_pass_start = 34 if face_enabled else 14
                        first_pass_end = 50
                        self._post_item_progress(item, first_pass_start)
                        engine.enhance(source_for_engine, temp_file, scale=4,
                                       progress_callback=self._tile_progress_callback(item, first_pass_start, first_pass_end),
                                       cancel_check=lambda i=item: self._is_cancelled(i))
                        self._post_item_progress(item, first_pass_end)
                        engine.enhance(temp_file, final_temp, scale=2,
                                       progress_callback=self._tile_progress_callback(item, 50, 82),
                                       cancel_check=lambda i=item: self._is_cancelled(i))
                    else:
                        pass_start = 34 if face_enabled else 14
                        self._post_item_progress(item, pass_start)
                        engine.enhance(source_for_engine, final_temp, scale=scale,
                                       progress_callback=self._tile_progress_callback(item, pass_start, 82),
                                       cancel_check=lambda i=item: self._is_cancelled(i))
                    self._post_item_progress(item, 82)
                    if self._is_cancelled(item):
                        raise InterruptedError("Processing stopped by user")
                    with Image.open(final_temp) as image:
                        output = image.convert("RGB")
                        if output.size != target_size:
                            self._post_item_progress(item, 91)
                            if resize_mode == "preserve":
                                output = ImageOps.contain(output, target_size, method=Image.Resampling.LANCZOS)
                                canvas = Image.new("RGB", target_size, "white")
                                canvas.paste(output, ((target_size[0] - output.width) // 2,
                                                      (target_size[1] - output.height) // 2))
                                output = canvas
                            else:
                                output = output.resize(target_size, Image.Resampling.LANCZOS)
                        if self._is_cancelled(item):
                            raise InterruptedError("Processing stopped by user")
                        output.save(final_temp, format="PNG", dpi=(dpi, dpi))
                        actual_size = output.size
                    if self._is_cancelled(item):
                        raise InterruptedError("Processing stopped by user")
                    os.replace(final_temp, output_file)
                    completed.append((item, output_file, actual_size))
                    self._post_item_progress(item, 100)
                    self.root.after(0, lambda i=item, p=output_file, d=dpi: self._mark_item_complete(i, p, d))
                except InterruptedError:
                    cancelled.append(os.path.basename(source))
                    self.root.after(0, lambda i=item: self._mark_item_cancelled(i))
                except Exception as exc:
                    failures.append((os.path.basename(source), str(exc)))
                    self.root.after(0, lambda i=item: self._mark_item_failed(i))
                finally:
                    for temp_file in temporary_files:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
            self.root.after(0, lambda: self._finish_batch(completed, failures, cancelled))
        except Exception as exc:
            for item, *_rest in jobs:
                self.root.after(0, lambda i=item: self._mark_item_failed(i))
            self.root.after(0, lambda error=str(exc): self._finish_error(error))

    def _outpaint_source(self, source_path, output_path, target_size, cancel_check=lambda: False):
        """Expand the source canvas to the requested aspect ratio with LaMa inpainting."""
        with Image.open(source_path) as image:
            source = ImageOps.exif_transpose(image).convert("RGB")
        canvas_w, canvas_h = self._ai_canvas_dimensions(source.size, target_size)
        # LaMa's full-resolution inference can exhaust memory on large photos.
        # Its model is resolution robust; let Real-ESRGAN upscale this preview-sized canvas afterward.
        if canvas_w < source.width or canvas_h < source.height:
            shrink = min(canvas_w / source.width, canvas_h / source.height)
            source = source.resize((max(1, round(source.width * shrink)), max(1, round(source.height * shrink))), Image.Resampling.LANCZOS)
            canvas_w = max(canvas_w, source.width)
            canvas_h = max(canvas_h, source.height)
        left, top = (canvas_w - source.width) // 2, (canvas_h - source.height) // 2
        canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
        canvas.paste(source, (left, top))
        mask = Image.new("L", (canvas_w, canvas_h), 255)
        mask.paste(0, (left, top, left + source.width, top + source.height))
        if cancel_check():
            raise InterruptedError("Processing stopped by user")
        bundled_model = application_resource_root() / "models" / "big-lama.pt"
        if bundled_model.is_file():
            os.environ["LAMA_MODEL"] = str(bundled_model)
        from simple_lama_inpainting import SimpleLama
        filled = SimpleLama()(canvas, mask).convert("RGB").crop((0, 0, canvas_w, canvas_h))
        # Keep the original subject pixels intact; AI output is used only for the new margins.
        filled.paste(source, (left, top))
        filled.save(output_path, format="PNG")

    def _mark_item_complete(self, item, output_file, dpi):
        item["output_path"] = output_file
        item["output_dpi"] = dpi
        self._refresh_batch_rows()

    def _finish_batch(self, completed, failures, cancelled=None):
        cancelled = cancelled or []
        self.enhance_button.configure(state="normal")
        self.choose_faces_button.configure(state="normal")
        self.stop_all_button.configure(state="disabled", text=self.t("หยุดทั้งหมด"))
        self._is_processing = False
        self._active_items.clear()
        for item in self.batch_items:
            item["stop_button"].configure(state="disabled", text=self.t("หยุด"))
        if completed:
            completed_items = [entry[0] for entry in completed]
            item_to_show = self.selected_item if self.selected_item in completed_items else completed_items[0]
            self._show_item(item_to_show)
        self._set_status("error" if failures else ("cancelled" if cancelled else "done"))
        summary = f"{self.t('ไฟล์ที่เลือกเสร็จแล้ว')}: {len(completed)}"
        if cancelled:
            summary += f"\n{self.t('ยกเลิกแล้ว')}: {len(cancelled)}"
        if failures:
            summary += f"\n{self.t('เกิดข้อผิดพลาด')}: {len(failures)}"
        if failures:
            summary += "\n\n" + "\n".join(f"{name}: {error}" for name, error in failures[:5])
        messagebox.showinfo("ARM AI", summary)

    def _finish_error(self, error):
        self.enhance_button.configure(state="normal")
        self.choose_faces_button.configure(state="normal")
        self.stop_all_button.configure(state="disabled", text=self.t("หยุดทั้งหมด"))
        self._is_processing = False
        self._active_items.clear()
        for item in self.batch_items:
            item["stop_button"].configure(state="disabled", text=self.t("หยุด"))
        self._set_status("error")
        messagebox.showerror(self.t("ARM AI ERROR"), error)


def _saved_startup_language():
    settings_path = Path(os.environ.get("APPDATA", str(Path.home()))) / "ArmAI" / "ImageEnhancer" / "settings.json"
    try:
        saved = json.loads(settings_path.read_text(encoding="utf-8"))
        code = saved.get("language") if isinstance(saved, dict) else None
        return code if code in LANGUAGE_CHOICES else "th"
    except (OSError, json.JSONDecodeError):
        return "th"


def main():
    root = tk.Tk()
    language = _saved_startup_language()
    translate = lambda text: text if language == "th" else TRANSLATIONS.get(language, EN).get(text, EN.get(text, text))
    root.title(f"ARM AI Image Enhancer — {APP_VERSION}")
    width, height = 500, 260
    x = max(0, (root.winfo_screenwidth() - width) // 2)
    y = max(0, (root.winfo_screenheight() - height) // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.resizable(False, False)
    root.configure(bg="#EEF5FB")

    splash = tk.Frame(root, bg="#EEF5FB", padx=24, pady=18)
    splash.pack(fill="both", expand=True)
    logo_path = application_resource_root() / "assets" / "app_logo.png"
    splash_logo = None
    if logo_path.exists():
        try:
            with Image.open(logo_path) as source:
                image = source.convert("RGBA")
                image.thumbnail((210, 68), Image.Resampling.LANCZOS)
            splash_logo = ImageTk.PhotoImage(image)
            logo_label = tk.Label(splash, image=splash_logo, bg="#EEF5FB", bd=0)
            logo_label.image = splash_logo
            logo_label.pack(pady=(0, 5))
        except (OSError, ValueError):
            pass
    tk.Label(splash, text="ARM AI IMAGE ENHANCER", bg="#EEF5FB", fg="#17324D",
             font=("Tahoma", 15, "bold")).pack(pady=(0, 12))
    loading_var = tk.StringVar(value=translate("กำลังโหลดส่วนประกอบโปรแกรม…"))
    loading_label = tk.Label(splash, textvariable=loading_var, bg="#EEF5FB", fg="#36546A",
                              font=("Tahoma", 10))
    loading_label.pack(fill="x", pady=(0, 9))
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("Startup.Horizontal.TProgressbar", troughcolor="#DCE7F3", background="#2596F3",
                    bordercolor="#B6C9DC", lightcolor="#2596F3", darkcolor="#2596F3")
    progress = ttk.Progressbar(splash, mode="indeterminate", length=420,
                               style="Startup.Horizontal.TProgressbar")
    progress.pack(fill="x", pady=(0, 3))
    progress.start(12)

    startup_messages = [
        ("กำลังโหลดส่วนประกอบโปรแกรม…", 1000),
        ("กำลังตรวจสอบอุปกรณ์…", 1000),
        ("กำลังเตรียมหน้าต่างโปรแกรม…", 1000),
        ("กำลังโหลดโมดูล AI…", 3000),
    ]
    stage = {"index": 0, "after": None, "final": False, "visible": True,
             "ready": False, "engine_manager": None, "error": None}

    def blink_final_status():
        if not stage["final"] or stage["ready"] or stage["error"] is not None:
            return
        stage["visible"] = not stage["visible"]
        loading_var.set(translate("กำลังเปิดโปรแกรม…") if stage["visible"] else "")
        stage["after"] = root.after(1000, blink_final_status)

    def begin_final_status():
        stage["final"] = True
        stage["visible"] = True
        loading_var.set(translate("กำลังเปิดโปรแกรม…"))
        stage["after"] = root.after(1000, blink_final_status)
        maybe_finish_startup()

    def advance_startup_status():
        if stage["index"] >= len(startup_messages):
            begin_final_status()
            return
        message, delay = startup_messages[stage["index"]]
        loading_var.set(translate(message))
        stage["index"] += 1
        stage["after"] = root.after(delay, advance_startup_status)

    def finish_startup(engine_manager=None, error=None):
        if stage["after"] is not None:
            try:
                root.after_cancel(stage["after"])
            except tk.TclError:
                pass
        progress.stop()
        if error is not None:
            loading_var.set(translate("เกิดข้อผิดพลาด"))
            messagebox.showerror("ARM AI ERROR", str(error), parent=root)
            root.destroy()
            return
        for child in root.winfo_children():
            child.destroy()
        ArmAIApp(root, engine_manager=engine_manager)

    def maybe_finish_startup():
        if stage["error"] is not None:
            finish_startup(error=stage["error"])
        elif stage["ready"] and stage["final"]:
            finish_startup(engine_manager=stage["engine_manager"])

    def load_engine():
        try:
            from app.engine.engine_manager import EngineManager
            engine_manager = EngineManager()
            stage["engine_manager"] = engine_manager
            stage["ready"] = True
            root.after(0, maybe_finish_startup)
        except Exception as exc:
            try:
                stage["error"] = exc
                root.after(0, maybe_finish_startup)
            except tk.TclError:
                pass

    advance_startup_status()
    threading.Thread(target=load_engine, name="arm-ai-startup", daemon=True).start()
    root.mainloop()


if __name__ == "__main__":
    main()
