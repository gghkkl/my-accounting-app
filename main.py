import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import os
import sys

# === تحديد مسار قاعدة البيانات ===
# هذا الكود يخلي التطبيق يقرأ ويكتب ملف data.db في نفس المجلد اللي فيه الـ exe
if getattr(sys, 'frozen', False):
    # إذا كان التطبيق شغال كـ exe
    application_path = os.path.dirname(sys.executable)
else:
    # إذا كان شغال كـ سكربت بايثون عادي
    application_path = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(application_path, "data.db")

# إعدادات المظهر العام (داكن - أزرق) - نفس ما هي
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

class AccountingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # إعداد قاعدة البيانات أول ما يشتغل التطبيق
        self.init_db()

        # إعدادات النافذة الرئيسية
        self.title("المحاسب الذكي - Smart Accountant")
        self.geometry("900x600")
        
        # تقسيم الشاشة (شبكة)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === القائمة الجانبية (Sidebar) ===
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="المحاسب \nPRO", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # أزرار القائمة مع تأثيرات (Hover)
        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="لوحة التحكم", command=self.show_dashboard)
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_add = ctk.CTkButton(self.sidebar_frame, text="إضافة عملية", command=self.show_add_page)
        self.btn_add.grid(row=2, column=0, padx=20, pady=10)

        self.btn_exit = ctk.CTkButton(self.sidebar_frame, text="خروج", fg_color="#d63031", hover_color="#ff7675", command=self.destroy)
        self.btn_exit.grid(row=5, column=0, padx=20, pady=20)

        # === منطقة المحتوى الرئيسية ===
        self.main_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # سنقوم بإنشاء الصفحات لكن نخفيها ونظهر المطلوبة فقط
        self.create_dashboard_page()
        self.create_add_page()
        
        # البدء بصفحة التحكم
        self.show_dashboard()

        # متغيرات البيانات
        self.balance = 0.0
        
        # تحميل البيانات المحفوظة من الفلاش
        self.load_data()

    def init_db(self):
        """إنشاء قاعدة البيانات والجدول إذا ما كانت موجودة"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def load_data(self):
        """قراءة البيانات من الفلاش وتحديث الواجهة"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # جلب كل العمليات
        cursor.execute("SELECT description, amount, type FROM transactions ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()

        # حساب الرصيد
        self.balance = 0.0
        for desc, amount, type_ in rows:
            if type_ == "income":
                self.balance += amount
            else:
                self.balance -= amount

        # تحديث بطاقة الرصيد
        self.lbl_balance_amount.configure(text=f"${self.balance:,.2f}")
        
        # تحديث شريط الحالة
        progress_val = min(self.balance / 1000, 1.0) if self.balance > 0 else 0
        self.progress_bar.set(progress_val)

        # تحديث السجل
        self.textbox_history.configure(state="normal")
        self.textbox_history.delete("0.0", "end") # تفريغ السجل القديم
        
        if not rows:
            self.textbox_history.insert("0.0", "لا توجد عمليات بعد...\n")
        else:
            for desc, amount, type_ in rows:
                if type_ == "income":
                    log_text = f"[+] {amount} - {desc}\n"
                else:
                    log_text = f"[-] {amount} - {desc}\n"
                self.textbox_history.insert("end", log_text)
                
        self.textbox_history.configure(state="disabled")

    def create_dashboard_page(self):
        self.dashboard_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        # بطاقة الرصيد (بتصميم جذاب)
        self.balance_card = ctk.CTkFrame(self.dashboard_frame, height=150, corner_radius=15, fg_color="#0984e3")
        self.balance_card.pack(fill="x", pady=10)
        
        self.lbl_balance_title = ctk.CTkLabel(self.balance_card, text="الرصيد الحالي", font=("Arial", 16), text_color="white")
        self.lbl_balance_title.pack(pady=(15, 5))
        
        self.lbl_balance_amount = ctk.CTkLabel(self.balance_card, text="$0.00", font=("Arial", 40, "bold"), text_color="white")
        self.lbl_balance_amount.pack(pady=5)

        # شريط الحالة (أنيميشن بسيط للصحة المالية)
        self.lbl_health = ctk.CTkLabel(self.dashboard_frame, text="الحالة المالية:", font=("Arial", 14))
        self.lbl_health.pack(anchor="w", pady=(20, 5))
        
        self.progress_bar = ctk.CTkProgressBar(self.dashboard_frame, width=400, height=15)
        self.progress_bar.set(0.5) # القيمة الافتراضية
        self.progress_bar.pack(fill="x", pady=5)

        # سجل العمليات الحديثة
        self.lbl_history = ctk.CTkLabel(self.dashboard_frame, text="آخر العمليات المسجلة:", font=("Arial", 18, "bold"))
        self.lbl_history.pack(anchor="w", pady=(30, 10))
        
        self.textbox_history = ctk.CTkTextbox(self.dashboard_frame, height=200)
        self.textbox_history.pack(fill="x")
        self.textbox_history.insert("0.0", "لا توجد عمليات بعد...\n")
        self.textbox_history.configure(state="disabled") # منع الكتابة اليدوية

    def create_add_page(self):
        self.add_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        lbl_title = ctk.CTkLabel(self.add_frame, text="تسجيل عملية جديدة", font=("Arial", 24))
        lbl_title.pack(pady=20)

        self.entry_desc = ctk.CTkEntry(self.add_frame, placeholder_text="وصف العملية (مثلاً: راتب، تسوق)", width=300, height=40)
        self.entry_desc.pack(pady=10)

        self.entry_amount = ctk.CTkEntry(self.add_frame, placeholder_text="المبلغ (مثلاً: 500)", width=300, height=40)
        self.entry_amount.pack(pady=10)

        # أزرار نوع العملية
        self.transaction_type = ctk.StringVar(value="income")
        
        radio_income = ctk.CTkRadioButton(self.add_frame, text="دخول (إيراد)", variable=self.transaction_type, value="income", fg_color="#00b894")
        radio_income.pack(pady=5)
        
        radio_expense = ctk.CTkRadioButton(self.add_frame, text="خروج (مصروف)", variable=self.transaction_type, value="expense", fg_color="#d63031")
        radio_expense.pack(pady=5)

        btn_save = ctk.CTkButton(self.add_frame, text="حفظ العملية", width=200, height=50, command=self.save_transaction)
        btn_save.pack(pady=30)

    # دوال التنقل
    def show_dashboard(self):
        self.add_frame.pack_forget()
        self.dashboard_frame.pack(fill="both", expand=True)

    def show_add_page(self):
        self.dashboard_frame.pack_forget()
        self.add_frame.pack(fill="both", expand=True)

    # دوال المنطق (Logic)
    def save_transaction(self):
        desc = self.entry_desc.get()
        try:
            amount = float(self.entry_amount.get())
        except ValueError:
            messagebox.showerror("خطأ", "الرجاء إدخال مبلغ صحيح!")
            return

        if not desc:
            messagebox.showerror("خطأ", "الرجاء كتابة الوصف")
            return

        # نوع العملية
        type_ = self.transaction_type.get()

        # الحفظ في قاعدة البيانات
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (description, amount, type) VALUES (?, ?, ?)", (desc, amount, type_))
        conn.commit()
        conn.close()

        # تحديث الواجهة
        self.load_data() # نعيد تحميل البيانات عشان تتحدث كل شي

        # تنظيف الحقول
        self.entry_desc.delete(0, "end")
        self.entry_amount.delete(0, "end")
        
        messagebox.showinfo("تم", "تم تسجيل العملية بنجاح!")
        self.show_dashboard()

if __name__ == "__main__":
    app = AccountingApp()
    app.mainloop()