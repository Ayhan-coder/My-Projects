# String constants section
        .section .rodata
bird_species_sparrow:   .string "Sparrow"
bird_species_warbler:   .string "Warbler"
bird_species_nightingale:   .string "Nightingale"
format_string_combine:   .string "%s-%s"
note_c:   .string "C"
note_t:   .string "T"
note_d:   .string "D"
space_char:   .string " "
error_unknown_species:   .string "Unknown species: %s\n"
format_generation:   .string "%s Gen %d:"
format_note:   .string " %s"
newline:   .string "\n"
cmd_exit:   .string "exit"
cmd_quit:   .string "quit"
###########################################################
.text

# Function: get_species
# Input: string pointer in %rdi
# Output: species code in %eax (0=Sparrow, 1=Warbler, 2=Nightingale, 3=Unknown)

.globl  get_species
get_species:
        pushq   %rbp
        movq    %rsp, %rbp
        subq    $16, %rsp
        movq    %rdi, -8(%rbp)            # Store input string pointer
        movq    -8(%rbp), %rax
        movl    $bird_species_sparrow, %esi
        movq    %rax, %rdi
        call    strcmp                     # Compare with "Sparrow"
        testl   %eax, %eax
        jne     .not_sparrow
        movl    $0, %eax                  # Return 0 for Sparrow
        jmp     .get_species_end
.not_sparrow:
        movq    -8(%rbp), %rax
        movl    $bird_species_warbler, %esi
        movq    %rax, %rdi
        call    strcmp                     # Compare with "Warbler"
        testl   %eax, %eax
        jne     .not_warbler
        movl    $1, %eax                   # Return 1 for Warbler
        jmp     .get_species_end
.not_warbler:
        movq    -8(%rbp), %rax
        movl    $bird_species_nightingale, %esi
        movq    %rax, %rdi
        call    strcmp                     # Compare with "Nightingale"
        testl   %eax, %eax
        jne     .not_nightingale
        movl    $2, %eax                   # Return 2 for Nightingale
        jmp     .get_species_end
.not_nightingale:
        movl    $3, %eax                   # Return 3 for unknown species
.get_species_end:
        leave
        ret
#######################################################
# Function: op_plus (addition operation)
# Input: %rdi = pointer to notes array, %esi = species code
# Performs species-specific addition operation on the notes

.globl  op_plus
op_plus:
        pushq   %rbp
        movq    %rsp, %rbp
        subq    $48, %rsp
        movq    %rdi, -40(%rbp)           # Store notes array pointer
        movl    %esi, -44(%rbp)           # Store species code
        
        # Check if we have at least 2 notes to operate on
        movq    -40(%rbp), %rax
        movl    1024(%rax), %eax          # Load note count
        cmpl    $1, %eax
        jle     .op_plus_insufficient_notes
        
        # Get pointers to last two notes
        movq    -40(%rbp), %rax
        movl    1024(%rax), %eax
        subl    $1, %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -40(%rbp), %rax
        addq    %rdx, %rax
        movq    %rax, -8(%rbp)            # Pointer to last note
        
        movq    -40(%rbp), %rax
        movl    1024(%rax), %eax
        subl    $2, %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -40(%rbp), %rax
        addq    %rdx, %rax
        movq    %rax, -16(%rbp)           # Pointer to second last note
        
        # Handle operation based on species
        cmpl    $2, -44(%rbp)             # Check species
        je      .op_plus_nightingale
        cmpl    $2, -44(%rbp)
        ja      .op_plus_default
        cmpl    $0, -44(%rbp)
        je      .op_plus_sparrow
        cmpl    $1, -44(%rbp)
        je      .op_plus_warbler
        jmp     .op_plus_default

.op_plus_sparrow:
        # Sparrow operation: combine last two notes with hyphen
        movq    -8(%rbp), %rcx            # Last note
        movq    -16(%rbp), %rdx           # Second last note
        leaq    -32(%rbp), %rax           # Temp buffer
        movq    %rcx, %r8
        movq    %rdx, %rcx
        movl    $format_string_combine, %edx
        movl    $16, %esi                 # Buffer size
        movq    %rax, %rdi
        movl    $0, %eax
        call    snprintf                  # Format combined string
        
        # Remove the two notes we combined
        movq    -40(%rbp), %rax
        movl    1024(%rax), %eax
        leal    -2(%eax), %edx
        movq    -40(%rbp), %rax
        movl    %edx, 1024(%rax)
        
        # Add the new combined note
        movq    -40(%rbp), %rax
        movl    1024(%rax), %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -40(%rbp), %rax
        addq    %rax, %rdx
        leaq    -32(%rbp), %rax
        movq    %rax, %rsi
        movq    %rdx, %rdi
        call    strcpy
        
        # Increment note count
        movq    -40(%rbp), %rax
        movl    1024(%rax), %eax
        leal    1(%eax), %edx
        movq    -40(%rbp), %rax
        movl    %edx, 1024(%rax)
        jmp     .op_plus_end

