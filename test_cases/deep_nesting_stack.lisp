;; Deep nesting test to stress macro expansion
(defmacro deep-nest (n)
  (if (zerop n)
      'done
      `(let ((x ,n)
             (depth-marker ,(format nil "depth-~A" n)))
         (format t "Depth ~A: x=~A~%" ,n x)
         (deep-nest ,(1- n)))))

;; Execute deep nesting
(deep-nest 50)
