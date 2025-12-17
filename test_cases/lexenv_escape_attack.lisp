;; Test 2: Lexical Environment Escape - Try to escape macro scope
(defmacro lexenv-escape-attack ()
  `(progn
     ;; Try to access the lexical environment directly
     (format t "Attempting lexical environment escape~%")
     ;; Method 1: Try to access implementation internals
     (handler-case
         (progn
           (format t "Current lexical environment: ~A~%" 
                   (sb-kernel:lexenv-vars sb-kernel:*lexenv*))
           "LEXENV_ACCESS_SUCCESS")
       (error (e) (format t "Lexenv access failed: ~A~%" e)))
     
     ;; Method 2: Try to manipulate stack frames
     (handler-case
         (progn
           (format t "Stack frame manipulation attempt~%")
           (sb-debug:backtrace 5)
           "STACK_ACCESS_SUCCESS")
       (error (e) (format t "Stack access failed: ~A~%" e)))))

;; Test execution
(defun test-lexenv-escape ()
  (let ((protected-var "SENSITIVE"))
    (format t "Protected variable: ~A~%" protected-var)
    (lexenv-escape-attack)
    (format t "Variable still protected: ~A~%" protected-var)))

(test-lexenv-escape)
