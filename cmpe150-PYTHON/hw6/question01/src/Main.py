inp_filename, operation, out_filename = input().split()


# DO_NOT_EDIT_ANYTHING_ABOVE_THIS_LINE
def transpose(img_matrix):#bunu ben kendim fazladan lazim olur diye ekledim.
    output_matrix = [[0] * len(img_matrix) for _ in range(len(img_matrix[0]))]
    for i in range(len(img_matrix)):
        for j in range(len(img_matrix[0])):
            output_matrix[j][i] = img_matrix[i][j]
    return output_matrix
def read_imagefile(f):
    global height
    img_matrix=[]
    f = open(inp_filename,"r")
    code, width, height, maclevel = f.readline().rstrip().split()

    width = int(width)
    height = int(height)
    for i in range(height):img_matrix.append([])

    for i in range(height):
        for j in f.readline().rstrip().split():
            img_matrix[i].append(j)
    return img_matrix

def misalign(img_matrix):
    for i in range(len(img_matrix)):
        if i % 2 == 1:
            img_matrix[i] = img_matrix[i][::-1]
    img_matrix = img_matrix[::-1]
    return img_matrix

def sort_columns(img_matrix):
    transposed_img_matrix = transpose(img_matrix)
    for i in range(len(transposed_img_matrix)):
        transposed_img_matrix[i].sort()
    return transposed_img_matrix
def sort_rows_border(img_matrix):

    borders = []
    for i in range(len(img_matrix)):
        if any(pixel == 0 for pixel in img_matrix[i]):
            borders.append(i)
    sub_images = []
    start = 0
    for border in borders:
        sub_images.append(img_matrix[start:border])
        start = border + 1
    sub_images.append(img_matrix[start:])
    sub_images.sort(key=lambda x: x[0])
    sorted_img_matrix = []
    for sub_image in sub_images:
        sorted_img_matrix.extend(sub_image)
    return sorted_img_matrix

def convolution(img_matrix, kernel):
    padding_size = len(kernel) // 2
    img_matrix = [[0] * padding_size + row + [0] * padding_size for row in img_matrix]
    img_matrix = [[0] * len(img_matrix[0])] * padding_size + img_matrix + [[0] * len(img_matrix[0])] * padding_size

    output_matrix = [[0] * len(img_matrix[0]) for _ in range(len(img_matrix))]
    for i in range(padding_size, len(img_matrix) - padding_size):
        for j in range(padding_size, len(img_matrix[0]) - padding_size):
            region = [row[j - padding_size:j + padding_size + 1] for row in img_matrix[i - padding_size:i + padding_size + 1]]
            output_matrix[i][j] = sum([sum([int(region[x][y]) * int(kernel[x][y]) for y in range(3)]) for x in range(3)])
    output_matrix = [row[padding_size:-padding_size] for row in output_matrix[padding_size:-padding_size]]
    return output_matrix

def write_imagefile(f,img_matrix):
    header = "P2 {} {} 255\n".format(len(img_matrix[0]), len(img_matrix))
    f.write(header)
    for row in img_matrix:
        for pixel in row:
            f.write(str(pixel) + " ")
        f.write("\n")

# DO_NOT_EDIT_ANYTHING_BELOW_THIS_LINE
f = open(inp_filename, "r")
img_matrix = read_imagefile(f)
f.close()

if operation == "misalign":
    img_matrix = misalign(img_matrix)

elif operation == "sort_columns":
    img_matrix = sort_columns(img_matrix)

elif operation == "sort_rows_border":
    img_matrix = sort_rows_border(img_matrix)

elif operation == "highpass":
    kernel = [
        [-1, -1, -1],
        [-1, 9, -1],
        [-1, -1, -1]
    ]
    img_matrix = convolution(img_matrix, kernel)

f = open(out_filename, "w")
write_imagefile(f, img_matrix)
f.close()
