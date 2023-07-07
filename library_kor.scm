(정의 (그대로 x) 
  x)
(정의 (그대로2 x) 
  x)

(정의 (절댓값 x) 
  (만약 (< x 0) 
    (- 0 x) 
    x))

(정의 (foldl proc init list) 
  (만약 list 
    (foldl proc (proc init (좌 list)) (우 list)) 
    init))

(정의 (foldr proc init list) 
  (만약 list 
    (proc (좌 list) (foldr proc init (우 list))) 
    init))

(정의 (리스트 . items) 
  (foldr 짝 공 items))

(정의 (거꾸로 list) 
  (foldl (람다 (a x) (짝 x a)) 공 list))

(정의 (unary-map proc list) 
  (foldr (람다 (x rest) (짝 (proc x) rest)) 공 list))

(정의 (map proc . arg-lists) 
  (만약 (좌 arg-lists) 
    (짝 (적용 proc (unary-map 좌 arg-lists)) 
    (적용 map (짝 proc (unary-map 우 arg-lists)))) 공))

(정의 (접합 a b) 
  (foldr 짝 b a))

(정의 (caar x) (좌 (좌 x))) 
(정의 (cadr x) (좌 (우 x)))

(매크로 (특이인용 x) 
  (만약 (짝? x) 
    (만약 (같다? (좌 x) '비인용) 
      (cadr x) 
      (만약 (짝? (좌 x)) 
        (만약 (같다? (caar x) '비인용연결) 
          (리스트 '접합 (cadr (좌 x)) 
          (리스트 '특이인용 (우 x))) 
        (리스트 '짝 (리스트 '특이인용 (좌 x)) (리스트 '특이인용 (우 x)))) 
    (리스트 '짝 (리스트 '특이인용 (좌 x)) (리스트 '특이인용 (우 x))))) 
  (리스트 '인용 x)))

(매크로 (임시 defs . body) 
  `((람다 ,(map 좌 defs) ,@body) ,@(map cadr defs)))

; (매크로 (cond . clauses)
;   (정의 (cond-clauses->if lst)
;     (만약 (아톱? lst)
;           공
;           (임시 ((clause (좌 lst)))
;                 (만약 (또는 (같다? (좌 clause) 'else)
;                             (같다? (좌 clause) #참))
;                       (만약 (공? (우 clause))
;                             (좌 clause)
;                             (짝 '좌 (우 clause)))
;                       (만약 (공? (우 clause))
;                             ; test by itself
;                             (리스트 '또는
;                                     (좌 clause)
;                                     (cond-clauses->if (우 lst)))
;                             ; test => expression
;                             (만약 (같다? (cadr clause) '=>)
;                                   (if (1arg-lambda? (caddr clause))
;                           ; test => (lambda (x) ...)
;                           (let ((var (caadr (caddr clause))))
;                             `(let ((,var ,(car clause)))
;                                (if ,var ,(cons 'begin (cddr (caddr clause)))
;                                    ,(cond-clauses->if (cdr lst)))))
;                           ; test => proc
;                           (let ((b (gensym)))
;                             `(let ((,b ,(car clause)))
;                                (if ,b
;                                    (,(caddr clause) ,b)
;                                    ,(cond-clauses->if (cdr lst))))))
;                       (list 'if
;                             (car clause)
;                             (cons 'begin (cdr clause))
;                             (cond-clauses->if (cdr lst)))))))))
;   (cond-clauses->if clauses))
