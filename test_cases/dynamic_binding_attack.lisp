;; Test 3: Dynamic Binding Hijack - Try to use dynamic variables
(defmacro dynamic-binding-attack (target-symbol value)
  `(progn
     ;; Try to create a dynamic binding that affects parent
     (format t "Attempting dynamic binding attack on ~A~%" ',target-symbol)
     
     ;; Method 1: Use proclaim to make variable special
     (handler-case
         (progn
           (proclaim '(special ,target-symbol))
           (setf ,target-symbol ,value)
           (format t "Dynamic binding successful!~%")
           "DYNAMIC_HIJACK_SUCCESS")
       (error (e) (format t "Dynamic binding failed: ~A~%" e)))
     
     ;; Method 2: Use defvar to override
     (handler-case
         (progn
           (eval '(defvar ,target-symbol ,value))
           (format t "Defvar override successful!~%")
           "DEFVAR_HIJACK_SUCCESS")
       (error (e) (format t "Defvar override failed: ~A~%" e)))))

;; Test execution
(defun test-dynamic-binding ()
  (let ((important-data "ORIGINAL"))
    (format t "Before attack: important-data = ~A~%" important-data)
    (dynamic-binding-attack important-data "COMPROMISED")
    (format t "After attack: important-data = ~A~%" important-data)))

(test-dynamic-binding)
