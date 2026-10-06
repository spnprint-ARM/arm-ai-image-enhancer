"""Offline browser for the credits and license texts shipped with the application."""
import json
import os
import sys
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox, ttk

LABELS = {
    "ช่วยเหลือ": ("Help", "帮助", "Aide"),
    "ใบอนุญาตและเครดิตบุคคลที่สาม": ("Third-party licenses and credits", "第三方许可证与致谢", "Licences et crédits des tiers"),
    "ค้นหา": ("Search", "搜索", "Rechercher"),
    "ชื่อ": ("Name", "名称", "Nom"),
    "เวอร์ชัน": ("Version", "版本", "Version"),
    "ใบอนุญาต": ("License", "许可证", "Licence"),
    "ผู้พัฒนา": ("Developers", "开发者", "Développeurs"),
    "ดูข้อความใบอนุญาต": ("View license text", "查看许可证文本", "Voir la licence"),
    "ดูไฟล์รวม": ("View all notices", "查看全部声明", "Voir toutes les notices"),
    "เปิดโฟลเดอร์ licenses": ("Open licenses folder", "打开许可证文件夹", "Ouvrir le dossier licenses"),
    "ปิด": ("Close", "关闭", "Fermer"),
    "อ่านข้อมูลใบอนุญาตไม่สำเร็จ": ("Could not read license information", "无法读取许可证信息", "Impossible de lire les licences"),
    "เปิดลิงก์ไม่สำเร็จ": ("Could not open the link", "无法打开链接", "Impossible d’ouvrir le lien"),
    "ไม่พบรายการ": ("No matching components", "没有匹配的组件", "Aucun composant correspondant"),
    "สิทธิ์ของโค้ดและไฟล์โมเดลแสดงแยกกัน โปรดอ่านรายละเอียดของแต่ละรายการ": (
        "Code and model terms are listed separately. Please read each component's details.",
        "代码与模型文件的许可条款分别列出，请阅读各项详情。",
        "Les conditions du code et des modèles sont séparées. Consultez les détails de chaque composant."),
}

def translate(text, language):
    if language == "th":
        return text
    values = LABELS.get(text)
    return values[{"en": 0, "zh": 1, "fr": 2}.get(language, 0)] if values else text

def notices_root():
    """Prefer files next to the installed EXE; support older internal data layouts."""
    if getattr(sys, "frozen", False):
        candidates = [Path(sys.executable).resolve().parent]
        if getattr(sys, "_MEIPASS", None):
            candidates.append(Path(sys._MEIPASS))
    else:
        candidates = [Path(__file__).resolve().parents[2]]
    return next((root for root in candidates if (root / "licenses" / "components.json").is_file()), candidates[0])