.op_plus_warbler:
        # Warbler operation: create "T-C" note
        leaq    -32(%rbp), %rax
        movl    $4402516, (%rax)          # "T-C" string
        
        # Remove two notes
        movq    -40(%rbp), %rax
        movl    1024(%rax), %eax
        leal    -2(%eax), %edx
        movq    -40(%rbp), %rax
        movl    %edx, 1024(%rax)
        
        # Add the new note
        movq    -40(%rbp), %rax
        movl    1024(%rax), %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -40(%rbp), %rax
        addq    %rax, %rdx
        leaq    -32(%rbp), %rax
        movq    %rax, %rsi
        movq    %rdx, %rdi
        call    strcpy
        
        # Increment note count
        movq    -40(%rbp), %rax
        movl    1024(%rax), %eax
        leal    1(%eax), %edx
        movq    -40(%rbp), %rax
        movl    %edx, 1024(%rax)
        jmp     .op_plus_end

.op_plus_nightingale:
        # Nightingale operation: duplicate last note if space allows
        movq    -40(%rbp), %rax
        movl    1024(%rax), %eax
        cmpl    $125, %eax
        jg      .op_plus_nightingale_end
        
        # Copy second last note to end
        movq    -40(%rbp), %rax
        movl    1024(%rax), %eax
        subl    $2, %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -40(%rbp), %rax
        addq    %rax, %rdx
        movq    -40(%rbp), %rax
        movl    1024(%rax), %ecx
        movslq  %ecx, %rax
        leaq    0(,%rax,8), %rcx
        movq    -40(%rbp), %rax
        addq    %rcx, %rax
        movq    %rdx, %rsi
        movq    %rax, %rdi
        call    strcpy
        
        # Copy last note to new position
        movq    -40(%rbp), %rax
        movl    1024(%rax), %eax
        subl    $1, %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -40(%rbp), %rax
        addq    %rax, %rdx
        movq    -40(%rbp), %rax
        movl    1024(%rax), %eax
        addl    $1, %eax
        cltq
        leaq    0(,%rax,8), %rcx
        movq    -40(%rbp), %rax
        addq    %rcx, %rax
        movq    %rdx, %rsi
        movq    %rax, %rdi
        call    strcpy
        
        # Update note count (+2)
        movq    -40(%rbp), %rax
        movl    1024(%rax), %eax
        leal    2(%eax), %edx
        movq    -40(%rbp), %rax
        movl    %edx, 1024(%rax)
        jmp     .op_plus_nightingale_end

.op_plus_insufficient_notes:
        nop
        jmp     .op_plus_end
.op_plus_default:
        nop
        jmp     .op_plus_end
.op_plus_nightingale_end:
        nop
.op_plus_end:
        leave
        ret

# Function: op_star (multiplication operation)
# Input: %rdi = pointer to notes array, %esi = species code
# Performs species-specific multiplication operation on the notes

.globl  op_star
op_star:
        pushq   %rbp
        movq    %rsp, %rbp
        subq    $32, %rsp
        movq    %rdi, -24(%rbp)           # Store notes array pointer
        movl    %esi, -28(%rbp)           # Store species code
        
        # Check if we have any notes
        movq    -24(%rbp), %rax
        movl    1024(%rax), %eax
        testl   %eax, %eax
        je      .op_star_empty_array
        
        # Handle operation based on species
        cmpl    $2, -28(%rbp)
        je      .op_star_nightingale
        cmpl    $2, -28(%rbp)
        ja      .op_star_default
        cmpl    $0, -28(%rbp)
        je      .op_star_sparrow
        cmpl    $1, -28(%rbp)
        je      .op_star_warbler
        jmp     .op_star_default

.op_star_sparrow:
        # Sparrow operation: duplicate last note if space allows
        movq    -24(%rbp), %rax
        movl    1024(%rax), %eax
        cmpl    $127, %eax
        jg      .op_star_sparrow_end
        
        # Copy last note to new position
        movq    -24(%rbp), %rax
        movl    1024(%rax), %eax
        subl    $1, %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -24(%rbp), %rax
        addq    %rax, %rdx
        movq    -24(%rbp), %rax
        movl    1024(%rax), %eax
        cltq
        leaq    0(,%rax,8), %rcx
        movq    -24(%rbp), %rax
        addq    %rcx, %rax
        movq    %rdx, %rsi
        movq    %rax, %rdi
        call    strcpy
        
        # Increment note count
        movq    -24(%rbp), %rax
        movl    1024(%rax), %eax
        leal    1(%eax), %edx
        movq    -24(%rbp), %rax
        movl    %edx, 1024(%rax)
        jmp     .op_star_sparrow_end

