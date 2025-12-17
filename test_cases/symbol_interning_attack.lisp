;; Test 1: Symbol Interning Attack - Try to access parent scope symbols
(defmacro symbol-interning-attack (parent-var)
  `(progn
     ;; Try to intern the same symbol name and access parent value
     (let ((symbol-name (symbol-name ',parent-var)))
       (format t "Attempting to access parent symbol: ~A~%" symbol-name)
       ;; Try to access via symbol-value
       (handler-case
           (symbol-value (intern symbol-name))
         (error (e) (format t "Error accessing: ~A~%" e)))
       ;; Try to modify parent through symbol table
       (handler-case
           (setf (symbol-value (intern symbol-name)) "HIJACKED!")
         (error (e) (format t "Error setting: ~A~%" e))))))

;; Test execution
(defun test-symbol-interning ()
  (let ((secret-data "PROTECTED"))
    (format t "Before attack: secret-data = ~A~%" secret-data)
    (symbol-interning-attack secret-data)
    (format t "After attack: secret-data = ~A~%" secret-data)))

(test-symbol-interning)