def license_path(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Invalid license file path")
    return path

def load_components(root):
    data = json.loads((root / "licenses" / "components.json").read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("components"), list):
        raise ValueError("Unsupported license information format")
    required = ("id", "name", "version", "license", "author", "source", "license_files")
    ids = set()
    for entry in data["components"]:
        if any(key not in entry for key in required) or entry["id"] in ids:
            raise ValueError("Invalid component entry")
        ids.add(entry["id"])
        if not entry["license_files"]:
            raise ValueError("No license text for component")
        for file in entry["license_files"]:
            license_path(root, file)
    return data["components"]

class ThirdPartyCredits(tk.Toplevel):
    def __init__(self, parent, language="th", resource_root=None):
        super().__init__(parent)
        self.language = language
        self.resource_root = Path(resource_root) if resource_root else notices_root()
        self.title(self.t("ใบอนุญาตและเครดิตบุคคลที่สาม"))
        self.transient(parent)
        width = min(1000, self.winfo_screenwidth() - 40)
        height = min(680, self.winfo_screenheight() - 80)
        self.geometry(f"{width}x{height}")
        self.minsize(min(700, width), min(480, height))
        try:
            self.components = load_components(self.resource_root)
        except (OSError, ValueError, TypeError, KeyError) as error:
            messagebox.showerror(self.t("อ่านข้อมูลใบอนุญาตไม่สำเร็จ"), str(error), parent=self)
            self.destroy()
            return
        self.by_id = {entry["id"]: entry for entry in self.components}
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        search_bar = ttk.Frame(self, padding=(16, 14, 16, 8))
        search_bar.grid(row=0, column=0, sticky="ew")
        search_bar.columnconfigure(1, weight=1)
        ttk.Label(search_bar, text=self.t("ค้นหา")).grid(row=0, column=0, padx=(0, 8))
        self.query = tk.StringVar()
        self.search_box = ttk.Entry(search_bar, textvariable=self.query)
        self.search_box.grid(row=0, column=1, sticky="ew")

        list_frame = ttk.Frame(self, padding=(16, 0, 16, 0))
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(list_frame, columns=("name", "version", "license"), show="headings", selectmode="browse")
        for key, label, size in (("name", "ชื่อ", 250), ("version", "เวอร์ชัน", 170), ("license", "ใบอนุญาต", 440)):
            self.tree.heading(key, text=self.t(label))
            self.tree.column(key, width=size, minwidth=120, stretch=key == "license")
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(list_frame, orient="horizontal", command=self.tree.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=scroll.set, xscrollcommand=horizontal.set)
        self.tree.bind("<<TreeviewSelect>>", self._selected)
        self.tree.bind("<Double-1>", lambda _event: self.view_license())
        self.tree.bind("<Return>", lambda _event: self.view_license())

        details = ttk.Frame(self, padding=(16, 10))
        details.grid(row=2, column=0, sticky="ew")
        details.columnconfigure(0, weight=1)
        self.name_var = tk.StringVar()
        self.author_var = tk.StringVar()
        ttk.Label(details, textvariable=self.name_var, font=("Tahoma", 12, "bold")).grid(row=0, column=0, sticky="w")
        author = ttk.Label(details, textvariable=self.author_var, wraplength=width-50)
        author.grid(row=1, column=0, sticky="w", pady=(4, 2))
        self.source = ttk.Label(details, foreground="#1769aa", cursor="hand2", takefocus=True, wraplength=width-50)
        self.source.grid(row=2, column=0, sticky="w")
        self.source.bind("<Button-1>", lambda _event: self.open_source())
        self.source.bind("<Return>", lambda _event: self.open_source())
        self.notes = tk.Text(details, height=4, wrap="word", relief="flat", font=("Tahoma", 10), takefocus=True)
        self.notes.grid(row=3, column=0, sticky="ew", pady=(5, 0))
        note_scroll = ttk.Scrollbar(details, orient="vertical", command=self.notes.yview)
        note_scroll.grid(row=3, column=1, sticky="ns", pady=(5, 0))
        self.notes.configure(yscrollcommand=note_scroll.set, state="disabled")
        details.bind("<Configure>", lambda event: (author.configure(wraplength=max(200,event.width-10)), self.source.configure(wraplength=max(200,event.width-10))))
        self.hint = ttk.Label(self, text=self.t("สิทธิ์ของโค้ดและไฟล์โมเดลแสดงแยกกัน โปรดอ่านรายละเอียดของแต่ละรายการ"), wraplength=width-40)
        self.hint.grid(row=3, column=0, sticky="w", padx=16)
        self.bind("<Configure>", lambda event: self.hint.configure(wraplength=max(200,event.width-32)) if event.widget is self else None)

        buttons = ttk.Frame(self, padding=16)
        buttons.grid(row=4, column=0, sticky="ew")
        self.view_button = ttk.Button(buttons, text=self.t("ดูข้อความใบอนุญาต"), command=self.view_license)
        self.view_button.pack(side="left")
        ttk.Button(buttons, text=self.t("ดูไฟล์รวม"), command=self.view_notices).pack(side="left", padx=8)
        ttk.Button(buttons, text=self.t("เปิดโฟลเดอร์ licenses"), command=self.open_folder).pack(side="left")
        ttk.Button(buttons, text=self.t("ปิด"), command=self.destroy).pack(side="right")
        self.bind("<Escape>", lambda _event: self.destroy())
        self.query.trace_add("write", self._filter)
        self._filter()
        self.search_box.focus_set()

    def t(self, text):
        return translate(text, self.language)

    def _filter(self, *_args):
        old = self.tree.selection()
        query = self.query.get().casefold().strip()
        self.tree.delete(*self.tree.get_children())
        for entry in self.components:
            if query and query not in " ".join(str(entry.get(key, "")) for key in ("name", "version", "license", "author", "source")).casefold():
                continue
            self.tree.insert("", "end", iid=entry["id"], values=(entry["name"], entry["version"], entry["license"]))
        rows = self.tree.get_children()
        if rows:
            selected = old[0] if old and old[0] in rows else rows[0]
            self.tree.selection_set(selected)
            self.tree.focus(selected)
        self._selected()

    def _selected(self, _event=None):
        selected = self.tree.selection()
        self.current = self.by_id.get(selected[0]) if selected else None
        self.view_button.configure(state="normal" if self.current else "disabled")
        self.name_var.set(f"{self.current['name']} — {self.current['version']}" if self.current else self.t("ไม่พบรายการ"))
        self.author_var.set(f"{self.t('ผู้พัฒนา')}: {self.current['author']}" if self.current else "")
        self.source.configure(text=self.current["source"] if self.current else "")
        self.notes.configure(state="normal")
        self.notes.delete("1.0", "end")
        if self.current:
            self.notes.insert("1.0", self.current.get("notes", ""))
        self.notes.configure(state="disabled")

    def _show_files(self, title, files):
        try:
            sections = [f"{file}\n{'=' * 72}\n{license_path(self.resource_root, file).read_text(encoding='utf-8', errors='replace')}" for file in files]
        except (OSError, ValueError) as error:
            messagebox.showerror(self.t("อ่านข้อมูลใบอนุญาตไม่สำเร็จ"), str(error), parent=self)
            return
        window = tk.Toplevel(self)
        window.title(title)
        window.transient(self)
        window.geometry(f"{min(900,self.winfo_screenwidth()-40)}x{min(650,self.winfo_screenheight()-80)}")
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        text = tk.Text(window, wrap="word", font=("Consolas", 10), padx=12, pady=12)
        text.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(window, orient="vertical", command=text.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        text.configure(yscrollcommand=scroll.set)
        text.insert("1.0", "\n\n".join(sections))
        text.configure(state="disabled")
        ttk.Button(window, text=self.t("ปิด"), command=window.destroy).grid(row=1, column=0, sticky="e", padx=12, pady=10)
        window.bind("<Escape>", lambda _event: window.destroy())
        text.focus_set()

    def view_license(self):
        if self.current:
            self._show_files(f"{self.current['name']} — {self.t('ใบอนุญาต')}", self.current["license_files"])

    def view_notices(self):
        self._show_files("THIRD_PARTY_NOTICES.txt", ["THIRD_PARTY_NOTICES.txt"])

    def open_source(self):
        if not self.current:
            return
        url = self.current["source"]
        if not url.startswith(("https://", "http://")):
            return
        try:
            if not webbrowser.open(url):
                raise OSError(url)
        except OSError as error:
            messagebox.showerror(self.t("เปิดลิงก์ไม่สำเร็จ"), str(error), parent=self)

    def open_folder(self):
        try:
            os.startfile(str(self.resource_root / "licenses"))
        except OSError as error:
            messagebox.showerror(self.t("อ่านข้อมูลใบอนุญาตไม่สำเร็จ"), str(error), parent=self)