.op_star_warbler:
        # Warbler operation: duplicate last two notes if space allows
        movq    -24(%rbp), %rax
        movl    1024(%rax), %eax
        cmpl    $1, %eax
        jle     .op_star_warbler_end
        movq    -24(%rbp), %rax
        movl    1024(%rax), %eax
        cmpl    $125, %eax
        jg      .op_star_warbler_end
        
        # Copy second last note to end
        movq    -24(%rbp), %rax
        movl    1024(%rax), %eax
        subl    $2, %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -24(%rbp), %rax
        addq    %rax, %rdx
        movq    -24(%rbp), %rax
        movl    1024(%rax), %eax
        cltq
        leaq    0(,%rax,8), %rcx
        movq    -24(%rbp), %rax
        addq    %rcx, %rax
        movq    %rdx, %rsi
        movq    %rax, %rdi
        call    strcpy
        
        # Copy last note to new position
        movq    -24(%rbp), %rax
        movl    1024(%rax), %eax
        subl    $1, %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -24(%rbp), %rax
        addq    %rax, %rdx
        movq    -24(%rbp), %rax
        movl    1024(%rax), %eax
        addl    $1, %eax
        cltq
        leaq    0(,%rax,8), %rcx
        movq    -24(%rbp), %rax
        addq    %rcx, %rax
        movq    %rdx, %rsi
        movq    %rax, %rdi
        call    strcpy
        
        # Update note count (+2)
        movq    -24(%rbp), %rax
        movl    1024(%rax), %eax
        leal    2(%eax), %edx
        movq    -24(%rbp), %rax
        movl    %edx, 1024(%rax)
        jmp     .op_star_warbler_end

.op_star_nightingale:
        # Nightingale operation: duplicate all notes if space allows
        movq    -24(%rbp), %rax
        movl    1024(%rax), %eax
        addl    %eax, %eax
        cmpl    $127, %eax
        jg      .op_star_nightingale_end
        
        # Duplicate each note
        movq    -24(%rbp), %rax
        movl    1024(%rax), %eax
        movl    %eax, -8(%rbp)            # Original count
        movl    $0, -4(%rbp)              # Counter
        jmp     .op_star_nightingale_loop
.op_star_nightingale_loop_iter:
        # Copy note[i] to note[i+count]
        movl    -4(%rbp), %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -24(%rbp), %rax
        addq    %rax, %rdx
        movq    -24(%rbp), %rax
        movl    1024(%rax), %ecx
        movl    -4(%rbp), %eax
        addl    %ecx, %eax
        cltq
        leaq    0(,%rax,8), %rcx
        movq    -24(%rbp), %rax
        addq    %rcx, %rax
        movq    %rdx, %rsi
        movq    %rax, %rdi
        call    strcpy
        addl    $1, -4(%rbp)
.op_star_nightingale_loop:
        movl    -4(%rbp), %eax
        cmpl    -8(%rbp), %eax
        jl      .op_star_nightingale_loop_iter
        
        # Update note count (double)
        movq    -24(%rbp), %rax
        movl    1024(%rax), %eax
        leal    (%eax,%eax), %edx
        movq    -24(%rbp), %rax
        movl    %edx, 1024(%rax)
        jmp     .op_star_end

.op_star_empty_array:
        nop
        jmp     .op_star_end
.op_star_default:
        nop
        jmp     .op_star_end
.op_star_sparrow_end:
        nop
        jmp     .op_star_end
.op_star_warbler_end:
        nop
        jmp     .op_star_end
.op_star_nightingale_end:
        nop
.op_star_end:
        leave
        ret

# Function: softness
# Input: %rdi = note string pointer
# Output: %eax = softness level (1=C, 2=T, 3=D, 4=unknown)

.globl  softness
softness:
        pushq   %rbp
        movq    %rsp, %rbp
        subq    $16, %rsp
        movq    %rdi, -8(%rbp)            # Store note pointer
        
        # Compare with "C"
        movq    -8(%rbp), %rax
        movl    $note_c, %esi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        jne     .not_c
        movl    $1, %eax                  # Return 1 for C
        jmp     .softness_end
.not_c:
        # Compare with "T"
        movq    -8(%rbp), %rax
        movl    $note_t, %esi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        jne     .not_t
        movl    $2, %eax                  # Return 2 for T
        jmp     .softness_end
.not_t:
        # Compare with "D"
        movq    -8(%rbp), %rax
        movl    $note_d, %esi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        jne     .not_d
        movl    $3, %eax                  # Return 3 for D
        jmp     .softness_end
.not_d:
        movl    $4, %eax                  # Return 4 for unknown
.softness_end:
        leave
        ret

# Function: op_minus (subtraction operation)
# Input: %rdi = pointer to notes array, %esi = species code
# Performs species-specific subtraction operation on the notes


.globl  op_minus
op_minus:
        pushq   %rbp
        movq    %rsp, %rbp
        subq    $64, %rsp
        movq    %rdi, -56(%rbp)           # Store notes array pointer
        movl    %esi, -60(%rbp)           # Store species code
        
        # Check if we have any notes
        movq    -56(%rbp), %rax
        movl    1024(%rax), %eax
        testl   %eax, %eax
        je      .op_minus_empty_array
        
        # Handle operation based on species
        cmpl    $2, -60(%rbp)
        je      .op_minus_nightingale
        cmpl    $2, -60(%rbp)
        ja      .op_minus_default
        cmpl    $0, -60(%rbp)
        je      .op_minus_sparrow
        cmpl    $1, -60(%rbp)
        je      .op_minus_warbler
        jmp     .op_minus_default

