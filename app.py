import os
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image
import google.generativeai as genai
from thefuzz import process

class IconRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("مُدقق ومسمي الأيقونات الذكي بـ Gemini AI")
        self.root.geometry("750x650")

        # إطار المفتاح المباشر لـ Gemini API
        api_frame = tk.LabelFrame(root, text=" مفتاح Google Gemini API ", font=("Arial", 10, "bold"), padx=10, pady=5)
        api_frame.pack(fill="x", padx=15, pady=5)

        self.api_key_var = tk.StringVar()
        self.api_entry = tk.Entry(api_frame, textvariable=self.api_key_var, font=("Arial", 10), show="*", width=50)
        self.api_entry.pack(side="left", padx=5, expand=True, fill="x")

        # إطار اختيار المجلد
        folder_frame = tk.LabelFrame(root, text=" مجلد الأيقونات ", font=("Arial", 10, "bold"), padx=10, pady=5)
        folder_frame.pack(fill="x", padx=15, pady=5)

        self.folder_path = tk.StringVar()
        self.folder_entry = tk.Entry(folder_frame, textvariable=self.folder_path, font=("Arial", 10), width=50)
        self.folder_entry.pack(side="left", padx=5, expand=True, fill="x")

        browse_btn = tk.Button(folder_frame, text="استعراض...", font=("Arial", 10), command=self.browse_folder)
        browse_btn.pack(side="right", padx=5)

        # أزرار التشغيل
        action_frame = tk.Frame(root, padx=10, pady=5)
        action_frame.pack(fill="x", padx=15)

        self.ai_btn = tk.Button(action_frame, text="🔍 التعرف والتسمية بالذكاء الاصطناعي (Gemini Vision)", font=("Arial", 11, "bold"), bg="#2196F3", fg="white", pady=6, command=self.start_ai_thread)
        self.ai_btn.pack(fill="x", pady=2)

        # سجل العمليات (Log)
        log_frame = tk.LabelFrame(root, text=" سجل العمليات والنتائج ", font=("Arial", 10, "bold"), padx=10, pady=5)
        log_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.log_area = scrolledtext.ScrolledText(log_frame, font=("Courier New", 9), bg="#1e1e1e", fg="#00ff00")
        self.log_area.pack(fill="both", expand=True, padx=5, pady=5)

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path.set(path)

    def log_message(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def clean_game_name(self, name):
        # تنظيف الاسم من أي رموز غير مسموحة في Windows
        cleaned = re.sub(r'[\\/*?:"<>|]', '', name)
        return cleaned.strip()

    def start_ai_thread(self):
        threading.Thread(target=self.process_with_ai, daemon=True).start()

    def process_with_ai(self):
        folder = self.folder_path.get()
        api_key = self.api_key_var.get().strip()

        if not api_key:
            messagebox.showerror("خطأ", "يرجى أدخال مفتاح Gemini API أولاً!")
            return

        if not folder or not os.path.isdir(folder):
            messagebox.showerror("خطأ", "يرجى اختيار مجلد صحيح للأيقونات!")
            return

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception as e:
            messagebox.showerror("خطأ في الاتصال", f"تعذر الاتصال بـ Gemini API: {e}")
            return

        self.log_area.delete("1.0", tk.END)
        self.log_message("--- بدأت عملية تحليل الأيقونات بالذكاء الاصطناعي ---")

        valid_extensions = (".png", ".jpg", ".jpeg", ".ico")
        renamed_count = 0

        for filename in os.listdir(folder):
            if filename.lower().endswith(valid_extensions):
                filepath = os.path.join(folder, filename)
                name_without_ext, ext = os.path.splitext(filename)

                try:
                    # فتح الصورة لتحليلها
                    img = Image.open(filepath)
                    prompt = "Identify the exact video game name represented in this icon. Return ONLY the official title of the video game, with no extra text or quotes."
                    
                    response = model.generate_content([prompt, img])
                    game_title = self.clean_game_name(response.text)

                    if game_title:
                        new_filename = f"{game_title}{ext}"
                        new_filepath = os.path.join(folder, new_filename)

                        if filepath != new_filepath and not os.path.exists(new_filepath):
                            os.rename(filepath, new_filepath)
                            self.log_message(f"[نجاح AI] {filename} -> {new_filename}")
                            renamed_count += 1
                        else:
                            self.log_message(f"[تم التعرف]: {game_title} (الملف مسمى مسبقاً)")
                    else:
                        self.log_message(f"[تعذر التعرف]: {filename}")

                except Exception as e:
                    self.log_message(f"[خطأ في المعالجة]: {filename} -> {e}")

        self.log_message(f"\n--- اكتملت العملية! تم التعرف وتسمية {renamed_count} أيقونة بالذكاء الاصطناعي. ---")
        messagebox.showinfo("اكتملت العملية", f"تمت إعادة تسمية {renamed_count} أيقونة بنجاح عبر Gemini AI!")

if __name__ == "__main__":
    root = tk.Tk()
    app = IconRenamerApp(root)
    root.mainloop()
