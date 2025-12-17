;; Test case for variable collision between macro and main scope
;; This test aims to understand how SBCL isolates macro variables

(defmacro test-collision (var-name value)
  `(let ((,var-name ,value)
         (internal-var "macro-internal"))
     (format t "Inside macro: ~A = ~A~%" ',var-name ,var-name)
     (format t "Internal var: ~A~%" internal-var)
     ,var-name))

;; Main function with same variable names
(defun main-function ()
  (let ((x "main-x")
        (internal-var "main-internal"))
    (format t "Before macro: x = ~A~%" x)
    (format t "Before macro: internal-var = ~A~%" internal-var)
    
    ;; Call macro with same variable name
    (let ((result (test-collision x "macro-x")))
      (format t "After macro: x = ~A~%" x)
      (format t "After macro: internal-var = ~A~%" internal-var)
      (format t "Macro result: ~A~%" result))))

;; Test with edge cases
(defmacro collision-edge-case (var)
  `(let ((var ,var)  ; Same name as parameter
         (var2 "shadow-test"))
     (format t "Shadowed var: ~A~%" var)
     var))

(defun test-shadowing ()
  (let ((var "original")
        (var2 "original2"))
    (format t "Original var: ~A~%" var)
    (collision-edge-case "new-value")
    (format t "After macro var: ~A~%" var)))

;; Execute tests
(main-function)
(test-shadowing)
