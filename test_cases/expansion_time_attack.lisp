;; Test 5: Macro Expansion Time Attack - Try to execute at expansion time
(defmacro expansion-time-attack (target-var)
  ;; This code runs at macro expansion time, not execution time
  (format t "EXPANSION TIME: Attempting to access ~A~%" target-var)
  
  ;; Try to evaluate the target variable at expansion time
  (handler-case
      (progn
        (format t "EXPANSION TIME: Variable value is ~A~%" 
                (eval target-var))
        `(format t "Expansion time access successful!~%"))
    (error (e) 
      (format t "EXPANSION TIME: Access failed: ~A~%" e)
      `(format t "Expansion time attack failed~%"))))

;; Test execution
(defun test-expansion-time ()
  (let ((confidential "CLASSIFIED"))
    (format t "Confidential data: ~A~%" confidential)
    (expansion-time-attack confidential)
    (format t "Data still confidential: ~A~%" confidential)))

(test-expansion-time)