.op_minus_sparrow:
        # Sparrow operation: remove softest note
        movl    $-1, -4(%rbp)             # Index of softest note
        movl    $100, -8(%rbp)            # Current minimum softness
        movl    $0, -12(%rbp)             # Counter
        jmp     .op_minus_sparrow_loop
.op_minus_sparrow_loop_iter:
        # Get softness of current note
        movl    -12(%rbp), %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -56(%rbp), %rax
        addq    %rdx, %rax
        movq    %rax, %rdi
        call    softness
        movl    %eax, -36(%rbp)
        
        # Check if this is the new minimum
        movl    -36(%rbp), %eax
        cmpl    -8(%rbp), %eax
        jge     .op_minus_sparrow_loop_next
        movl    -36(%rbp), %eax
        movl    %eax, -8(%rbp)
        movl    -12(%rbp), %eax
        movl    %eax, -4(%rbp)
.op_minus_sparrow_loop_next:
        addl    $1, -12(%rbp)
.op_minus_sparrow_loop:
        movq    -56(%rbp), %rax
        movl    1024(%rax), %eax
        cmpl    %eax, -12(%rbp)
        jl      .op_minus_sparrow_loop_iter
        
        # If we found a note to remove
        cmpl    $-1, -4(%rbp)
        je      .op_minus_sparrow_end
        
        # Shift notes down to fill gap
        movl    -4(%rbp), %eax
        movl    %eax, -12(%rbp)
        jmp     .op_minus_sparrow_shift
.op_minus_sparrow_shift_iter:
        movl    -12(%rbp), %eax
        addl    $1, %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -56(%rbp), %rax
        addq    %rax, %rdx
        movl    -12(%rbp), %eax
        cltq
        leaq    0(,%rax,8), %rcx
        movq    -56(%rbp), %rax
        addq    %rcx, %rax
        movq    %rdx, %rsi
        movq    %rax, %rdi
        call    strcpy
        addl    $1, -12(%rbp)
.op_minus_sparrow_shift:
        movq    -56(%rbp), %rax
        movl    1024(%rax), %eax
        subl    $1, %eax
        cmpl    %eax, -12(%rbp)
        jl      .op_minus_sparrow_shift_iter
        
        # Decrement note count
        movq    -56(%rbp), %rax
        movl    1024(%rax), %eax
        leal    -1(%eax), %edx
        movq    -56(%rbp), %rax
        movl    %edx, 1024(%rax)
        jmp     .op_minus_sparrow_end

.op_minus_warbler:
        # Warbler operation: simply remove last note
        movq    -56(%rbp), %rax
        movl    1024(%rax), %eax
        leal    -1(%eax), %edx
        movq    -56(%rbp), %rax
        movl    %edx, 1024(%rax)
        jmp     .op_minus_end

.op_minus_nightingale:
        # Nightingale operation: remove last note if it matches second last
        movq    -56(%rbp), %rax
        movl    1024(%rax), %eax
        cmpl    $1, %eax
        jle     .op_minus_nightingale_end
        
        # Get pointers to last two notes
        movq    -56(%rbp), %rax
        movl    1024(%rax), %eax
        subl    $1, %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -56(%rbp), %rax
        addq    %rdx, %rax
        movq    %rax, -24(%rbp)           # Last note
        
        movq    -56(%rbp), %rax
        movl    1024(%rax), %eax
        subl    $2, %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -56(%rbp), %rax
        addq    %rdx, %rax
        movq    %rax, -32(%rbp)           # Second last note
        
        # Compare the two notes
        movq    -32(%rbp), %rdx
        movq    -24(%rbp), %rax
        movq    %rdx, %rsi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        jne     .op_minus_nightingale_end
        
        # If they match, remove last note
        movq    -56(%rbp), %rax
        movl    1024(%rax), %eax
        leal    -1(%eax), %edx
        movq    -56(%rbp), %rax
        movl    %edx, 1024(%rax)
        jmp     .op_minus_nightingale_end

.op_minus_empty_array:
        nop
        jmp     .op_minus_end
.op_minus_default:
        nop
        jmp     .op_minus_end
.op_minus_sparrow_end:
        nop
        jmp     .op_minus_end
.op_minus_nightingale_end:
        nop
.op_minus_end:
        leave
        ret

# Function: op_h (H operation)
# Input: %rdi = pointer to notes array, %esi = species code
# Performs species-specific H operation on the notes


.globl  op_h
op_h:
        pushq   %rbp
        movq    %rsp, %rbp
        subq    $96, %rsp
        movq    %rdi, -88(%rbp)           # Store notes array pointer
        movl    %esi, -92(%rbp)           # Store species code
        
        # Handle operation based on species
        cmpl    $2, -92(%rbp)
        je      .op_h_nightingale
        cmpl    $2, -92(%rbp)
        ja      .op_h_default
        cmpl    $0, -92(%rbp)
        je      .op_h_sparrow
        cmpl    $1, -92(%rbp)
        je      .op_h_warbler
        jmp     .op_h_default

