# mowkow
머꼬: 한글 LISP

## 실행 방법
Python 3.x 설치 후 다음 명령을 수행합니다.
```
python _main.py
```

종료하려면 그냥 엔터를 입력하면 됩니다.

## 테스트 입력

다음 입력을 수행해 보세요.

```
>  (+ 10 20)
30
>  (그대로 10)
10
>  (그대로 (+ 10 20))
30
>  (그대로 '(+ 10 20))
(+ 10 20)
>  (절댓값 (- 20))
오류: <내장함수 '-'>: 인수 개수 오류입니다.
>  (절댓값 (- 0 20))
20
>  (머 '(1 2 3))
1
>  (꼬 '(1 2 3))
(2 3)
>  (잠시 ((이 2) (삼 3)) (+ 이 삼))
5
>  (정의 (계승 수) (만약 (= 수 0) 1 (* 수 (계승 (- 수 1)))))
>  (계승 4)
24
>  (정의 계승 (람다 (수) (만약 (= 수 0) 1 (* 수 (계승 (- 수 1))))))
>  (계승 5)
120
>  (잠시 ((인수 5) (계승 (람다 (수) (만약 (= 수 0) 1 (* 수 (계승 (- 수 1))))))) (계승 인수))
120
```
