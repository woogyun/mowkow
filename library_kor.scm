(정의 (머리 x) (머 x))
;(정의 머 머리)
(정의 (꼬리 x) (꼬 x))
;(정의 꼬 꼬리)
(정의 (머머 x) (머 (머 x))) 
(정의 (꼬머 x) (머 (꼬 x)))

(정의 (그대로 x) 
  x)
(정의 (그대로2 x) 
  x)

(정의 (절댓값 x) 
  (만약 (< x 0) 
    (- 0 x) 
    x))

(정의 (머리돌기 proc init list) 
  (만약 list 
    (머리돌기 proc (proc init (머 list)) (꼬 list)) 
    init))

(정의 (꼬리돌기 proc init list) 
  (만약 list 
    (proc (머 list) (꼬리돌기 proc init (꼬 list))) 
    init))

(정의 (리스트 . items) 
  (꼬리돌기 짝 공 items))

(정의 (거꾸로 list) 
  (머리돌기 (람다 (a x) (짝 x a)) 공 list))

(정의 (한맵 proc list) 
  (꼬리돌기 (람다 (x rest) (짝 (proc x) rest)) 공 list))

(정의 (맵 proc . arg-lists) 
  (만약 (머 arg-lists) 
    (짝 (적용 proc (한맵 머 arg-lists)) 
    (적용 맵 (짝 proc (한맵 꼬 arg-lists)))) 공))

(정의 (접합 a b) 
  (foldr 짝 b a))

(매크로 (특이인용 x) 
  (만약 (짝? x) 
    (만약 (같다? (머 x) '비인용) 
      (꼬머 x) 
      (만약 (짝? (머 x)) 
        (만약 (같다? (caar x) '비인용연결) 
          (리스트 '접합 (cadr (머 x)) 
          (리스트 '특이인용 (꼬 x))) 
        (리스트 '짝 (리스트 '특이인용 (머 x)) (리스트 '특이인용 (꼬 x)))) 
    (리스트 '짝 (리스트 '특이인용 (머 x)) (리스트 '특이인용 (꼬 x))))) 
  (리스트 '인용 x)))

(매크로 (임시 defs . body) 
  `((람다 ,(맵 머 defs) ,@body) ,@(맵 꼬머 defs)))

; (매크로 (cond . clauses)
;   (정의 (cond-clauses->if lst)
;     (만약 (아톰? lst)
;           공
;           (임시 ((clause (머 lst)))
;                 (만약 (또는 (같다? (머 clause) 'else)
;                             (같다? (머 clause) #참))
;                       (만약 (공? (꼬 clause))
;                             (머 clause)
;                             (짝 '머 (꼬 clause)))
;                       (만약 (공? (꼬 clause))
;                             ; test by itself
;                             (리스트 '또는
;                                     (머 clause)
;                                     (cond-clauses->if (꼬 lst)))
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