.op_h_sparrow:
        # Sparrow operation: transform notes
        movl    $0, -4(%rbp)              # Counter
        jmp     .op_h_sparrow_loop
.op_h_sparrow_loop_iter:
        movl    -4(%rbp), %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -88(%rbp), %rax
        addq    %rdx, %rax
        movq    %rax, -16(%rbp)           # Current note pointer
        
        # Check for hyphenated notes
        movq    -16(%rbp), %rax
        movl    $45, %esi                 # '-' character
        movq    %rax, %rdi
        call    strchr
        movq    %rax, -24(%rbp)           # Pointer to hyphen
        cmpq    $0, -24(%rbp)
        je      .op_h_sparrow_single_note
        
        # Handle hyphenated note
        movq    -24(%rbp), %rax
        subq    -16(%rbp), %rax
        movl    %eax, -28(%rbp)           # Length before hyphen
        
        # Extract first part (before hyphen)
        movl    $0, -8(%rbp)              # Counter
        jmp     .op_h_sparrow_extract_first
.op_h_sparrow_extract_first_iter:
        movl    -8(%rbp), %eax
        movslq  %eax, %rdx
        movq    -16(%rbp), %rax
        addq    %rdx, %rax
        movzbl  (%rax), %edx
        movl    -8(%rbp), %eax
        cltq
        movb    %dl, -44(%rbp,%rax)       # Store in temp buffer
        addl    $1, -8(%rbp)
.op_h_sparrow_extract_first:
        movl    -8(%rbp), %eax
        cmpl    -28(%rbp), %eax
        jge     .op_h_sparrow_extract_first_end
        cmpl    $6, -8(%rbp)
        jle     .op_h_sparrow_extract_first_iter
.op_h_sparrow_extract_first_end:
        movl    -8(%rbp), %eax
        cltq
        movb    $0, -44(%rbp,%rax)        # Null-terminate
        
        # Extract second part (after hyphen)
        movq    -24(%rbp), %rax
        leaq    1(%rax), %rdx
        leaq    -52(%rbp), %rax
        movq    %rdx, %rsi
        movq    %rax, %rdi
        call    strcpy
        
        # Transform first part
        leaq    -44(%rbp), %rax
        movl    $note_c, %esi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        jne     .op_h_sparrow_first_not_c
        leaq    -44(%rbp), %rax
        movw    $84, (%rax)               # Change "C" to "T"
        jmp     .op_h_sparrow_transform_second
.op_h_sparrow_first_not_c:
        leaq    -44(%rbp), %rax
        movl    $note_t, %esi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        jne     .op_h_sparrow_first_not_t
        leaq    -44(%rbp), %rax
        movw    $67, (%rax)               # Change "T" to "C"
        jmp     .op_h_sparrow_transform_second
.op_h_sparrow_first_not_t:
        leaq    -44(%rbp), %rax
        movl    $note_d, %esi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        jne     .op_h_sparrow_transform_second
        leaq    -44(%rbp), %rax
        movl    $5516612, (%rax)          # Change "D" to "CT"
        
.op_h_sparrow_transform_second:
        # Transform second part
        leaq    -52(%rbp), %rax
        movl    $note_c, %esi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        jne     .op_h_sparrow_second_not_c
        leaq    -52(%rbp), %rax
        movw    $84, (%rax)               # Change "C" to "T"
        jmp     .op_h_sparrow_combine
.op_h_sparrow_second_not_c:
        leaq    -52(%rbp), %rax
        movl    $note_t, %esi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        jne     .op_h_sparrow_second_not_t
        leaq    -52(%rbp), %rax
        movw    $67, (%rax)               # Change "T" to "C"
        jmp     .op_h_sparrow_combine
.op_h_sparrow_second_not_t:
        leaq    -52(%rbp), %rax
        movl    $note_d, %esi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        jne     .op_h_sparrow_combine
        leaq    -52(%rbp), %rax
        movl    $5516612, (%rax)          # Change "D" to "CT"
        
.op_h_sparrow_combine:
        # Combine transformed parts
        leaq    -52(%rbp), %rcx
        leaq    -44(%rbp), %rdx
        leaq    -36(%rbp), %rax
        movq    %rcx, %r8
        movq    %rdx, %rcx
        movl    $format_string_combine, %edx
        movl    $8, %esi
        movq    %rax, %rdi
        movl    $0, %eax
        call    snprintf
        
        # Store back in notes array
        movl    -4(%rbp), %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -88(%rbp), %rax
        addq    %rax, %rdx
        leaq    -36(%rbp), %rax
        movq    %rax, %rsi
        leaq    -36(%rbp), %rax
        movq    %rax, %rsi
        movq    %rdx, %rdi
        call    strcpy
        jmp     .op_h_sparrow_next_note

