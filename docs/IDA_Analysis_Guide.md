# IDA Analysis Guide for SBCL x86

## Overview
This guide covers using IDA Pro to analyze SBCL crashes and vulnerabilities found through fuzzing.

## Setup

### 1. SBCL x86 Binary Location
After installation, the main binary is typically located at:
```
C:\Program Files (x86)\Steel Bank Common Lisp\sbcl.exe
```

### 2. IDA Pro Configuration
1. Open IDA Pro (32-bit version)
2. Load `sbcl.exe` binary
3. Let IDA perform initial analysis
4. Enable debugging symbols if available

## Analysis Workflow

### Phase 1: Binary Overview
1. **Entry Point Analysis**
   - Find `main()` function
   - Identify initialization routines
   - Map out basic program flow

2. **Function Identification**
   - Look for macro-related functions
   - Find evaluation loops
   - Identify memory allocation routines

### Phase 2: Crash Analysis
1. **Load Crash Dump**
   - Use crash address from fuzzer output
   - Set breakpoint at crash location
   - Examine stack trace

2. **Root Cause Analysis**
   - Trace back to input processing
   - Identify vulnerable function
   - Understand memory corruption

### Phase 3: Exploit Development
1. **Control Flow Analysis**
   - Determine if crash is exploitable
   - Find ROP gadgets if needed
   - Map out exploit strategy

2. **Payload Development**
   - Create reliable trigger
   - Develop exploitation technique
   - Test across different inputs

## Key Functions to Analyze

### 1. Macro Processing
- `macroexpand()` - Macro expansion engine
- `eval()` - Expression evaluation
- `read()` - Input parsing

### 2. Memory Management
- `malloc()` / `free()` equivalents
- Garbage collector functions
- Stack management

### 3. Symbol Resolution
- Symbol table operations
- Package system functions
- Namespace resolution

## Common Vulnerability Patterns

### 1. Buffer Overflows
```assembly
mov eax, [ebp+input_length]
mov ecx, [ebp+buffer_ptr]
rep movsb  ; No bounds checking!
```

### 2. Stack Overflows
```assembly
push ebp
mov ebp, esp
sub esp, 0x100  ; Fixed stack allocation
; Recursive call without depth check
```

### 3. Use-After-Free
```assembly
call free_symbol
; ... later ...
mov eax, [ebp+symbol_ptr]  ; Using freed pointer
```

## Debugging Techniques

### 1. Dynamic Analysis
```
# Set breakpoint at crash
bp 0x401234

# Run with crashing input
r --load crash_input.lisp

# Examine registers and stack
r  # Show registers
du esp  # Show stack
```

### 2. Memory Analysis
```
# Check heap corruption
!heap -p -a

# Examine memory around crash
db crash_address-0x20 crash_address+0x20
```

### 3. Call Stack Analysis
```
# Show call stack
k

# Trace function calls
t  # Single step
p  # Step over
```

## Common SBCL Internals

### 1. Object Representation
- **Immediate Objects**: Numbers, characters stored directly
- **Heap Objects**: Cons cells, symbols, strings on heap
- **Tagged Pointers**: Low bits indicate object type

### 2. Garbage Collection
- **Mark-and-Sweep**: Standard GC algorithm
- **Generational**: Young/old generations
- **Conservative**: Treats ambiguous pointers as valid

### 3. Macro System
- **Expansion Time**: Compile-time vs runtime
- **Environment**: Lexical scoping
- **Recursive Expansion**: Potential for infinite loops

## Red Flags to Look For

### 1. Unchecked Loops
```c
while (input_available()) {
    process_input();  // No depth limit!
}
```

### 2. Fixed-Size Buffers
```c
char buffer[256];
strcpy(buffer, user_input);  // No length check!
```

### 3. Recursive Functions
```c
void expand_macro(macro_t *m) {
    if (is_macro(m->expansion)) {
        expand_macro(m->expansion);  // No recursion limit!
    }
}
```

## Analysis Checklist

### Initial Analysis
- [ ] Map out main program flow
- [ ] Identify macro processing functions
- [ ] Find memory allocation routines
- [ ] Locate error handling code

### Crash Investigation
- [ ] Load crash dump in IDA
- [ ] Set breakpoint at crash address
- [ ] Trace back to input processing
- [ ] Identify root cause

### Exploit Development
- [ ] Determine exploitability
- [ ] Create reliable trigger
- [ ] Develop payload
- [ ] Test across different scenarios

## Tips and Tricks

### 1. Useful IDA Scripts
```python
# Find all function calls
for func in Functions():
    for ref in XrefsTo(func):
        print(f"Call to {GetFunctionName(func)} at {hex(ref.frm)}")
```

### 2. Memory Layout
- Use "View > Open subviews > Segments" to understand memory layout
- Check stack vs heap corruption
- Look for RWX sections

### 3. Dynamic Analysis
- Use IDA's built-in debugger
- Set conditional breakpoints
- Monitor memory changes

## Common Pitfalls

1. **Don't assume**: Always verify your assumptions with dynamic analysis
2. **Context matters**: Same crash can have different root causes
3. **ASLR/DEP**: Modern mitigations affect exploitation
4. **Compiler optimizations**: Release builds may behave differently

## Resources

### IDA Pro Documentation
- IDA Pro Book by Chris Eagle
- Hex-Rays documentation
- Community scripts and plugins

### SBCL Internals
- SBCL source code comments
- Common Lisp specifications
- Compiler implementation papers

### Assembly References
- Intel x86 instruction set
- Calling conventions
- Stack frame layout
