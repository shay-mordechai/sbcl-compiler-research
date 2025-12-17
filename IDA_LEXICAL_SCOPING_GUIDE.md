# מדריך IDA למחקר SBCL Lexical Scoping

## 🎯 מטרת המחקר
להבין כיצד SBCL מממש lexical scoping ברמת הקומפיילר, ומדוע macros יכולים לעקוף אותו.

## 📋 תכנית המחקר

### שלב 1: הכנת הסביבה
1. **פתח את SBCL ב-IDA Pro**
   ```
   File → Open → c:\Program Files (x86)\Steel Bank Common Lisp\sbcl.exe
   ```

2. **הגדרת symbols (אם יש)**
   - IDA ינסה לזהות symbols אוטומטיט
   - חפש functions עם שמות כמו: `bind`, `lexical`, `special`, `proclaim`

### שלב 2: זיהוי פונקציות קריטיות
חפש את הפונקציות הבאות (Ctrl+F):

#### A. פונקציות Binding:
```
bind_variable
make_binding  
lexical_binding
dynamic_binding
special_binding
```

#### B. פונקציות Symbol Management:
```
intern_symbol
find_symbol
symbol_value
set_symbol_value
proclaim_special
```

#### C. פונקציות Macro:
```
macroexpand
expand_macro
macro_function
defmacro
```

### שלב 3: ניתוח זרימת הקוד

#### מה לחפש:
1. **איך SBCL מחליט** בין lexical ל-dynamic binding
2. **איפה הוא שומר** מידע על special variables
3. **איך proclaim משפיע** על ההחלטה הזו
4. **איפה יש validation** (או חסר validation)

#### נקודות עניין:
```assembly
; חפש קוד שנראה כך:
cmp [variable_type], LEXICAL_TYPE
je lexical_path
jmp dynamic_path

; או בדיקות כמו:
test [special_flag], 1
jnz special_handling
```

### שלב 4: מציאת נקודת הפגיעות

#### השאלות שצריך לענות עליהן:
1. **היכן SBCL בודק** אם משתנה הוא special?
2. **האם יש validation** שמונע שינוי binding type באמצע?
3. **איך macros יכולים** להשפיע על ההחלטה הזו?
4. **איפה נמצא הקוד** שמטפל ב-proclaim?

### שלב 5: דוגמת ניתוח

#### קובץ בדיקה פשוט:
צור קובץ `test_lexical.lisp`:
```lisp
(let ((x "lexical"))
  (format t "Before: ~A~%" x)
  (proclaim '(special x))
  (setf x "dynamic") 
  (format t "After: ~A~%" x))
```

#### ב-IDA:
1. הרץ את הקובץ תחת debugger
2. שים breakpoints על פונקציות binding
3. עקוב אחרי השינוי מ-lexical ל-dynamic

## 🔍 נקודות מחקר ספציפיות

### A. Symbol Table Structure
```c
// חפש structures כמו:
struct symbol {
    char* name;
    int type;        // LEXICAL vs SPECIAL
    void* value;
    void* binding;   // רשימת bindings
};
```

### B. Binding Stack
```c
// איך SBCL מנהל stack של bindings:
struct binding_frame {
    symbol* sym;
    void* old_value;
    int binding_type;
    binding_frame* next;
};
```

### C. Proclaim Implementation
```assembly
; חפש את הקוד שמטפל ב:
; (proclaim '(special variable-name))
; 
; זה כנראה:
; 1. מוצא את הsymbol
; 2. משנה את הtype שלו
; 3. לא בודק אם הוא כבר bound!
```

## 🎯 מה לחפש כחולשות

### 1. **Race Conditions**
- האם יש בדיקות לפני שינוי binding type?
- מה קורה אם proclaim קורה תוך כדי lexical binding?

### 2. **Type Confusion** 
- איך SBCL מבדיל בין lexical ל-dynamic?
- האם יש validation של השינוי?

### 3. **Stack Corruption**
- מה קורה ל-binding stack כשמשנים type?
- האם יש memory leaks או corruption?

## 📝 תיעוד הממצאים

### תבנית לתיעוד:
```
Function: [שם הפונקציה]
Address: [כתובת]
Purpose: [מה הפונקציה עושה]
Vulnerability: [איך זה קשור לחולשה שלנו]
Assembly Code: [קוד assembly רלוונטי]
Notes: [הערות נוספות]
```

## 🚀 צעדים הבאים

1. **זהה את proclaim_special function**
2. **נתח את symbol table management**  
3. **מצא את נקודת החולשה המדויקת**
4. **בדוק אפשרויות exploitation נוספות**
5. **כתוב PoC מתקדם יותר**

זה יעניק לך הבנה מעמיקה של איך compilers מטפלים בscoping ואיפה יכולות להיות חולשות!