.op_h_sparrow_single_note:
        # Handle single note (not hyphenated)
        movq    -16(%rbp), %rax
        movl    $note_c, %esi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        jne     .op_h_sparrow_single_not_c
        movl    -4(%rbp), %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -88(%rbp), %rax
        addq    %rdx, %rax
        movw    $84, (%rax)               # Change "C" to "T"
        jmp     .op_h_sparrow_next_note
.op_h_sparrow_single_not_c:
        movq    -16(%rbp), %rax
        movl    $note_t, %esi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        jne     .op_h_sparrow_single_not_t
        movl    -4(%rbp), %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -88(%rbp), %rax
        addq    %rdx, %rax
        movw    $67, (%rax)               # Change "T" to "C"
        jmp     .op_h_sparrow_next_note
.op_h_sparrow_single_not_t:
        movq    -16(%rbp), %rax
        movl    $note_d, %esi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        jne     .op_h_sparrow_next_note
        movl    -4(%rbp), %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -88(%rbp), %rax
        addq    %rdx, %rax
        movl    $5516612, (%rax)          # Change "D" to "CT"

.op_h_sparrow_next_note:
        addl    $1, -4(%rbp)
.op_h_sparrow_loop:
        movq    -88(%rbp), %rax
        movl    1024(%rax), %eax
        cmpl    %eax, -4(%rbp)
        jl      .op_h_sparrow_loop_iter
        jmp     .op_h_end

.op_h_warbler:
        # Warbler operation: add a "T" note if space allows
        movq    -88(%rbp), %rax
        movl    1024(%rax), %eax
        cmpl    $127, %eax
        jg      .op_h_warbler_end
        
        # Add "T" note
        movq    -88(%rbp), %rax
        movl    1024(%rax), %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -88(%rbp), %rax
        addq    %rdx, %rax
        movw    $84, (%rax)               # "T"
        
        # Increment note count
        movq    -88(%rbp), %rax
        movl    1024(%rax), %eax
        leal    1(%rax), %edx
        movq    -88(%rbp), %rax
        movl    %edx, 1024(%rax)
        jmp     .op_h_warbler_end

.op_h_nightingale:
        # Nightingale operation: transform last three notes
        movq    -88(%rbp), %rax
        movl    1024(%rax), %eax
        cmpl    $2, %eax
        jle     .op_h_nightingale_end
        
        # Get last three notes
        movq    -88(%rbp), %rax
        movl    1024(%rax), %eax
        subl    $3, %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -88(%rbp), %rax
        addq    %rax, %rdx
        leaq    -60(%rbp), %rax
        movq    %rdx, %rsi
        movq    %rax, %rdi
        call    strcpy                    # Third last note
        
        movq    -88(%rbp), %rax
        movl    1024(%rax), %eax
        subl    $2, %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -88(%rbp), %rax
        addq    %rax, %rdx
        leaq    -68(%rbp), %rax
        movq    %rdx, %rsi
        movq    %rax, %rdi
        call    strcpy                    # Second last note
        
        movq    -88(%rbp), %rax
        movl    1024(%rax), %eax
        subl    $1, %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -88(%rbp), %rax
        addq    %rax, %rdx
        leaq    -76(%rbp), %rax
        movq    %rdx, %rsi
        movq    %rax, %rdi
        call    strcpy                    # Last note
        
        # Transform third last note: combine with last note
        movq    -88(%rbp), %rax
        movl    1024(%rax), %eax
        subl    $3, %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -88(%rbp), %rax
        leaq    (%rdx,%rax), %rdi
        leaq    -76(%rbp), %rdx
        leaq    -60(%rbp), %rax
        movq    %rdx, %r8
        movq    %rax, %rcx
        movl    $format_string_combine, %edx
        movl    $8, %esi
        movl    $0, %eax
        call    snprintf
        
        # Transform second last note: combine with third last
        movq    -88(%rbp), %rax
        movl    1024(%rax), %eax
        subl    $2, %eax
        cltq
        leaq    0(,%rax,8), %rdx
        movq    -88(%rbp), %rax
        leaq    (%rdx,%rax), %rdi
        leaq    -60(%rbp), %rdx
        leaq    -68(%rbp), %rax
        movq    %rdx, %r8
        movq    %rax, %rcx
        movl    $format_string_combine, %edx
        movl    $8, %esi
        movl    $0, %eax
        call    snprintf
        
        # Remove last note
        movq    -88(%rbp), %rax
        movl    1024(%rax), %eax
        leal    -1(%eax), %edx
        movq    -88(%rbp), %rax
        movl    %edx, 1024(%rax)
        jmp     .op_h_nightingale_end

.op_h_default:
        nop
        jmp     .op_h_end
.op_h_warbler_end:
        nop
        jmp     .op_h_end
.op_h_nightingale_end:
        nop
.op_h_end:
        nop
        leave
        ret

# Function: process_input_line
# Input: %rdi = pointer to input line string
# Processes a line of input commands
        .globl  process_input_line
