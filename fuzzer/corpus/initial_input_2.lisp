;; Defmacro with parameters
(defmacro test-with-params (name value)
  `(format t "~a = ~a~%" ,name ,value))
