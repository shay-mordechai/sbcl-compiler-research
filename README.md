# Architectural Security Analysis: SBCL Compiler Trust Boundary
**Tracking:** CERT-IL Ref #11265 | MITRE CVE Request ID: 1977672
**Principle:** Trust but Verify

---

## 1. Executive Summary

This repository documents a security research investigation into the Steel Bank Common Lisp (SBCL) macro expansion phase, following the principle of responsible disclosure and differential verification.

**Initial Hypothesis:** Three semantic mechanisms appeared to bypass lexical scope isolation during macro expansion—Dynamic Binding Modification, Symbol Table Pollution, and Namespace Confusion. Coupled with suspicious upstream commits, this initially resembled a classic Zero-Day vulnerability accompanied by a Silent Patch.

**Differential Testing Verdict:** Applying a strict "Trust but Verify" methodology, all three Proofs-of-Concept were tested against a legacy baseline (SBCL 1.4.3) and a modern release (SBCL 2.5.9+). The PoCs produced **identical behavior on both versions**. 

**Conclusion:** The behaviors conform to the ANSI Common Lisp specification. Macros are implicitly trusted code permitted to execute `proclaim`, `intern`, and `shadow` at compile-time. As demonstrated by our differential analysis, the upstream patches addressed separate runtime stability and concurrency issues—not macro-level security sandboxing.

---

## 2. The Finding: When Lexical Scope Is Not a Security Boundary

The core discovery of this research is that Common Lisp provides **no security boundary** between project source code and macro code executing at compile-time. 

From the perspective of a developer coming from languages with a more conservative compilation model (e.g., Java, C#, Rust), this behavior can create a false sense of security regarding isolation boundaries during the Build phase. While the behavior is by design, it demonstrates how compile-time code execution creates an attack surface overlooked in traditional security models.

**Modern Threat Model: Compile-Time Supply Chain Poisoning**
In CI/CD environments, a developer importing a third-party library implicitly trusts every macro it defines to run with full compiler access. A poisoned macro can:
1. Influence the compilation environment to alter symbol behaviors.
2. Exfiltrate local compilation data (e.g., hardcoded API keys) during the build phase.
3. Leave absolutely no trace in the final compiled binary.

This vector is entirely invisible to standard runtime security tools (DAST/RASP), as the exploit concludes in the pipeline before deployment. 

---

## 3. Mechanisms & Proof of Concept (PoC)

The `trust_but_verify_poc` directory contains the evaluation artifacts demonstrating the three mechanisms:

1. **Dynamic Binding Modification:** Using `(proclaim '(special ,target))` inside a macro to alter the symbol's metadata globally, changing how the compiler resolves the symbol.
2. **Global Symbol Table Pollution:** Using `intern` to acquire a global pointer to a local variable's symbol object and mutating its Property List (`plist`).
3. **Cross-Package Namespace Confusion:** Using `make-package` and `shadow` to alter the Package Namespace in a way that contradicts intuitive scope assumptions during compile-time symbol resolution.

---

## 4. Documentation & Archive Search Methodology (Empirical Evidence)

To verify whether this risk boundary was previously analyzed or documented, an empirical audit was conducted across SBCL's official documentation and development mailing lists. The absence of documentation regarding macro-driven environment poisoning confirms a industry-wide "Failure to Warn."

### A. Official Manual Audit
Queries against the official SBCL manual verified that keywords linking macro execution to security boundaries or environmental poisoning are entirely absent:
```bash
curl -s "[https://www.sbcl.org/manual/](https://www.sbcl.org/manual/)" | grep -i "macro.*trust\|trust.*macro\|macro.*security\|compile.*time.*code"

```

*Verdict:* Zero matches found regarding macro security contexts or compilation poisoning threat boundaries.

### B. Developer Mailing List Archive Search (`sbcl-devel`)

A forensic search on the SourceForge public mail archives for the structural interactions between `proclaim` and lexical isolation boundaries yielded no prior security discussion:

```bash
curl "[https://sourceforge.net/p/sbcl/mailman/search/?q=proclaim+lexical+scope&mail_list=sbcl-devel](https://sourceforge.net/p/sbcl/mailman/search/?q=proclaim+lexical+scope&mail_list=sbcl-devel)"

```

*Results Breakdown:*

* Found standard design discussions regarding REPL behavior (e.g., *Top-level setf = REPL-lexical variables*).
* Found historic build failures related to flags (e.g., *Bug#273606: sbcl: (proclaim '(optimize (debug 3)))*).
* **Zero results** documented or analyzed macro expansion as an AppSec/Supply Chain threat vector.

---

## 5. Technical Analysis of Upstream Commits

While differential testing proved that upstream modifications did not alter macro-level scope behaviors, our forensic audit of the Git differentials (`evidence_artifacts`) explains what these hotfixes actually resolved:

### A. Thread-Safety & Mutation Restrictions (`src/compiler/x86-64/cell.lisp`)

Upstream commits aggressively locked down the virtual operations (`VOPs`) for global cell mutations (`dynbind`, `unbind`, and `%cas-symbol-global-value`). The hotfix wraps these global state modifications inside a `pseudo-atomic` block and forces an `emit-symbol-write-barrier`:

```lisp
(pseudo-atomic (:elide-if #+immobile-space
                          (not (symbol-set-barrier-p symbol value-ref))
                          #-immobile-space t)
  (emit-symbol-write-barrier vop symbol temp value-ref)
  (storew val symbol symbol-value-slot other-pointer-lowtag))

```

**Analysis:** This mechanism prevents asynchronous thread interrupts or concurrent garbage collection passes from corrupting global symbol metadata during execution. It ensures internal synchronization (correctness) rather than macro isolation.

### B. Thread-Local Storage Indirection (`src/compiler/x86-64/tls.lisp`)

The introduction of the `#+tls-load-indirect` architecture overhauled how dynamic variables resolve through fixed TLS offsets. Instead of direct mapping, the runtime now routes bindings through a map and catches invalid dereferences via a trap handler (`handle_tls_deref_trap` in `x86-64-arch.c`):

```assembly
(inst shr :dword scratch-reg 1)
(inst mov (ea -4 rbx-tn scratch-reg) symbol)

```

**Analysis:** This indirection stabilizes parallel runtime lookups across environments, removing thread-local memory collisions during severe state changes.

---

## 6. Disclosure Timeline

| Date | Event |
| --- | --- |
| Aug 4, 2025 | Initial report submitted to CERT-IL (#11265) |
| Dec 17, 2025 | Full technical report + PoCs submitted |
| Jan 13, 2026 | CVE Request initiated via MITRE (ID: 1977672) |
| Feb 9, 2026 | CERT-IL confirms coordination |
| Feb 25 – Mar 13, 2026 | Upstream commits: TLS indirection architecture |
| Apr 2, 2026 | Direct email to sbcl-bugs mailing list warning of compile-time scope anomalies |
| Apr 8–10, 2026 | Upstream commits: `dynbind` pseudo-atomic and CAS constraints |
| May 25, 2026 | Public disclosure after 90-day period |

---

## 7. Repository Structure

* `evidence_artifacts/`: Upstream patches analyzed during the code-correctness review.
* `trust_but_verify_poc/`: Verification scripts and evaluation logs.
* `vulnerable_baseline/`: Execution traces on legacy SBCL v1.4.3.
* `patched_version/`: Execution traces on modern SBCL releases.