process_input_line:
        pushq   %rbp
        movq    %rsp, %rbp
        subq    $1872, %rsp
        movq    %rdi, -1864(%rbp)         # Store input line pointer
        
        # Copy input line to local buffer
        movq    -1864(%rbp), %rcx
        leaq    -304(%rbp), %rax
        movl    $256, %edx
        movq    %rcx, %rsi
        movq    %rax, %rdi
        call    strncpy
        movb    $0, -49(%rbp)             # Null terminator
        
        # Tokenize input
        movl    $0, -4(%rbp)              # Token count
        leaq    -304(%rbp), %rax
        movl    $space_char, %esi
        movq    %rax, %rdi
        call    strtok
        movq    %rax, -16(%rbp)           # First token
        jmp     .process_tokens
.process_next_token:
        # Store token
        movl    -4(%rbp), %eax
        cltq
        movq    -16(%rbp), %rdx
        movq    %rdx, -816(%rbp,%rax,8)   # Store in tokens array
        addl    $1, -4(%rbp)
        
        # Get next token
        movl    $space_char, %esi
        movl    $0, %edi
        call    strtok
        movq    %rax, -16(%rbp)
.process_tokens:
        cmpq    $0, -16(%rbp)             # Check if token exists
        je      .tokens_done
        cmpl    $63, -4(%rbp)             # Check max tokens
        jle     .process_next_token
.tokens_done:

        # Check if we have any tokens
        cmpl    $0, -4(%rbp)
        je      .process_input_line_end
        
        # Get species from first token
        movq    -816(%rbp), %rax
        movq    %rax, %rdi
        call    get_species
        movl    %eax, -32(%rbp)           # Store species code
        
        # Check for unknown species
        cmpl    $3, -32(%rbp)
        jne     .species_known
        movq    -816(%rbp), %rax
        movq    %rax, %rsi
        movl    $error_unknown_species, %edi
        movl    $0, %eax
        call    printf
        jmp     .process_input_line_end

.species_known:
        # Initialize notes array
        movl    $0, -832(%rbp)            # Note count
        movl    $1, -20(%rbp)             # Token index (skip species)
        jmp     .process_initial_notes
.process_initial_note:
        # Check if token is a note (C, T, or D)
        movl    -20(%rbp), %eax
        cltq
        movq    -816(%rbp,%rax,8), %rax
        movl    $note_c, %esi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        je      .is_note
        movl    -20(%rbp), %eax
        cltq
        movq    -816(%rbp,%rax,8), %rax
        movl    $note_t, %esi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        je      .is_note
        movl    -20(%rbp), %eax
        cltq
        movq    -816(%rbp,%rax,8), %rax
        movl    $note_d, %esi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        jne     .not_note
.is_note:
        # Add note to array
        movl    -20(%rbp), %eax
        cltq
        movq    -816(%rbp,%rax,8), %rax
        movl    -832(%rbp), %ecx
        leaq    -1856(%rbp), %rdx
        movslq  %ecx, %rcx
        salq    $3, %rcx
        addq    %rcx, %rdx
        movq    %rax, %rsi
        movq    %rdx, %rdi
        call    strcpy
        movl    -832(%rbp), %eax
        addl    $1, %eax
        movl    %eax, -832(%rbp)
        addl    $1, -20(%rbp)
.process_initial_notes:
        movl    -20(%rbp), %eax
        cmpl    -4(%rbp), %eax
        jl      .process_initial_note
.not_note:

        # Process operations
        movl    $0, -24(%rbp)             # Generation counter
        jmp     .process_operations
.process_operation:
        # Get operation character
        movl    -20(%rbp), %eax
        cltq
        movq    -816(%rbp,%rax,8), %rax
        movzbl  (%rax), %eax
        movb    %al, -33(%rbp)
        
        # Check if it's a known operation
        cmpb    $43, -33(%rbp)            # '+'
        je      .valid_operation
        cmpb    $42, -33(%rbp)            # '*'
        je      .valid_operation
        cmpb    $45, -33(%rbp)            # '-'
        je      .valid_operation
        cmpb    $72, -33(%rbp)            # 'H'
        jne     .not_operation
.valid_operation:
        # Perform the operation
        movsbl  -33(%rbp), %eax
        cmpl    $72, %eax
        je      .op_h_case
        cmpl    $72, %eax
        jg      .default_case
        cmpl    $45, %eax
        je      .op_minus_case
        cmpl    $45, %eax
        jg      .default_case
        cmpl    $42, %eax
        je      .op_star_case
        cmpl    $43, %eax
        jne     .default_case
        # '+' operation
        cmpl    $43, %eax
        jne     .default_case
        movl    -32(%rbp), %edx
        leaq    -1856(%rbp), %rax
        movl    %edx, %esi
        movq    %rax, %rdi
        call    op_plus
        jmp     .after_operation

.default_case:
        nop
        jmp     .after_operation

.op_star_case:
        # '*' operation
        movl    -32(%rbp), %edx
        leaq    -1856(%rbp), %rax
        movl    %edx, %esi
        movq    %rax, %rdi
        call    op_star
        jmp     .after_operation
