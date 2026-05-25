# SBCL IDA Analysis Script
# Script לניתוח אוטומטי של SBCL ב-IDA Pro

import idc
import idaapi
import idautils

def find_lexical_scoping_functions():
    """
    מחפש פונקציות הקשורות ל-lexical scoping ב-SBCL
    """
    print("=== SBCL Lexical Scoping Analysis ===")
    
    # רשימת פונקציות לחיפוש
    target_functions = [
        # Binding functions
        "bind_variable", "make_binding", "lexical_binding", "dynamic_binding",
        "special_binding", "bind_special", "proclaim_special",
        
        # Symbol functions  
        "intern_symbol", "find_symbol", "symbol_value", "set_symbol_value",
        "symbol_function", "symbol_plist",
        
        # Proclaim functions
        "proclaim", "declaim", "proclamation",
        
        # Macro functions
        "macroexpand", "expand_macro", "macro_function", "defmacro",
        
        # Environment functions
        "lexenv", "environment", "augment_environment"
    ]
    
    found_functions = []
    
    print("Searching for critical functions...")
    for func_name in target_functions:
        # חיפוש לפי שם מדויק
        addr = idc.get_name_ea_simple(func_name)
        if addr != idc.BADADDR:
            found_functions.append((func_name, addr))
            print(f"  [FOUND] {func_name} at 0x{addr:X}")
            continue
            
        # חיפוש חלקי (substring)
        for func_ea in idautils.Functions():
            current_name = idc.get_func_name(func_ea)
            if func_name.lower() in current_name.lower():
                found_functions.append((current_name, func_ea))
                print(f"  [PARTIAL] {current_name} at 0x{func_ea:X} (matches {func_name})")
    
    print(f"\nFound {len(found_functions)} relevant functions")
    return found_functions

def analyze_symbol_structure():
    """
    מנסה לזהות את מבנה הsymbol ב-SBCL
    """
    print("\n=== Symbol Structure Analysis ===")
    
    # חיפוש אחר structures שנראים כמו symbols
    structures = []
    
    # חיפוש strings שמכילים "symbol"
    for string_ea in idautils.Strings():
        string_val = str(string_ea)
        if "symbol" in string_val.lower():
            print(f"  String reference: {string_val} at 0x{string_ea.ea:X}")
            
            # חיפוש references לstring הזה
            for ref in idautils.DataRefsTo(string_ea.ea):
                func_name = idc.get_func_name(ref)
                if func_name:
                    print(f"    Referenced in function: {func_name}")

def analyze_proclaim_implementation():
    """
    ניתוח מעמיק של מימוש proclaim
    """
    print("\n=== Proclaim Implementation Analysis ===")
    
    # חיפוש פונקציית proclaim
    proclaim_funcs = []
    for func_ea in idautils.Functions():
        func_name = idc.get_func_name(func_ea)
        if "proclaim" in func_name.lower():
            proclaim_funcs.append((func_name, func_ea))
    
    for func_name, func_ea in proclaim_funcs:
        print(f"\nAnalyzing {func_name} at 0x{func_ea:X}")
        
        # ניתוח הפונקציה
        func_end = idc.find_func_end(func_ea)
        current_addr = func_ea
        
        interesting_instructions = []
        
        while current_addr < func_end:
            disasm = idc.GetDisasm(current_addr)
            
            # חיפוש אחר פעולות מעניינות
            if any(keyword in disasm.lower() for keyword in 
                  ['mov', 'or', 'and', 'test', 'cmp', 'call']):
                
                # בדיקה אם זה קשור לflags או למבנה symbol
                if any(flag in disasm.lower() for flag in 
                      ['flag', 'special', 'type', 'binding']):
                    interesting_instructions.append((current_addr, disasm))
            
            current_addr = idc.next_head(current_addr)
        
        # הדפסת הוראות מעניינות
        if interesting_instructions:
            print("  Interesting instructions:")
            for addr, instr in interesting_instructions[:10]:  # הגבלה ל10 הראשונות
                print(f"    0x{addr:X}: {instr}")

def find_vulnerability_indicators():
    """
    חיפוש אחר אינדיקטורים לחולשות אבטחה
    """
    print("\n=== Vulnerability Indicators ===")
    
    vulnerability_patterns = [
        # תבניות שעלולות להצביע על חולשות
        ("Buffer operations", ["strcpy", "strcat", "sprintf", "memcpy"]),
        ("Memory management", ["malloc", "free", "realloc"]),
        ("Type checking", ["type_check", "validate", "assert"]),
        ("Binding operations", ["bind", "unbind", "special", "lexical"]),
        ("Error handling", ["error", "exception", "handler"])
    ]
    
    for category, patterns in vulnerability_patterns:
        print(f"\n{category}:")
        for pattern in patterns:
            # חיפוש functions שמכילות את הpattern
            for func_ea in idautils.Functions():
                func_name = idc.get_func_name(func_ea)
                if pattern in func_name.lower():
                    print(f"  {func_name} at 0x{func_ea:X}")

def generate_analysis_report():
    """
    יצירת דוח ניתוח מפורט
    """
    print("\n" + "="*50)
    print("SBCL LEXICAL SCOPING VULNERABILITY ANALYSIS")
    print("="*50)
    
    # הרצת כל הניתוחים
    functions = find_lexical_scoping_functions()
    analyze_symbol_structure()
    analyze_proclaim_implementation()
    find_vulnerability_indicators()
    
    print("\n=== Research Next Steps ===")
    print("1. Set breakpoints on proclaim-related functions")
    print("2. Analyze symbol flag modification code") 
    print("3. Trace variable access path (lexical vs dynamic)")
    print("4. Look for validation gaps in binding type changes")
    print("5. Test edge cases with mixed binding types")
    
    print("\n=== Key Questions to Answer ===")
    print("- Where is the SPECIAL flag stored in symbol structure?")
    print("- How does proclaim modify this flag?") 
    print("- Is there validation when changing binding types?")
    print("- What happens to existing bindings when type changes?")
    
    return functions

# הרצת הניתוח
if __name__ == "__main__":
    generate_analysis_report()
