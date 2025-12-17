;; Collision attack test - attempt to hijack variables
(defmacro collision-attack (target-var)
  `(progn
     (format t "Before attack: attempting to access ~A~%" ',target-var)
     (let ((,target-var "HIJACKED!")
           (attack-marker "attack-successful"))
       (format t "Inside macro: ~A = ~A~%" ',target-var ,target-var)
       (format t "Attack marker: ~A~%" attack-marker)
       ,target-var)))

;; Test collision attack
(defun test-collision-attack ()
  (let ((secret-var "original-secret")
        (public-var "original-public"))
    (format t "Original secret: ~A~%" secret-var)
    (format t "Original public: ~A~%" public-var)
    
    ;; Attempt to hijack secret-var
    (let ((result (collision-attack secret-var)))
      (format t "After attack secret: ~A~%" secret-var)
      (format t "Attack result: ~A~%" result))
    
    ;; Attempt to hijack public-var  
    (let ((result2 (collision-attack public-var)))
      (format t "After attack public: ~A~%" public-var)
      (format t "Attack result2: ~A~%" result2))))

;; Advanced collision test with eval
(defmacro eval-injection-test (code)
  `(progn
     (format t "Evaluating injected code: ~A~%" ',code)
     (eval ',code)))

(defun test-eval-injection ()
  (let ((sensitive-data "TOP-SECRET"))
    (format t "Sensitive data: ~A~%" sensitive-data)
    (eval-injection-test (format t "Attempting to access: ~A~%" sensitive-data))))

;; Execute tests
(test-collision-attack)
(test-eval-injection)
