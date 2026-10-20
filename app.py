import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from thefuzz import process

class IconRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("مُدقق ومسمي الأيقونات الذكي للعبة")
        self.root.geometry("700x550")
        
        # إطار اختيار المجلد
        folder_frame = tk.LabelFrame(root, text=" مجلد الأيقونات ", font=("Arial", 11, "bold"), padx=10, pady=10)
        folder_frame.pack(fill="x", padx=15, pady=10)

        self.folder_path = tk.StringVar()
        self.folder_entry = tk.Entry(folder_frame, textvariable=self.folder_path, font=("Arial", 10), width=50)
        self.folder_entry.pack(side="left", padx=5, expand=True, fill="x")

        browse_btn = tk.Button(folder_frame, text="استعراض...", font=("Arial", 10), command=self.browse_folder)
        browse_btn.pack(side="right", padx=5)

        # إطار قائمة الألعاب
        games_frame = tk.LabelFrame(root, text=" قائمة أسماء الألعاب (اكتب كل لعبة في سطر) ", font=("Arial", 11, "bold"), padx=10, pady=10)
        games_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.games_text = scrolledtext.ScrolledText(games_frame, font=("Arial", 10), height=10)
        self.games_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        default_games = "Alan Wake 2\nAssassin's Creed\nAssassin's Creed II\nBattlefield 3\nBattlefield 4\nCyberpunk 2077\nGod of War Ragnarok"
        self.games_text.insert(tk.END, default_games)

        # زر التنفيذ وسجل التنبيهات
        action_frame = tk.Frame(root, padx=10, pady=10)
        action_frame.pack(fill="x", padx=15)

        self.start_btn = tk.Button(action_frame, text="بدء إعادة التسمية الذكية", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", padx=10, pady=5, command=self.start_renaming)
        self.start_btn.pack(fill="x")

        # سجل العمليات (Log)
        log_frame = tk.LabelFrame(root, text=" سجل العمليات والنتائج ", font=("Arial", 10, "bold"), padx=10, pady=5)
        log_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.log_area = scrolledtext.ScrolledText(log_frame, font=("Courier New", 9), height=8, bg="#1e1e1e", fg="#00ff00")
        self.log_area.pack(fill="both", expand=True, padx=5, pady=5)

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path.set(path)

    def log_message(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def start_renaming(self):
        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("خطأ", "يرجى اختيار مجلد صحيح للأيقونات أولاً!")
            return

        raw_games = self.games_text.get("1.0", tk.END).split("\n")
        games_list = [g.strip() for g in raw_games if g.strip()]

        if not games_list:
            messagebox.showerror("خطأ", "قائمة الألعاب فارغة! يرجى إدخال أسماء الألعاب.")
            return

        self.log_area.delete("1.0", tk.END)
        self.log_message("--- بدأت عملية مطابقة وإعادة التسمية ---")

        valid_extensions = (".png", ".ico", ".jpg", ".jpeg")
        renamed_count = 0

        for filename in os.listdir(folder):
            if filename.lower().endswith(valid_extensions):
                name_without_ext, ext = os.path.splitext(filename)
                
                best_match, score = process.extractOne(name_without_ext, games_list)

                if score >= 60:
                    old_path = os.path.join(folder, filename)
                    new_filename = f"{best_match}{ext}"
                    new_path = os.path.join(folder, new_filename)

                    if old_path == new_path:
                        continue

                    if not os.path.exists(new_path):
                        try:
                            os.rename(old_path, new_path)
                            self.log_message(f"[تم] {filename} -> {new_filename} (توافق: {score}%)")
                            renamed_count += 1
                        except Exception as e:
                            self.log_message(f"[خطأ] تعذر تغيير {filename}: {e}")
                    else:
                        self.log_message(f"[تخطي] الملف موجود مسبقاً: {new_filename}")
                else:
                    self.log_message(f"[تجاهل] مطابقة ضعيفة لـ: {filename} (نسبة الشبه: {score}%)")

        self.log_message(f"--- تمت العملية بنجاح! تم تغيير اسم {renamed_count} أيقونة. ---")
        messagebox.showinfo("اكتملت العملية", f"تمت إعادة تسمية {renamed_count} أيقونة بنجاح!")

if __name__ == "__main__":
    root = tk.Tk()
    app = IconRenamerApp(root)
    root.mainloop()
