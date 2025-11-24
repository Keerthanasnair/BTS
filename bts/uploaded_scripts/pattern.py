
num = float(input('Enter number of rows to print: '))
# for i in range(1,num+1):
#     for j in range(i):
#         print('*',end='')
#     print()
# for i in range(num,0,-1):
#     for j in range(i):
#         print('*',end='')
#     print()
for i in range(1,6):
    for j in range(i):
        print(j+1,chr(65+j),end=' ')
    print()

# rows = 1
# while rows <= num:
#     columns = 1
#     while columns <= rows:
#         print('*',end='')
#         columns += 1
#     print()
#     rows += 1

# def pattern(n):
#     for i in range(n,0,-1):
#         for j in range(i):
#             print('*',end='')
#         print()
    
# pattern(num)
