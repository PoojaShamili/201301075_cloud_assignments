	section .data  		
a:	dq	3		
b:	dq	4		

	section .bss 		
c:	resq	1		

	section .text		
	global	 main		
main:				
	push 	rbp	

addb:				
	mov	rax,[a]	 	
	add	rax,[b]		
	mov	[c],rax		

	mov     rax,0           
	pop	rbp
	ret			

