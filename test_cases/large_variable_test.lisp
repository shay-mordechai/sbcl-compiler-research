;; Large variable name test - potential buffer overflow
(defmacro large-var-test ()
  (let ((large-var-name (make-string 5000 #\a)))
    `(let ((,(intern large-var-name) "test-value"))
       (format t "Large variable created successfully~%")
       ,(intern large-var-name))))

;; Test with extremely large variable name
(defmacro extreme-var-test ()
  (let ((extreme-name (make-string 50000 #\x)))
    `(let ((,(intern extreme-name) "extreme-test"))
       "success")))

;; Execute tests
(large-var-test)
(extreme-var-test)
