import rx
from rx import operators as ops


rx.of(1,2,3,4,5,6,7,8,9,10).pipe(
    ops.filter(lambda i: (i+1)%2 == 0),
    ops.sum()
).subscribe(lambda x: print(f"Value is {x}"))