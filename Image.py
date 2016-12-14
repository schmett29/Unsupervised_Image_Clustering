#All text files will be read into this class
import math
import numpy as np
from scipy import ndimage
import operator
from numpy.linalg import svd
class Image(object):

    def __init__(self,file_name,rows=0,cols=0):
        self.file_name = file_name.split('/')[-1]
        self.original_matrix = self._create_matrix(file_name)
        self.area_ = self.area()
        self.rows = self.original_matrix.shape[0]
        self.cols = self.original_matrix.shape[1]
        self.size = len(self.original_matrix)*len(self.original_matrix[0])
        # print "ORIGINAL"
        # print self.original_matrix
        # print

        #BLUR Image, get area and coordinates of blurred image object
        self.b_matrix = self.mean_average_blur()
        self.b_area_ = self.b_area()
        self.b_center = self.b_center_of_area()
        #
        # print "BLURRED"
        # print self.b_matrix
        # print

        self.b_radians = self.b_axis_of_least_second_movement()
        self.r_b_matrix = self.rotate_blurred_matrix()


        # print "ROTATED"
        # print self.r_b_matrix
        # print

        self.z_r_b_matrix = self.zoom()








        # print "ZOOMED"
        # print self.z_r_b_matrix
        # print

        self.z_rows = self.z_r_b_matrix.shape[0]
        self.z_cols = self.z_r_b_matrix.shape[1]

        self.scale_cols = self.cols/self.z_cols
        self.scale_rows = self.rows/self.z_rows

        self.s_z_r_b_matrix = self.scale()
        self.corners = self.cornerDetector()

        self.grouped_corners = self.buildPockets()

        # img = self.s_z_r_b_matrix
        # for x,y in self.grouped_corners:
        #     img[x][y] = 5
        # print img

        self.neighborhoods = self.corner_neighborhood()

        self.edges = self.getEdgeList()

        self.edge_groups = self.edges_neighborhood()


    def _create_matrix(self,name): #reads image from textfile into numpy array
        file = open(name,'r')
        array = []
        for line in file:
            #print line
            array.append([int(x) for x in line.split(" ")])
        return np.array(array)

    def rotate_blurred_matrix(self):
        rads = self.b_radians
        return ndimage.rotate(self.b_matrix, -math.degrees(rads),reshape=False)


    def decisionTree(self, database_images,k=9,
                     area_sigma=30,
                     b_area_sigma=30,
                     center_diff_sigma=5,
                     rads_sigma=0.01,
                     scale_cols_sigma=1,
                     scale_rows_sigma=1,
                     hamming_simga1=.8,
                     hamming_simga2=.85,
                     hamming_simga3=.9,
                     hamming_simga4=.9,
                     ):  #return k closets neighbors
        euclideanDistance = lambda a,b: math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
        score =  {image: 0 for image in database_images}

        for image in database_images:
            points = 0
            if abs(self.area_ - image.area_) < area_sigma:
                points+=2
            else:
                points-=1

            if abs(self.b_area_ - image.b_area_) < b_area_sigma:
                points+=2
            else:
                points-=1

            if euclideanDistance(self.b_center,image.b_center) < center_diff_sigma:
                points+=2
            else:
                points-=1

            if abs(self.b_radians - image.b_radians) == rads_sigma:
                points+=2
            else:
                points-=1

            if abs(self.scale_cols - image.scale_cols) < scale_cols_sigma:
                points+=2
            else:
                points-=1

            if abs(self.scale_rows - image.scale_rows) < scale_rows_sigma:
                points+=2
            else:
                points-=1

            if self.hamming_distance4(image.s_z_r_b_matrix) > hamming_simga1:
                points+=2
            else:
                points-=1

            if self.hamming_distance4(image.s_z_r_b_matrix) > hamming_simga2:
                points+=2
            else:
                points-=1

            if self.hamming_distance4(image.s_z_r_b_matrix) > hamming_simga3:
                points+=3

            if self.hamming_distance4(image.s_z_r_b_matrix) > hamming_simga4:
                points+=4


            #points+= - abs(len(self.neighborhoods)-len(image.neighborhoods))**2

            c = 0
            #a = self.edges
            for neighborhood1 in self.neighborhoods:
                #print svd(neighborhood1)
                U1= svd(neighborhood1,compute_uv=False)
                for neighborhood2 in image.neighborhoods:

                    U2= svd(neighborhood2,compute_uv=False)

                    #print svd(neighborhood1) - svd(neighborhood2,compute_uv=False)
                    diff = abs(sum(U1 - U2))

                    # print diff
                    if diff==0:

                        points+=2
                        c+=1

            score[image] = points

        out = []
        d = dict(sorted(score.iteritems(), key=operator.itemgetter(1), reverse=True)[:int(k)])
        count = 0
        for key in d:
            out.append(key.file_name)
            if key.file_name.startswith(self.file_name[:3]):
                count+=1
        return out,count




    def corner_neighborhood(self):
        corners = self.grouped_corners
        img = self.s_z_r_b_matrix
        neighborhoods = []

        for r,c in corners:
            try:
                neighborhood = np.array([img[a][b] for a in range(r-2,r+3) for b in range(c-2,c+3)]).reshape((5,5))
            except IndexError:
                continue
            #print neighborhood
            neighborhoods.append(neighborhood)

        return neighborhoods


    def edges_neighborhood(self):
        corners = self.edges
        img = self.s_z_r_b_matrix
        neighborhoods = []
        for r,c in corners:
            try:
                neighborhood = np.array([img[a][b] for a in range(r-2,r+3) for b in range(c-2,c+3)]).reshape((5,5))
            except IndexError:
                continue
            #print neighborhood
            neighborhoods.append(neighborhood)

        return neighborhoods



    def zoom(self):
        r,c = self.b_center
        img = self.r_b_matrix
        #print r,c

        side_rows = round((self.b_area_)**.5)
        side_cols = side_rows


        return img

        while self.rows%side_rows !=0: #so that it scaled properly
            side_rows+=1
        while self.cols%side_cols !=0: #so that it scaled properly
            side_cols+=1

        print side_rows,side_cols

        offset_r = side_rows
        offset_c = side_cols+1
        x = img[max(0,r-offset_r):min(r+offset_r,self.rows),max(0,c-offset_c):min(self.cols,c+offset_c)]
        return x





    def mean_average_blur(self,alpha = 10): #blures the object, removes noise
        image_array = self.original_matrix
        image_output = image_array.copy()
        height=len(image_array)
        width = len(image_array[0])
        image_array[0] = [0]*width
        image_array[height-1] = [0]*width
        for x in range(height):
            image_array[x][0]=0
            image_array[x][width-1]=0

        for row in range(height):
            for col in range(width):
                #rowStart = row/alpha*alpha
                #colStart = col/alpha*alpha
                neighbors = [image_array[x][y] for x in range(max(row-2,0),min(row+2,height)) for y in range(max(0,col-2),min(col+2,width))]
                ones = neighbors.count(1)
                zeros = neighbors.count(0)
                image_output[row][col] = 1 if ones>=zeros else 0

        return image_array
        #return image_output

    def __len__(self):
        return self.size

    def rows(self):
        return self.rows

    def cols(self):
        return self.cols

    def b_area(self):
        return self.b_matrix.sum()

    def area(self):
        return self.original_matrix.sum()



    def b_center_of_area(self): #returns estimated center of object
        img = self.b_matrix
        #self.area_ = self.b_area
        r_=0
        c_=0
        for r in range(self.rows):
            for c in range(self.cols):
                r_+= r*img[r][c]
                c_+= c*img[r][c]
        a = 1./self.b_area_
        r_ = r_*a
        c_ = c_*a

        return int(round(r_)),int(round(c_))



    def b_axis_of_least_second_movement(self): #returns the radian degree of rotation
        a = 0.0
        b = 0.0
        c = 0.0
        img = self.b_matrix
        c_,r_ = self.b_center_of_area()
        for r in range(self.rows):
            for c in range(self.cols):
                a+= (r - r_)*(c-c_)*img[r][c]
                b+= (r-r_)**2*img[r][c]
                c+= (c-c_)**2*img[r][c]
        out = 2.*a/(b - c)
        return 0.5*math.atan(out)


    def hamming_distance1(self,arr2):
        img = self.original_matrix
        shared = 0.0
        for r in range(self.rows):
            for c in range(self.cols):
                if img[r][c] == arr2[r][c]:
                    shared+=1
        return shared/self.size


    def hamming_distance2(self,arr2):
        img = self.b_matrix
        shared = 0.0
        for r in range(self.rows):
            for c in range(self.cols):
                if img[r][c] == arr2[r][c]:
                    shared+=1
        return shared/self.size


    def hamming_distance3(self,arr2):
        img = self.r_b_matrix
        shared = 0.0
        for r in range(self.rows):
            for c in range(self.cols):
                if img[r][c] == arr2[r][c]:
                    shared+=1
        return shared/self.size


    def hamming_distance4(self,arr2):
        img = self.s_z_r_b_matrix
        shared = 0.0
        for r in range(self.rows):
            for c in range(self.cols):
                if img[r][c] == arr2[r][c]:
                    shared+=1
        return shared/self.size




    def scale(self): #Kronecker product


        a = np.kron(self.z_r_b_matrix, np.ones((self.scale_rows,self.scale_cols)))


        return a.astype(int)




    def cornerDetector(self):
        corners = []
        image_array = self.s_z_r_b_matrix
        rows = self.rows
        cols = self.cols

        for i in range(rows):
            for j in range(cols):
                if image_array[i][j] ==1:
                    neighbors = [image_array[x][y] for x in range(max(i-1,0),min(i+2,rows)) for y in range(max(0,j-1),min(j+2,cols))]
                    #print neighbors
                    if neighbors.count(0)>4:
                        corners.append((i,j))
        self.corners = corners
        return corners


    def buildPockets_recurse(self,t,corners):
        x,y = t[0],t[1]
        #print "looking at neighbors of",(x,y),
        #print "corners is currently",corners
        if len(corners) == 0:
            return []
        pocket = []
        neighbors = [(a,b) for a in range(x-2,x+3) for b in range(y-2,y+3)] # grab the nearest corners
        neighbors.remove((x,y))
        for z,w in neighbors:
            if (z,w) in corners:

                corners.remove((z,w))
                pocket.extend([(z,w)] + self.buildPockets_recurse((z,w),corners))
        return pocket


    def buildPockets(self):
        pockets = []
        corners = list(self.corners)
        getKey = lambda a : math.sqrt(a[0]**2+a[1]**2)
        corners = sorted(corners,key=getKey)
        #print corners
        for i in range(len(self.corners)):
            if not corners:
                break
            x,y = corners.pop(0) # pop off the first corner
            pocket = [(x,y)]
            neighbors = [(a,b) for a in range(x-2,x+3) for b in range(y-2,y+3)] # grab the nearest corners
            neighbors.remove((x,y))
            for z,w in neighbors:
                if (z,w) in corners:
                    #print "found neighbor",(z,w)
                    corners.remove((z,w))

                    pocket.extend([(z,w)] + self.buildPockets_recurse((z,w),corners))

            pockets.append(pocket)
            #print "pockets",pockets
        pockets_averaged = []
        #print "here",pockets
        for group in pockets:
            #print group
            avg_x = sum([p[0] for p in group])/len(group)
            avg_y = sum([p[1] for p in group])/len(group)
            pockets_averaged.append((avg_x,avg_y))
        #print 1
        return pockets_averaged



    def intensityMap(self):  #UNUSED
        #corners = []
        image_array = self.matrix
        image_out = image_array
        rows = self.rows
        cols = self.cols
        for i in range(rows):
            for j in range(cols):
                if image_array[i][j] ==1:
                    neighbors = [image_array[x][y] for x in range(max(i-1,0),min(i+2,rows)) for y in range(max(0,j-1),min(j+2,cols))]
                    #print neighbors
                    image_out[i][j] = neighbors.count(1)

        return image_out

    def distances(self):
        points = self.grouped_corners
        if(len(points) > 1):
            distances = {}
            for i in range(len(points)):
                a = points[i]
                for j in range(i + 1, len(points)):
                    b = points[j]
                    distances[(a,b)] = math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
            maximum = max(distances, key=distances.get)
            print "Max distance between " + str(maximum) + "= " + str(distances[maximum])
            minimum = min(distances, key=distances.get)
            print "Min distance between " + str(minimum) + "= " + str(distances[minimum])
        else:
            print "Only " + str(len(points)) + " point(s)"


    def getEdgeList(self):
        edgelist = []
        edge_horizont = ndimage.sobel(self.s_z_r_b_matrix, 0)
        edge_vertical = ndimage.sobel(self.s_z_r_b_matrix, 1)
        magnitude = np.hypot(edge_horizont, edge_vertical)
        for x in range(len(magnitude)):
            for y in range(len(magnitude[x])):
                if magnitude[x][y] != float(0):
                    edgelist.append((x, y))
        return edgelist


















