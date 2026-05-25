;; Test 6: Package System Attack - Try to hijack through packages
(defmacro package-hijack-attack (symbol-name)
  `(progn
     ;; Try to manipulate the package system to access variables
     (format t "Attempting package system hijack~%")
     
     ;; Method 1: Try to intern symbol in different package
     (handler-case
         (progn
           (let ((new-symbol (intern (string ,symbol-name) :cl-user)))
             (format t "Interned symbol in CL-USER: ~A~%" new-symbol)
             (setf (symbol-value new-symbol) "PACKAGE_HIJACKED")
             (format t "Package hijack successful!~%")
             new-symbol))
       (error (e) (format t "Package hijack failed: ~A~%" e)))
     
     ;; Method 2: Try to use find-symbol to locate parent variables
     (handler-case
         (progn
           (multiple-value-bind (symbol status)
               (find-symbol (string ,symbol-name))
             (when symbol
               (format t "Found symbol: ~A, status: ~A~%" symbol status)
               (format t "Symbol value: ~A~%" (symbol-value symbol))
               "FIND_SYMBOL_SUCCESS")))
       (error (e) (format t "Find-symbol failed: ~A~%" e)))))

;; Test execution  
(defun test-package-hijack ()
  (let ((private-data "PRIVATE"))
    (format t "Private data: ~A~%" private-data)
    (package-hijack-attack 'private-data)
    (format t "Data still private: ~A~%" private-data)))

(test-package-hijack)
