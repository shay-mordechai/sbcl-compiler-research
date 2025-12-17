# SBCL Lexical Scoping - נקודות מחקר קריטיות

## 🎯 השאלה המרכזית
**איך `proclaim` יכול לשנות lexical variable ל-dynamic באמצע execution?**

## 🔍 מה חיפשנו וגילינו

### מה שאנחנו יודעים עובד:
```lisp
;; החולשה שגילינו:
(let ((secret "PROTECTED"))
  (proclaim '(special secret))  ; ← זה משנה את הtypе
  (setf secret "COMPROMISED")   ; ← זה עוקף את הlexical binding
  secret)  ; → "COMPROMISED"
```

### מה שצריך להבין ב-IDA:

#### **1. Symbol Resolution Process**
```
User Code: (let ((secret "value")) ...)
     ↓
SBCL Compiler: Create lexical binding
     ↓  
Runtime: symbol_value(secret) → lexical או dynamic?
     ↓
proclaim: שינוי מlexical לdynamic באמצע!
```

#### **2. נקודות חיפוש ב-IDA:**

##### A. **proclaim Implementation**
```assembly
; חפש פונקציה שמטפלת ב-proclaim
; כנראה תראה משהו כמו:
proclaim_special:
    mov rax, [symbol_ptr]
    or  [rax + symbol_flags], SPECIAL_FLAG  ; ← פה הבעיה!
    ret
```

##### B. **Variable Access Functions**
```assembly
; איך SBCL מחליט איך לגשת למשתנה:
symbol_value:
    mov rax, [symbol_ptr]
    test [rax + flags], SPECIAL_FLAG
    jnz dynamic_access        ; אם special → dynamic
    jmp lexical_access        ; אחרת → lexical
```

##### C. **Binding Creation**
```assembly
; איך נוצר binding חדש:
create_binding:
    ; האם יש validation כאן?
    ; מה קורה אם הsymbol כבר special?
```

## 🕵️ איפה לחפש ב-IDA

### **שלב 1: מציאת Entry Points**
```
Functions לחפש (Ctrl+F):
- proclaim
- special
- symbol_value
- binding
- lexical
- dynamic
```

### **שלב 2: ניתוח Symbol Structure**
```c
// מבנה סמל ב-SBCL (השערה):
struct sbcl_symbol {
    uint64_t header;     // Type info
    char* name;          // Symbol name  
    uint64_t flags;      // SPECIAL_FLAG כאן?
    void* value;         // Global value
    void* function;      // Function binding
    void* package;       // Package info
};
```

### **שלב 3: מציאת החולשה**
**השאלות הקריטיות:**
1. **איפה הflag של SPECIAL נשמר?**
2. **מה קורה כש-proclaim משנה את הflag באמצע lexical binding?**
3. **האם יש validation שמונע את זה?**
4. **איך זה משפיע על variable resolution?**

## 🎯 התיאוריה שלנו על החולשה

### **מה שכנראה קורה:**
```
1. (let ((secret "PROTECTED")) → יוצר lexical binding
2. proclaim '(special secret)  → משנה global flag של הsymbol
3. setf secret "COMPROMISED"   → עכשיו משתמש בdynamic binding!
4. כשיוצאים מהlet → lexical binding לא מתאושש
```

### **למה זה בעיה:**
- **Lexical isolation נשבר** - החולשה שלנו
- **Type confusion** - משתנה שיכול להיות גם lexical וגם dynamic
- **Security bypass** - code יכול לשנות משתנים שאמורים להיות מוגנים

## 🛠️ כלי עזר למחקר

### **קובצי בדיקה מוכנים:**
```lisp
;; test_basic.lisp - בדיקה בסיסית
(let ((x "lexical"))
  (format t "Before proclaim: ~A~%" x)
  (proclaim '(special x))
  (format t "After proclaim: ~A~%" x))

;; test_advanced.lisp - בדיקה מתקדמת  
(defvar *global* "global")
(let ((*global* "lexical"))
  (format t "Lexical: ~A~%" *global*)
  (proclaim '(special *global*))
  (setf *global* "dynamic")
  (format t "Dynamic: ~A~%" *global*))
```

### **נקודות Breakpoint ב-IDA:**
1. **Entry לproclaim function**
2. **Symbol flag modification**  
3. **Variable access (symbol_value)**
4. **Binding creation/destruction**

## 🎓 מה נלמד מזה

### **Compiler Security:**
- איך compilers מטפלים בscoping
- מה קורה כשרונטיים משנים metadata
- איפה יכולות להיות חולשות בtype systems

### **Vulnerability Research:**
- זיהוי type confusion vulnerabilities
- ניתוח רונטיים של languages
- מציאת semantic security bugs

### **הערך המקצועי:**
- **ניסיון בreverse engineering של compilers**
- **הבנה מעמיקה של scoping mechanisms**
- **מחקר vulnerability מתקדם**

זה מחקר מתקדם שמעניק הבנה עמוקה של איך compilers עובדים ואיפה הם יכולים להישבר! 🚀