.op_minus_case:
        # '-' operation
        movl    -32(%rbp), %edx
        leaq    -1856(%rbp), %rax
        movl    %edx, %esi
        movq    %rax, %rdi
        call    op_minus
        jmp     .after_operation
.op_h_case:
        # 'H' operation
        movl    -32(%rbp), %edx
        leaq    -1856(%rbp), %rax
        movl    %edx, %esi
        movq    %rax, %rdi
        call    op_h
        nop
.after_operation:
        # Print generation
        movq    -816(%rbp), %rax
        movl    -24(%rbp), %edx
        movq    %rax, %rsi
        movl    $format_generation, %edi
        movl    $0, %eax
        call    printf
        
        # Print all notes
        addl    $1, -24(%rbp)
        movl    $0, -28(%rbp)
        jmp     .print_notes
.print_note:
        leaq    -1856(%rbp), %rax
        movl    -28(%rbp), %edx
        movslq  %edx, %rdx
        salq    $3, %rdx
        addq    %rdx, %rax
        movq    %rax, %rsi
        movl    $format_note, %edi
        movl    $0, %eax
        call    printf
        addl    $1, -28(%rbp)
.print_notes:
        movl    -832(%rbp), %eax
        cmpl    %eax, -28(%rbp)
        jl      .print_note
        
        # Newline
        movl    $10, %edi
        call    putchar
        
        # Move to next token
        addl    $1, -20(%rbp)
        jmp     .process_operations


.not_operation:
        # Check if it's a note to add
        movl    -20(%rbp), %eax
        cltq
        movq    -816(%rbp,%rax,8), %rax
        movl    $note_c, %esi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        je      .add_note
        movl    -20(%rbp), %eax
        cltq
        movq    -816(%rbp,%rax,8), %rax
        movl    $note_t, %esi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        je      .add_note
        movl    -20(%rbp), %eax
        cltq
        movq    -816(%rbp,%rax,8), %rax
        movl    $note_d, %esi
        movq    %rax, %rdi
        call    strcmp
        testl   %eax, %eax
        jne     .skip_token
.add_note:
        # Add note to array
        movl    -20(%rbp), %eax
        cltq
        movq    -816(%rbp,%rax,8), %rax
        movl    -832(%rbp), %ecx
        leaq    -1856(%rbp), %rdx
        movslq  %ecx, %rcx
        salq    $3, %rcx
        addq    %rcx, %rdx
        movq    %rax, %rsi
        movq    %rdx, %rdi
        call    strcpy
        movl    -832(%rbp), %eax
        addl    $1, %eax
        movl    %eax, -832(%rbp)
        addl    $1, -20(%rbp)
        jmp     .process_operations
.skip_token:
        addl    $1, -20(%rbp)
.process_operations:
        movl    -20(%rbp), %eax
        cmpl    -4(%rbp), %eax
        jl      .process_operation
        jmp     .process_input_line_end
.process_input_line_end:
        leave
        ret
# Main function
# This is the entry point of our bird song simulator
# It reads commands from stdin and processes them until user exits
.globl  main
main:
        # Set up stack frame
        pushq   %rbp
        movq    %rsp, %rbp
        subq    $256, %rsp                # Reserve space for input_buffer
command_loop:
        # Read a line of input from the user
        movq    stdin(%rip), %rdx         # File stream for stdin
        leaq    -256(%rbp), %rax         # Load address of input_buffer
        movl    $256, %esi               # Max chars to read
        movq    %rax, %rdi               # Buffer to read into
        call    fgets                    # Read line from stdin
        testq   %rax, %rax              # Check if we hit EOF
        je      finish_program           # If EOF, exit gracefully
        # Clean up the input by removing trailing newline
        leaq    -256(%rbp), %rax        # Get input_buffer address
        movl    $newline, %esi          # "\n" string to search for
        movq    %rax, %rdi              # Search in input_buffer
        call    strcspn                 # Find position of newline
        movb    $0, -256(%rbp,%rax)     # Replace newline with null
        # Check if user wants to exit
        leaq    -256(%rbp), %rax        # input_buffer address
        movl    $cmd_exit, %esi         # "exit" command string
        movq    %rax, %rdi              # Compare input_buffer
        call    strcmp
        testl   %eax, %eax             # If strings match (result = 0)
        je      finish_program          # Exit if command was "exit"
        # Also check for alternate quit command
        leaq    -256(%rbp), %rax        # input_buffer address again
        movl    $cmd_quit, %esi         # "quit" command string
        movq    %rax, %rdi              # Compare input_buffer
        call    strcmp
        testl   %eax, %eax             # If strings match
        je      finish_program          # Exit if command was "quit"
        # Process the command line
        leaq    -256(%rbp), %rax        # Get input_buffer
        movq    %rax, %rdi              # Pass as parameter
        call    process_input_line      # Process the command
        jmp     command_loop            # Continue reading commands
finish_program:
        movl    $0, %eax
        leave
        ret