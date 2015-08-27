	section .data  		
a:	dd	3		
b:	dd	4		
	
	section .bss 		
c:	resd	1		

	section .text		
	global	 main		
main:				
		
addb:				
	mov	eax,[a]	 	
	add	eax,[b]		
	mov	[c],eax		

	mov     eax,0           
	ret			

