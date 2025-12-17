;; Nested macro test
(defmacro nested-test (x)
  `(let ((result ,x))
     (when result
       (print result))
     result))
